"""Library: keep accepted history durable and portable.

Every revision of every record lives in one append-only ``records`` table using the
portable envelope ``{kind, id, revision, sequence, recorded_at, payload}``. A command
runs in one SQLite transaction and commits one receipt; a retry with the same
request ID returns that receipt. The Library never interprets payloads: owners
validate their own records, and every write or kind-scoped read names its owner.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, cast

from pydantic import ValidationError

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Iterator
    from pathlib import Path

    from pydantic import BaseModel

type JSON = dict[str, Any]
type Clock = Callable[[], datetime]

SCHEMA_VERSION = 1
FORMAT_VERSION = 1
MAX_SAFE_INTEGER = 9007199254740991

# The single ordinary writer of every portable record kind (module-design.md).
KIND_OWNER: dict[str, str] = {
    **dict.fromkeys(
        ["source", "knowledge", "target", "curriculum", "exercise", "teaching", "mapping"],
        "content",
    ),
    **dict.fromkeys(
        [
            "attempt",
            "study",
            "assessment",
            "review",
            "projection",
            "exposure",
            "condition_checkpoint",
        ],
        "evidence",
    ),
    **dict.fromkeys(
        ["enrollment", "session", "concern", "schedule", "practice_offer", "selection"],
        "practice",
    ),
    **dict.fromkeys(
        [
            "timing_run",
            "activity_span",
            "session_feedback",
            "measurement_cohort",
            "measurement_report",
        ],
        "measurement",
    ),
    **dict.fromkeys(["operation", "transition"], "workflows"),
}


class Conflict(Exception):  # noqa: N818 - a domain outcome, not a programming error
    """A stale expected revision, or a request ID reused with different input."""


def utc(moment: datetime) -> str:
    """Format a moment as the portable UTC ``Time`` (millisecond precision)."""
    t = moment.astimezone(UTC)
    return t.strftime("%Y-%m-%dT%H:%M:%S.") + f"{t.microsecond // 1000:03d}Z"


def parse_utc(text: str) -> datetime:
    """Parse a portable ``Time`` string."""
    return datetime.strptime(text, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC)


def canonical(value: object) -> bytes:
    """Serialize float-free JSON as RFC 8785 (JCS) bytes.

    ponytail: records hold no floats and only ASCII keys, so sorted compact JSON is
    exactly JCS; a float is refused rather than formatted. Add ECMAScript number
    formatting if a record ever needs one.
    """
    _check_jcs_safe(value)
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode()


def _check_jcs_safe(value: object) -> None:
    children = _children(value)
    if isinstance(value, float):
        msg = "floats are not allowed in portable records"
        raise TypeError(msg)
    if isinstance(value, int) and not isinstance(value, bool) and abs(value) > MAX_SAFE_INTEGER:
        msg = "integer exceeds the portable safe range"
        raise ValueError(msg)
    if isinstance(value, dict) and not all(
        isinstance(k, str) for k in cast("dict[object, object]", value)
    ):
        msg = "object keys must be strings"
        raise TypeError(msg)
    for child in children:
        _check_jcs_safe(child)


def _children(value: object) -> list[object]:
    if isinstance(value, dict):
        return list(cast("dict[str, object]", value).values())
    if isinstance(value, list):
        return list(cast("list[object]", value))
    return []


def digest(value: object) -> str:
    """SHA-256 hex digest of the canonical form."""
    return hashlib.sha256(canonical(value)).hexdigest()


def new_id() -> str:
    """Return a new opaque record identity, never derived from content."""
    return str(uuid.uuid4())


def ref(kind: str, id_: str, revision: int) -> JSON:
    """Return an exact reference to one record revision."""
    return {"kind": kind, "id": id_, "revision": revision}


def exact_key(reference: JSON) -> tuple[str, int]:
    """Return what identifies one exact revision in a ref: its id and revision."""
    return (reference["id"], reference["revision"])


@dataclass(frozen=True)
class Record:
    """One revision of a portable record."""

    kind: str
    id: str
    revision: int
    sequence: int
    recorded_at: str
    payload: JSON

    @property
    def ref(self) -> JSON:
        """The exact reference to this revision."""
        return ref(self.kind, self.id, self.revision)

    @property
    def view(self) -> JSON:
        """The payload with its exact reference, as read views return it."""
        return {"ref": self.ref, **self.payload}


@dataclass(frozen=True)
class Receipt:
    """The committed outcome of one command; replayed for a retried request ID."""

    request_id: str
    command: str
    input_digest: str
    result: JSON
    first_sequence: int | None
    committed_sequence: int | None
    record_refs: list[JSON]


def _check_owner(kind: str, by: str) -> None:
    owner = KIND_OWNER.get(kind)
    if owner is None:
        msg = f"unknown record kind {kind!r}"
        raise ValueError(msg)
    if owner != by:
        msg = f"{by} cannot access {kind} records; {owner} owns them"
        raise PermissionError(msg)


def _record(row: sqlite3.Row) -> Record:
    return Record(
        kind=row["kind"],
        id=row["id"],
        revision=row["revision"],
        sequence=row["sequence"],
        recorded_at=row["recorded_at"],
        payload=json.loads(row["payload"]),
    )


class Tx:
    """A consistent view of the store inside one command or read."""

    def __init__(self, conn: sqlite3.Connection, now: str, *, writable: bool) -> None:
        """Bind to an open transaction; ``now`` is the command's store time."""
        self._conn = conn
        self.now = now
        self._writable = writable
        self.written: list[JSON] = []
        self.sequences: list[int] = []
        row = conn.execute("SELECT COALESCE(MAX(sequence), 0) FROM records").fetchone()
        self.watermark: int = row[0]
        """The last committed sequence before this transaction (its source prefix)."""
        self._next_sequence: int = row[0] + 1

    def put(
        self,
        kind: str,
        payload: JSON,
        *,
        by: str,
        id: str | None = None,  # noqa: A002 - the portable field name
        base: int | None = None,
    ) -> JSON:
        """Append a revision and return its exact reference.

        Without ``base`` this creates a new record (revision 1). With ``base`` it
        appends the next revision only if ``base`` is still the current one.
        """
        _check_owner(kind, by)
        if not self._writable:
            msg = "read-only view"
            raise PermissionError(msg)
        record_id = id or new_id()
        current = self._current_revision(kind, record_id)
        if current != (base or 0):
            msg = f"{kind} {record_id} is at revision {current}, not {base or 0}"
            raise Conflict(msg)
        revision = current + 1
        self._conn.execute(
            "INSERT INTO records (sequence, kind, id, revision, recorded_at, payload)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (self._next_sequence, kind, record_id, revision, self.now, canonical(payload).decode()),
        )
        self.sequences.append(self._next_sequence)
        self._next_sequence += 1
        written = ref(kind, record_id, revision)
        self.written.append(written)
        return written

    @contextmanager
    def savepoint(self) -> Generator[None]:
        """Discard this block's writes if it raises; the command itself continues."""
        self._conn.execute("SAVEPOINT block")
        marks = (len(self.written), len(self.sequences), self._next_sequence)
        try:
            yield
        except BaseException:
            self._conn.execute("ROLLBACK TO block")
            self._conn.execute("RELEASE block")
            del self.written[marks[0] :]
            del self.sequences[marks[1] :]
            self._next_sequence = marks[2]
            raise
        self._conn.execute("RELEASE block")

    def _current_revision(self, kind: str, id_: str) -> int:
        row = self._conn.execute(
            "SELECT COALESCE(MAX(revision), 0) FROM records WHERE kind = ? AND id = ?",
            (kind, id_),
        ).fetchone()
        return int(row[0])

    def get(
        self,
        kind: str,
        id: str,  # noqa: A002 - the portable field name
        *,
        by: str,
        revision: int | None = None,
    ) -> Record | None:
        """One revision of a record (the current one unless ``revision`` is given)."""
        _check_owner(kind, by)
        if revision is None:
            row = self._conn.execute(
                "SELECT * FROM records WHERE kind = ? AND id = ? ORDER BY revision DESC LIMIT 1",
                (kind, id),
            ).fetchone()
        else:
            row = self._conn.execute(
                "SELECT * FROM records WHERE kind = ? AND id = ? AND revision = ?",
                (kind, id, revision),
            ).fetchone()
        return _record(row) if row else None

    def require(self, kind: str, id: str, *, by: str) -> Record:  # noqa: A002
        """Return the current revision of a record that must exist."""
        record = self.get(kind, id, by=by)
        if record is None:
            msg = f"no {kind} {id}"
            raise LookupError(msg)
        return record

    def at(self, exact: JSON, *, by: str) -> Record:
        """Return the exact revision a reference names; a dangling one is an error."""
        record = self.get(exact["kind"], exact["id"], by=by, revision=exact["revision"])
        if record is None:
            msg = f"dangling reference {exact}"
            raise LookupError(msg)
        return record

    def current(self, kind: str, *, by: str) -> list[Record]:
        """Return the current revision of every record of a kind, oldest first.

        ponytail: scans the kind and filters in Python; add json_extract indexes
        when one learner's library outgrows memory.
        """
        _check_owner(kind, by)
        rows = self._conn.execute(
            "SELECT r.* FROM records r JOIN ("
            " SELECT id, MAX(revision) AS revision FROM records WHERE kind = ? GROUP BY id"
            ") latest ON r.id = latest.id AND r.revision = latest.revision"
            " WHERE r.kind = ? ORDER BY r.sequence",
            (kind, kind),
        ).fetchall()
        return [_record(r) for r in rows]

    def history(self, kind: str, id: str, *, by: str) -> list[Record]:  # noqa: A002
        """Every revision of one record, oldest first."""
        _check_owner(kind, by)
        rows = self._conn.execute(
            "SELECT * FROM records WHERE kind = ? AND id = ? ORDER BY revision", (kind, id)
        ).fetchall()
        return [_record(r) for r in rows]


