# Second design pass: decisions between the contracts

Audit date: 2026-10-15. Baseline: research snapshot `8b744fb`, checked against the user-visible working files before this pass. Scope: the general memorization web app's proposed first release, including the everyday-learning continuation. These findings concern documents, not confirmed defects in a running product. No production application, learner experiment or browser run was performed.

The audit found **seven concrete gaps**, listed below in workflow order as the original findings, not ranked live incidents. **Patch status, 2026-10-15:** the user subsequently requested “patch those gaps.” All seven now have concrete proposed resolutions in the [lifecycle contract](learning-lifecycle-contract.md), [tracking contract](../learning-observability/tracking-contract.md) and [case-by-case closure](cross-contract-closure.md). The “still to design” descriptions below record the audit-time omissions; they are not the current backlog. The patch completes those specifications without claiming runtime behavior or measured policy quality.

## How the pass was performed

Read the main build plan, material workflow, everyday-learning design, relevant representation/inference/selection sections, compatibility lifecycle/records, observability metric/cohort/query contracts and deletion scope. Check the original retrieval ledger for requirements that a small release might erase. For each candidate finding, look for the existing rule before calling it missing; distinguish a broad principle from a defined state transition. Trace a normal path, an interrupted path and a correction/late-arrival path where applicable.

The most consequential boundary is not the choice of a storage technology. It is whether one response, exposure or content revision has the same meaning to the authoring flow, scheduler and dashboard.

## A01. A correct first attempt has no capability-schedule transition

