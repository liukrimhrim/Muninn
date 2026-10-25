# Current decision frontier

Snapshot after the bounded investigations and consolidated first-build plan; query the ticket files for current state. The map remains the canonical index of resolved decisions.

| Decision | State | Dependency |
|---|---|---|
| [Can the learner state avoid false credit while choosing affordable practice?](issues/04-evidence-spike.md) | Open; targeted clarification now takes precedence over help; prior accepted plan preserved | Semantic accuracy, broader model and earlier spike questions remain open |
| [Which examples and outcomes should validate the general system?](issues/05-pilot-outcome.md) | Open; chat trials plus blinded historical-annotation comparison complete | Agreement is not accuracy; broader validation choices and delayed outcomes remain open |
| [What evidence would justify fewer reviews without worse retained skill?](issues/06-evaluation-contract.md) | Blocked | Validation examples and outcomes |
| [What is the smallest system worth building after the spike?](issues/07-minimal-system.md) | Open; conditional first-build plan complete | Delivery/model setup and final release choices remain open; broader validation dependencies are not silently closed |
| [How should learners turn material into reusable practice across subjects?](issues/09-learning-workflow.md) | Open; proposed workflow and bounded source-to-practice continuation complete | Automatic drafting, semantic quality, authoring effort and final input/delivery choices remain open |
| [How should the system represent details, relationships, and larger knowledge structures?](issues/10-knowledge-representation.md) | Open; explicit coverage and practice grouping implemented in the spike | Broader target boundaries and empirical validation remain open |
| [What can the system infer from limited practice, and how should it express uncertainty?](issues/11-learner-inference.md) | Open; bounded research, proposed contract and assumption probe complete | Calibration, delayed outcomes and final model choice remain open |
| [How should the system choose exercise purpose, format, and coverage under a time budget?](issues/12-adaptive-review-selection.md) | Open; bounded comparison and proposed policy complete | Costs, priorities, delayed outcomes and real omissions still need validation |

Research tickets, the product-scope decision, and the diagnosis prototype discussion are resolved and linked from [the map](map.md). The user confirmed the exercise sequence and reported that the assessment judgment made sense; actual learner validation remains open. No HITL decision was answered on the user's behalf.

The [independent annotation comparison](spikes/independent-assessment/review.md) remains a historical comparison with 23 matches, 10 disagreements and three abstentions among 36 comparable judgments. Its clarification/help conflict is addressed by the [action-policy continuation](spikes/answer-intake/clarification-notes.md). The subsequent [representation continuation](spikes/representation/README.md) verifies explicit capability coverage and combined practice in the existing pipeline.

The [inference design](inference-design.md), [primary-source investigation](research/sparse-inference.md) and [numerical probe](spikes/inference/README.md) now specify how estimates can guide practice without becoming observed success or reinforcement. Fourteen new checks pass, including matched-prior controls, contradictory answers, asymmetric noise and shared evidence identity. No learner-facing numerical model or review omission was introduced.

The [selection proposal](selection-design.md) and [executable comparison](spikes/selection/README.md) now compare short diagnostic questions, focused practice and combined exercises under authored budgets, recomputing after each answer. Thirty-one replay checks and three page-handler checks pass. An independent audit's contract-order and task-level-uncertainty findings were corrected. No empirical learning benefit is implied.

The [material workflow](material-workflow.md) and [bounded continuation](spikes/material/README.md) now carry literal sources and authored semantic proposals through the existing practice loop. Twenty behavioral and four page-handler checks cover source anchors, conditions, connected targets, exact reuse, stale mappings, corrections and retained history. Independent review findings were corrected. Automatic semantic extraction, browser rendering and learning benefit remain unverified.

The [first-build plan](first-build-plan.md) now specifies a real source-to-practice-to-resume path, five implementation slices and acceptance cases. Its coverage table assigns all 55 retrieved ideas a destination. Reusable code contracts are distinguished from authored examples; no new implementation or learning result is claimed.

Next: prepare and implement one saved learning encounter once delivery and the actual model setup are selected. Broader evaluation thresholds need not block that first functional slice. The earlier demo reviews remain optional; no additional learner exercise or repeat approval of the accepted sequence is needed to prepare implementation.
