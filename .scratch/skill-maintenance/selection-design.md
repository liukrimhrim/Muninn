# Choose the next useful exercise within the time available

Status: first-release selection finalized in [Design Baseline 1](design-baseline.md), 2026-10-16, with the everyday-learning and lifecycle extensions controlling daily ordering and saved state. The executable comparison is an authored probe; study-time savings and safe future review omissions remain unmeasured.

## Recommendation

For the proposed first-release daily behavior, use [session planning and bounded repair](everyday-learning-design.md#4-planning-a-session-within-real-time). It adds persistent concerns, explicit waiting-time priorities, multiple-curriculum scope, uncertain cost, absence/backlog behavior and learner overrides. The comparison below documents the original bounded experiment; its authored target order and transient limits are not silently promoted to the finished daily policy.

Keep the current evidence and diagnosis rules, then choose among eligible exercises using their full cost and overlapping coverage. Choose one next action, observe its answer, and recompute. A planned combination is a proposal, not proof that its targets were demonstrated or strengthened.

Use this order for the comparison: resolve supported ambiguity when a useful question fits; offer focused practice for an observed error; otherwise check pending targets. A blocked target does not prevent useful work on unrelated targets. A whole-task failure without an identified target remains an unresolved task-level concern and stops ordinary selection for clarification.

The observed baseline limitation is specific: the current planner groups targets in authored order without comparing cost. On the original conversation's illustrative Q1–Q4 example, it chooses Q1, Q2 and Q3 for seven stated minutes. Q3 and Q4 offer the same target coverage for six. This justifies comparing coverage combinations; it does not justify a claim about better learning or a large optimization service.

The [standalone demo](spikes/selection/index.html) starts with a proposed next action and offers optional sample-answer buttons. There is no learner assignment or review form. The [replay notes](spikes/selection/README.md) explain how to reproduce the result.

## Selection contract

Each candidate has a purpose, an actual versioned exercise and rubric, capability coverage, permitted conditions and a complete time estimate. The estimate includes setup, answering and feedback. A question proposed for diagnosis also states its supported concern and the teaching branches its possible answers would lead to. These branches are authored hypotheses; the selector does not infer them from prose.

The existing assessment bridge and planner remain responsible for observations, assistance, accepted misreads, clarification precedence and contract compatibility. The new comparison reads those results. It never assigns every prerequisite a pass, weakens a required recall mode, turns an omission into an error or sends an inferred rating to FSRS.

The session also retains which prompts were attempted, time charged once per answer, which checks were demonstrated without a new hint, and which targets received corrective practice. A duplicate delivery adds neither time nor evidence. A changed grade is not silently accepted under an old answer ID. An overrun is retained and reduces the remaining budget to zero when appropriate; it does not erase the answer.

## Decision rules being compared

1. **Enforce the evidence contract.** An exercise must match the target's action, mode and conditions. Recognition cannot satisfy an unaided-recall target because it is cheaper. Unresolved assessment review blocks only the affected targets, except that an unlocalized whole-task concern requires clarification first.
2. **Require a reason to diagnose.** A question needs a pending concern supported by the existing assessment and at least two distinct teaching branches. Do not manufacture a question merely because a hypothetical wrong answer could occur. Keep the existing provisional cap of three diagnostic prompts per session in this experiment; it is a configurable fixture limit, not a scientifically optimal number or a persisted cross-session limit.
3. **Protect time for the follow-up.** A diagnostic question must leave room for each declared substantive branch. A branch requiring corrective practice also reserves a fresh check of the repaired target. An inconclusive branch can pause explicitly. If the question does not fit, retain the concern and consider unrelated useful work; do not substitute an invented diagnosis.
4. **Compare combinations within one purpose.** If all currently eligible targets can fit, prefer the combination with the least total time. Compare whole exercises at their full cost; do not pretend Q2 becomes shorter because another exercise already covered one of its targets. Break equal costs by fewer exercises, then stable identifier order.
5. **Make partial coverage priorities explicit.** If full coverage cannot fit, prioritize a freshly repaired target for its immediate check, then the authored target order. Compare coverage in that order, then cost. This is an inspectable experimental tie-break, not a learned importance score or a user-approved general priority rule. No weighted sum combines learning, information and time.
6. **Replan after the answer.** Only observed unhinted evidence can satisfy a current check. Missing, ambiguous and assisted parts remain visible. Do not repeat the identical prompt in the same session to make a missing observation disappear. A newly observed error takes precedence over the remaining broad checks.
7. **Stop honestly.** Keep unmet needs when there is no suitable affordable action. Distinguish completing the current session from validating retention. A check after corrective practice in this session is immediate evidence; the underlying later-check obligation remains. A fictional “later” phase in the demo is not evidence that real time passed.

For this tiny catalog, enumerating candidate subsets is enough to compare combinations. It is deliberately bounded to the supplied examples and has no performance claim for a large curriculum. There is no solver dependency, learning-gain score or learned cost estimator.

## What the executed examples show

| Situation | Selected path | Illustrative time and remaining obligation |
|---|---|---|
| Five pending targets and overlapping exercises | Q3, then Q4 after observing its answer | 360 seconds; all five targets shown in the authored later responses |
| Ambiguous command, then a wrong clarification | Clarify → practice the command → new combined incident | 105 seconds of a 120-second budget; immediate check completes, future retention checks remain |
| Same ambiguity with only 40 seconds | Skip unaffordable diagnosis; check eligible evidence choice | 35 seconds; command concern and functional-verification check remain pending |
| Known mathematical parts, wrong connection | Practice the connection → new integrated comparison | 100 seconds; keep the later retention check after immediate success |
| Larger answer omits the connection | Combined exercise → focused connection check | 110 seconds; do not repeat questions about already shown parts |
| One taught association | One unaided recall | 10 seconds; cheaper recognition is ineligible |

The correct clarification takes a different route from the wrong clarification: it proceeds to a combined check without command remediation. An inconclusive clarification retains assessment review instead of inventing a command deficit. A hinted correct answer does not satisfy an independent check. These contrasts run through the same validator, bridge and planner as the earlier prototype.

Thirty-one replay checks and three checks of the actual page handlers passed. The handler checks use a minimal DOM surface and do not establish browser layout or accessibility. An independent audit exposed two interoperability bugs before completion: object-property order could falsely reject a compatible contract, and a targetless whole-task concern could be lost from completion status. Both are fixed and covered by reproductions. The original evidence artifacts, accepted plan and frozen historical annotation comparison are unchanged.

## What this does and does not settle

This supplies a concrete selection policy for the current design. It preserves the user's general learning scope, the larger-exercise diagnosis sequence, the accepted misread distinction, focused repair and combined practice. It also restores the original conversation's overlap example without presenting its invented costs or reinforcement assumptions as results.

The experiment handles qualitative diagnosis hypotheses supplied by assessment. It does not select questions from a fitted knowledge-state model, estimate uncertainty reduction, calibrate transfer or suppress future reviews based on an inferred probability. The [inference contract](inference-design.md) remains the boundary for that later work. Several criteria from one response remain shared evidence; choosing an exercise combination does not change their dependence.

Real use still needs measured total costs, trustworthy content and assessment, explicit goal priorities, realistic candidate exercise availability and delayed outcomes. Declared diagnostic branches need checking against actual responses; reserving time for them cannot guarantee the learner will follow an anticipated path. A richer selector should earn its complexity against a named failure of this comparison policy.

## Next build and validation steps

1. **Specify the material-to-practice workflow.** The loop now has working proposals for representation, inference and selection. The remaining product gap is how a learner brings in material, checks or corrects proposed knowledge and exercises, and returns to practice. Compare manual, assisted and curated input using contrasting subjects; do not assume Kubernetes, one file format or a fully automatic grader.
2. **Connect one complete local example.** After that workflow is specified, reuse the actual content contracts, assessment bridge and selection behavior. Keep the observation record reviewable and avoid adding infrastructure merely to host the experiment.
3. **Measure before promoting policy.** Record proposed versus actual time, assessment disagreements, diagnostic prompts, help and retained performance separately. Use prospective checks for inference and a separate delayed comparison for review omissions, following the [evaluation contract question](issues/06-evaluation-contract.md). No study-time or retention tradeoff has been chosen for the user.

No learner homework or repeat approval of the accepted exercise sequence is needed to continue the design. The broad policy ticket remains open for empirical validation and later choices; the bounded selection comparison is complete.
