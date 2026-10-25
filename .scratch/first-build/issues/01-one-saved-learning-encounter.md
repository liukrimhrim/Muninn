# 01 — One saved learning encounter (build slice 1)

Status: ready-for-human

Implements slice 1 of the [first-build plan](../../skill-maintenance/first-build-plan.md#build-order-and-exit-checks) under [Design Baseline 1](../../skill-maintenance/design-baseline.md). Implementation authorized by the user on 2026-10-24 with these setup choices: Python 3.12 + FastAPI + stdlib `sqlite3`, plain HTML/JS (no build step), Anthropic `claude-opus-5-5` for drafting and assessment (key from `ANTHROPIC_API_KEY`), one learner, one process, one local store.

## Exit check (from the plan)

From a fresh store, use previously unauthored material, answer in free text, restart, and recover the exact source, exercise, answer and judgment. Export and restore into a separate empty store, then continue the same curriculum with no model call during restore. A retry creates one attempt; a model failure preserves the answer. The summary distinguishes independent/helped/unknown evidence and accounts for preparation, feedback and waiting without duplicate time.

## Code layout

One module file per design module (`module-design.md`); the seven names are responsibilities, not packages.

| File | Design module | Owns record kinds |
|---|---|---|
| `muninn/library.py` | Library | receipts, envelope, schema metadata, active-store choice |
| `muninn/content.py` | Content | source, knowledge, target, curriculum, exercise, teaching, mapping |
| `muninn/evidence.py` | Evidence | attempt, study, assessment, review, projection, exposure, condition_checkpoint |
| `muninn/practice.py` | Practice | enrollment, session, concern, schedule, practice_offer, selection |
| `muninn/measurement.py` | Measurement | timing_run, activity_span, session_feedback, measurement_cohort, measurement_report |
| `muninn/workflows.py` | Application Workflows | operation, transition; provider adapter |
| `muninn/web.py` + `muninn/static/` | Web Interaction | none (transient browser state only) |

Allowed imports follow `module-design.md` § Dependency direction; `tests/test_architecture.py` enforces it (M01/M02) and proves the check fails on seeded violations. Every record write and kind-scoped read passes `by=<owner>`; the Library refuses a foreign kind at runtime.

## Storage and format

- One append-only `records` table holds the portable envelope `{kind, id, revision, sequence, recorded_at, payload}` (compatibility-design §2). Revisions are never overwritten. `receipts` holds `CommandReceipt` rows. `PRAGMA user_version` = `store_schema_version` 1; a newer version refuses writable startup.
- Payloads are pydantic models with `extra="forbid"` owned by each module; the same validators run at write and at import. No floats are stored, so sorted-key compact JSON equals RFC 8785 (JCS) output for these records.
- Export: one `library-<library_id>-<export_id>.learning.json` with `format_version` 1, all revisions by sequence, receipts, and `integrity` = SHA-256 over JCS without `integrity`. Restore goes into a new empty store file, validates, reopens and compares the learning fingerprint, then switches `data/active.json`. The previous store stays on disk.

## Decisions on the digest ambiguities

1. Relation meaning stays free text (`knowledge.form = relation`, `dependencies[].role`); there is no enum in the contract.
2. The model returns verbatim quotes; the app computes UTF-8 byte offsets at the first occurrence. A quote that is not found is a failed check.
3. The assessor's proposed `next` stays in `raw_response`; learner feedback is `assessment.explanation`. Slice 1 delivers no follow-up questions or teaching.
4. Acceptable alternative answers live in each criterion's `requirement` text (the exercise record has no other slot).
5. Semantic review of drafted content is the learner's outline preview; `design_review` records `actor: learner-preview`, `disposition: provisional`.
6. Exercises may not cover an `execute`-mode target in free text; such targets stay visible as having no exercise.
7. Server-initiated commands use deterministic request IDs (`uuid5(operation_id, phase)`), so replays are idempotent.
8. On startup, `pending`/`running` operations become `interrupted` and are offered for explicit retry, which creates a new operation in the same `request_group`. Malformed output is retried once automatically (`try_index` 2); timeouts are not retried automatically.
9. Hints: `reveal_hint` records an exposure and returns the text; the browser's display acknowledgement appends `Assistance`. A reveal without an acknowledgement makes that criterion's independence unknown, not independent.
10. Answer occurrence time is the server receive time (`basis: qualified_clock`, raw client time kept). The single local process makes that the best available clock.
11. Recall-mode targets use the capability schedule in slice 1; the FSRS adapter arrives in slice 4.
12. Summaries are computed live; no `measurement_report` is saved in slice 1.
13. `timing_run` takeover and `unknown_tail` spans are in slice 1, because "without duplicate time" needs them.

## Capability transitions implemented (lifecycle contract § transitions)

| Event per exact target | Schedule effect |
|---|---|
| Draft accepted | Enrollment entry `unstarted`; no schedule |
| Exercise delivered | Admit target (`active`, `admitted_at`); schedule rev1 `need: initial`, open initial obligation, no due date |
| First independent full demonstration | Initial obligation consumed; successor `later` obligation; `need: independent_check`, `due_at = answer time + 24h` |
| Helped full demonstration | Obligation stays open; `need: independent_check`, `due_at = answer time + 24h` |
| Supported error | Obligation open; `need: repair`; repair concern opened |
| Not shown / cannot judge / partial coverage | Obligation open; `need: initial` or `clarify`; no due date, no failure |
| Assessment pending, failed or malformed | No transition |

## Acceptance assertions → tests

- Exit check end to end over HTTP with a scripted provider: `tests/test_exit_check.py`.
- Receipts and retries (C15), interrupted/stale operations (C16, M08, V12), restore with a provider that fails when called (C01, M09), corrupt imports (C08), export atomicity (C18), restore refusal (C20): `tests/test_library.py`, `tests/test_workflows.py`.
- CCA01/CCA02/CCA03, W01/W03/B01/B02, O01/O02/O13/O14, D06/D08/D09: unit tests at the owning module.
- Then a live run with the real model on fresh material in a real browser (typing, help, submit, refresh/resume, export/restore).

## Deferred (later slices)

Diagnosis, clarification turns, teaching and fresh variants (slice 2); corrections, reuse and content-change compatibility (slice 3); FSRS, 7-day checks, due-work selection, budgets, tracking cohorts (slice 4); semantic qualification on the acceptance pack (slice 5).

## Comments

**2026-10-24 — implemented (scripted model).** All five modules, the web UI and 90 tests are in place; `bin/lint` is green. The exit check passes end to end over HTTP with a scripted model: restart recovers the exact source, exercise, answer and judgment; export → restore into a new store → continue works with a provider that fails if called; a retried submit makes one attempt; a timeout keeps the answer until an explicit retry; the summary separates independent/helped/unsettled evidence and counts overlapping time once. The UI flow (intake, outline, autosave, hint, reload-resume, submit, feedback, summary, export/restore) was checked in a real browser against the scripted server.

Code review (standards + spec) found eight spec defects, all fixed with regression tests: explicit retries now stay in their request group; an unconfirmed hint leaves independence unknown; hints cannot be revealed after submission; unknown-length gaps reach summaries; all intake time is attributed to the new material; SDK auto-retries are off; a later session resumes an earlier unfinished draft; past session summaries keep their own results; exercises follow the current outline order.

Departure from the spec: the Anthropic provider enables server-side refusal fallback (`fallbacks: "default"`); the model that actually answered is recorded on every assessment.

**Still open for this slice:** the live run with the real model on previously unauthored material (needs `ANTHROPIC_API_KEY`), observed in a real browser.
