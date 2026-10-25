# 02 — Diagnose and repair within a larger task (build slice 2)

Status: ready-for-human

Implements slice 2 of the [first-build plan](../../skill-maintenance/first-build-plan.md#build-order-and-exit-checks) on top of [slice 1](01-one-saved-learning-encounter.md), under the same setup choices (Python 3.12, FastAPI, stdlib `sqlite3`, plain HTML/JS, Anthropic `claude-opus-5-5` behind the provider seam). Governing rules: [diagnosis design](../../skill-maintenance/diagnosis-design.md), [lifecycle contract §3](../../skill-maintenance/learning-lifecycle-contract.md#3-authoring-is-a-checked-operation-before-delivery) (authoring intents `exercise_variant`, `teaching_intervention`; teaching-to-study binding) and [everyday learning §5](../../skill-maintenance/everyday-learning-design.md#5-diagnosis-and-repair-that-can-stop) (three diagnostic prompts per session and per concern; stop after two unsuccessful repair cycles).

## Exit check (from the plan)

Run a fact and a connected explanation through the same core. Correct parts survive a connection error; omitted evidence and misreads take different paths; help is recorded; the next task changes after the learner's response. A useful clarification can also end with "still uncertain".

## The flow

```
larger-task answer ─ assess (protocol v2: observations + misread + competing hypotheses + optional question with branches)
  ├ supported misread only ─────────── brief correction; no concern, no question, no repair; no error counted
  ├ omitted / unjudgeable + useful Q ─ uncertainty concern → clarification turn(s)
  ├ supported error, 1 hypothesis ──── repair concern → teaching
  └ supported error, ≥2 hypotheses with different practice + discriminating Q ─ diagnosis → clarification
clarification answer → its outcome picks the saved branch: resolve | teach <hypothesis> | still uncertain (or ask again within the allowance)
teaching: authoring op (teaching_intervention) → checked → accepted `teaching` → `study` started → learner completes → concern route verification
verification: authoring op (exercise_variant) → checked coverage → accepted exercise → attempt bound by `verification_of` → cycle outcome
  recovered → concern resolved (the post-teaching 24 h check stays) · unsuccessful → change approach; second time stop
  assisted → later check, no re-teaching · missing/unjudgeable → stop automatic repair, offer pause
```

## Decisions

1. **Competing diagnoses come from the assessor, decisions from Practice.** Assess protocol v2 adds `misread_criterion_keys`, `hypotheses [{key, criterion_keys, cause, practice}]` and an optional `question {prompt, criteria [{key, requirement, about_criterion_key}], reference_response, expected_seconds, branches}`. The old `next` field is dropped (it was provenance only). Evidence checks the output deterministically; Practice decides with pure rules whether a question earns its time.
2. **A question earns its time only when its branches differ.** Branch rules: `demonstrated → resolve | teach h`, `error → teach h`, `inconclusive → still_uncertain`; a question is asked only when the demonstrated and error branches lead to different practice. An error concern asks only when at least two hypotheses call for different practice; otherwise it goes straight to teaching (with no single hypothesis, the teaching is labelled support under uncertainty).
3. **One concern per answer.** Supported (non-misread) errors open a repair/diagnosis concern scoped to the erred requirements; with no errors, omitted/unjudgeable requirements open an uncertainty concern only when a useful question exists. An unresolved (open or paused) concern overlapping the same scope is reused, so a new session or rewording cannot reset its counts: the reused concern takes in the new scope, an error kind outlives an uncertainty, and a concern stopped after two unsuccessful cycles stays stopped whatever the new answer shows.
4. **Misread.** `assessment.interpretation = supported_misread` with the misread criteria; requires at least one demonstrated criterion in the same answer (the sound reasoning). Observations carry `misread: true`; `qualify` does not count them as errors, and the target is "not settled" (no fabricated success, no repair need).
5. **Clarification questions are exercises with `use: clarification`.** Proposed by the assessment operation, checked by Content (criteria map to judged, non-demonstrated original criteria and inherit their coverage), saved before delivery, and delivered as `attempt.purpose = clarification` with `attempt.concern`. Their branches live on the concern (`concern.question`). Ordinary selection never serves clarification or verification exercises. Clarification answers are kept as observations but never set a target's label: a focused question cues its answer, so it cannot clear (or create) a whole-task result. Labels use each requirement's latest usable observation (demonstrated or supported error), and a whole-target demonstration still needs one answer showing every requirement.
6. **Diagnostic allowance.** Three per persisted session (all concerns) and three per concern (all sessions). Each criterion of a question is one diagnostic request, so wrapping three requests in one question uses three slots. A prompt counts when its draft is delivered (resume does not count twice). When the allowance cannot fund a question, an error concern falls back to teaching under uncertainty and an uncertainty concern ends "still uncertain".
7. **Teaching** (`teaching_intervention`): Workflows gathers the packet (concern scope, requirement statements, knowledge and source text, the learner's quoted evidence, the supported hypothesis or the open alternatives as Practice's `help_basis` says, earlier approaches and whether they worked); Content prepares the request and `accept_teaching` runs the checks itself: nonempty content and approach, every quote in the source (or an explicit derivation), and after an unsuccessful cycle a different approach and different text. Accepted output becomes a `teaching` record (review checks saved, disposition accepted, provisional under the protocol). It is delivered as an Evidence `study` (`status: started`, `teaching` ref, identical content); only the learner's explicit "I've worked through this" appends `completed`. Two refused tries leave "this explanation is not ready" with retry or pause; no third call.
8. **Completed teaching replaces the open obligation** (`replaced`, not satisfied) with a later obligation due 24 h after completion; the concern moves to verification and opens a repair cycle holding the completed study refs.
9. **Fresh integrated variant** (`exercise_variant`): must cover exactly the original exercise's target requirements (checked coverage), have a prompt different from every earlier prompt in the family, declare `variation_kind: new_instance` with an explanation of why the old final answer cannot satisfy it, not contain its reference answer in the prompt, and pass the slice-1 exercise checks. Content builds the packet from its own definitions and `accept_variant` runs these checks itself. Saved as an exercise in the same family with `use: verification` and a `design_review.variation`. Delivered with `attempt.verification_of {concern, cycle_id, studies, scope}`.
10. **Clarification and verification offers are `extra` slots.** They never consume or move a schedule; a supported error on them still sets `need: repair`. The immediate post-teaching check therefore leaves the 24 h check untouched.
11. **Cycle outcome** from the concern's scope in the verification answer: all demonstrated without help → recovered (concern resolved); any supported error → unsuccessful (first: repair with a changed approach; second: stop, `route: content_review`, "These two approaches have not resolved this yet"); demonstrated with help → assisted (`route: later_check`, no re-teaching); otherwise, including help that may have been seen but was never confirmed, incomplete (`route: assessment_review`, stop and offer pause). Errors outside the concern's scope open a new concern in ordinary waiting order.
12. **Next step order** (`practice.next_step`): resume an open draft → resume a started study → the oldest actionable open concern (ask / teach / verify / stopped) → the next unanswered practice exercise → nothing. Stopped concerns wait for the learner's explicit pause.
13. **Time.** The browser times clarification answers as `diagnosis` and teaching as `study`; nothing new server-side. Budget-based early stopping waits for slice 4 budgets.

## Record additions (unreleased format 1; every addition has a default so slice-1 records still validate)

| Owner | Record | Addition |
|---|---|---|
| Content | `exercise` | `use: practice/clarification/verification`; `design_review.variation {kind, basis, changed, held_fixed, old_answer_insufficient}?` |
| Content | `teaching` (new) | lifecycle §3 shape: targets, scope, concern, content, approach, sources, supporting_claims, derivation, authoring_operation, review, status |
| Evidence | `attempt` | `concern: Ref?`, `verification_of {concern, cycle_id, studies, scope}?` |
| Evidence | `study` (new) | session, targets, scope, kind (repair), teaching, concern, content, status, started_at, completed_at, time_evidence |
| Evidence | `projection.observations[]` | `misread: bool` |
| Practice | `concern` | `kind: error/uncertainty`, `hypotheses [{key, cause, practice}]`, `focus?` (the supported hypothesis), `question {exercise, branches}?`, `cycles [{id, studies, verification?, outcome}]`. The concern view also publishes derived `help` (supported/uncertain/direct) and `still_uncertain`; they are not stored |

## Tests (agreed seams, scripted model)

- Exit check over HTTP: `tests/test_slice2_exit_check.py`.
- Application commands: clarification branches, still uncertain, caps, cycle limits, assisted/incomplete verification, refused teaching, concern reuse, earlier-session pending answers: `tests/test_repair.py`.
- Pure rules: v2 assessment checks, misread qualification, scoped outcomes, teaching and variant checks, question discrimination and help basis: `tests/test_evidence.py`, `tests/test_content.py`, `tests/test_practice_rules.py`.
- Library/restore: concerns, studies, teaching and variants survive export/restore with a provider that fails if called (inside the exit check). Architecture test unchanged.

## Deferred

Diagnostic presentation reservations with confirmed/uncertain display states (P24/P33/P42: a delivered prompt counts conservatively instead); budget-based stopping and branch-cost reservation (P17, slice 4); learner "question this judgment" and correcting a misread after the fact (slice 3); manual "continue anyway" past a stop, including a learner-chosen worked example after "still uncertain"; cross-target exposure scope for teaching (slice 4); staleness of authoring requests on a changed target or source (only the concern revision is checked now, because nothing can revise a target or source before slice 3's content editing).

## Comments

**2026-10-24 — implemented (scripted model).** Assess protocol v2, clarification questions, teaching and fresh variants with their checks, concerns with branches and cycles, the bounded next-step order, the HTTP endpoints (`/sessions/{id}/next` now also starts authoring in the background, `GET /studies/{id}`, `POST /studies/{id}/complete`, `POST /concerns/{id}/pause`) and the browser pages (clarification, study, preparing, not ready, stopped; concern notes on feedback and summary). 141 tests pass and `bin/lint` is green. The exit check passes over HTTP: a fact and a connected explanation in one exercise; the fact stays independent through the connection error; omitted evidence asks a neutral question while a misread gets a correction and no question; teaching is accepted before delivery and its completed study binds the fresh check; the next task after each answer differs; a clarification can end "still uncertain"; restart and export/restore keep the whole repair history with a provider that fails if called. The UI flow was checked in a real browser against `tests.dev_server` (answer, clarification, reload-resume, teaching, fresh check, summary; the misread and still-uncertain paths).

The browser check found two defects, both fixed with regression tests: a cued clarification answer was clearing the larger task's error from the target label (clarification answers no longer set labels); and the preparing page sent a span context that was not an exact ref, so its batch was refused (fixed on the page, and the server now refuses a malformed span on its own instead of rejecting the whole batch, which was silently losing later time; this hardening is outside the slice-2 spec).

Code review (standards + spec) found these, all fixed: a stopped concern could restart repair through a later omitted-evidence answer; a reused concern dropped new errors outside its scope; a clarification from an earlier session still waiting for grading made the page redirect forever (the practice view now shows any waiting answer in the enrollment, with its retry); the summary counted questions instead of requests; Practice now owns the supported-error rule (via Evidence), "support under uncertainty" and "still uncertain"; Content owns the variant packet, its coverage and checks; a started study resumes before concerns. Kept as is: Practice reads Evidence's published `AssessmentOutput` (the validated assessor protocol) instead of a second copy of it.

**Still open for this slice:** the live run with the real model (needs `ANTHROPIC_API_KEY`): previously unauthored material through an actual diagnosis, teaching and fresh check, observed in a real browser.
