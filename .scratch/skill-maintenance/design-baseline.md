# Memorization learning web app — Design Baseline 1

Status: finalized for implementation planning, 2026-10-16, at the user's request: “ok, finalize the design.” This freezes the current revised design and its first-release defaults. It is not authorization to implement, deploy, send learning material to a model, or run a learner experiment. The application has not been built or qualified.

This is the entry document for the design. It follows reviewed research-branch snapshot `ccda8c1`, including the independent module review and its response. Canonical snapshots live on `codex/research/observability-campaign`; primary-checkout files are working copies compared when each snapshot is saved.

## 1. Product and first-release scope

Build a general memorization-oriented learning web app for facts, relationships, connected explanations and text-described procedures. Kubernetes is example material, not the product or a mandatory pilot. The same learning path must work for a simple fact and a connected explanation; describing a procedure does not demonstrate its execution.

The first-release reference design serves one learner through a browser, one application process and one local durable SQLite store. This fixes the planning target; actual setup remains unauthorized. A configured remote model may support authoring and assessment, so local storage is not a promise of offline operation. Hosted multi-user operation, synchronization and a production hosting/security topology require a separate design change.

The three user-facing places are material/learning outline, practice, and progress/corrections. Material intake accepts plain text, proposes a source-linked editable outline and meaningful knowledge units, relates new material to existing knowledge through reviewed mappings, and supplies suitable exercises. The learner can correct content and judgments without losing earlier answers or curriculum progress.

For familiar material, start with an appropriate larger exercise; for unfamiliar material, allow learning first. Assess the actual answer by requirement, identify the smallest supported gap or an explicit uncertainty, give focused help, check its use in a fresh appropriate task, and check again later. A misread is not automatically a knowledge gap. A composite failure cannot mark every constituent unit wrong. Direct facts can use direct recall prompts.

## 2. Architecture and durable invariants

| Module | Owns |
|---|---|
| Content | Material, knowledge/targets, task meaning, rubrics and compatibility mappings |
| Evidence | Actual observations, assessment, assistance/exposure interpretation and named qualification definitions |
| Practice | Learning needs, review opportunities, per-target ownership, scheduling and next-action policy |
| Measurement | Timing/effort, fixed comparison plans, metrics and reproducible reports |

Application Workflows coordinates commands; Library supplies durability/transaction/archive mechanics; Web Interaction presents state and captures intentions. These are logical responsibilities, not a requirement for seven separately packaged wrappers or services. The [module contract](module-design.md) defines the allowed dependencies, narrow interfaces and single-writer ownership of all 27 record kinds. Public portable data does not expose repository code or authorize foreign table access. Low coupling is an implementation objective checked through concrete changes, not a conclusion from the dependency diagram.

Preserve these invariants:

- Save the answer, submitted offer and pending model-assessment operation in one command before an external request. No model request runs inside a write transaction.
- Accept corrections and their Evidence/Practice effects atomically. A valid held schedule commits with the correction; a technical failure rolls back. A timeout is not a wrong answer.
- Practice owns scheduling effects and per-target review roles. Evidence supplies the same named/versioned qualification rules to practice and reports. Measurement cannot demand extra practice to improve its sample.
- Keep direct observations, hypotheses, forecasts and causal claims distinct. Update FSRS only from actual eligible owned recall reviews; never fabricate reviews from graph inference or extra practice.
- Preserve exact identities, raw answers/help, corrections, schedules, pending work, algorithm identities and historical report definitions through export/restore and future upgrades.
- Historical reads use one source cutoff, evaluation time and set of rule identities. No current state or new model judgment may leak into replay. Unknown time, unavailable old algorithms and missing evidence stay explicit.

## 3. Frozen operating defaults

The following are revisable design defaults, not empirical optima or a claim that the user individually selected every constant. Their complete conditions and exceptions remain in the linked contracts.

| Area | Baseline decision |
|---|---|
| Daily selection | Resume the bounded current encounter, then choose ready work by preserved waiting time with explicit goal-order ties. Fit against honest full-cost estimates, preserve unmet work, and allow learner override. No weighted utility sum. |
| Diagnosis and repair | Three diagnostic prompts per persisted session and three per unresolved concern across sessions. After two completed, supported unsuccessful repair cycles, stop automatic remediation and offer review/prerequisite investigation/pause. Unanswered, helped or unjudgeable verification follows its separate stop rules. |
| Capability review | Retain the written 24-hour initial/post-help and seven-day qualifying-maintenance defaults, with the lifecycle contract's first-success, correction, exposure, timing and hold rules. These are not FSRS recall intervals. |
| Exposure and freshness | Relevant aids affect the corresponding requirements. Minimum delay needs supported time/end conditions; unknown historical time has a prospective recovery path. Surface variety alone establishes no transfer claim. |
| Weak-unit shortlist | Use `observed-concerns-2`: up to five distinct units with unresolved supported errors, ranked by comparable consecutive error episodes with visible ties. Recovery, insufficient evidence and unlocalized failure have separate presentations. The shortlist is advisory and may be shorter than five. |
| Dashboard | Analytical C is the default, with A's quick orientation and B's capability detail in their useful roles. Use plain labels, dated trends, explicit workflow steps and evidence drilldown. |
| Tracking | `routine-tracking-1` freezes targets, baselines and three seven-day observation windows. Bind ordinary check offers prospectively; add no testing burden solely for tracking. Missing or later-disqualified endpoints remain in the planned population. |
| Effort and progress | Show descriptive improvement, maintenance, later independent checks and all attributable effort, with missingness and timing quality. Keep raw grading distinct from claim-qualified results. No universal mastery/efficiency score or causal saving claim. |
| Retention/deletion | Archive preserves history. Whole-library deletion is the first-release erasure scope; actual deletion needs its own explicit action/confirmation. Selective permanent erasure remains deferred. |

