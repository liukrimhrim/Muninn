"""Build the frozen baseline library of storage format 1 (compatibility-design.md section 9).

``uv run python -m tests.fixtures.format1`` builds ONE library through the real ``App``
commands, a scripted model and a controlled clock, then writes into ``format-1/``:

- ``library.sqlite``: the store at schema 1, closed cleanly (no ``-wal``/``-shm``);
- ``library.learning.json``: its export archive, byte for byte as the export download;
- ``expected.json``: the situations read back from a copy of the closed store.

It holds every section 9 situation this build can produce and every record kind it can
write. The files are frozen: never regenerate them. A format change adds a migration and
a new fixture directory, and every older fixture must keep upgrading. Existing files are
never overwritten unless ``--force`` is given.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from muninn import content, evidence, practice, workflows
from muninn.library import (
    FORMAT_VERSION,
    KIND_OWNER,
    SCHEMA_VERSION,
    Store,
    Tx,
    learning_fingerprint,
    parse_utc,
)
from muninn.workflows import RELEASE, App
from tests.conftest import Clock, FailIfCalled, ScriptedProvider, rid
from tests.drafts import (
    ALL_SHOWN,
    ANSWER,
    CONNECTION_ERROR,
    NOTES_SOURCE,
    SOURCE,
    VOCAB_SOURCE,
    assessment,
    judged,
    notes_outline,
    outline,
    teaching,
    variant,
    vocab_outline,
)

JSON = dict[str, Any]
TAB1_OPENED, TAB2_OPENED = "2026-10-24T10:05:00.000Z", "2026-10-25T11:22:00.000Z"
FIXTURE = Path(__file__).parent / "format-1"
STORE, ARCHIVE, EXPECTED = "library.sqlite", "library.learning.json", "expected.json"
GAPS = {
    "two subject curricula sharing one unchanged target": (
        "not reachable: no flow creates a shared exact target; reuse links claims, never "
        "goals (the fixture has one reused claim), and linking an admitted goal into a "
        "second enrollment was deferred in slice 4 (ledger CCA04, P19, C09)"
    ),
    "a retired target": (
        "not reachable: no command retires a goal or removes it from a curriculum "
        "(ledger C10, deferred in slice 3); revise_target writes a 'changed' mapping and "
        "keeps the old revision 'accepted', only deselected"
    ),
    "a held mapping": (
        "not reachable: every mapping is written 'accepted' (content._mapping); what a "
        "change holds is the exercise written for the old goal, derived at read time"
    ),
    "measurement_report records": (
        "not reachable: no command saves a report (saved reports are deferred: ledger "
        "X12, P08, P31, B07), and Measurement has no payload contract for the kind"
    ),
}


def _goals(app: App, curriculum: JSON) -> list[JSON]:
    return app.read(
        lambda tx: [
            t for s in tx.at(curriculum, by="content").payload["sections"] for t in s["targets"]
        ]
    )


def _draft(app: App, title: str, text: str) -> tuple[str, list[JSON]]:
    """Add material and draft it; return the curriculum id and its goals in outline order."""
    added = app.add_material(rid(), title=title, text=text, purpose=None)
    op = app.run_operation(added["operation"]["id"])
    curriculum = next(o for o in op["outputs"] if o["kind"] == "curriculum")
    return curriculum["id"], _goals(app, curriculum)


def _step(app: App, session: JSON, kind: str, exercise_id: str | None = None) -> JSON:
    """Take the session's next step, which the scenario expects to be ``kind``."""
    step = app.next_exercise(rid(), session_id=session["id"], exercise_id=exercise_id)
    if step["kind"] != kind:
        msg = f"the scenario expected {kind}, got {step['kind']}"
        raise RuntimeError(msg)
    return step


def _deliver(app: App, session: JSON, exercise_id: str | None = None) -> JSON:
    """Take the session's next exercise (``exercise_id``: the learner's own choice)."""
    return dict(_step(app, session, "exercise", exercise_id)["attempt"])


def _submit(app: App, attempt: JSON, text: str, request_id: str | None = None) -> JSON:
    return app.submit_answer(
        request_id or rid(),
        attempt_id=attempt["id"],
        base=attempt["revision"],
        response=text,
        client_at=None,
    )