_SCHEMA = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE records (
    sequence INTEGER PRIMARY KEY,
    kind TEXT NOT NULL,
    id TEXT NOT NULL,
    revision INTEGER NOT NULL,
    recorded_at TEXT NOT NULL,
    payload TEXT NOT NULL,
    UNIQUE (kind, id, revision)
);
CREATE TABLE receipts (
    request_id TEXT PRIMARY KEY,
    command TEXT NOT NULL,
    input_digest TEXT NOT NULL,
    result TEXT NOT NULL,
    first_sequence INTEGER,
    committed_sequence INTEGER,
    record_refs TEXT NOT NULL
);
"""


class Store:
    """One learner's library in one SQLite file, with a single writer."""

    def __init__(self, conn: sqlite3.Connection, clock: Clock, library_id: str) -> None:
        """Wrap an opened, version-checked connection (use ``Store.open``)."""
        self._conn = conn
        self._clock = clock
        self.library_id = library_id
        # ponytail: one lock serializes every read and command; fine for one learner.
        self._lock = threading.RLock()

    @classmethod
    def open(cls, path: Path, *, clock: Clock) -> Store:
        """Open or create a store, refusing one written by a newer release unchanged."""
        conn = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        if version > SCHEMA_VERSION:
            conn.close()
            msg = f"store schema {version} is newer than this release supports ({SCHEMA_VERSION})"
            raise RuntimeError(msg)
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = FULL")
        if version == 0:
            _create(conn, new_id(), [], [])
        library_id = conn.execute("SELECT value FROM meta WHERE key = 'library_id'").fetchone()[0]
        return cls(conn, clock, library_id)

    def close(self) -> None:
        """Close the connection."""
        with self._lock:
            self._conn.close()

    def now(self) -> str:
        """Return the store clock as a portable time."""
        return utc(self._clock())

    def run(
        self,
        request_id: str,
        command: str,
        inputs: JSON,
        fn: Callable[[Tx], JSON],
    ) -> Receipt:
        """Run ``fn`` as one atomic command and return its receipt.

        A request ID seen before returns its saved receipt when the input matches and
        raises ``Conflict`` when it differs. Any exception rolls the whole command back.
        """
        input_digest = digest({"command": command, "inputs": inputs})
        with self._lock:
            self._conn.execute("BEGIN IMMEDIATE")
            try:
                receipt = self._replay_or_execute(request_id, command, input_digest, fn)
            except BaseException:
                self._conn.execute("ROLLBACK")
                raise
            self._conn.execute("COMMIT")
            return receipt

    def _replay_or_execute(
        self, request_id: str, command: str, input_digest: str, fn: Callable[[Tx], JSON]
    ) -> Receipt:
        saved = self._receipt(request_id)
        if saved is not None:
            if saved.input_digest != input_digest:
                msg = f"request {request_id} was already used with different input"
                raise Conflict(msg)
            return saved
        tx = Tx(self._conn, self.now(), writable=True)
        result = fn(tx)
        receipt = Receipt(
            request_id=request_id,
            command=command,
            input_digest=input_digest,
            result=result,
            first_sequence=tx.sequences[0] if tx.sequences else None,
            committed_sequence=tx.sequences[-1] if tx.sequences else None,
            record_refs=tx.written,
        )
        if tx.written:  # a read-only no-op writes no receipt
            self._conn.execute(
                "INSERT INTO receipts VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    receipt.request_id,
                    receipt.command,
                    receipt.input_digest,
                    canonical(receipt.result).decode(),
                    receipt.first_sequence,
                    receipt.committed_sequence,
                    canonical(receipt.record_refs).decode(),
                ),
            )
        return receipt

    def read[T](self, fn: Callable[[Tx], T]) -> T:
        """Run ``fn`` against one consistent read-only snapshot."""
        with self._lock:
            self._conn.execute("BEGIN")
            try:
                return fn(Tx(self._conn, self.now(), writable=False))
            finally:
                self._conn.execute("COMMIT")

    def snapshot(self) -> tuple[list[JSON], list[JSON]]:
        """Every record (by sequence) and receipt (by request ID) from one snapshot."""
        with self._lock:
            self._conn.execute("BEGIN")
            try:
                records: list[JSON] = [
                    {
                        "kind": r["kind"],
                        "id": r["id"],
                        "revision": r["revision"],
                        "sequence": r["sequence"],
                        "recorded_at": r["recorded_at"],
                        "payload": json.loads(r["payload"]),
                    }
                    for r in self._conn.execute("SELECT * FROM records ORDER BY sequence")
                ]
                receipts: list[JSON] = [
                    {
                        "request_id": r["request_id"],
                        "command": r["command"],
                        "input_digest": r["input_digest"],
                        "result": json.loads(r["result"]),
                        "first_sequence": r["first_sequence"],
                        "committed_sequence": r["committed_sequence"],
                        "record_refs": json.loads(r["record_refs"]),
                    }
                    for r in self._conn.execute("SELECT * FROM receipts ORDER BY request_id")
                ]
            finally:
                self._conn.execute("COMMIT")
        return records, receipts

    def _receipt(self, request_id: str) -> Receipt | None:
        row = self._conn.execute(
            "SELECT * FROM receipts WHERE request_id = ?", (request_id,)
        ).fetchone()
        if row is None:
            return None
        return Receipt(
            request_id=row["request_id"],
            command=row["command"],
            input_digest=row["input_digest"],
            result=json.loads(row["result"]),
            first_sequence=row["first_sequence"],
            committed_sequence=row["committed_sequence"],
            record_refs=json.loads(row["record_refs"]),
        )


