# Storage format 1 baseline fixture

The frozen baseline library of storage format 1, released on 2026-11-02 with `muninn-0.1.0` ([compatibility design §9](../../../.scratch/skill-maintenance/compatibility-design.md#9-concrete-acceptance-cases)). One library built through the real application commands with a scripted model and a controlled clock (2026-10-24 to 2026-10-28, UTC) by `uv run python -m tests.fixtures.format1`.

| File | What it is | sha256 |
|---|---|---|
| `library.sqlite` | the store: schema 1 (`PRAGMA user_version = 1`), closed cleanly | `ff9c2710b9cf12fd52edd87a4fbdf3858a11433b3f9daf9ff0dcad9d9d560fdb` |
| `library.learning.json` | its export archive, `format_version` 1, written by `muninn-0.1.0` | `a505f51ab9596ff75dc0685121741b3f3097922a2b93d1b2207fec8caa57e067` |
| `expected.json` | the expected values, recorded once from a copy of the frozen store and reviewed by eye | |

**§9 situations.** Two curricula in two subjects ("Binary search", "Tarvi words") hold: an independent success, a hinted attempt, an ambiguous (`cannot_judge`) answer, a supported misread, one grade superseded through dispute and accepted correction, one recall rating superseded by a re-rating on an FSRS goal, a pending repair (an open repair concern after one unsuccessful cycle), an overdue FSRS review, a saved draft, a submitted answer never assessed, and that answer's request, whose response was lost after commit (`lost_response`: replaying its request ID returns the saved receipt).

**Every record kind this build writes** (`record_kinds` in `expected.json`): besides the above, a repair cycle (teaching, completed study, fresh verification check); a third curriculum, "Searching notes", that reuses one binary-search claim, has a flagged claim and a changed goal (mappings `equivalent` and `changed`, a transition, two held exercises); a confirmed-closed feedback view (condition checkpoint); a tracking plan with one assigned check; two timer runs, one taken over by the other, leaving a stale late span and an unknown tail, with the second run still active (startup interrupts it); and session feedback.

**Known gaps** (not reachable in this build, so not faked):

- *Two subject curricula sharing one unchanged target*: no flow creates a shared exact target; reuse links claims, never goals (ledger CCA04, P19, C09).
- *A retired target*: no command retires a goal or removes it from a curriculum (ledger C10); `revise_target` writes a `changed` mapping and keeps the old revision `accepted`.
- *A held mapping*: every mapping is written `accepted`; a change holds the exercise written for the old goal instead.
- *`measurement_report` records*: no command saves a report (saved reports are deferred: ledger X12, P08, P31, B07).

**Rule.** Never regenerate or edit these files; the generator refuses unless forced, and the tests check both hashes. A storage format change adds a migration and a new fixture directory (`format-2/`, …), and every older fixture must keep upgrading through each documented step to the current release. Tests only ever open copies.