**What already exists.** [Material intake](material-workflow.md#the-learners-path) permits familiar learners to begin with a larger task. The [capability schedule table](first-build-plan.md#evidence-diagnosis-and-reviews) defines initial study, immediate post-help verification, due success, failure, missing evidence and corrections.

**Counterexample.** A new target has no due timestamp. The learner explains it correctly without help on the first exercise. No study was completed, no old due review exists, and this is not post-help verification. The baseline table has no applicable success transition. An implementer could leave the target pending forever, schedule nothing, or invent an interval.

**Draft clarification added.** Retain the independent first demonstration and schedule the first later capability check 24 hours after the actual answer under the proposed simple policy. Do not force a lesson or another immediate quiz. Initial supported error creates a repair need; initial missing/ambiguous evidence retains an initial/clarification need. A mixed larger task applies these transitions only to requirements/targets its evidence supports. Direct recall continues to use its actual eligible rated FSRS review.

The 24-hour choice is a provisional baseline consistent with this design's first later check, not a research-derived estimate of prior mastery. It remains a policy proposal. Unknown occurrence time must not be replaced by grading time; the subsequent lifecycle patch supplies A05's prospective recovery rule.

**Acceptance cases.**

- CCA01: An initial unhinted explanation succeeds at 10:00; assessment arrives at 10:20. Proposed first later due time is next day 10:00, with no invented study episode.
- CCA02: One larger initial answer demonstrates A, omits B and contradicts C. A receives its later check; B remains unobserved; C gets a supported concern. The whole answer does not get one blanket schedule transition.

## A02. Material selection and admission to ongoing practice need an explicit boundary

**What already exists.** The [material workflow](material-workflow.md) separates source capture, an editable outline, selected capabilities and exercises. [Enrollment and schedule records](compatibility-design.md#3-portable-logical-records) retain selected goals and an `initial` need. [Daily selection](everyday-learning-design.md#4-planning-a-session-within-real-time) distinguishes pending work from new material, permits overrides and handles whole-curriculum pause/archive.

**Counterexample.** The learner imports a long document and keeps 200 targets in the outline, but starts only three today. Are the other 197 merely available material, selected long-term goals, or already active obligations? The documents preserve all three concepts in prose without defining their transition and count rules. Treating all as overdue creates work the learner never started; hiding them from the goal denominator makes three studied targets appear to complete the curriculum.

**Recommended direction.** Define a small lifecycle: available material → selected goal → admitted practice → ongoing maintenance, with pause/removal treated separately. Import alone must not create dated obligations. Selected-but-unstarted targets remain visible in goal coverage without masquerading as overdue reviews. Choosing a session's new work admits only those targets. Shared exact targets reuse existing learning/schedules when another curriculum selects them. Prior learning can be demonstrated directly; a self-report of familiarity guides the starting task but is not evidence of mastery.

Specify the ordinary completion language at the same boundary: “session finished,” “selected targets demonstrated at least once,” and “later checks satisfied as of [date]” have different meanings. None permanently graduates a target from maintenance. Existing checkpoint storage is sufficient to preserve a rule after it is chosen; it does not itself define that rule.

**Missing at audit time; now specified in the [closure](cross-contract-closure.md).** Exact state ownership, activation/pausing controls, meaning of “start this curriculum,” treatment of an already-open combined task when some goals are paused, and goal-versus-active-work denominators. Do not add a configurable curriculum-management framework to answer these questions.

**Acceptance cases.**

- CCA03: Import 200 selected targets, begin three, stop. The remaining 197 are visible as unstarted goals, not 197 missed reviews or zero mastery.
- CCA04: Start a second curriculum containing two already active targets. It adds no duplicate schedules, initial tests or time credit; stopping the first curriculum does not stop shared work still selected by the second.

## A03. Targeted teaching and new exercise variants lack a complete generation contract

**What already exists.** The [build plan](first-build-plan.md#the-result-to-build) promises targeted explanations and fresh integrated checks. Its semantic boundary names only `draft_material` and `assess_answer`; the [operation record](compatibility-design.md#3-portable-logical-records) has the same two purposes. The [everyday exercise gate](everyday-learning-design.md#authoring-and-acceptance-gate) defines candidate quality and bounded regeneration. `study.content` preserves teaching after delivery.

**Counterexample.** An actual learner exposes a connection error not covered by the initial examples. The next step needs a useful explanation and a new task. An implementer must decide whether assessment invents teaching, material drafting runs again, or an undocumented model call generates it. There is no complete binding for the new explanation's sources, acceptance, delivery and relationship to the later check. Saving free-form teaching afterward does not establish that the content was checked before it was shown.

**Recommended direction.** Keep one application and reuse the authoring boundary. Give material drafting explicit intents for initial outline, exercise variant and teaching intervention. Each request binds current target/source revisions, supported concern, prior teaching/exposures and the specific learner action to elicit. Assessment returns observations and proposed next-action rationale; it must not silently deliver unchecked new teaching as a grading side effect.

Before delivery, check teaching against the same source/scope constraints as the target and record its provenance. A correct worked example must preserve the conditions needed for the explanation. Save the accepted teaching definition before its presentation, and connect actual study completion and verification to it. If the target/source is held or the model is unavailable, reuse suitable accepted content or leave a visible authoring need; do not improvise unsupported material simply to keep the loop moving.

**Missing at audit time; now specified in the [closure](cross-contract-closure.md).** Exact intent inputs/outputs, proposed-versus-accepted statuses, invalid/stale-output handling for teaching, and the bounded path from an assessment suggestion to a delivered intervention. This can extend existing records; it does not call for another model service.

**Acceptance cases.**

- CCA05: A fresh learner error requires a new explanation. The delivered content has checked source/target bindings and later verification refers to the actual completed teaching, not a hypothetical plan.
- CCA06: The source changes while generation is pending. The late explanation cannot be delivered under the new claim without review; the learner's earlier answer and unrelated work remain available.

## A04. Two real attempts can race to update the same schedule

**What already exists.** [Compatibility](compatibility-design.md#8-browser-continuity-and-unfinished-work) specifies idempotent retries, abandoned request handling, exact input revisions and preserved drafts. Accepted assessment/correction updates are atomic. [Everyday continuity](everyday-learning-design.md#7-record-changes-needed-for-this-behavior) reserves diagnostic allowance across tabs. The scheduler-upgrade section defines replay ordering for an explicit engine transition.

**Counterexample.** Two tabs start distinct attempts against the same due target. Both have different valid request IDs; neither is a duplicate. The learner answers A first and B later. B's error is assessed before A's success. Atomic commits alone do not say whether the later-arriving old success can erase the more recent repair need, or whether both requests advance the same due obligation. Checking each operation's own input revision does not detect this cross-attempt conflict.

**Recommended direction.** Bind a scheduled attempt to the exact review obligation and schedule revision it was offered to satisfy. Give ordinary due offers one explicit owner/reservation or an equivalent conflict rule using the existing store. Preserve genuine second answers as evidence; do not discard them to simplify concurrency. Define which can satisfy the obligation, how abandoned reservations release, and how extra attempts are classified. Never let model completion order stand in for learner occurrence order.

Late accepted assessments require a deterministic recomputation of affected current schedule/concern state from effective bound events. Preserve the decisions originally made and their revisions. Known event order, exact ties and genuinely uncertain order need distinct rules; uncertain history cannot be made certain by sorting model responses. Apply the same rules during correction replay and restore.

**Missing at audit time; now specified in the [closure](cross-contract-closure.md).** Ordinary attempt reservation, event-order policy, rebasing a delayed result, conservative handling of ambiguous timing, and the boundary between stored response evidence and a schedule-advancing review. Existing retry/timer machinery helps but does not settle those semantics.

**Acceptance cases.**

- CCA07: A then B are actually answered, with success then error; model results arrive B then A. Current state must agree with the defined event-order policy and preserve the later error, rather than depend on API latency.
- CCA08: Two distinct requests target one due obligation. Both raw answers survive, but the obligation cannot be advanced twice merely because both were offered from the same old state.

## A05. Exposure eligibility needs a submission boundary and a recovery route for unknown time

**What already exists.** [Exposure policy](everyday-learning-design.md#exposure-no-help-answers-and-delay) preserves correctness, distinguishes in-task help and delayed qualification, and applies a proposed 24-hour next-offer deferral across sessions. [The data contract](../learning-observability/data-contract.md#5-exposure-corrections-and-the-unit-behind-a-flag) handles bounded/unknown timing and explicitly distinguishes presentation from completed study.

**Counterexample 1.** The learner answers unaided at 10:00, sees ordinary feedback at 10:01, and submits their recall rating or receives model grading at 10:02. Testing eligibility against the latest exposure at 10:02 can wrongly disqualify the answer that came before the feedback. An answer-bearing dialog left open across the check has the opposite problem: its opening timestamp alone does not prove that help was unavailable during the answer.

**Narrow clarification added.** Assess assistance/exposure relative to the bound answer's actual production/submission interval, not the later grading/rating arrival time. Feedback after submission remains relevant to future learning but cannot retroactively become help on that response. A view that remains accessible during the attempt must be closed or treated as available help according to the target's conditions. A genuinely late report of exposure that happened before the response can revise its qualification with provenance; a newly computed report preserves the old saved report.

**Counterexample 2.** An imported or self-reported exposure has unknown time. The current conservative policy withholds delay certification, but does not define how the target ever exits that state. Repeated ordinary practice is available; a permanent inability to schedule a qualifying check is not a defined recovery policy.

**Recommended direction.** Separate uncertainty about an old observation from eligibility for future checks. Where supported, use a trustworthy time at which exposure was known to have ended as a conservative upper bound, while preserving the original uncertain event time. If exposure may be ongoing or no such bound exists, record that limitation and start a clearly prospective observation plan once conditions become known. Do not turn import time into the supposed historical exposure time or certify an unobserved exposure-free past.

**Missing at audit time; now specified in the [closure](cross-contract-closure.md).** The exact uncertainty-to-future-eligibility transition and its record representation, bounded/ongoing display behavior, and how non-recorded outside learning limits the claim. A blanket expiry or perpetual hold must not emerge accidentally.

**Acceptance cases.**

- CCA09: Post-submission feedback precedes grading/rating. The original response is not reclassified as hinted; feedback still counts as a later exposure.
- CCA10: A solution drawer remains open while a response is produced. The app cannot certify that task-specific help was unavailable solely because the reveal occurred yesterday.
- CCA11: Unknown historical exposure is retained, then trustworthy prospective conditions are established. New eligible checking can eventually resume without fabricating historical timestamps or rewriting old report qualification.

## A06. The dashboard needs a workflow that creates its planned comparisons

**What already exists.** [C's population rule](../learning-observability/c-dashboard-contract.md#2-population-and-observation-rules) and the [cohort contract](../learning-observability/data-contract.md#6-frozen-endpoints-and-deterministic-queries) freeze targets, baseline, anchor, windows and assignment before results. The observability design permits ordinary reviews to supply endpoints and prohibits unapproved additional testing burden. The prototype uses authored dates and responses.

**Counterexample.** The learner simply imports material and practices over two weeks, without setting up a study. Who creates the fixed target group and its check windows? Which existing response is the baseline? What happens when a planned check becomes ineligible after help, or when curriculum membership changes? If the app waits until the learner opens the chart and chooses favorable past endpoints, it violates the prospective rules. If nothing creates cohorts, the main comparison view can remain empty indefinitely despite useful learning history.

**Recommended direction.** Define two explicit products within the same dashboard: ordinary dated practice history that makes observational claims, and a fixed comparison plan that is recorded prospectively. The latter needs a simple creation rule/UI, defaults for baseline and windows, preview of included targets and existing review work, assignment before the answer, and a visible plan-change/retirement policy. Reuse scheduled practice where possible; tracking must not silently add an assessment program. Lack of a valid comparison plan should still allow useful dated evidence and effort history.

**Missing at audit time; now specified in the [closure](cross-contract-closure.md).** How an ordinary learner initiates tracking or receives an automatic proposed plan; exact window defaults/closure; baseline with missing or helped evidence; changing eligibility; cancellation and curriculum changes; and whether the first release supports both modes or explicitly narrows its claims. The formula for a cohort is already specified; the missing part is how a legitimate cohort comes into existence and stays meaningful.

**Acceptance cases.**

- CCA12: A learner never configures an experiment. Ordinary history remains useful; any fixed comparison shown can identify the plan that existed before its endpoints.
- CCA13: A target is added or a check is exposed/missed after the plan is frozen. Preserve its original population and reason; no retrospective substitute, favorable cohort trimming or hidden extra assessment.

## A07. Raw answer status and claim-qualified metric status are not fully reconciled

**What already exists.** [C's status table](../learning-observability/c-dashboard-contract.md#2-population-and-observation-rules) defines S/E/H/U/M/N, with U meaning a submitted answer without a usable judgment. Its formulas use `P=S+E+H+U+M`. [Query steps 5–6](../learning-observability/data-contract.md#6-frozen-endpoints-and-deterministic-queries) classify observed outcomes, then separately test delay/exposure/mode/comparability, retaining ineligible endpoints in the planned denominator. They correctly say not to inherit the descriptive success count, but do not provide the complete mapping into each qualified aggregate.

**Counterexample.** Of eight matured planned checks, five are judged correct without in-task help, two incorrect and one missing. One of the five correct checks fails the stated delay/exposure condition. Raw history is 5S+2E+1M. A retained-performance numerator cannot still be five. Moving that answer into U without changing U's definition incorrectly calls a valid grading result ungraded. Removing it from P would hide the planned endpoint. The assessment-coverage formula also becomes misleading if U mixes ungraded and fully graded but ineligible responses without separate counts.

**Recommended direction.** Keep observed outcome and claim qualification as separate axes all the way through aggregation and display. Define a versioned mapping for each claim: qualifying success/error, helped evidence, unavailable assessment, missing submission, and otherwise judged but ineligible/uncertain. Retain exact reason counts and the full planned denominator. Assessment coverage must continue to measure grading coverage, not exposure compliance. Do not reuse a single generic “success” count for all charts.

**Missing at audit time; now specified in the [closure](cross-contract-closure.md).** Whether the displayed partition adds an explicit ineligible/uncertain group or uses separately named per-claim status counts; the precedence of multiple exclusion reasons; qualified success/transition formulas; sensitivity calculations; and labels understandable to the learner. The existing simple missing-only range is invalid when some judged outcomes are unusable for the claim unless its assumptions are re-established. This is a metric-definition decision, not a new learner failure state.

**Acceptance cases.**

- CCA14: Raw outcomes are 5S+2E+1M; one S violates the delay condition. Raw independent correctness remains 5/7, claim-qualified successes are four of eight planned endpoints, and the excluded success is visible with its reason. No invented failure or ungraded answer.
- CCA15: One otherwise graded answer is both helped and outside the window. The predeclared qualification precedence produces one endpoint in the main partition and both reasons in drilldown; no double counting or denominator shrinkage.

## Things checked that are not newly missing design

| Area | Existing treatment and audit disposition |
|---|---|
| General scope, relations and precise diagnosis | Already explicit; do not redesign this as a Kubernetes course or a fact-card-only system |
| Misread versus gap, alternate valid responses, whole-task attribution | Already specified; remaining risk is semantic implementation quality, not absence of the distinction |
| Three diagnostic prompts, repair-cycle binding, hinted/unjudgeable exits | Detailed in the latest proposal, including crash/restore and changed concerns; limits remain provisional rather than scientifically optimal |
| Stable identity, source corrections, split/merge compatibility | Detailed preservation/mapping rules exist; a general split/merge editor is explicitly outside the initial release |
| Full effort, timer ownership, interruption and saved reports | Detailed records and cases exist; real collection/browser qualification remains necessary |
| Archive and permanent deletion | First-release scope is accepted; selective erasure is deliberately deferred, not forgotten |
| Numerical mastery, inferred review omission, causal efficiency claims | Explicit later evaluation gates exist; adding a fitted model is not a repair for the gaps above |
| Deployment/provider/browser matrix | Known choices before setup/release. They are not newly discovered design defects, and this audit does not authorize external data transmission |
| Large files, rich formats and exact library versions | Initial intake is short plain text; numerical provider limits and runtime versions belong to implementation planning. No hidden promise of PDF/diagram/execution support |

## Disposition and finite follow-up

The audit and the subsequently requested seven-gap design patch are complete within their scopes. A01–A05 are integrated through the lifecycle contract; A06–A07 through the tracking contract. The main plans, compatibility/measurement records and C calculation rules now link the same canonical behavior. The [closure record](cross-contract-closure.md) traces all fifteen cases plus boundary checks. The original human-dependent policy tickets remain distinct from completion of this patch; they do not leave these seven omissions unspecified.

The fifteen cases have now been traced through one consistent set of proposed records/rules and the main plan/addenda reconciled. Implementation tests must next prove the stored transitions and real browser/model seams; actual delayed evidence must establish any learning benefit. Neither further prose nor authored arithmetic substitutes for those later stages. No new infrastructure, dashboard variant or broad research campaign is required by this audit.