def _create(
    conn: sqlite3.Connection, library_id: str, records: list[JSON], receipts: list[JSON]
) -> None:
    """Create the schema and load any records in one transaction.

    A crash leaves a file without ``user_version``, which reopens as a new store.
    """
    conn.execute("BEGIN IMMEDIATE")
    try:
        for statement in _SCHEMA.split(";"):
            if statement.strip():
                conn.execute(statement)
        conn.execute("INSERT INTO meta (key, value) VALUES ('library_id', ?)", (library_id,))
        conn.executemany(
            "INSERT INTO records (sequence, kind, id, revision, recorded_at, payload)"
            " VALUES (:sequence, :kind, :id, :revision, :recorded_at, :payload)",
            [{**r, "payload": canonical(r["payload"]).decode()} for r in records],
        )
        conn.executemany(
            "INSERT INTO receipts VALUES (:request_id, :command, :input_digest, :result,"
            " :first_sequence, :committed_sequence, :record_refs)",
            [
                {
                    **r,
                    "result": canonical(r["result"]).decode(),
                    "record_refs": canonical(r["record_refs"]).decode(),
                }
                for r in receipts
            ],
        )
        conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise


# --- portable archive (compatibility-design.md section 7) --------------------

_ENVELOPE_KEYS = {
    "format",
    "format_version",
    "export_id",
    "exported_at",
    "library_id",
    "writer_release",
    "through_sequence",
    "records",
    "receipts",
    "integrity",
}
_RECORD_KEYS = {"kind", "id", "revision", "sequence", "recorded_at", "payload"}
_RECEIPT_KEYS = {
    "request_id",
    "command",
    "input_digest",
    "result",
    "first_sequence",
    "committed_sequence",
    "record_refs",
}


