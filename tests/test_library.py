from datetime import UTC, datetime

import pytest

from muninn.library import Conflict, Store


def fixed_clock():
    return datetime(2026, 10, 24, 10, 0, tzinfo=UTC)


@pytest.fixture
def store(tmp_path):
    s = Store.open(tmp_path / "lib.sqlite", clock=fixed_clock)
    yield s
    s.close()


def add_source(tx, text="Water boils at 100 C at sea level."):
    return {"source": tx.put("source", {"title": "t", "text": text}, by="content")}


def test_a_command_commits_records_with_one_receipt(store):
    receipt = store.run("req-1", "add_source", {"text": "x"}, add_source)
    ref = receipt.result["source"]
    assert ref["revision"] == 1
    assert receipt.first_sequence == 1
    assert receipt.committed_sequence == 1
    record = store.read(lambda tx: tx.get("source", ref["id"], by="content"))
    assert record is not None
    assert record.payload["text"] == "Water boils at 100 C at sea level."
    assert record.recorded_at == "2026-10-24T10:00:00.000Z"


def test_retrying_a_command_returns_the_saved_receipt_without_writing_again(store):
    first = store.run("req-1", "add_source", {"text": "x"}, add_source)
    again = store.run("req-1", "add_source", {"text": "x"}, add_source)
    assert again == first
    sources = store.read(lambda tx: tx.current("source", by="content"))
    assert len(sources) == 1


def test_reusing_a_request_id_with_different_input_is_a_conflict(store):
    store.run("req-1", "add_source", {"text": "x"}, add_source)
    with pytest.raises(Conflict):
        store.run("req-1", "add_source", {"text": "y"}, add_source)


def test_a_failing_command_writes_nothing(store):
    def half_then_fail(tx):
        add_source(tx)
        msg = "boom"
        raise RuntimeError(msg)

    with pytest.raises(RuntimeError):
        store.run("req-1", "add_source", {}, half_then_fail)
    assert store.read(lambda tx: tx.current("source", by="content")) == []
    # the request id stays free: the same id can now succeed
    assert store.run("req-1", "add_source", {}, add_source).first_sequence == 1


def test_a_module_cannot_write_or_read_another_modules_records(store):
    with pytest.raises(PermissionError):
        store.run("r", "c", {}, lambda tx: tx.put("source", {}, by="evidence"))
    store.run("r2", "add_source", {}, add_source)
    with pytest.raises(PermissionError):
        store.read(lambda tx: tx.current("source", by="practice"))


def test_a_new_revision_must_name_the_current_one(store):
    ref = store.run("r1", "add", {}, add_source).result["source"]

    def revise(base):
        def fn(tx):
            return {
                "source": tx.put("source", {"title": "t2"}, by="content", id=ref["id"], base=base)
            }

        return fn

    assert store.run("r2", "revise", {"b": 1}, revise(1)).result["source"]["revision"] == 2
    with pytest.raises(Conflict):
        store.run("r3", "revise", {"b": 1}, revise(1))


def test_reopening_the_store_keeps_records_and_library_identity(tmp_path):
    path = tmp_path / "lib.sqlite"
    s = Store.open(path, clock=fixed_clock)
    library_id = s.library_id
    ref = s.run("r1", "add", {}, add_source).result["source"]
    s.close()
    s = Store.open(path, clock=fixed_clock)
    assert s.library_id == library_id
    assert s.read(lambda tx: tx.get("source", ref["id"], by="content")) is not None
    assert s.run("r1", "add", {}, add_source).result["source"] == ref
    s.close()


def test_a_store_from_a_newer_release_is_refused_unchanged(tmp_path):
    import sqlite3

    path = tmp_path / "lib.sqlite"
    Store.open(path, clock=fixed_clock).close()
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA user_version = 99")
    conn.commit()
    conn.close()
    before = path.read_bytes()
    with pytest.raises(RuntimeError, match="newer"):
        Store.open(path, clock=fixed_clock)
    assert path.read_bytes() == before


# --- export / restore -------------------------------------------------------

import json  # noqa: E402

from muninn.library import export_library, learning_fingerprint, restore_library  # noqa: E402


def no_semantic_errors(records):
    return []


def build(store):
    src = store.run("r1", "add", {}, add_source).result["source"]

    def cite(tx):
        knowledge = tx.put("knowledge", {"statement": "boiling point", "source": src}, by="content")
        return {"knowledge": knowledge}

    store.run("r2", "cite", {}, cite)
    return src


def test_export_holds_every_revision_receipt_and_an_integrity_digest(store):
    build(store)
    envelope = export_library(store, writer_release="test")
    assert envelope["format"] == "memorization-library"
    assert envelope["format_version"] == 1
    assert envelope["library_id"] == store.library_id
    assert envelope["through_sequence"] == 2
    assert [r["sequence"] for r in envelope["records"]] == [1, 2]
    assert [r["request_id"] for r in envelope["receipts"]] == ["r1", "r2"]
    assert len(envelope["integrity"]["digest"]) == 64


