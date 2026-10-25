# How should the system choose exercise purpose, format, and coverage under a time budget?

Type: grilling
Label: wayfinder:grilling
Status: open
Mode: HITL
Assignee: unassigned
Parent: ../map.md
Blocked by: none for bounded selection comparison; real review omissions still depend on the evaluation contract

## Question

Decide how the system selects an adaptive sequence across the learner's graph. Account for goal-relevant prerequisite gaps, observed weaknesses, uncertainty, overlapping exercise coverage, learning versus diagnostic purpose, feedback cost and format changes. Determine when to use atomic prompts versus integrated reconstruction, when successful practice can replace separate reviews, and how bounded inference-based omissions would be checked. Compare the simple schedule against meaningful adaptive alternatives without a weighted-sum utility function.

## Comments

The user authorized the concrete next step: compare short diagnostic questions, focused practice and combined exercises under a time budget. Use authored costs for this experiment, not an assumed personal study budget. Preserve the current accepted diagnosis sequence and keep actual review omissions unvalidated. This claim covers the bounded comparison and design recommendation, not final human approval of every selection tradeoff.

For a failed large exercise, selection must support targeted diagnostic follow-ups, focused reinforcement, and a fresh integrated recheck. Define a stopping rule and time budget for diagnosis so it does not become an exhaustive prerequisite quiz. An ambiguous cause must remain explicit when time runs out. [Diagnosis design](../spec.md#diagnose-failure-before-choosing-reinforcement).

Transcript anchors: lines 610, 756–888, 982–1030, 1234–1357, 1610–1691 and 1743–1825. Exercise formats are alternatives, not a compulsory ladder. Set-cover is a coverage analogy, not evidence of learning gains or a required solver. The current spike does not resolve this selection question.

Context: [conversation coverage audit](../research/provenance.md#conversation-coverage-audit).

The [comprehensive retrieval](../research/conversation-retrieval.md) restores the Q1–Q4 overlap example and the reasons static coverage is insufficient: uncertain effects, prior practice, elapsed time, and new evidence after each answer. Include learner-specific substitution, difficulty adaptation, and mixed practice as candidates to compare, not assumed policies. Selection must account for target fluency and recognition of applicable knowledge as well as recall of named concepts.

The [diagnosis prototype](13-diagnosis-prototype.md) demonstrates a bounded, explicit ordering from broader assessment to selective probes and repair, then integration. It shows selection reasons and budget stops. This is a baseline to inspect; it does not estimate learning gain, optimize probe information, or validate review omissions.

Working [representation](../representation-design.md) and [inference](../inference-design.md) contracts now permit a bounded comparison without declaring those broad decisions final. Next slice: use current math, operations and simple-fact fixtures with explicit qualitative hypotheses and authored costs; compare a distinguishing question, focused practice and an integrated exercise under the same budget. Recompute after each answer and retain unresolved needs when nothing appropriate fits. A question should change the teaching branch; do not turn every unknown component into a mandatory quiz. Keep inference-based future deferrals as recorded candidates until prospective validation. No new user exercise or repeat approval of the existing sequence is needed for this design work.

That bounded slice is complete in the [selection design](../selection-design.md) and [executable comparison](../spikes/selection/README.md). The real assessment bridge and planner feed the selector. The restored Q1–Q4 illustration reproduces authored first-fit at 420 seconds and finds equivalent expected coverage at 360 seconds. Math, operations and fact paths show focused repair, partial larger answers, useful clarification, format constraints and budget stops. All times and responses remain authored, not learner measurements.

Thirty-one replay checks and three real page-handler checks pass. Independent audit found and reproduced two seam defects: property-order-sensitive contract comparison and loss of an unresolved task-level concern from completion status. Both are fixed and covered. Prior artifacts and the accepted learner plan are unchanged; browser layout is unverified.

The proposed policy reserves diagnosis follow-up time including a check after correction, compares full exercise costs without weighted utility, recomputes after observed answers, and preserves future checks after immediate practice. Partial-budget ordering is an explicit experimental choice. Calibrated uncertainty, learned costs, delayed retention, personal time/quality tradeoffs and real review omissions remain open. Release the bounded investigation claim; do not represent it as final human approval. The next product-design gap is the material-to-practice workflow.
