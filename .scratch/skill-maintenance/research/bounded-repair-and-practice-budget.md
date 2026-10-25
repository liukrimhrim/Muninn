# Bounded repair and useful practice under a time budget

Research note, 2026-10-15. Supports [What supports bounded repair and useful practice when time and evidence are limited?](../issues/16-repair-budget-evidence.md). Planning evidence only; no production implementation, learner experiment or policy optimization was performed. Six primary studies were checked. This is a focused review, not a systematic review or proof of universal effects.

## Conclusion

The evidence supports retrieval, corrective feedback, worked examples and delayed checks as useful options. It does **not** establish an optimal number of diagnostic questions, unsuccessful repairs, new items per session or overdue reviews. Those numbers must be explicit operational starting choices, evaluated against actual learner time and later performance.

The design should distinguish two questions: **what does this response justify believing?** and **what useful action fits now?** A failure can justify help without proving a precise cognitive cause. A question can collect evidence while also teaching. A successful response immediately after help does not establish durable independent performance. Stopping an unproductive sequence should preserve its evidence and unresolved work, rather than manufacture success or a permanent weakness label.

## What the existing design already settles

[Diagnosis](../diagnosis-design.md), [selection](../selection-design.md) and the [first-build plan](../first-build-plan.md) already distinguish observed error, missing evidence, accepted misread, ambiguity and assistance. Selection reserves follow-up time, charges full exercise cost and preserves unfinished targets. The [earlier evidence review](learning-evidence.md) already cautions against treating graph coverage as demonstrated benefit.

There is a concrete inconsistency to resolve: diagnosis §7 permits three follow-ups **per larger attempt**; selection and the build plan use three **per session**. Selection explicitly says its cap is a fixture policy without persisted cross-session semantics. Neither wording determines what happens when the learner reopens the app or another task exposes the same concern. The research below cannot choose between them. The product design must specify the counting scope, interruption/resume behavior and repeated-repair response together.

## What the primary evidence supports—and its boundaries