def _spans(
    app: App, run: JSON, session: JSON, opened: str, *spans: tuple[int, str, str, str]
) -> None:
    """Record browser spans (ordinal, category, wall start, wall end) of a tab opened then."""
    origin = parse_utc(opened)
    batch = [
        {
            "id": rid(),
            "run_id": run["id"],
            "ordinal": n,
            "category": category,
            "monotonic_start_ms": int((parse_utc(start) - origin).total_seconds() * 1000),
            "monotonic_end_ms": int((parse_utc(end) - origin).total_seconds() * 1000),
            "raw_wall_start": start,
            "raw_wall_end": end,
            "session": session,
            "context": [],
        }
        for n, category, start, end in spans
    ]
    app.record_spans(rid(), spans=batch)


def _claim(app: App, target: JSON, statement: str) -> JSON:
    """Return the exact ref of the claim with this statement among a goal's claims."""
    return app.read(
        lambda tx: next(
            k
            for k in tx.at(target, by="content").payload["content"]
            if tx.at(k, by="content").payload["statement"] == statement
        )
    )


def _revise(app: App, target: JSON) -> JSON:
    """Change a goal's conditions after it was drafted: a new revision and a mapping."""
    goal = app.read(lambda tx: tx.at(target, by="content").payload)
    return app.revise_target(
        rid(),
        target_id=target["id"],
        base=target["revision"],
        action=goal["action"],
        mode=goal["mode"],
        conditions=[*goal["conditions"], "for a list that may be unsorted"],
        requirements=[
            {"id": r["id"], "statement": r["statement"]} for r in goal["evidence_requirements"]
        ],
        reason="the goal should say the list may be unsorted",
    )


def _repair_cycle(app: App, session: JSON, clock: Clock) -> tuple[JSON, JSON]:
    """Teach the open concern, complete the study, then answer the fresh check (slice 2)."""
    taught = _step(app, session, "preparing")
    app.run_operation(taught["operation"]["id"])
    study = _step(app, session, "study")["study"]
    clock.advance(minutes=5)
    app.complete_study(rid(), study_id=study["id"], base=study["revision"], client_at=None)
    prepared = _step(app, session, "preparing")
    app.run_operation(prepared["operation"]["id"])
    fresh = dict(_step(app, session, "verification")["attempt"])
    clock.advance(minutes=3)
    app.run_operation(_submit(app, fresh, ANSWER)["operation"]["id"])
    return study, fresh


