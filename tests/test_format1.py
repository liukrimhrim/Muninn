"""Storage format 1 is released: its frozen baseline library must keep opening.

The fixture in ``tests/fixtures/format-1/`` was built once by ``tests.fixtures.format1``
(compatibility-design.md section 9) and is never regenerated. These tests read it only
through copies. Ledger: C01 round trip, M09 version continuity; C02-C05 start with the
first real format change, which must ship a migration that upgrades this fixture.
"""

import hashlib
import json
import shutil
import sqlite3
from collections import Counter
from contextlib import closing

from muninn import practice, workflows
from muninn.library import KIND_OWNER, Store, export_library, learning_fingerprint, parse_utc
from muninn.workflows import RELEASE, App
from tests.conftest import FailIfCalled, rid
from tests.drafts import ANSWER
from tests.fixtures import format1
from tests.fixtures.format1 import ARCHIVE, FIXTURE, STORE

SHA256 = {
    STORE: "ff9c2710b9cf12fd52edd87a4fbdf3858a11433b3f9daf9ff0dcad9d9d560fdb",
    ARCHIVE: "a505f51ab9596ff75dc0685121741b3f3097922a2b93d1b2207fec8caa57e067",
}
EXPECTED = json.loads((FIXTURE / "expected.json").read_text(encoding="utf-8"))


def frozen_hashes():
    return {name: hashlib.sha256((FIXTURE / name).read_bytes()).hexdigest() for name in SHA256}


def sidecars():
    """SQLite files that opening the fixture in place would leave behind."""
    return [p.name for p in FIXTURE.iterdir() if p.name.endswith(("-wal", "-shm", "-journal"))]


def open_copy(tmp_path, clock):
    """Open a copy of the frozen store with this release, at the time it was frozen."""
    copy = tmp_path / STORE
    shutil.copyfile(FIXTURE / STORE, copy)
    with closing(sqlite3.connect(copy)) as conn:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 1  # schema 1
    clock.now = parse_utc(EXPECTED["frozen_at"])
    return Store.open(copy, clock=clock)


def test_the_frozen_files_are_the_released_ones():
    assert frozen_hashes() == SHA256
    assert format1.main([]) == 1  # the generator refuses to overwrite them
    assert sidecars() == []


def test_the_fixture_holds_each_section_9_situation_it_names():
    assert (EXPECTED["release"], EXPECTED["format_version"], EXPECTED["schema_version"]) == (
        "muninn-0.1.0",
        1,
        1,
    )
    seen = EXPECTED["observed"]
    attempts = seen["attempts"]
    assert {"Binary search", "Tarvi words"} <= set(seen["curricula"])  # two subjects
    independent = attempts["independent"]
    assert (independent["assistance"], independent["assessments"][0]["outcomes"]) == (
        [],
        {"c1": "demonstrated"},
    )
    assert [a["criterion_ids"] for a in attempts["hinted"]["assistance"]] == [["c2"]]
    assert attempts["ambiguous"]["assessments"][0]["outcomes"]["c3"] == "cannot_judge"
    assert attempts["misread"]["assessments"][0]["interpretation"] == "supported_misread"
    first, second = attempts["superseded_grade"]["assessments"]
    assert second["supersedes"] == first["ref"]
    ((rated, rerated),) = seen["reviews"]
    assert (rerated["supersedes"], seen["targets"]["word"]["schedule"]["policy"]) == (
        rated["ref"],
        "fsrs-recall",
    )
    (concern,) = seen["concerns"]  # a pending repair, after one unsuccessful cycle
    assert (concern["status"], concern["route"]) == ("open", "repair")
    word = seen["targets"]["word"]["schedule"]
    assert word["due_at"] < EXPECTED["frozen_at"]
    assert word["obligation"]["status"] == "open"
    assert word["fsrs_card"] is not None
    assert (attempts["draft"]["status"], attempts["draft"]["response"]) == ("draft", "It must be")
    unassessed = attempts["unassessed"]
    assert (unassessed["status"], unassessed["assessing"]["status"]) == ("submitted", "pending")
    assert EXPECTED["lost_response"]["result"]["attempt"]["id"] == unassessed["ref"]["id"]
    assert set(EXPECTED["gaps"]) == {
        "two subject curricula sharing one unchanged target",
        "a retired target",
        "a held mapping",
        "measurement_report records",
    }


