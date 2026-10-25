# 03 — Correct knowledge and judgments (build slice 3)

Status: ready-for-human

Implements slice 3 of the [first-build plan](../../skill-maintenance/first-build-plan.md#build-order-and-exit-checks) on top of [slice 1](01-one-saved-learning-encounter.md) and [slice 2](02-diagnose-and-repair.md), under the same setup choices (Python 3.12, FastAPI, stdlib `sqlite3`, plain HTML/JS, Anthropic `claude-opus-5-5` behind the provider seam). Governing rules: [compatibility §3 and §6](../../skill-maintenance/compatibility-design.md#6-curriculum-revisions-and-evidence-continuity) (exact refs, mappings, transitions, cases C09–C12), [lifecycle §4](../../skill-maintenance/learning-lifecycle-contract.md#effective-event-order-and-recomputation) (one occurrence-order resolver; `descendant-correction-1`; `resolution_rule`/`check_effects`), [material workflow](../../skill-maintenance/material-workflow.md#sources-existing-knowledge-and-uncertainty) (reuse and contradictions), [everyday learning §6 Corrections](../../skill-maintenance/everyday-learning-design.md#corrections) and [module design](../../skill-maintenance/module-design.md#shared-transaction-private-responsibilities) ("Accept a corrected assessment", "Change a curriculum or exposure interpretation").

## Exit check (from the plan)

A changed condition invalidates dependent exercise mappings. A corrected grade updates the effective state once. Old definitions and judgments remain inspectable. A flagged contradiction cannot disappear through reuse. Unrelated material remains usable.

## The flows

```
edit a goal (action/mode/conditions/requirement wording)
  → new target revision (same id) + `changed` mapping + new curriculum revision + enrollment revision, one `transition`
  → exercises bound to the old revision are held (stale exact refs); old evidence and schedule stay with the old revision
  → the new revision is unstarted; "this exercise still checks the edited goal" rebinds an exercise explicitly

"this material is wrong" on a claim → claim disputed (reason kept)
  → every target resting on it (transitively) and every exercise covering one is held; unrelated targets keep working
  → resolve by correcting the claim (meaning change: dependents get new revisions, as above) or keeping it as is

new material → drafting packet lists existing claims → the draft may propose "same claim" / "conflicts"
  → acceptance waits for the learner's review of the proposals
  → same + both unflagged: reuse the existing identity (its new passage is attached) or keep separate
  → same as a flagged claim, or a conflict: kept separate and saved disputed; reuse is refused

"this judgment is wrong" (reason) → reassessment operation (original prompt, rubric, help, answer, earlier judgment, the learner's reason)
  → checked output waits; the page previews the exact effect (dry run of the correction)
  → accept: assessment revision under the same id (supersedes, reason), projections rebuilt in occurrence order,
    schedules replayed by the one resolver, concerns reconciled, one `transition` — all in one receipt
  → keep: the operation is cancelled; nothing changes
```

## Decisions

1. **Bindings are exact.** Schedules, projections, enrollment entries and exercise coverage match a target by exact `(id, revision)`, never by id alone. An exercise is usable only when it is accepted, covers the *current* revision of each of its targets, and none of those targets rests on disputed material (Content's `exercise_hold`). Stale mappings are held by derivation from their exact refs; nothing re-stamps them.
2. **Every goal edit is a changed contract** (`mapping.relation = changed`, no `criterion_map`): the old revision keeps its evidence, schedule and due date; the new one starts unstarted and untested. Equivalent-wording edits that carry a schedule forward are deferred. Requirements keep their ids; adding or removing a requirement needs a new exercise and is deferred.
3. **Explicit rebinding.** "This exercise still checks the edited goal" appends an exercise revision whose coverage names the current target revisions (same criteria and requirement ids), reviewed by the learner. Only a practice exercise held as stale can be rebound. Old attempts stay bound to the exercise revision they answered.
4. **Disputes are status, holds are derived.** Flagging a claim appends a `disputed` revision with `dispute {reason, related}`; dependents are not versioned, because the meaning has not changed yet. Holds follow the current status of every cited claim, transitively through `dependencies`. Schedules are not rewritten by a hold; the due date stays stored and the progress view says why it cannot be served. Correcting the statement or scope is a meaning change and versions dependents (claims citing it, then targets, curricula and enrollments); keeping the wording clears the flag with a status-only revision.
5. **Reuse is reviewed before acceptance.** The initial-outline protocol (v2) receives existing claims (`E1…`) and may mark each drafted claim `same` or `conflicts` with reasons. When any proposal exists the operation succeeds with `acceptance: pending` and the learner decides. Reuse attaches the new passage to the existing claim (a sources-only revision; provenance kept) and records an accepted `equivalent` mapping. A match with a flagged claim, or a conflict, can only be kept separate *and disputed*; asking to reuse it is refused. A disputed claim's flag cannot be cleared by reuse. A listed claim reworded after drafting can only stay separate.
6. **Corrections are reviewed by the assessor, decided by the learner.** "This judgment is wrong" offers "I misread it", "My answer is valid", "The question is unclear" and free text. It saves a `reassess-answer` v1 operation (same output schema as assess-answer v2, no question). A self-report is a claim to check, not a success. The checked result waits; the preview is the correction applied inside a rolled-back savepoint, so it shows exactly what accepting does, and accepting with the preview's digest refuses (writing nothing) if the effect has changed since. The corrected judgment records the model that actually answered the review. Only answers whose judgments set labels can be disputed (not clarification answers). One live review per answer.
7. **One resolver.** Only the owner of the *current* obligation advances it; a second owner of an already met or replaced check counts as extra. Ordinary acceptance, late results, completed teaching and corrections all rebuild each affected exact target's projection from the current assessment revisions in occurrence order (submission time, then commit sequence), and replay its capability schedule from admission over that chronology (answers and completed studies). The replay reuses obligation identities by `(origin, kind)`, appends only the changed dispositions (terminal predecessors, invalidated opportunities, then the current state), and writes nothing when the replayed state equals the saved one, so a repeated correction adds no effect. A known later unassessed owned answer holds the schedule (`need: held`).
8. **Descendants after a correction** (`descendant-correction-1`, 24-hour capability policy): an owned answer whose opportunity no longer exists in the replayed lineage re-anchors only as an independent demonstration at or after both its offered due time and the replayed due time (`replaced`, not consumed; successor due answer + 24 h); otherwise it has no scheduling effect, though a supported error still sets repair. Correction revisions carry `resolution_rule` and `check_effects` (offers on invalidated opportunities: `reanchored`/`no_advance`/`pending`, and `held` with `revokes_reservation` for an unsubmitted draft, whose later submission counts as extra).
9. **Concern reconciliation.** A concern citing the corrected assessment keeps only the scope still supported by its effective evidence; with none left it becomes `superseded` (its teaching and time stay in history). A corrected verification answer re-derives its cycle outcome. New supported errors outside every open concern open an ordinary error concern (no question). Content changes narrow or supersede concerns on replaced revisions; concerns on held targets wait.
10. **Transitions.** Workflows writes `transition {scope, category: curriculum|assessment, before, after, actor, reason}` in the same command, linking the revised records (before = the revision each one replaced). It contains no scheduling decision.
11. **Histories.** The target history shows every definition revision with its own evidence, the schedule decisions with reasons, mappings, and every judgment with its correction lineage (earlier revisions stay readable). Feedback marks a corrected judgment and keeps the earlier one inspectable.

## Record additions (unreleased format 1; every addition has a default so slice-1/2 records still validate)

| Owner | Record | Addition |
|---|---|---|
| Content | `knowledge` | `dispute {reason, related: Ref[]}?` |
| Content | `mapping` (new) | `from, to, relation, disposition, criterion_map, reviewer, reason, supersedes` (compatibility §3) |
| Content | `exercise` | `design_review.rebound_from: Ref?` |
| Practice | `schedule` | `resolution_rule: Algorithm?`, `check_effects [{offer, disposition, revokes_reservation, basis, reason}]` |
| Workflows | `transition` (new) | compatibility §3 shape |
| Workflows | `operation` | `answered_by: text?` (the model that actually answered; the requested one stays in `model`) |

A reassessment is an `assess_answer` operation (no authoring intent) whose protocol is `reassess-answer`; its input is the exact assessment revision it reviews.

Protocols: `draft-initial-outline` v2 (`existing` proposals per drafted claim), `reassess-answer` v1.

## Tests (agreed seams, scripted model)

- Exit check over HTTP: `tests/test_slice3_exit_check.py`.
- Application commands: goal edits, rebinding, flags and corrections of claims, reuse review, judgment corrections (error→correct, correct→error, misread, verification cycle, descendant, pending hold, repeat), previews: `tests/test_corrections.py`.
- Pure rules: reuse proposal checks and reuse choices: `tests/test_content.py`. The replay folds are private to Practice and are exercised through the commands above.
- Library/restore: mappings, transitions, revised assessments and replayed schedules survive export/restore with a provider that fails if called (inside the exit check). Architecture test unchanged.

## Deferred

Equivalent target revisions that carry a schedule forward; adding/removing requirements; split/merge editing and criterion-map reinterpretation (C11); seven-day intervals and the recall stream in replay (slice 4); exposure-relevance scope and timing holds from exposure (slice 4); correcting clarification answers; per-slot release of a mixed offer when only one of its targets changes (the whole draft is released and kept); learner-supplied criterion outcomes without a model review; saved reports and caught-up checkpoints (no saved reports exist yet).

## Comments

**2026-10-25 — implemented (scripted model).** Goal edits with changed mappings and held stale exercises, explicit rebinding, claim flags with derived holds, claim corrections that version their dependents, reuse review before acceptance, and judgment disputes with a model review, an exact preview and accept/keep. Schedules, projections and concerns now go through one occurrence-order resolver for ordinary acceptance, late results, completed teaching and corrections; schedules, projections, enrollment entries, offers and concern scopes bind exact target revisions. New HTTP endpoints: `POST /targets/{id}/revise`, `GET /targets/{id}/history`, `POST /knowledge/{id}/flag`, `POST /knowledge/{id}/revise`, `POST /exercises/{id}/rebind`, `GET /operations/{id}/proposals`, `POST /operations/{id}/accept`, `POST /attempts/{id}/dispute`, `GET /operations/{id}/correction`, `POST /operations/{id}/correction/accept` (with `preview`), `POST /operations/{id}/correction/keep`. Browser pages: goal edit, "This material is wrong" / correct / keep on each claim, held exercises with rebind, goal history (every version, its answers, every judgment revision, check decisions), "This judgment is wrong" on feedback and history, the review page with its preview, and the reuse review page. 172 tests pass and `bin/lint` is green. The exit check passes over HTTP (`tests/test_slice3_exit_check.py`), including export/restore with a provider that fails if called.

Browser check against `tests.dev_server`: dispute → review → preview → accept (and the "kept" path), goal edit → held exercise → rebind → practice resumes on the new contract, flag → holds → keep clears them, second material whose repeat of a flagged claim stays held while the clean match is reused, goal history with both judgments. It found two UI defects, both fixed: forms saved on the page's own hash did not navigate back (this also affected slice 1's "Edit titles", fixed with the same `go()` call), and the check decisions list read terminal obligation revisions as needs.

Code review (standards + spec). Standards fixes: one shared `library.exact_key`; typed holds from Content (the browser and `exercise_hold` no longer parse prose); Evidence owns "disputable" and the misread set; Content owns "this draft needs a reuse review"; one waiting-review guard (closing a gap where "keep" during a running review was later overwritten); typed replay state; dead constants and helpers removed. Spec fixes, each with a regression test: a second owner of a met check no longer moves it; concern scopes match exact revisions (a late grade on an old goal version stays with that version); a revoked draft's pending answer no longer holds the schedule; a corrected fresh check does not unpause a paused concern; a repeated correction writes no concern or schedule revision; reuse of a claim reworded after drafting is refused; rebinding is guarded server-side; accept is tied to the preview digest; the review's answering model is recorded. Kept as is: a rebound exercise's `design_review.actor` is the learner's review (the original reviewer stays in `rebound_from`).

**Still open for this slice:** the live run with the real model (needs `ANTHROPIC_API_KEY`): a real reassessment of a disputed answer and real reuse proposals on new material, observed in a real browser.