def build(directory: Path) -> JSON:  # noqa: PLR0915 - one scripted learning history
    """Build the library into ``directory``; return the ids that name each situation."""
    clock = Clock()  # 2026-10-24T10:00:00Z
    store = Store.open(directory / STORE, clock=clock)
    app = App(
        store,
        ScriptedProvider(
            outline(),  # binary search: a recall fact and a connected explanation
            vocab_outline(),  # Tarvi: one recall word, the second subject
            notes_outline,  # searching notes: proposes reusing the binary-search claims
            judged(ALL_SHOWN),  # a1, with hint h1 shown on c2
            judged({"c1": "demonstrated", "c2": "demonstrated", "c3": "cannot_judge"}),  # a2
            judged(CONNECTION_ERROR, misread=["c3"]),  # a3
            assessment({"c1": "demonstrated"}, {"c1": ["Blue"]}),  # b1
            judged(ALL_SHOWN),  # a4, the due check
            judged(CONNECTION_ERROR),  # the review of a4's judgment
            teaching(),  # repair teaching for the corrected error
            variant(),  # the fresh check after the study
            judged(CONNECTION_ERROR),  # the fresh check still has the error
        ),
    )
    app.recover()
    try:
        search, (fact, connection) = _draft(app, "Binary search", SOURCE)
        clock.advance(minutes=2)
        tarvi, (word,) = _draft(app, "Tarvi", VOCAB_SOURCE)
        exercise = app.read(lambda tx: tx.current("exercise", by="content")[0].id)
        clock.advance(minutes=1)
        added = app.add_material(rid(), title="Searching notes", text=NOTES_SOURCE, purpose=None)
        review = app.run_operation(added["operation"]["id"])  # waits for the reuse review
        notes = app.accept_material(
            rid(), operation_id=review["ref"]["id"], decisions={"b1": "separate", "b2": "reuse"}
        )["curriculum"]
        explain, linear = _goals(app, notes)

        # day 0, binary search: a hinted first answer, then two extra answers by choice
        clock.advance(minutes=2)
        s1 = app.start_session(rid(), curriculum_id=search)["session"]
        tab1 = app.open_timer(rid(), document_run_id="tab-1", takeover=False)["run"]
        a1 = _deliver(app, s1)
        clock.advance(minutes=1)
        app.reveal_hint(rid(), attempt_id=a1["id"], hint_id="h1")
        a1 = app.acknowledge_hint(
            rid(), attempt_id=a1["id"], base=a1["revision"], hint_id="h1", client_at=None
        )["attempt"]
        clock.advance(minutes=2)
        app.run_operation(_submit(app, a1, ANSWER)["operation"]["id"])
        clock.advance(minutes=4)
        a2 = _deliver(app, s1, exercise)
        app.run_operation(_submit(app, a2, ANSWER)["operation"]["id"])
        clock.advance(minutes=3)
        a3 = _deliver(app, s1, exercise)
        app.run_operation(_submit(app, a3, ANSWER)["operation"]["id"])
        _spans(
            app,
            tab1,
            s1,
            TAB1_OPENED,
            (1, "answer", "2026-10-24T10:05:00.000Z", "2026-10-24T10:08:00.000Z"),
            (2, "feedback", "2026-10-24T10:08:00.000Z", "2026-10-24T10:12:00.000Z"),
            (3, "answer", "2026-10-24T10:12:00.000Z", "2026-10-24T10:15:00.000Z"),
        )
        app.end_session(rid(), session_id=s1["id"], base=s1["revision"], reason="done")
        clock.advance(minutes=1)
        cohort = app.start_tracking(rid(), curriculum_id=search)["cohort"]

        # day 0, Tarvi: an independent recall, its feedback page, a rating and a re-rating
        clock.advance(minutes=4)
        s2 = app.start_session(rid(), curriculum_id=tarvi)["session"]
        b1 = _deliver(app, s2)
        app.run_operation(_submit(app, b1, "Blue.")["operation"]["id"])
        app.view_feedback(rid(), attempt_id=b1["id"])  # the tab is closed without leaving it
        clock.advance(minutes=1)
        app.rate_recall(rid(), attempt_id=b1["id"], target=word, choice="remembered")
        clock.advance(minutes=1)
        app.rate_recall(rid(), attempt_id=b1["id"], target=word, choice="difficult")
        app.end_session(rid(), session_id=s2["id"], base=s2["revision"], reason="done")
        app.session_feedback(
            rid(), session_id=s2["id"], effort="easy", usefulness="useful", note=None
        )

        # day 1: the earlier feedback page is confirmed closed; a second tab takes the timer
        clock.advance(hours=25)
        checkpoint = app.confirm_closed(rid(), targets=[word])["checkpoint"]
        s3 = app.start_session(rid(), curriculum_id=search)["session"]
        tab2 = app.open_timer(rid(), document_run_id="tab-2", takeover=True)["run"]
        late = (4, "progress_inspection", "2026-10-24T10:15:00.000Z", "2026-10-24T10:16:00.000Z")
        _spans(app, tab1, s1, TAB1_OPENED, late)  # the first tab's late span: kept, stale

        # day 1, binary search: the due check passes, then its judgment is corrected
        a4 = _deliver(app, s3)
        app.run_operation(_submit(app, a4, ANSWER)["operation"]["id"])
        clock.advance(minutes=10)
        disputed = app.dispute_judgment(rid(), attempt_id=a4["id"], reason="I made a mistake")
        app.run_operation(disputed["operation"]["id"])
        clock.advance(minutes=2)
        app.accept_correction(rid(), operation_id=disputed["operation"]["id"])

        # the corrected error is taught and checked fresh; the error stays: repair pending
        study, fresh = _repair_cycle(app, s3, clock)

        # an answer whose response was lost after commit, never assessed; then a draft
        clock.advance(minutes=3)
        a5 = _deliver(app, s3, exercise)
        lost = rid()
        unassessed = _submit(app, a5, ANSWER, request_id=lost)
        clock.advance(minutes=2)
        a6 = _deliver(app, s3, exercise)
        app.save_draft(rid(), attempt_id=a6["id"], base=a6["revision"], response="It must be")
        _spans(
            app,
            tab2,
            s3,
            TAB2_OPENED,
            (1, "answer", "2026-10-25T11:22:00.000Z", "2026-10-25T11:32:00.000Z"),
            (2, "assessment_correction", "2026-10-25T11:32:00.000Z", "2026-10-25T11:34:00.000Z"),
            (3, "study", "2026-10-25T11:34:00.000Z", "2026-10-25T11:39:00.000Z"),
            (4, "answer", "2026-10-25T11:39:00.000Z", "2026-10-25T11:47:00.000Z"),
        )

        # day 2, searching notes: a claim is flagged and a goal is changed (slice 3)
        clock.advance(hours=22)
        flagged = _claim(app, explain, "Binary search requires a sorted array.")
        app.flag_material(
            rid(),
            knowledge_id=flagged["id"],
            base=flagged["revision"],
            reason="it also needs random access",
        )
        revised = _revise(app, linear)
        reused = app.read(  # the explanation reuses the binary-search halving claim
            lambda tx: next(
                k
                for k in tx.at(explain, by="content").payload["content"]
                if k["id"] in {c["id"] for c in tx.at(connection, by="content").payload["content"]}
            )
        )

        # days later the Tarvi review is overdue; the app stops with tab 2 still timing
        clock.advance(days=2)
        archive = app.export()
    finally:
        store.close()
    text = json.dumps(archive, ensure_ascii=False, separators=(",", ":"))  # as JSONResponse
    (directory / ARCHIVE).write_text(text, encoding="utf-8")
    return {
        "frozen_at": archive["exported_at"],
        "ids": {
            "curricula": {"binary_search": search, "tarvi": tarvi, "notes": notes["id"]},
            "targets": {
                "fact": fact,
                "connection": connection,
                "word": word,
                "notes_explain": explain,
                "notes_linear": linear,
                "notes_linear_revised": revised["target"],
            },
            "attempts": {
                "hinted": a1["id"],
                "ambiguous": a2["id"],
                "misread": a3["id"],
                "independent": b1["id"],
                "superseded_grade": a4["id"],
                "verification": fresh["id"],
                "unassessed": a5["id"],
                "draft": a6["id"],
            },
            "claims": {"flagged": flagged["id"], "reused": reused["id"]},
            "study": study["id"],
            "checkpoint": checkpoint,
            "cohort": cohort["id"],
        },
        "lost_response": {
            "request_id": lost,
            "command": "submit_answer",
            "inputs": {"attempt_id": a5["id"], "base": a5["revision"], "response": ANSWER},
            "result": unassessed,
        },
    }