def export_library(store: Store, *, writer_release: str) -> JSON:
    """Export the whole library as one archive from one consistent snapshot."""
    records, receipts = store.snapshot()
    envelope: JSON = {
        "format": "memorization-library",
        "format_version": FORMAT_VERSION,
        "export_id": new_id(),
        "exported_at": store.now(),
        "library_id": store.library_id,
        "writer_release": writer_release,
        "through_sequence": records[-1]["sequence"] if records else 0,
        "records": records,
        "receipts": receipts,
    }
    envelope["integrity"] = {"algorithm": "sha256-jcs", "digest": digest(envelope)}
    return envelope


def learning_fingerprint(envelope: JSON) -> str:
    """Identity of the learning content, ignoring export id, time and writer release."""
    return digest(
        {
            key: envelope[key]
            for key in ("format_version", "library_id", "through_sequence", "records", "receipts")
        }
    )


def _strict_pairs(pairs: list[tuple[str, Any]]) -> JSON:
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        msg = "duplicate JSON key"
        raise ValueError(msg)
    return dict(pairs)


def _refuse_number(text: str) -> Any:  # noqa: ANN401 - json hook signature
    msg = f"non-integer number {text!r} is not allowed"
    raise ValueError(msg)


def parse_archive(text: str) -> JSON:
    """Parse archive text, refusing duplicate keys, floats and non-finite numbers."""
    value = json.loads(
        text,
        object_pairs_hook=_strict_pairs,
        parse_float=_refuse_number,
        parse_constant=_refuse_number,
    )
    if not isinstance(value, dict):
        msg = "an archive is a JSON object"
        raise ValueError(msg)  # noqa: TRY004 - refusal is a ValueError throughout
    archive = cast("JSON", value)
    canonical(archive)  # rejects invalid Unicode and unsafe integers
    return archive


