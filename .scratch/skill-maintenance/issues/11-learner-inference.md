# What can the system infer from limited practice, and how should it express uncertainty?

Type: grilling
Label: wayfinder:grilling
Status: open
Mode: HITL
Assignee: unassigned
Parent: ../map.md
Blocked by: none for bounded investigation; the working representation contract is available

## Question

Define how direct observations support estimates about untested components, relationships, groups and assessment modes. Distinguish a known weakness from an uncertain estimate and distinguish predictive evidence from actual reinforcement. Compare a descriptive baseline and simple probabilistic alternatives, determine which graph relationships may inform each, and specify calibration probes and responses to contradictions. Keep inferred estimates separate from actual FSRS reviews. Decide how to avoid needing an independent test of every component without assuming automatic positive transfer.

## Comments

The user authorized continuing after the explicit-coverage prototype, and clarified that another approval of the already accepted diagnosis/practice sequence was unnecessary. Use the implemented capability/criterion contracts as a working boundary for this investigation. The broader representation and validation questions remain open; they do not prevent comparing inference assumptions now. Do not ask the user to reconfirm settled principles or treat an optional demo review as a blocking requirement.

User requirement: “when the learner failed a large exercise, we need to figure which exact episode of knowledge needs reinforcement.” Interpret this provisionally as locating specific components, connections, or steps. The design must distinguish competing causes with targeted follow-ups, handle multiple gaps and integration failures, and admit when evidence does not identify an exact cause. Define what evidence warrants a reinforcement choice and how a failed integrated recheck revises the diagnosis. This requirement is confirmed; the inference mechanism is not. See [the proposed diagnosis loop](../spec.md#diagnose-failure-before-choosing-reinforcement).

Transcript anchors: lines 705–808, 892–935, 1126–1158, 1375–1385, 1590–1598 and 1866–1868. Review the earlier BKT/PFA/GKT findings and the incompletely investigated KST/ALEKS and Math Academy leads as needed. The earlier research established boundaries, not the best general learner model. No specific probabilistic model or transfer coefficient is approved.

Context: [conversation coverage audit](../research/provenance.md#conversation-coverage-audit).

The [comprehensive retrieval](../research/conversation-retrieval.md) also restores diagnosis after successful composite attempts, distinctions among selection/execution/interpretation gaps, response-specific evidence, and learner differences in implicit versus explicit practice. Compare structural feasible-state diagnosis (KST) with component-wise estimates. The original Math Academy, ALEKS, and Knowledge Spaces leads remain incompletely investigated; source claims do not establish their efficacy or suitability here.

The [diagnosis prototype](13-diagnosis-prototype.md) supplies concrete states and transitions for ambiguous outcomes, multiple gaps, success with a local weakness, assisted practice, and a diagnosis revised after a larger check. It uses self-assessed or authored rubric evidence, not automated interpretation or a fitted learner model.

The [answer-to-practice draft](../diagnosis-design.md) specifies the preceding assessment step using actual answer text in constructed cases. Keep uncertainty about grading separate from uncertainty about knowledge. An omitted explanation is unobserved, and one error cannot establish whether knowledge was forgotten, never learned, or temporarily unavailable. The draft includes question branches that change practice, a provisional diagnosis limit, and source-checked assessment frameworks. It has not been validated with real learners or accepted as the final inference model.

The [chat-assisted assessment trial](../spikes/assessment-trial/README.md) supplies ten inspectable AI judgments and a separate human comparison path. Structural validation passed, but there are no independent human reference judgments yet; do not promote these examples into a measured inference model.

The [answer-intake continuation](../spikes/answer-intake/README.md) now connects input-bound assessments to the existing planner. It retains omitted and ambiguous criteria in the assessment without converting them into learner failures, and attaches assistance to specific targets. Ten recorded responses and seven assessor-authored contrasts exercise that boundary. The 34 replay and four CLI checks verify structural handling and policy behavior, not semantic validity. Independent assessment, indirect inference and calibration remain open; no confidence probabilities or graph-wide credit were introduced.

The subsequent [blinded annotation comparison](../spikes/independent-assessment/review.md) supplies historical human references for 36 comparable facet judgments: 23 matches, 10 disagreements and three abstentions. Six disagreements concern pragmatic inference; none by itself establishes a learner deficit. Source labels are not automatically correct, and the comparison has no independent human teaching-action labels. The real bridge also returns a clarification proposal alongside immediate help for `SE.27b.333.1`. Reconcile action precedence without rewriting the original observation, and keep unshown related knowledge distinct from credited knowledge. The assessment method and calibrated inference remain undecided.

The [clarification continuation](../spikes/answer-intake/clarification-notes.md) implements target-scoped action precedence in the existing planner. It keeps the original observation, holds off corrective help while its interpretation is unresolved, and lets later direct evidence resolve only the affected target. The recorded conflict and constructed continuations pass through the real components. This verifies the action policy, not whether the assessor chose a justified question or correctly interpreted the answer.

The bounded investigation is complete in [sparse-inference research](../research/sparse-inference.md), [the proposed inference contract and build plan](../inference-design.md), and [the numerical assumption probe](../spikes/inference/README.md). Fourteen checks verify matched marginal priors, hand-calculated updates, contradictory evidence, zero-likelihood handling, duplicate and revised judgments, assistance/omission exclusions, asymmetric error assumptions, and the actual shared-criterion seam. Fixed synthetic parameters establish no learner calibration or retention benefit. Independent exact-fraction calculations agreed with the initial numerical outputs and identified the need to add asymmetric error cases; those cases are now included.

Recommendation: preserve the descriptive ledger; add explicit, revisable hypotheses for next-action selection and compare finite-state forecasts beside it. A strict prerequisite chain can infer untested knowledge, but excluded states cannot recover through updating, and error assumptions can reverse the apparent diagnosis. Keep model assumptions and grading uncertainty inspectable. No numerical estimator was connected to the live planner, no review was deferred, and no FSRS history changed.

The general model and omission policy remain open pending prospective evidence, not another user approval of the accepted exercise sequence. Release this investigation claim. The next bounded work can compare exercise selection under a budget using the current representation and inference contracts; choosing real study-time and retention tradeoffs belongs to a concrete later trial.
