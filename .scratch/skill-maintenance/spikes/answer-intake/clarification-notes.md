# Clarification before corrective practice

Completed 2026-10-14 after the user's “go ahead.” This is a bounded change to the existing logic prototype. It addresses the concrete action conflict from [the independent annotation comparison](../independent-assessment/review.md); it does not settle the broader learner model or validate semantic judgments.

Open [the walkthrough](clarification.html). It starts with the archived thermometer answer and the assessment frozen before human annotations were revealed. Buttons supply clearly labelled invented continuations. No new learner exercise is requested, and nothing is sent to a learner.

## Behavior

The planner now derives pending clarification from the assessment records already in history. A targeted `clarify` or `follow_up` takes precedence over corrective help for those targets. The original error, quotations and assistance remain unchanged. Questions covering multiple targets stay together.

| Subsequent evidence | Immediate action |
|---|---|
| Clear correct observation | End clarification for that target; retain the earlier error in history |
| Clear error, with no new question proposed | Offer focused help for that error |
| Interpretation still unclear and questioning stops | Pause for assessment review; do not revive help from the earlier error |
| Only part of the question answered | Review the remaining target instead of repeating the whole question |
| No evidence for the target | Keep the question pending; omission does not settle it |
| Separate target has a clear error | Help remains available for that target |

A clarification does not itself clear a future check. A correct current response still leaves delayed recall untested. A later unhinted demonstration can clear its check under the existing policy; a hinted response keeps the helped target pending. A repeated old record cannot reopen a question that later evidence resolved.

This belongs in the existing `NextSession.plan` function so the bridge, CLI, standalone intake page and direct planning calls agree. The bridge and assessment protocol did not change. No state field, service, storage layer, automatic grader or general memory model was added. The returned `review` action means the assessment remains unresolved; it is not a learner failure label or an automatic request for another answer.

## Verification

Before editing the planner, six of 16 focused checks failed, including the archived conflict, unresolved and omitted replies, partial resolution, and errors elsewhere while clarification was pending. [The before report](clarification-before.json) records that run. After the change:

- [22 clarification checks](clarification-results.json) pass, including the six failures, preservation of evidence, target-scoped help, pending checks, duplicate delivery and actual walkthrough button handlers.
- [35 connected intake checks](report.json) pass. These preserve the accepted binary-search misread and one combined later Kubernetes exercise. The prior run had 34 checks; the extra check verifies that the page labels clarification correctly.
- [22 existing next-session checks](../next-session-replay-results.json) pass.
- [Five CLI and historical-report checks](clarification-cli-results.json) pass using temporary constructed records, including targeted clarification, clear-error help, retained evidence and stale-input rejection.

All five frozen assessment files still match their digests. The independently audited comparison and review remain byte-for-byte unchanged. Its comparison runner now refuses changed component dependencies rather than overwriting the audited report with revised planning behavior. Replay that historical comparison from commit `bef617c`; use this continuation for the new policy.

Reproduce from the repository root:

```sh
node .scratch/skill-maintenance/spikes/answer-intake/clarification-replay.mjs
node .scratch/skill-maintenance/spikes/answer-intake/replay.mjs
node .scratch/skill-maintenance/spikes/replay-next-session.mjs
node .scratch/skill-maintenance/spikes/answer-intake/verify-clarification-cli.mjs
```

The first two commands also regenerate their standalone HTML pages from the real functions. Button handlers ran against a minimal DOM surface, not a browser. Rendering and accessibility remain unverified; the earlier local-browser access denial was not bypassed.

## Limits and next design question

The caller and assessor still supply target identity, assistance, timing and whether a question would change practice. The program checks record integrity and executes that proposal; it cannot establish that the question is justified or that a new answer settles its meaning. The continuations are authored policy examples, not new student responses or another independent evaluation. Assessment revision, automatic question generation and general diagnostic-turn limits remain outside this change.

The remaining representation question is how to map answer-analysis details to meaningful learning targets: preserve important distinctions such as movement versus wearing away without turning each grammatical relationship into a separate memorization obligation. The earlier comparison identifies disputed examples to investigate, not a proven target taxonomy or a measured benefit from this action policy.