The [everyday-learning contract](everyday-learning-design.md), [lifecycle rules](learning-lifecycle-contract.md) and [tracking contract](../learning-observability/tracking-contract.md) are the detailed authorities. An ordinary tracking plan is not a randomized optimization experiment.

## 4. Contract index and precedence

| Question | Authoritative detail |
|---|---|
| Product requirements and retained conversation insights | [System specification](spec.md), [55-item retrieval ledger](research/conversation-retrieval.md) |
| Knowledge, targets, groups and exercise coverage | [Representation](representation-design.md) |
| Intake, authoring, reuse and content corrections | [Material workflow](material-workflow.md), with lifecycle authoring/teaching extensions |
| Narrow diagnosis and cautious inference | [Diagnosis](diagnosis-design.md), [inference](inference-design.md) |
| Selection, persistent repair and dashboard-to-practice flow | [Selection](selection-design.md), [everyday learning](everyday-learning-design.md), [worked cases](everyday-learning-cases.md) |
| Admission, offers, effective order and correction consequences | [Learning lifecycle](learning-lifecycle-contract.md) |
| Module interfaces, dependency direction and field/rule ownership | [Module design](module-design.md), [review dispositions](module-design-review-response.md) |
| Stable records, atomic commands, portable history and upgrades | [Compatibility](compatibility-design.md) |
| Measurement rationale and statistical boundaries | [Observability design](../learning-observability/spec.md), [original measurement requirements](observability-design.md) |
| Presentation and evidence navigation | [C dashboard contract](../learning-observability/c-dashboard-contract.md), with the everyday contract's successor shortlist |
| Source snapshots, time/effort, report persistence and replay | [Observability data contract](../learning-observability/data-contract.md) |
| Planned endpoints and claim-qualified aggregation | [Tracking contract](../learning-observability/tracking-contract.md) |
| Archive and erasure limits | [Deletion contract](../learning-observability/deletion-design.md) |
| Build order and acceptance work | [Main build plan](first-build-plan.md), [observability slices](../learning-observability/plan.md), [readiness ledger](../learning-observability/readiness-review.md) |

This baseline controls scope and current decision status. Detailed contracts control their named fields and rules. Read the compatibility base table with the explicit lifecycle/data/tracking additions, including the module review's schedule effects, neutral attempt purpose and removal of duplicate elapsed fields. Earlier summaries cannot override those specific rules. A new contradiction requires a documented correction, not silent selection of the convenient interpretation.

Prototype code, synthetic fixtures, old audit findings and dated ticket comments are evidence of earlier work, not the normative product contract. In particular, the existing dashboard's version-1 ranking does not override `observed-concerns-2`. Historical “proposal” or “awaiting review” wording is superseded for included baseline behavior. Candidate fitted models, graph-based omission policies and future experiments remain candidates; finalizing this design does not adopt them.

## 5. Handoff and qualification

After separate implementation authorization, follow the existing five end-to-end slices: one saved encounter; larger-task diagnosis and repair; corrections and continuity; real later reviews with budgeted practice; then fresh cross-subject qualification. Build observation into those slices. Do not build an analytics platform or empty module framework first. Optional prediction audits and policy-comparison experiments are later work.

Implementation preparation selects language/framework and exact versions, supported browser matrix, actual machine/store location, and an authorized model endpoint/credential path. A deployment outside the single-learner reference design requires an explicit design amendment. These are concrete setup choices for execution, not an instruction to reopen the accepted product scope or assign more prototype homework.

| Gate | Evidence required |
|---|---|
| Function and persistence | Real application commands, store, scheduler/provider seams and browser behavior; include stale clients, retries, holds, crash recovery, export/restore and historical replay. Carry M01–M10, V01–V12 and the existing contract case packs into those slices. |
| Semantic quality and usability | Fresh examples across fact/relation/procedure demands, independently checked assessment/diagnosis, understandable flows and accessible browser operation. Existing presentation approval is not a completed study. |
| Prediction quality, if introduced | Prospective forecasts evaluated on later independent evidence with calibration, uncertainty and dependence accounted for. No model is required for initial descriptive reporting. |
| Learning benefit and optimization | A separately agreed comparison, retention-loss/cost tolerances, learner burden, allocation and stopping rules, followed by real delayed outcomes. No experiment or review omission is approved here. |

Historical open tickets retain investigation/validation questions beyond this bounded baseline; they are not a request to reapprove its settled behavior. Their current disposition is implementation qualification, deferred model/optimization research, or future subject/deployment expansion as described here. The finalization task records this scope without declaring those empirical outcomes achieved.

## 6. Verification and future change

The prior four design audits have recorded case dispositions. All eighteen independent module-review comments have explicit responses, including qualified disagreements; the original audit is retained. Finalization checks document links/anchors, review/case coverage, the 55-item build-plan mapping, the 27-owner registry, the declared dependency graph and consistency with the revised field contracts. These checks validate the documents, not a running application or learning efficacy.

Change the baseline when a named user requirement, implementation failure or observed result justifies it. Record the reason, affected interfaces/fields, compatibility impact and acceptance evidence; version changed policies/claims and preserve old learning/report meanings. Do not silently rewrite this baseline's scope or historic evidence. Routine implementation choices can be made within these contracts without another design campaign.