def test_restore_into_an_empty_store_reproduces_the_library(store, tmp_path):
    build(store)
    envelope = export_library(store, writer_release="test")
    restored = restore_library(
        tmp_path / "restored.sqlite",
        json.dumps(envelope),
        clock=fixed_clock,
        validate=no_semantic_errors,
    )
    try:
        assert restored.library_id == store.library_id
        assert learning_fingerprint(export_library(restored, writer_release="x")) == (
            learning_fingerprint(envelope)
        )
        # an old request replays its receipt instead of writing again
        assert restored.run("r1", "add", {}, add_source).first_sequence == 1
    finally:
        restored.close()


@pytest.mark.parametrize(
    "corrupt",
    [
        lambda e: e.update(format_version=2),
        lambda e: e["records"][0].update(kind="mystery"),
        lambda e: e["records"][0].update(extra=1),
        lambda e: e["records"].append(dict(e["records"][0], sequence=3)),
        lambda e: e["records"][1]["payload"]["source"].update(revision=9),
        lambda e: e["receipts"].pop(),
    ],
    ids=[
        "newer-format",
        "unknown-kind",
        "unknown-field",
        "duplicate-revision",
        "dangling-ref",
        "missing-receipt",
    ],
)
def test_a_corrupt_archive_is_refused_before_anything_is_created(store, tmp_path, corrupt):
    build(store)
    envelope = export_library(store, writer_release="test")
    corrupt(envelope)
    envelope.pop("integrity")
    from muninn.library import digest

    envelope["integrity"] = {"algorithm": "sha256-jcs", "digest": digest(envelope)}
    target = tmp_path / "restored.sqlite"
    with pytest.raises(ValueError):  # noqa: PT011 - each corruption has its own message
        restore_library(
            target, json.dumps(envelope), clock=fixed_clock, validate=no_semantic_errors
        )
    assert not target.exists()


def test_a_tampered_or_truncated_archive_is_refused(store, tmp_path):
    build(store)
    text = json.dumps(export_library(store, writer_release="test"))
    tampered = text.replace("boiling point", "freezing point")
    for bad in (
        tampered,
        text[: len(text) // 2],
        text.replace('"format"', '"format":1,"format"', 1),
    ):
        with pytest.raises(ValueError):  # noqa: PT011
            restore_library(
                tmp_path / "r.sqlite", bad, clock=fixed_clock, validate=no_semantic_errors
            )
    assert not (tmp_path / "r.sqlite").exists()


def test_owner_validation_errors_refuse_the_restore(store, tmp_path):
    build(store)
    text = json.dumps(export_library(store, writer_release="test"))
    with pytest.raises(ValueError, match="bad knowledge"):
        restore_library(
            tmp_path / "r.sqlite",
            text,
            clock=fixed_clock,
            validate=lambda records: ["bad knowledge"],
        )


def test_restore_never_overwrites_an_existing_store(store, tmp_path):
    build(store)
    text = json.dumps(export_library(store, writer_release="test"))
    existing = tmp_path / "existing.sqlite"
    Store.open(existing, clock=fixed_clock).close()
    before = existing.read_bytes()
    with pytest.raises(FileExistsError):
        restore_library(existing, text, clock=fixed_clock, validate=no_semantic_errors)
    assert existing.read_bytes() == before


def test_the_active_store_choice_is_durable(tmp_path):
    from muninn.library import activate, active_store

    assert active_store(tmp_path) is None
    activate(tmp_path, tmp_path / "a.sqlite")
    assert active_store(tmp_path) == tmp_path / "a.sqlite"
    activate(tmp_path, tmp_path / "b.sqlite")
    assert active_store(tmp_path) == tmp_path / "b.sqlite"


def test_a_savepoint_discards_only_its_own_writes(store):
    def discarded(tx):
        with tx.savepoint():
            add_source(tx, text="discarded")
            msg = "refused"
            raise ValueError(msg)

    def fn(tx):
        kept = add_source(tx)["source"]
        with pytest.raises(ValueError, match="refused"):
            discarded(tx)
        later = add_source(tx, text="after")["source"]
        return {"kept": kept, "later": later}

    receipt = store.run("r", "c", {}, fn)
    texts = store.read(lambda tx: [r.payload["text"] for r in tx.current("source", by="content")])
    assert len(texts) == 2
    assert "discarded" not in texts
    assert receipt.record_refs == [receipt.result["kept"], receipt.result["later"]]
    assert (receipt.first_sequence, receipt.committed_sequence) == (1, 2)
