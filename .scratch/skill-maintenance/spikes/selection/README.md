# Exercise selection under a time budget

Throwaway comparison of a short diagnostic question, focused practice and overlapping checks. Uses the existing assessment validator, bridge, representation examples and pure `NextSession` planner. All added answers, grading judgments and times are authored. No learner model is fitted, review is skipped in real use, or FSRS record is changed.

The [standalone demo](index.html) shows a next action immediately. Its sample-answer buttons and six walkthroughs are optional; the user does not need to answer an exercise or complete a review form. [Selection design](../../selection-design.md) records the proposed policy and its limits.

## Reproduce

With Node.js (verified with v26.0.0), no packages:

```sh
node .scratch/skill-maintenance/spikes/selection/replay.mjs
```

The runner loads the real components, checks the contrasting paths, writes [report.json](report.json), and builds the self-contained [index.html](index.html) from [shell.html](shell.html). Source hashes, selected actions, charges, remaining concerns and retained future checks are in the report. Thirty-one replay checks and three page-handler checks pass. The handlers run against a minimal DOM; browser rendering and accessibility are unverified. No local-server or alternative browser route was used to work around the earlier browser denial.

## Concrete baseline comparison

The original conversation's Q1–Q4 illustration is assistant-authored source material, not observed learner data: [transcript lines 1268–1293](../../../../sources/fsrs_learning_conversation.md "Source line 1268").

| Exercise | Expected coverage | Stated total time |
|---|---|---:|
| Q1 | A, B | 120 seconds |
| Q2 | B, C, D | 180 seconds |
| Q3 | D, E | 120 seconds |
| Q4 | A, B, C, D | 240 seconds |

The real current planner allocates bundles in authored order: Q1, Q2, Q3, totaling 420 seconds. Its narrower assigned target lists do not shorten the actual exercises. The comparison finds Q3+Q4 at 360 seconds. It acts on Q3 first and recomputes after the response. The planned coverage alone creates no evidence. This establishes an improvement in the invented coverage arithmetic, not learning efficacy or measured time savings.

## Reused and new responsibilities

- Existing `createTrial`, `createBridge` and `NextSession` handle input binding, capability projections, hints, contract drift, clarification and per-target observations. Their files are unchanged.
- [selector.mjs](selector.mjs) chooses among complete authored exercise contracts, checks total cost, reserves diagnostic follow-up time, compares small subsets, charges answers once and reselects. It does not grade answers.
- [examples.mjs](examples.mjs) reuses the math, operations and fact capability definitions, adding focused tasks, sample responses and costs. It also restores the symbolic five-target coverage example.
- The supplied diagnostic hypotheses come from an existing unresolved assessment. Distinct correct/error/inconclusive branches can lead to checking, practice or explicit assessment review. They are not calibrated probabilities or proof of the underlying cause.

An immediate check after correction can finish this session while the existing planner still retains future checks. No clock is simulated and no delay is measured. Actual-duration fields are exercised with authored values, including one overrun; they are not wall-clock learner measurements.

## Verified awkward cases

The replays cover overlapping combinations; unshown parts after broad success; a new local error; ambiguity versus error; a question with identical teaching branches; insufficient time for diagnosis plus repair/check; the provisional diagnostic cap; recognition versus unaided recall; hints; version drift; equivalent contracts with reordered fields; duplicate answers and conflicting duration metadata; overruns; mismatched task bindings; fresh prompt requirements; and whole-task failures without target attribution.

The independent audit found the reordered-contract rejection and lost task-level concern. The final checks reproduce both seams and verify the corrections. It also confirmed the imported components and the supplied walkthrough paths. This is a behavior audit, not independent grading or real learner validation.

The subset enumeration is intentionally small and exact. A production curriculum would need a separate performance decision. Partial-budget priority follows repaired targets, then the authored goal order; that explicit experimental choice has not been approved as a universal learner preference. Broad model and review-omission questions remain open.