def _refs(value: object) -> Iterator[JSON]:
    children = _children(value)
    if isinstance(value, dict) and set(cast("JSON", value)) == {"kind", "id", "revision"}:
        yield cast("JSON", value)
        return
    for child in children:
        yield from _refs(child)


def check_archive(envelope: JSON) -> list[str]:
    """List technical integrity errors: envelope, identities, references, receipts."""
    if set(envelope) != _ENVELOPE_KEYS:
        return [f"envelope keys differ: {sorted(set(envelope) ^ _ENVELOPE_KEYS)}"]
    if envelope["format"] != "memorization-library":
        return ["not a memorization library archive"]
    if envelope["format_version"] != FORMAT_VERSION:
        return [f"unsupported format_version {envelope['format_version']}"]
    body = {k: v for k, v in envelope.items() if k != "integrity"}
    if envelope["integrity"] != {"algorithm": "sha256-jcs", "digest": digest(body)}:
        return ["integrity digest does not match"]
    records: list[JSON] = envelope["records"]
    errors = _check_records(records)
    if envelope["through_sequence"] != len(records):
        errors.append("through_sequence does not match the records")
    return errors + _check_receipts(envelope["receipts"], records)


def _check_records(records: list[JSON]) -> list[str]:
    errors: list[str] = []
    seen: set[tuple[str, str, int]] = set()
    revisions: dict[tuple[str, str], list[int]] = {}
    for i, r in enumerate(records):
        if set(r) != _RECORD_KEYS:
            errors.append(f"record {i} keys differ: {sorted(set(r) ^ _RECORD_KEYS)}")
            continue
        if r["kind"] not in KIND_OWNER:
            errors.append(f"record {i} has unknown kind {r['kind']!r}")
        if r["sequence"] != i + 1:
            errors.append(f"record {i} has sequence {r['sequence']}, expected {i + 1}")
        key = (r["kind"], r["id"], r["revision"])
        if key in seen:
            errors.append(f"duplicate record revision {key}")
        seen.add(key)
        revisions.setdefault((r["kind"], r["id"]), []).append(r["revision"])
    errors.extend(
        f"{kind} {id_} revisions are not contiguous from 1: {revs}"
        for (kind, id_), revs in revisions.items()
        if revs != list(range(1, len(revs) + 1))
    )
    errors.extend(
        f"{r.get('kind')} {r.get('id')} has dangling reference {x}"
        for r in records
        for x in _refs(r.get("payload"))
        if (x["kind"], x["id"], x["revision"]) not in seen
    )
    return errors


def _check_receipts(receipts: list[JSON], records: list[JSON]) -> list[str]:
    """Check that receipts partition the sequence and name exactly their records."""
    errors: list[str] = []
    expected_first = 1
    for receipt in sorted(receipts, key=lambda x: x.get("first_sequence") or 0):
        if set(receipt) != _RECEIPT_KEYS:
            errors.append(f"receipt keys differ: {sorted(set(receipt) ^ _RECEIPT_KEYS)}")
            continue
        first, last = receipt["first_sequence"], receipt["committed_sequence"]
        if first != expected_first or last is None or last < first:
            errors.append(f"receipt {receipt['request_id']} does not continue the sequence")
            continue
        covered = [
            {"kind": r["kind"], "id": r["id"], "revision": r["revision"]}
            for r in records[first - 1 : last]
        ]
        if covered != receipt["record_refs"]:
            errors.append(f"receipt {receipt['request_id']} does not match its records")
        expected_first = last + 1
    if expected_first != len(records) + 1:
        errors.append("receipts do not cover every record")
    return errors