# --- reading the situations back through the public views ------------------------------


def _owned(tx: Tx, kind: str) -> list[JSON]:
    """Every current record of a kind no public view shows, read through its owner."""
    return [r.view for r in tx.current(kind, by=KIND_OWNER[kind])]


def _schedule(tx: Tx, target: JSON) -> JSON | None:
    view = practice.schedule_view(tx, target)
    if view is None:
        return None
    # no public view shows the FSRS card; read it from Practice's record (test_later_checks)
    card = next(
        s["engine_state"].get("card") for s in _owned(tx, "schedule") if s["target"] == target
    )
    return {
        "ref": view["ref"],
        "type": view["type"],
        "policy": view["policy"]["name"],
        "need": view["need"],
        "due_at": view["due_at"],
        "obligation": {k: view["obligation"][k] for k in ("id", "kind", "status")},
        "hold_reason": view["hold_reason"],
        "reason": view["reason"],
        "next_offer": view["next_offer"],
        "revisions": len(practice.schedule_history(tx, target)),
        "fsrs_card": json.loads(card) if card else None,
    }


def _attempt(tx: Tx, attempt_id: str) -> JSON:
    a = evidence.attempt_view(tx, attempt_id=attempt_id)
    offer = practice.offer_for(tx, attempt_id)
    return {
        "ref": a["ref"],
        "session": a["session"],
        "exercise": a["exercise"],
        "purpose": a["purpose"],
        "status": a["status"],
        "response": a["response"],
        "started_at": a["started_at"],
        "submitted_at": a["submitted_at"],
        "assistance": a["assistance"],
        "verification_of": a.get("verification_of"),
        "offer": offer
        and {
            "ref": offer["ref"],
            "state": offer["state"],
            "roles": [[s["target"], s["role"]] for s in offer["slots"]],
        },
        "assessing": workflows.feedback_view(tx, attempt_id)["assessment"],
        "assessments": [
            {
                "ref": j["ref"],
                "outcomes": {r["criterion_id"]: r["outcome"] for r in j["results"]},
                "interpretation": j["interpretation"],
                "interpretation_criteria": j["interpretation_criteria"],
                "supersedes": j["supersedes"],
                "revision_reason": j["revision_reason"],
            }
            for j in evidence.assessment_history(tx, attempt_id)
        ],
    }