**1. Unsuccessful retrieval followed by the answer can help.** Kornell, Hays and Bjork studied fictional trivia and weakly associated word pairs. In Experiments 3–6, attempted retrieval followed by the answer improved later word-pair recall over equal-time study; one experiment used an average delay of 38 hours. The fictional-trivia comparison did not establish superiority over total-time-matched reading; a nonsignificant difference does not prove equivalence. This supports offering a meaningful attempt before feedback, without requiring error-free practice. It does not support repeated unsupported guessing, unlimited diagnostic questioning, or assuming every failed complex exercise improves learning. [Kornell et al., 2009, methods and General Discussion, pp. 989–998](https://web.williams.edu/Psychology/Faculty/Kornell/Publications/Kornell.Hays.Bjork.2009.pdf).

**2. Testing changes the learner as well as measuring them.** Students studied prose and either restudied it or took free-recall tests without feedback. Restudy performed better on an immediate test; prior testing produced better delayed retention, including a week later. Consequently, a diagnostic retrieval is an exposure in the learning history, even when no answer is supplied. Immediate fluency and later retention can favor different activities. The experiment does not identify which component caused an individual's error or establish transfer from prose recall to operational execution. [Roediger and Karpicke, 2006, Experiments 1–2 and General Discussion, pp. 249–255](https://learninglab.psych.purdue.edu/downloads/2006/2006_Roediger_Karpicke_PsychSci.pdf).

**3. Worked examples are a substantive alternative to more problem solving.** Sweller and Cooper's algebra experiments compared conventional solving with example-based acquisition. In Experiment 5, equal acquisition time allowed the example group to encounter more material, followed by better speed and fewer errors on similar test problems. Differences on dissimilar problems were not significant. This supports trying a worked step when continued search is unproductive, then checking the intended application. It does not show that examples always outperform retrieval, that identical help should be repeated indefinitely, or that gains automatically transfer to different problems. [Sweller and Cooper, 1985, Experiment 5 and General Discussion, pp. 84–88](https://onderwijs.felienne.nl/vakdidactiek/materiaal/sweller_worked_examples.pdf).

**4. Correctness and confidence convey different information.** Butler, Karpicke and Roediger tested general-knowledge multiple-choice responses, feedback and subsequent cued recall. Feedback helped preserve low-confidence correct answers as well as correct errors; Experiment 2 included a two-day delay. A learner's uncertainty therefore need not imply an incorrect answer, and useful feedback need not be restricted to errors. This is a reason to preserve confidence separately, not to turn it into a mastery grade. The study does not validate LLM confidence, diagnose why a particular answer was hesitant, or require a confidence survey after every task. [Butler et al., 2008, Experiments 1–2, pp. 918–928](https://learninglab.psych.purdue.edu/downloads/2008/2008_Butler_Karpicke_Roediger_JEPLMC.pdf).

**5. Useful spacing depends on the retention horizon.** Cepeda and colleagues varied the gap before review and the delay to a final fact test. Performance first improved and then declined as the gap increased; the best gap changed with the final delay. This supports explicitly recording the intended horizon and actual elapsed time. It supplies no universal “review tomorrow, then next week” optimum and does not equate overdue status with forgotten knowledge. This review checked the author abstract in the institutional record, not the full experimental tables. [Cepeda et al., 2008, institutional abstract](https://digitalcommons.usf.edu/psy_facpub/1766/).

**6. Introducing more material can reduce useful progress under limited review capacity.** Reddy and colleagues varied new-item arrival in 15-minute vocabulary/gesture sessions. Higher arrival eventually reduced their throughput measure and accumulated low-deck items. Their post-hoc “mastery” measure was finishing at Leitner deck six or higher, based on self-assessed practice responses; it was not an independent delayed assessment. This motivates making new intake compete visibly with existing commitments. It does not provide our admission threshold, prove durable retention savings, or justify copying their scheduler or creating a queue service. [Reddy et al., 2016, §4.1–4.2 and §5](https://www.cs.cornell.edu/~tj/publications/reddy_etal_16c.pdf).

## Design implications to carry into the policy work

The following are proposals constrained by that evidence and this project's requirements, not findings that the studies directly tested.

### Route the concern before counting another failure

Use response evidence and the applicable criterion to choose among distinct routes:

- **Supported slip or misread:** preserve the original answer and the correction. If its reasoning already meets the learning target, briefly resolve the mismatch and continue. Do not create topical remediation solely to confirm the learner's report. An explicit contradictory rule still needs attention even when called a slip.
- **Possible content or grading fault:** hold the disputed interpretation for review. An invalid question, missing acceptable alternative or unsupported source claim cannot become a learner deficit merely because the assessor repeats its judgment. Unrelated compatible work can continue.
- **Supported gap:** choose help for the smallest meaningful target the evidence identifies. Preserve correctly demonstrated components. A relationship error can justify relation-focused help without reteaching every connected fact.
- **Unresolved cause:** ask only if plausible answers would change the useful next action. Otherwise offer help explicitly under uncertainty, continue elsewhere or stop. Abstention is a valid result.
- **Assisted performance:** record exactly what was supplied and which targets it could help. Success demonstrates performance under those conditions; it does not erase the earlier error or satisfy an unaided criterion by relabeling it.

These categories describe the current evidence, not fixed kinds of learner. Multiple concerns can coexist in one answer. Repeated failures are meaningful only after checking target compatibility, assistance, grading validity and duplicate records; a raw count is insufficient.

### Separate diagnosis from teaching in purpose, not in claimed cognitive purity

A diagnostic prompt must name the unresolved decision and its possible action branches. A teaching prompt must name what it supplies. Both retain their wording, time and exposure. A follow-up that reveals a missing relationship may reduce uncertainty, but it has also cued that relationship. A later successful response therefore cannot retroactively prove that the original independent task would have succeeded.

Stop diagnosis once further distinction would not change the action. Knowing “forgotten versus never learned” is unnecessary when either currently leads to the same helpful explanation. After help, use a task that checks the repaired demand without supplying its answer. If an integrated task does this clearly, a separate focused quiz is unnecessary. Retain a genuinely later obligation; do not relabel the immediate check as retention.

### Bound a repair episode and make resumption explicit

Preserve the triggering concern, relevant target version, attempted explanations, assistance, checks, accumulated cost and stopping reason. Reopening the app should not erase this context and restart the same unsuccessful sequence. This can use the planned session and attempt records; it is not a request for another service.

When the configured stopping condition is reached, change the decision: inspect the assessment/content, try a materially different explanation or prerequisite-focused task when justified, or leave the concern pending. Merely paraphrasing the same explanation is not evidence of a new strategy. Do not automatically split the knowledge unit because one learner struggled; a content-boundary change needs its own rationale and compatibility handling.

The learner can stop at any point. Show what was established, what remains uncertain and the proposed resumption action. A pause is not a failure or an accepted diagnosis. The exact repeat threshold and the point at which to propose review remain policy decisions below.

### Budget the whole next action, including its likely consequences

Before asking a diagnostic question, include answering and interpretation plus the declared follow-up help/check branches in its estimate. If the complete action cannot fit, do not spend the remaining time diagnosing a concern the system cannot usefully address. Offer a smaller eligible action, support without a completion claim, or a pause. Estimates are uncertain: retain overruns, stop offering additional mandatory work when time is exhausted, and preserve an interrupted answer.

Across sessions, show overdue work as pending opportunities with dates and reasons, not a debt the learner must clear before any useful new learning. Make new admissions explicit rather than converting every imported unit into an immediate obligation. Preserve the learner's goal priorities and show which goals are repeatedly deferred. This research does not choose a review/new-material quota or guarantee that either strict due-first or weak-first scheduling avoids starvation.

## Tricky acceptance scenarios for the design and later implementation

These are proposed cases, not executed tests. Concrete caps and priorities must be supplied by the policy under test.

| Case | Required observable behavior |
|---|---|
| **R1: Sound reasoning, wrong requested comparison.** The learner explains binary search correctly but supplies the absolute count rather than the difference, then corrects it. | Preserve the original and correction; recognize the supported reading mismatch; avoid logarithm remediation and a new failure streak. Do not invent direct evidence for an explanation never supplied. |
| **R2: The grader rejects a valid alternative.** The learner challenges a response marked wrong; source and rubric review support their answer. | Revise the effective assessment under the same attempt. Remove unsupported repair obligations and derived failure counts, retain the audit trail and spent time. No new review credit is manufactured. |
| **R3: Diagnosis gives away the connection.** A follow-up supplies the missing equation, and the learner completes the calculation. | Record supplied content and scoped success; do not treat it as an unaided demonstration of discovering the connection. A later independent check remains eligible. |
| **R4: Repeated supported errors survive different help.** Comparable checks keep exposing the same relation error and the configured repair bound is reached. | Stop the automatic loop with prior approaches visible. Offer a changed strategy, content/assessment review or pause; reopening does not silently reset the bound. Correct facts remain credited within their original scope. |
| **R5: Forty seconds remain; useful diagnosis plus repair needs longer.** Alternatively an accepted estimate overruns. | Decline the unaffordable diagnostic chain, preserve the concern and offer eligible shorter work or stopping. An overrun is recorded honestly; submission is saved and unfinished checks remain pending. |
| **R6: Return after a long absence.** Many targets are overdue while the learner wants one new topic in ten minutes. | Explain the proposed limited plan and remaining work. Do not declare every overdue target forgotten, erase old accomplishments, or promise to clear the backlog. Show what new learning adds to future commitments. |
| **R7: Focused success, integrated failure on a different condition.** The repaired relation is demonstrated, but the larger task exposes an applicability error. | Retain the relation evidence, identify the newly supported concern and replan within remaining time. Do not restart the entire topic or clear the later check solely because one component passed. |
| **R8: Retry, restore and correction affect stopping history.** A response is delivered twice, then an earlier failure is corrected. | Count one attempt and one time charge. Recompute evidence-based failure counts while preserving actual interventions and effort. Restore retains unfinished concerns; it does not generate new exposures or reset the unsuccessful-strategy history. |

## Decisions the literature cannot settle

The subsequent design must choose: the scope of a diagnostic cap; whether clarification and learner-requested help count toward it; the cross-session repair stopping rule; resumption after changed content or corrected grading; initial time estimates when no history exists; treatment of unknown costs; priority among due checks, repairs and new goals; limits on repeated deferral; and how the learner overrides a proposal without changing evidence.

No reviewed source establishes the right universal values. The existing three-prompt, 24-hour and seven-day choices can be retained or revised as versioned starting policies, with their rationale and expected failure cases stated. They must not be advertised as research-derived optima.

For later evaluation, retain separate counts and costs for clarification, teaching, practice, immediate checks, actual delayed checks, assessment corrections and abandoned sequences. Examine repeated unsuccessful approaches and deferred targets alongside delayed performance and the learner's experience. More prompts, a clean backlog or faster answers alone cannot demonstrate efficiency. A claim that a policy saves effort without harming retained capability still needs a prospective comparison with a defined outcome and full cost scope.