def lineage_conflict(store: Store, envelope: JSON) -> str | None:
    """Tell why an archive of this same library may not replace it (compatibility sections 4-5).

    The active store must be an exact prefix of the archive: a local record or receipt the
    archive lacks or holds differently (later learning, or a copy edited separately) would
    be hidden by the switch. Another library's archive is not compared.
    """
    if envelope.get("library_id") != store.library_id:
        return None
    records, receipts = store.snapshot()
    archived = {canonical(r) for r in envelope.get("receipts", [])}
    if records != envelope.get("records", [])[: len(records)] or any(
        canonical(r) not in archived for r in receipts
    ):
        return (
            "this library has learning the archive does not contain (work saved after the "
            "export, or a copy changed separately); restoring it would hide that work. "
            "Export the current library first, or restore the archive into another folder."
        )
    return None


def restore_library(
    path: Path,
    text: str,
    *,
    clock: Clock,
    validate: Callable[[list[Record]], list[str]],
) -> Store:
    """Restore an archive into a new store file and return it opened.

    Everything is checked before the file appears: archive integrity here, record
    meaning through ``validate`` (the owners' validators, wired by the caller). The
    store is written under a temporary name, reopened and compared with the
    archive, then renamed into place. Restore never calls a model.
    """
    if path.exists():
        msg = f"{path} exists; restore only into a new store"
        raise FileExistsError(msg)
    envelope = parse_archive(text)
    errors = check_archive(envelope)
    if not errors:
        errors = validate([Record(**r) for r in envelope["records"]])
    if errors:
        raise ValueError("archive refused: " + "; ".join(errors))
    staging = path.with_name(path.name + ".restoring")
    staging.unlink(missing_ok=True)
    conn = sqlite3.connect(staging, isolation_level=None)
    conn.row_factory = sqlite3.Row
    try:
        _create(conn, envelope["library_id"], envelope["records"], envelope["receipts"])
    finally:
        conn.close()
    restored = Store.open(staging, clock=clock)
    same = learning_fingerprint(export_library(restored, writer_release="restore-check"))
    restored.close()
    if same != learning_fingerprint(envelope):
        staging.unlink()
        msg = "restored store does not reproduce the archive"
        raise ValueError(msg)
    staging.rename(path)
    return Store.open(path, clock=clock)


# --- which store is active ----------------------------------------------------


def active_store(data_dir: Path) -> Path | None:
    """Return the store file the application writes to, if one was chosen."""
    pointer = data_dir / "active.json"
    if not pointer.exists():
        return None
    return data_dir / str(json.loads(pointer.read_text())["store"])


def activate(data_dir: Path, store_path: Path) -> None:
    """Durably make ``store_path`` (inside ``data_dir``) the active store."""
    staging = data_dir / "active.json.tmp"
    with staging.open("w") as f:
        json.dump({"store": store_path.name}, f)
        f.flush()
        os.fsync(f.fileno())
    staging.replace(data_dir / "active.json")


# --- shared vocabulary for model-assisted operations ---------------------------


@dataclass(frozen=True)
class ModelRequest:
    """A bounded model request prepared by its semantic owner (Content or Evidence).

    ``protocol`` is the owner's versioned protocol identity; ``output`` is the schema
    the response must satisfy. The application's provider adapter sends it.
    """

    protocol: JSON
    system: str
    user: str
    output: type[BaseModel]


def validate_payloads(
    records: list[Record], owner: str, payloads: dict[str, type[BaseModel]]
) -> list[str]:
    """Check each record ``owner`` writes against that owner's payload models."""
    errors: list[str] = []
    for r in records:
        if KIND_OWNER[r.kind] != owner:
            continue
        model = payloads.get(r.kind)
        if model is None:
            errors.append(f"{r.kind} records are not supported by this release")
            continue
        try:
            model.model_validate(r.payload)
        except ValidationError as e:
            errors.append(f"{r.kind} {r.id} r{r.revision}: {e.errors()[0]['msg']}")
    return errors