def test_the_fixture_holds_every_record_kind_this_build_can_write():
    archive = json.loads((FIXTURE / ARCHIVE).read_text(encoding="utf-8"))
    kinds = Counter(r["kind"] for r in archive["records"])
    assert dict(sorted(kinds.items())) == EXPECTED["record_kinds"]
    assert set(KIND_OWNER) - set(kinds) == {"measurement_report"} == set(EXPECTED["missing_kinds"])
    seen = EXPECTED["observed"]
    study, (concern,) = seen["study"], seen["concerns"]
    assert (study["status"], study["teaching"]["status"]) == ("completed", "accepted")
    assert [c["outcome"] for c in concern["cycles"]] == ["unsuccessful"]
    assert concern["cycles"][0]["studies"] == [study["ref"]]
    verification = seen["attempts"]["verification"]
    assert verification["purpose"] == "verification"
    assert concern["cycles"][0]["verification"] == verification["ref"]
    assert (seen["mapping"]["relation"], seen["mapping"]["disposition"]) == ("changed", "accepted")
    notes = seen["curricula"]["Searching notes"]
    assert [hold.split(":")[0] for _ref, hold in notes["exercises"]] == [
        "rests on material flagged as wrong",
        "written for an earlier version of",
    ]
    claims = seen["claims"]
    assert (claims["flagged"]["status"], len(claims["reused"]["sources"])) == ("disputed", 2)
    assert (seen["checkpoint"]["purpose"], seen["checkpoint"]["basis"]) == (
        "exposure_ended",
        "learner_confirmation",
    )
    word = seen["targets"]["word"]["schedule"]
    assert word["next_offer"]["basis"] == [seen["checkpoint"]["ref"]]
    assert seen["tracking"]["lifecycle"] == "active"
    assert seen["tracking"]["windows"][0]["endpoints"][1][1] is not None  # an assigned check
    assert [(r["document_run_id"], r["status"]) for r in seen["timing_runs"]] == [
        ("tab-1", "interrupted"),
        ("tab-2", "active"),
    ]
    assert (seen["effort"]["stale_spans"], seen["effort"]["unknown_tails"]) == (1, 1)
    assert [f["effort"] for f in seen["session_feedback"]] == ["easy"]


def test_a_copy_opens_with_this_release_and_reads_every_expected_value(tmp_path, clock):
    archive = json.loads((FIXTURE / ARCHIVE).read_text(encoding="utf-8"))
    assert learning_fingerprint(archive) == EXPECTED["fingerprint"]
    store = open_copy(tmp_path, clock)
    try:
        exported = export_library(store, writer_release=RELEASE)
        assert learning_fingerprint(exported) == EXPECTED["fingerprint"]
        app = App(store, FailIfCalled())
        assert format1.observe(app, EXPECTED["ids"]) == EXPECTED["observed"]
    finally:
        store.close()


def test_the_archive_restores_into_an_empty_store_without_a_model(tmp_path, clock):
    # C01: same logical snapshot, receipts, curricula, judgments, dates and drafts
    clock.now = parse_utc(EXPECTED["frozen_at"])
    text = (FIXTURE / ARCHIVE).read_text(encoding="utf-8")
    store = App.restore(tmp_path / "restored.sqlite", text, clock=clock)
    try:
        exported = export_library(store, writer_release=RELEASE)
        assert learning_fingerprint(exported) == EXPECTED["fingerprint"]
        app = App(store, FailIfCalled())
        assert format1.observe(app, EXPECTED["ids"]) == EXPECTED["observed"]
    finally:
        store.close()


def test_the_next_answer_on_a_copy_appends_once_and_never_touches_the_fixture(tmp_path, clock):
    lost = EXPECTED["lost_response"]
    draft = EXPECTED["observed"]["attempts"]["draft"]
    curriculum = EXPECTED["observed"]["curricula"]["Binary search"]
    tab2 = EXPECTED["observed"]["timing_runs"][-1]
    store = open_copy(tmp_path, clock)
    app = App(store, FailIfCalled())
    try:
        app.recover()  # startup ends what the stopped app left running, nothing else
        records, _ = store.snapshot()
        operation, run, tail = records[EXPECTED["through_sequence"] :]
        assert (operation["id"], operation["payload"]["status"]) == (
            lost["result"]["operation"]["id"],
            "interrupted",
        )
        assert (run["id"], run["payload"]["close_reason"]) == (tab2["ref"]["id"], "app restarted")
        assert (tail["kind"], tail["payload"]["continuity"]) == ("activity_span", "unknown_tail")

        # the request whose response was lost: the same receipt, nothing written
        replay = app.submit_answer(lost["request_id"], **lost["inputs"], client_at=None)
        assert replay == lost["result"]
        assert store.snapshot()[0] == records

        # the saved draft is submitted: one command, one receipt, appended after the rest
        request_id = rid()
        sent = app.submit_answer(
            request_id,
            attempt_id=draft["ref"]["id"],
            base=draft["ref"]["revision"],
            response=ANSWER,
            client_at=None,
        )
        after, receipts = store.snapshot()
        (receipt,) = [r for r in receipts if r["request_id"] == request_id]
        assert (receipt["first_sequence"], receipt["committed_sequence"]) == (
            len(records) + 1,
            len(after),
        )
        assert [
            {k: r[k] for k in ("kind", "id", "revision")} for r in after[len(records) :]
        ] == receipt["record_refs"]
        assert after[: len(records)] == records

        # it continues the same session of the same selected curriculum, assessment pending
        view = app.read(workflows.practice_view, draft["session"]["id"])["attempt"]
        assert (view["ref"], view["status"], view["response"]) == (
            sent["attempt"],
            "submitted",
            ANSWER,
        )
        assert view["assessment"]["status"] == "pending"
        enrollment = app.read(practice.enrollment_for, curriculum["ref"]["id"])
        assert enrollment is not None
        assert enrollment["goal_order"] == curriculum["goal_order"]
    finally:
        store.close()
    assert frozen_hashes() == SHA256
    assert sidecars() == []