def _outline(tx: Tx, curriculum_id: str) -> JSON:
    view = workflows.outline_view(tx, curriculum_id)
    enrollment = practice.enrollment_for(tx, curriculum_id)
    assert enrollment is not None  # every drafted curriculum is enrolled
    return {
        "ref": view["curriculum"]["ref"],
        "title": view["curriculum"]["title"],
        "enrollment": enrollment["ref"],
        "goal_order": enrollment["goal_order"],
        "targets": [[t["ref"], t["state"], t["hold"]] for t in view["targets"]],
        "exercises": [[e["ref"], e["hold"]] for e in view["exercises"]],
    }


def _study(tx: Tx, study_id: str) -> JSON:
    study = evidence.study_view(tx, study_id)
    taught = content.definition(tx, study["teaching"])
    page = workflows.study_page_view(tx, study_id)
    return {
        "ref": study["ref"],
        "session": study["session"],
        "status": study["status"],
        "started_at": study["started_at"],
        "completed_at": study["completed_at"],
        "concern": study["concern"],
        "teaching": {
            "ref": taught["ref"],
            "status": taught["status"],
            "approach": page["approach"],
            "quotes": page["quotes"],
            "review": taught["review"]["disposition"],
        },
    }


def _claim_view(tx: Tx, knowledge_id: str) -> JSON:
    claim = content.current_definition(tx, "knowledge", knowledge_id)
    assert claim is not None  # named by the scenario
    return {
        "ref": claim["ref"],
        "statement": claim["statement"],
        "status": claim["status"],
        "dispute": claim.get("dispute"),
        "sources": [p["source"] for p in claim["sources"]],
    }


def _tracking(tx: Tx, cohort_id: str) -> JSON:
    report = workflows.tracking_view(tx, cohort_id)
    return {
        "ref": report["ref"],
        "curriculum": report["curriculum"],
        "lifecycle": report["lifecycle"],
        "frozen_at": report["frozen_at"],
        "population": [[m["target"], m["baseline"]["state"]] for m in report["population"]],
        "windows": [
            {
                "start": w["start"],
                "end": w["end"],
                "endpoints": [[e["target"], e["assigned_attempt"]] for e in w["endpoints"]],
            }
            for w in report["windows"]
        ],
    }


def _observe(tx: Tx, ids: JSON) -> JSON:
    mapping = content.mapping_to(tx, ids["targets"]["notes_linear_revised"])
    assert mapping is not None  # the scenario changed this goal
    checkpoint = tx.at(ids["checkpoint"], by="evidence").view  # no public view shows one
    return {
        "curricula": {c["title"]: _outline(tx, c["ref"]["id"]) for c in content.curricula(tx)},
        "attempts": {name: _attempt(tx, a) for name, a in ids["attempts"].items()},
        "targets": {
            name: {
                "label": evidence.target_evidence(tx, t)["label"],
                "schedule": _schedule(tx, t),
            }
            for name, t in ids["targets"].items()
        },
        "reviews": [
            [
                {"ref": r.ref}
                | {k: r.payload[k] for k in ("choice", "rating", "occurred_at", "rated_at")}
                | {"supersedes": r.payload["supersedes"]}
                for r in tx.history("review", record.id, by="evidence")
            ]
            for record in tx.current("review", by="evidence")
        ],
        "concerns": [
            {k: c[k] for k in ("ref", "status", "route", "kind", "scope", "origin", "cycles")}
            for c in (r.view for r in tx.current("concern", by="practice"))
        ],
        "study": _study(tx, ids["study"]),
        "claims": {name: _claim_view(tx, k) for name, k in ids["claims"].items()},
        "mapping": {
            k: mapping[k] for k in ("ref", "from", "to", "relation", "disposition", "reason")
        },
        "checkpoint": {
            k: checkpoint[k] for k in ("ref", "targets", "established_at", "purpose", "basis")
        },
        "tracking": _tracking(tx, ids["cohort"]),
        "timing_runs": [
            {k: r[k] for k in ("ref", "document_run_id", "generation", "status", "close_reason")}
            for r in _owned(tx, "timing_run")
        ],
        "session_feedback": [
            {k: f[k] for k in ("ref", "session", "effort", "usefulness", "note")}
            for f in _owned(tx, "session_feedback")
        ],
        "effort": workflows.home_view(tx)["effort"],
        "home_due": workflows.home_view(tx)["due"],
    }


def observe(app: App, ids: JSON) -> JSON:
    """Read every named situation in one read-only snapshot (no writes, no model calls)."""
    return app.read(_observe, ids)


def record(directory: Path, frozen: JSON) -> JSON:
    """Open a copy of the closed store at the frozen time and record its expected values."""
    archive = json.loads((directory / ARCHIVE).read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as scratch:
        copy = Path(scratch) / STORE
        shutil.copyfile(directory / STORE, copy)
        store = Store.open(copy, clock=lambda: parse_utc(frozen["frozen_at"]))
        try:
            observed = observe(App(store, FailIfCalled()), frozen["ids"])
        finally:
            store.close()
    kinds = Counter(r["kind"] for r in archive["records"])
    return {
        "release": RELEASE,
        "format_version": FORMAT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "library_id": archive["library_id"],
        "through_sequence": archive["through_sequence"],
        "receipts": len(archive["receipts"]),
        "fingerprint": learning_fingerprint(archive),
        "record_kinds": dict(sorted(kinds.items())),
        "missing_kinds": sorted(set(KIND_OWNER) - set(kinds)),
        **frozen,
        "observed": observed,
        "gaps": GAPS,
    }


def main(argv: list[str] | None = None) -> int:
    """Write the fixture files; refuse to replace existing ones without ``--force``."""
    parser = argparse.ArgumentParser(description="Build the frozen format-1 baseline library.")
    parser.add_argument("--force", action="store_true", help="replace existing fixture files")
    args = parser.parse_args(argv)
    names = (STORE, f"{STORE}-wal", f"{STORE}-shm", ARCHIVE, EXPECTED)
    present = [n for n in names if (FIXTURE / n).exists()]
    if present and not args.force:
        print(f"refusing to overwrite {', '.join(present)}; see --help", file=sys.stderr)  # noqa: T201 - command-line output
        return 1
    FIXTURE.mkdir(exist_ok=True)
    for name in present:
        (FIXTURE / name).unlink()
    frozen = build(FIXTURE)
    leftovers = [p.name for p in FIXTURE.iterdir() if p.name.endswith(("-wal", "-shm"))]
    if leftovers:
        msg = f"the store did not close cleanly: {leftovers}"
        raise RuntimeError(msg)
    expected = record(FIXTURE, frozen)
    (FIXTURE / EXPECTED).write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {STORE}, {ARCHIVE} and {EXPECTED} to {FIXTURE}")  # noqa: T201 - command-line output
    return 0


if __name__ == "__main__":
    sys.exit(main())
