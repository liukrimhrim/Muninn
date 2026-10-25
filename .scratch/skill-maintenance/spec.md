# A general system for memorization-oriented learning

Status: finalized in [Design Baseline 1](design-baseline.md), 2026-10-16. This is the general memorization-learning web-app specification. The baseline fixes scope, contract precedence and first-release defaults; implementation and empirical qualification remain separate.

## Recommendation

The [everyday-learning design](everyday-learning-design.md) details how the system acts on this recommendation: dated observations versus current review needs, exercise variation and comparability, time-bounded session selection, cross-session repair limits, and progress-to-practice navigation. Its proposals and [worked cases](everyday-learning-cases.md) close previously underspecified behavior in the draft; their defaults are now frozen for baseline planning, while implementation and empirical validation remain distinct.

Build a general system that helps learners retain a connected body of knowledge with less unnecessary review. Its central design problem is choosing what the learner should retrieve next, at what level of detail, and in what format. That choice should use both observed performance and explicit uncertainty about untested knowledge. Facts, relationships, explanations, larger structures, and procedures all belong in this scope.

The earlier draft emphasized conservative evidence handling so strongly that it weakened this larger objective. A direct-review baseline is useful for comparison, but it is not the complete design. Keep FSRS as a candidate recall-scheduling component. Investigate graph-informed inference, diagnosis, review compression, and adaptive exercise formats without treating an untested mechanism as established. A flawed implementation does not disprove the underlying design opportunity.

The user explicitly confirmed the product scope: a general system for memorization-oriented learning across subjects. Kubernetes is one example of procedural knowledge. It does not define the product, mandatory exercise formats, or the first implementation. The earlier proposal placed too much emphasis on operational skill maintenance.

The first release can be small while its learning model remains independent of subject. Validate that model with contrasting examples, such as vocabulary, historical relationships, mathematical explanations, and procedures. The user selected a **web-based application**, with material intake, an editable learning outline, practice, feedback, progress and corrections accessible in the browser. This settles the interface choice. The baseline adopts assisted editable plain-text intake and a single-learner local reference build. Fresh validation material and actual environment setup are selected during implementation qualification; hosted multi-user operation is a separate extension. Choosing web delivery does not authorize implementation or deployment.

## What carries forward from the conversation

The user's needs are connected understanding, meaningful knowledge granularity, less redundant review, targeted diagnosis, and practice formats that sometimes demand real effort. The transcript's proposed mastery vector, graph propagation, and utility formulas were assistant hypotheses, not user-approved requirements or scientific results. They still require an explicit disposition: investigate, revise, or reject with a reason. Lack of validation does not make an idea irrelevant.

The [conversation coverage audit](research/provenance.md#conversation-coverage-audit) maps the original insights to the current design and outstanding decisions. It distinguishes ideas that were absent from those that survived only as brief mentions.

The subsequent [comprehensive retrieval](research/conversation-retrieval.md) preserves 55 distinct ideas, the original worked examples, the research leads, and this chat's later corrections. It supersedes the earlier audit as the detailed retrieval reference. Source attribution distinguishes user needs from assistant proposals; the catalog is not approval of every mechanism.

The general workflow must cover selecting learning material, identifying what to retain, checking or editing knowledge components and relationships, practicing retrieval, receiving feedback, and returning for later review. How much the learner authors manually and how much the system derives from source material remains open. The Kubernetes spike addresses evidence updates only; it does not validate this complete workflow.

“As atomic as possible” needs one qualification: split a component only if the split changes an assessment or a practice decision. Otherwise the learner pays authoring and testing overhead without useful feedback. A relation can itself be a target: explaining why readiness affects traffic is a capability, not merely an edge drawn between two notes. A new scenario tests a broader structure by asking the learner to select and combine relevant relations; enumerating all graph paths is unnecessary.

## Learning principles the design must preserve

**Remember both details and their organization.** Explicit targets should cover a fact, a relationship, a chain of reasoning, and a meaningful group of concepts. Recalling every pairwise link does not by itself demonstrate that the learner can reconstruct the whole structure. Ask for comparisons, missing links, explanations, and reconstruction from memory. Use an unfamiliar example to check whether the learner recognizes the same structure there.

**Distinguish fluent retrieval from reconstruction.** A learner may derive an answer correctly but still struggle to recall a frequently needed fact. Another learner may repeat the fact but fail to explain it. Preserve both observations. Which performance needs to become fluent depends on the learner's goal. The original motivation was to make useful knowledge readily available for reasoning, not simply to maximize card accuracy.

**Practice recognizing when knowledge applies.** Retrieving a rule when named differs from choosing it from the features of an unfamiliar situation. Relevant targets should include applicability conditions, contrasts with alternatives, and cues for selecting a principle or action. For a procedure, choosing an action, executing it, interpreting its result, and verifying a conclusion can expose different gaps. These are assessment distinctions, not a requirement to fit a separate latent score for each.

**Preserve the richer meaning of structure.** A group is more than a list of members. Exercises can ask how several relations jointly constrain an explanation, which principle unifies different cases, or what new consequence follows. Distinguish repeating a relationship from reconstructing its reason. Decide which details should be fluent and which can reasonably be derived; understanding, recall, and application need not form a fixed learning sequence.

**Keep knowledge components separate from exercises.** Small components support diagnosis. One exercise may retrieve several components and relationships. Record that mapping, including what is required, what is merely related, and what was actually observed. Do not force either one card per component forever or one coarse success grade for a large task.

**Change review size as knowledge becomes familiar.** Test the proposal that a learner can progress from small prompts to a larger integrated exercise. If that exercise reveals a gap, return to the relevant component or connection. This is adaptive chunking: changing the unit of practice while preserving the fine detail needed for diagnosis. Do not delete component histories or assume that a group became one psychological memory.

**Distinguish a known weakness from an uncertain estimate.** A learner with repeated failures needs practice and feedback. A learner whose knowledge is untested may need a short diagnostic question. Related performance may supply a useful estimate, with its assumptions and uncertainty attached. Direct observations, estimates of unobserved knowledge, and actual learning effects are different things.

**Choose exercises for learning as well as diagnosis.** A question can reveal a weakness without doing much to repair it. Another can provide useful practice while revealing little new information. State which purpose drives each selection, then provide feedback and a later check. Do not replace this distinction with one uncalibrated utility score.

**Use the graph to avoid unnecessary work.** Consider prerequisites that obstruct a selected goal, relationships that connect ideas, and overlap between candidate exercises. A foundational gap can matter more than an isolated detail. Raw graph degree is not a measure of personal importance. The target is an efficient sequence of retrieval exercises, not a tour of every node or path.

**Adapt format and effort.** Recognition, unaided recall, explanation, reconstruction, and execution are available forms, not a compulsory ladder. A learner can start with a demanding task, use a narrow prompt to repair one weakness, and return later to the larger task. Reduce wasted effort while preserving effort that serves the chosen learning goal. Cross-format substitution is a question to investigate, not an automatic update rule.

These principles preserve the conversation's design ambition. Their effect on review time and delayed retention still needs measurement. The finalized baseline and detailed contracts specify first-release behavior.

## Evidence that constrains the design

Read the source investigations for exact versions, citations, probes, and caveats:

- [Existing implementations](research/existing-implementations.md): what graph-aware review systems actually implement and what their public code does not establish.
- [Learning evidence](research/learning-evidence.md): retrieval, spacing, transfer, adaptive review, and the gap between recall prediction and retained task performance.
- [Memory-model boundary](research/memory-model.md): actual FSRS inputs and transitions, diagnostic alternatives, and what sparse personal data can support.
- [Sparse inference](research/sparse-inference.md): feasible-state assumptions, primary-source KST and cognitive-diagnosis boundaries, contradictory evidence and dependence between observations.

The [spike](spikes/README.md) supplies reproducible counterexamples to unsupported evidence credit. Its eight synthetic traces establish model behavior only. They do not establish learning gain, time savings, or superiority over existing systems.

Several findings materially change the earlier conversation:

| Earlier idea or uncertainty | Verified finding | Consequence |
|---|---|---|
| Extend FSRS by giving prerequisite credit | Official py-fsrs 6.3.2 accepts card ratings, not fractional indirect observations | Keep inferred capability evidence outside the FSRS update contract |
| Reuse an existing graph-aware scheduler | Four authored fixtures against the pinned Obsidian implementation reproduced a normalization discrepancy, an empty remediation queue, duplicate diamond credit and repeated credit for the same timestamp | Reuse the maintained library; verify eligibility, provenance and idempotency in the adapter |
| KARL shows learning efficiency | Its small trivia study's efficiency denominator is posttest response latency, not cumulative study time; it did not assess unseen operational tasks | Measure retained target behavior and the whole learner-time cost directly |
| Only KARL's model code is public | The paper-linked `Pinafore/fact-repetition` repository also contains scheduler/API code | Include that implementation in any later policy comparison, without assuming the historical study deployment is reproduced |

The [source-probe output](spikes/source-probe-results.txt) records the coordinator's independent reruns of the FSRS and Obsidian fixtures. The detailed reports provide immutable source links and exact reproduction commands. These findings establish bounded code behavior and study scope, not live-user severity.

## A small domain model

Use the [glossary](../../CONTEXT.md) to keep knowledge, tasks, observations, and capabilities distinct.

The [representation proposal](representation-design.md) now makes the boundaries concrete across operations, mathematics, language, science, and simple fact recall. A learning target is a goal-selected capability; an assessment criterion need not become a permanent target. Separate capabilities when evidence can distinguish them and the distinction changes useful practice. A semantic knowledge group describes an explanation or shared principle, while a practice bundle selects targets for one exercise. The [executable continuation](spikes/representation/README.md) implements explicit coverage and practice grouping through the existing spike across three example domains. Its checks establish behavior, not grading accuracy or improved learning.

| Record | Minimum information | Why it exists |
|---|---|---|
| Curriculum | Stable ID, revision, purpose, member target IDs and organization; learner's selected revision and goals | Preserve the learning plan and connect progress to meaningful targets when the interface or architecture changes |
| Knowledge component | Stable ID, statement, source and version | Identify what is being learned without tying it to one prompt |
| Capability | Component(s), observable action, assessment mode, relevant conditions, rubric version | Define what evidence would actually support a claim |
| Relation | Source, destination, type, provenance, author confidence | Separate prerequisite, explanation, analogy and contrast links |
| Knowledge group | Component/relation members, composition or shared principle, larger retrieval target | Support structure reconstruction and changes in review granularity without discarding component history |
| Exercise | ID/version, variant family, capabilities, mode, rubric, permitted help, estimated total time | Define an opportunity to observe and practice capabilities |
| Attempt | ID, exercise/version, family, timestamps, actual time, first response before feedback, later actions, hints, context, final outcome | Preserve what happened once |
| Observation | Attempt ID, capability, rubric criterion, result, evidence reference, assistance, assessor/version, confidence category | Bound each inference to something observed |
| Recall stream | Stable retrieval contract, actual rating history, FSRS version/parameters/state | Schedule a comparable recall task from real reviews |
| Learner estimate | Target, supporting observations, assumptions/model version, uncertainty, relevant context and age | Express an inference about untested knowledge without inventing an observation |
| Selection record | Eligible candidates, purpose, constraints, chosen exercise/format, intended coverage, reason, policy version | Explain and later evaluate practice choices |

These are logical domain concepts, not separate services or a physical database schema. The compatibility, lifecycle and data contracts specify the durable records. A group can be a composition relationship rather than a new storage system. JSON fixtures suffice for the spike. If the first implementation is local and serves one learner, a few SQLite tables and adjacency relations can preserve the history. The baseline reference store is SQLite in one local application; actual provisioning and any hosted extension require their own execution/design decisions. A general learning model does not by itself require a graph database or separate services.

Keep semantically rich relations separate from the curriculum's prerequisite relation. Only the latter may need an acyclic constraint; analogies and mutual explanations can form cycles. A curriculum graph describes knowledge and relations. A learner model estimates a person's changing knowledge. An exercise-to-component mapping describes possible coverage. These are distinct even if stored together.

The baseline adopts assisted, editable authoring from the transcript's hybrid proposal: retain an explicit, editable graph and use an LLM to propose components, relationships, exercises, and interpretations of responses. Attach the source and review status. Manual corrections remain available; alternative representations can be evaluated later for a named limitation. Unreviewed proposals must not silently become progression gates or evidence of learning. Authoring effort and correction burden are part of the cost comparison.

That proposal includes progressively refining and testing the representation, and connecting incoming material to the learner's existing knowledge. The material workflow and lifecycle contracts cover those interactions, alongside exercise generation, delivery or execution, assessment, and corrective feedback. A curated single-subject graph can validate a mechanism but cannot by itself validate the general material-to-practice workflow.

## Preserve curriculum progress as the architecture evolves

The user requires that architecture changes preserve existing curriculum progress. A learner must be able to continue an existing curriculum after an upgrade without reimporting material or repeating completed work solely because the software changed. Progress includes the selected curriculum and goals, content revisions, answers, assistance, judgments and corrections, actual review history, due dates and unfinished work. A completion percentage alone cannot preserve it.

Give curricula, targets, exercises and attempts stable identities independent of screen positions, database row locations or generated prompts. Keep curriculum organization separate from evidence about its targets: renaming or reordering a chapter must not reset those targets. Retain the exact content and assessment definitions referenced by older attempts, including retired targets. Splitting a target or changing its required action preserves its old history but does not automatically prove the new capabilities.

Separate three kinds of change:

| Change | Compatibility requirement |
|---|---|
| UI, internal modules, storage layout or hosting | Preserve the meaning and identity of saved records, effective progress, pending work and due timestamps; migration itself creates no practice or new assessment |
| Curriculum organization or target meaning | Reorganization preserves target evidence. Changed meaning receives a revision and explicit compatibility decision; retain previous achievement and identify only the new or changed learning needs |
| Assessor, learner model or scheduling policy | Preserve original evidence and earlier decisions with their versions. Any regrading, revised estimate or rescheduling is a separate recorded change, not a hidden side effect of a storage upgrade |

Version the stored data format separately from content and algorithm versions. New releases must read or migrate every previously released format through a documented upgrade path. An older application encountering a newer unsupported format must refuse to modify it. This does not require old application binaries to understand every future format.

Provide a documented, versioned export and restore path containing curriculum/content definitions, original learning records, current schedule state and their references. It must work without re-generating material or re-assessing answers through an external model. Before a migration, preserve a restorable copy; validate the migrated records before allowing new writes. Failure must leave a recoverable original, not an empty curriculum. A rollback must not silently discard learning recorded after the upgrade.

The [detailed compatibility design](compatibility-design.md) specifies record fields and references, a versioned export format, revision and retry rules, migration/cutover/recovery procedures, curriculum and model transitions, browser continuity, and 20 concrete acceptance cases. The [first-build plan](first-build-plan.md#compatibility-and-upgrade-checks) places these obligations in the release sequence. Use ordinary versioned records and specific migrations when formats actually change; there is no requirement for a plugin framework, separate compatibility service or fixed architecture. Implementation remains unauthorized.

## The first practice loop

1. **Define what to retain.** Select knowledge components and the intended recall demand: recall a fact, explain a connection, reconstruct a larger structure, or retrieve a procedure. State the allowed cues and desired retention period.
2. **Offer a qualifying exercise.** Use the current evidence and session budget. A short recall prompt, comparison, explanation, or reconstruction exercise should match that demand. Use hands-on practice when the learner's chosen target requires execution.
3. **Capture the attempt.** Keep the first response, help used, feedback, time, and final result. A correct final response after a hint is different evidence from unaided recall.
4. **Assess narrowly.** Emit observations only for criteria actually witnessed. Record ambiguous failures as unresolved; choose a discriminating follow-up instead of marking all prerequisites wrong. Preserve separate criteria when one exercise covers several components.
5. **Update observations and estimates separately.** Preserve direct evidence, assistance, contradictions, and freshness. An inference about an untested target can guide a future question while remaining explicitly uncertain. Update FSRS only from an actual comparable recall review. Do not invent a review grade for an inferred ancestor.
6. **Reassess after a delay.** Use unseen variants to see whether the capability persisted and transferred. Retire or compress future work only under an explicit, auditable rule.

Use four domain modules in one application: **Content** owns material and task meaning; **Evidence** owns observations, assessment and qualification; **Practice** owns learning needs, scheduling and selection; **Measurement** owns effort, tracking and reporting. The [module design](module-design.md) specifies their interfaces, record/rule ownership and acyclic dependencies, with Web Interaction, Application Workflows and Library supporting them. Corrections cross the necessary owners in one atomic command; callers cannot write another module's records or duplicate its interpretation rules. Attempt IDs and criterion identity prevent duplicate credit. Model changes remain replayable from retained history under the compatibility rules.

Keep grade corrections as explicit superseding records and rebuild affected state; a fake compensating review would misrepresent practice. A learner who forgot before seeing feedback supplies a failed recall observation even if the final response is correct. Real later relearning is a separate event. Save raw evidence before assessing it so a grader change can be audited.

## Diagnose failure before choosing reinforcement

The user explicitly requires that failure on a large exercise lead back to the specific knowledge that needs reinforcement. Here, “episode of knowledge” is interpreted as a knowledge component, relationship, or procedural step. This is a required behavior; the diagnosis method remains an open design decision.

The user confirmed the sequence **large exercise → locate the gap → focused reinforcement → fresh integrated check**. When reliable evidence already identifies the gap, focused practice can come first. This agreement establishes the intended sequence; diagnosis accuracy and learning benefit still require validation. See the [recorded feedback](issues/13-diagnosis-prototype.md). Support it as follows:

1. Map the exercise's assessment criteria to the components and connections they can reveal. Preserve the learner's response and any work already available. Do not require constant step-by-step narration merely to make grading easier.
2. Use that evidence to retain plausible explanations: a forgotten fact, a misunderstood relationship, a missing step, difficulty combining known parts, or a slip. A failed final answer does not make every prerequisite weak. More than one gap may be present.
3. Where the evidence cannot distinguish explanations, ask a short follow-up whose possible answers would change the reinforcement choice. Reuse prior observations and avoid testing every prerequisite. Record help or feedback given during diagnosis, since it can change subsequent performance.
4. Stop probing when there is enough evidence to choose useful practice, or when the diagnosis budget is exhausted. Keep unresolved alternatives visible. The target is the smallest supported actionable gap or set of gaps, not an invented exact cause.
5. Reinforce the diagnosed component or connection. If isolated knowledge is available but combination fails, practice combining it. If the material was never understood, provide instruction before more retrieval practice.
6. Return to a fresh larger exercise that requires the repaired knowledge, then check again after a delay. Success on the narrow prompt alone does not establish successful integration or lasting retention. Revise the diagnosis if the larger exercise still fails.

The [answer-to-practice design](diagnosis-design.md) now gives concrete learner-answer branches for binary search, grammar, and a fictional procedure. It distinguishes demonstrated knowledge, an observed error, absent evidence, and an assessment that cannot be settled. Follow-up questions must distinguish practice choices; one error does not establish forgetting or a slip. The constructed cases and manual counterexample review specify proposed behavior. Real learner attempts are still needed to establish diagnosis accuracy and useful reinforcement. Keep diagnosis time, unnecessary practice, and later integrated performance as separate measures.

Diagnosis also applies after a successful larger exercise. The original conversation describes completion that includes hesitation and an irrelevant action. Preserve those observations without treating hesitation alone as proof of weakness; a short follow-up may distinguish an action-selection gap from missing recall or a slip. Add a successful-but-uncertain case to the spike. Reinforcement may target selection, interpretation, or integration even when isolated facts and the final answer are correct.

The [two-subject diagnosis prototype](spikes/diagnosis-prototype.html) now makes this loop interactive with binary-search and English-grammar content. Its [notes and replay results](spikes/diagnosis-notes.md) record the authored behavior and limits. It supports discussion of these rules; it does not establish reliable diagnosis from real answers or improved retention. Human review remains open in [the prototype decision](issues/13-diagnosis-prototype.md).

## How to use FSRS without overstating its meaning

Use a maintained, pinned official implementation rather than porting its equations. Keep the library version, parameters, review ratings, UTC timestamps, and content contract with the history. A prompt about a relationship is a valid recall target; FSRS is not restricted to isolated facts.

Initially separate recognition, unaided recall, explanation and execution evidence. Do not fit four independent latent “masteries” per topic merely because the transcript proposed a four-dimensional vector. Those labels are useful assessment distinctions; their statistical independence and learnability are unproved.

Stable retrieval targets can use FSRS, including recall of a relationship or an explanation when the assessment contract is comparable. Broader capability estimates and indirect evidence need their own model. A small dataset may support descriptive uncertainty before it supports calibrated probabilities. In particular, no-review is **unknown**, not 0% mastery. This is a limit on what we claim, not a ban on investigating useful inference.

One exercise may directly elicit several retrieval targets. If each target's assessment contract is satisfied, an actual review may be recorded for each, at most once. Their shared attempt still makes them correlated observations. Merely being a prerequisite does not meet this condition. The precise mapping from a composite response to recall streams remains a design decision.

Separate two research questions: whether related performance predicts a learner's untested knowledge, and whether related practice improves that knowledge. A useful prediction does not prove a learning effect. Neither requires modifying the original FSRS equations to conduct an experiment. Compare explicit learner estimates and policy-level deferrals first. Any inferred-coverage policy needs later direct checks, a bounded deferral rule, and a way to restore review when the inference fails.

The [inference design](inference-design.md) now specifies the claim contract, scoped relationships, contradiction response and staged validation. A [fixed-parameter probe](spikes/inference/README.md) compares a strict state chain against an independent control with matched initial marginals. It demonstrates how structural assumptions change untested estimates, how duplicated evidence inflates them, and how error assumptions can reverse the apparent diagnosis. Fourteen checks establish calculation and provenance behavior only. The numerical model remains separate from the planner; no probabilities are assigned to the user's answers and no inferred FSRS reviews are created. The next bounded experiment compares concrete exercise choices under a budget using explicit hypotheses, without requiring another approval of the accepted learning sequence.

## Selection, coverage, and uncertainty

The selector should choose an exercise, its format, and its granularity for a stated purpose. For the target design, compare the remaining needs across the graph and the overlapping coverage of candidate exercises. A longer explanation that covers several needed relations may cost less than separate questions for each. Choosing the cheapest single question repeatedly can miss that opportunity.

The conversation's set-cover analogy captures this overlap. It does not require a weighted sum of learning, information, and time. Define the required targets and constraints, compare qualifying coverage choices within the time budget, observe the outcome, and then reselect. Expected coverage is a plan; demonstrated coverage is an observation. Inferred coverage remains a model estimate. Include feedback and setup in the cost.

The original coverage proposal is sequential: its assumptions can change with each answer, elapsed time, and prior practice. It also raises learner-specific differences in the usefulness of implicit versus explicit practice. Preserve personalization, difficulty adaptation, and mixed practice as candidates to investigate; no universal transfer coefficient, interleaving rule, or numerical benefit is established. Structural diagnosis over plausible knowledge states, as proposed by KST, remains an alternative to independent per-component estimates. The [retrieval's research inventory](research/conversation-retrieval.md#research-leads-and-their-actual-retrieval-status) identifies the unfinished investigations.

Maintain separate reasons for selection: repair a demonstrated weakness, distinguish possible weaknesses, verify a broad estimate, rehearse fluent recall, or practice an integrated structure. Goal-relevant prerequisites can justify priority. Do not let frequent diagnosis crowd out actual practice, or let a high-confidence estimate escape all later checks.

The rule below is an inspectable **comparison baseline**, not the final resolution of this selection problem. The [selection decision](issues/12-adaptive-review-selection.md) must determine when inference, grouping, and overlap justify a different choice.

Use an ordered rule, not a score mixing learning, uncertainty, transfer, and cost in arbitrary units:

1. Enforce the target's required evidence mode and critical assessment constraints.
2. Prioritize due recall, observed weaknesses, and unresolved mistakes. Reserve delayed checks of relationships and larger structures. Require execution evidence only for targets that include execution.
3. Within a chosen need, select the least costly exercise that can provide the required evidence. If the cause is ambiguous, use a narrow diagnostic question rather than a whole broad review.
4. Fit the session budget using total expected time, including preparation, feedback and recovery. If an appropriate exercise will not fit, retain the unmet target and offer clearly labeled preparation, or stop.
5. Include a predeclared audit quota for targets considered sufficiently covered. Stop when the budget or planned target is met.

This policy is deliberately inspectable. The learner should see a reason such as “you recalled the two facts, but their connection still needs a check.” Where two options remain incomparable, use a deterministic tie-break or a logged randomized choice for a later experiment—not fabricated estimates of information or learning gain.

In this conservative baseline, separate reviews are suppressed only after observed coverage, not when an exercise is merely scheduled. The target design may permit explicitly bounded inferred coverage if subsequent experiments justify it. Never hide a prerequisite because a dependent task is due if that dependent task is itself blocked. Compare richer policies against the baseline under the same constraints.

The [selection design](selection-design.md) now has an [executable comparison](spikes/selection/README.md) downstream of the existing assessment bridge and planner. It reserves time for diagnostic follow-up, compares whole exercise costs and overlapping coverage, and replans after each actual fixture response. On the conversation's invented Q1–Q4 example it finds 360 seconds of expected coverage versus the current authored-order planner's 420. Thirty-one behavior checks and three page-handler checks cover partial evidence, hints, format constraints, budget stops, duplicates and task-level ambiguity. These are authored calculations and state transitions; no learner-time saving, delayed retention or inference-based omission has been established.

## A worked example from the original conversation

Suppose the learner wants to retain how binary search works. Components include the ordered-search condition, eliminating half the candidates, and relating repeated halving to the number of steps. The connection between halving and logarithms is itself a retrieval target.

1. Ask the learner to explain the whole process from memory. This exercise can elicit several components and their connections.
2. If the explanation fails, retain competing possibilities: a missing algorithm step, a missing logarithm concept, or a missing connection. A question about how many halvings reduce 1,024 candidates to one checks part of the reasoning; its answer alone cannot distinguish all these explanations.
3. Use the response and only the necessary follow-ups to narrow the gap. If the learner can explain halving and logarithms separately but cannot connect them in binary search, practice that connection, then ask for a fresh integrated explanation. If a component itself fails, reinforce that component first. Do not restart every card about binary search or conclude that all logarithm knowledge is mastered.
4. Once broader explanations become reliable, try using them in place of some separate prompts. Preserve the component detail so that later failures can receive targeted repair.
5. Later, use a changed example and a few direct checks of components whose reviews were deferred. Measure whether fewer reviews preserved recall, explanation, and the ability to reconstruct the reasoning.

This walkthrough joins representation, diagnosis, practice, adaptive granularity, and review compression. It is a design example, not a completed learning experiment. A useful next spike should compare a simple schedule with selective diagnosis and overlapping exercises, rather than compare only blind credit with no indirect credit.

## Examples to validate the general model

Choose a small set of contrasting learning examples before a broad build. These examples test whether the same knowledge, exercise, attempt, and observation model works across subjects. They are proposed validation material, not separate products or promises of complete curricula.

| Type of knowledge | Example | What to check after a delay |
|---|---|---|
| Facts and associations | Vocabulary, definitions, names and dates | Unaided recall in the intended direction; recognition alone may be insufficient |
| Relationships | Causes of a historical event, contrasts between two concepts | Recall and explain the specified relationship |
| Connected structures | A mathematical argument, an algorithm, a conceptual outline | Reconstruct the main steps and explain their connections |
| Procedures | A recipe, command sequence, or operational workflow | Recall steps and conditions; check execution when execution is part of the target |

New content should fit the shared model without changes to subject-specific logic in the scheduler. Exercise content and assessment criteria can vary by subject. This is a design acceptance goal; the existing Kubernetes-only demo does not establish it.

The existing Kubernetes demo remains a useful procedural example. If a real execution exercise is later selected, its environment and assessment need their own design. It is not a prerequisite for a general memorization release.

Curated, versioned content is a reasonable starting point for checking the model. The [material-to-practice workflow](material-workflow.md) proposes assisted drafting with inspectable sources, meaningful scoped claims and connections, goal-selected capabilities, mapped exercises and corrections that preserve prior versions. Its [bounded continuation](spikes/material/README.md) compiles authored examples into the real practice loop; automatic extraction and semantic quality remain unverified. The written workflow is the first-release baseline. Keep held-out tasks outside generation prompts used for training exercises.

## Build and validation stages

The [first-build plan](first-build-plan.md) now supplies the concrete proposed release: real assisted material authoring, a genuine learner answer, targeted diagnosis and teaching, saved corrections and actual later reviews. It gives implementation order, existing-code boundaries and acceptance cases while retaining the broader inference/compression program below. This is a plan, not an implemented application or a completed learner evaluation.

| Stage | Concrete work | Evidence needed to continue |
|---|---|---|
| Define the first general workflow | Choose how material enters the system, how targets are reviewed, and contrasting examples to validate recall of facts, relations, structures and procedures | Product scope is settled; workflow, evaluation examples and acceptance thresholds still need decisions |
| Establish the comparison | Curate content/rubrics; record a fixed practice schedule, recall FSRS baseline, total learner time and delayed unseen checks | Reproducible attempts, trustworthy grading, evidence that the chosen task measures the goal |
| Build one full loop | Use the same flow for direct recall and a relationship or structure exercise from contrasting subjects; record observations and explain the next practice choice | The shared path works without subject-specific scheduler changes; reset/replay works; ambiguous and assisted cases remain visible |
| Compare adaptive review choices | Prototype selective diagnosis, small-versus-integrated exercises, overlapping coverage, and format changes against the simple schedule | Show what changes each choice and what happens after an unexpected result; synthetic traces establish behavior only |
| Evaluate inference and compression | Separate predicting untested knowledge from improving it; predeclare direct probes, bounded omissions, total time and decision rules | Prediction calibration on untested targets, and retained performance under fewer reviews, are reported separately; detect false deferrals |
| Select the simplest adequate model | Compare descriptive estimates or a simple probabilistic model before graph/neural alternatives | Extra complexity must improve the specific measured prediction or review outcome that motivated it; keep simpler alternatives when it does not |

Implementation acceptance checks should cover the real seams: identical attempt replay, rubric-version changes, hinted versus independent evidence, composite success with missing observations, ambiguous failure, graph diamonds/cycles, all-candidates-blocked, budget infeasibility, and UTC/elapsed-time handling in the actual FSRS adapter. Write these when implementing the loop; the throwaway spike is not a production foundation or test suite.

## Observe progress and the effort it costs

The [follow-up observability campaign](../learning-observability/map.md) investigates the remaining measurement-validity, statistics, dashboard and collection gaps. Its [expanded proposal](../learning-observability/spec.md) and [staged plan](../learning-observability/plan.md) include executable synthetic counterexamples and three dashboard arrangements; source research and correct arithmetic do not settle user-facing design or establish learner benefit.

The user requires observability for two purposes: meaningful progress should help motivate the learner, and measured outcomes versus total effort should reveal whether the system is useful or needs improvement. Good metrics and analytical tools must precede optimization. The [observability design](observability-design.md) specifies the learner dashboard, metric definitions and denominators, full time accounting, collection records, comparison rules, actionable signals and 18 acceptance cases.

Show new independent demonstrations, dated later checks, maintained capabilities and unresolved needs. Keep practice volume distinct from learning evidence, and keep assisted/immediate performance distinct from later independent performance. Maintaining existing knowledge is useful even when no new targets are added. A grade correction or a curriculum split must not manufacture learning gains.

Pair comparable outcomes with the entire cost: answering, diagnosis, study, feedback, preparation, corrections, progress inspection and blocking waits. Display uncertain/missing timing and missed assessments explicitly. Use stable target cohorts and versioned metric definitions so architecture or curriculum changes do not manufacture trends. The first version calculates these views from ordinary persisted records; no separate analytics service or weighted efficiency score is required.

Analytical tools must support evidence drilldown, target trajectories, fixed-cohort comparison, repair-path analysis, effort breakdown and measurement-quality/sensitivity inspection. The [optimization gates](observability-design.md#analytical-tools-and-the-optimization-gates) require valid and reproducible measurements before a bounded comparison, then observed benefit under agreed retention/cost constraints before adopting a change as an improvement. Monitoring can identify repeated repair loops, high recorded overhead or insufficient later evidence and suggest a bounded change. It cannot establish causal learning benefit, silently omit reviews or decide an acceptable retention loss. The evaluation contract below remains necessary for those claims. Implementation and actual monitoring remain unauthorized.

## How to tell whether it is better

Use FSRS with equivalent direct-recall content as a baseline. When evaluating relationships, structures, or procedures, also compare against a simple schedule with equivalent exercise formats. Changing both the content and the scheduling policy confounds the comparison. Report results by knowledge type and subject; one successful example does not validate every subject.

For a personal pilot, use matched topic or incident families, counterbalance assignments where possible, and hold out variants assessed after predeclared delays. A 7- and 28-day check is a reasonable proposed starting design, not a universal interval. Use separate assessment subsets across delays: the earlier assessment itself is practice. Learning carries over, so do not pretend an A/B crossover can reset a person's knowledge; keep families with shared prerequisites in the same condition, report contamination and outside-work exposure, and treat N=1 as feasibility evidence.

Record unassisted task success, explanation/rubric results, critical errors, help needed, and total learner time separately. Time includes diagnosis, practice, setup, feedback, failed attempts and assessments; also report authoring/maintenance time separately. Use speed as a fluency measure only after acceptable correctness. Do not collapse these into a weighted score.

Agree on an acceptable retained-performance floor or noninferiority margin before observing the result. If the user will not accept any predefined degradation, report the time/performance trade-off instead of declaring a winner. Reserve audit probes from supposedly covered components, since observing only selected exercises would hide false deferrals. Log candidate sets and selection reasons; if randomization is used later, log its probabilities. Do not infer causal policy value from biased historical logs alone.

Stop or revise the hypothesis when grading cannot distinguish independent use from hints, authoring overhead exceeds saved practice time, inferred coverage repeatedly fails delayed checks, or the adaptive policy does not improve the agreed outcome over the simple baseline. Predictive AUC, tidy graphs, and eight synthetic traces cannot substitute for this decision.

## Still for the user to decide

The product scope and interface are settled: general memorization-oriented learning delivered as a web application. Material entry, assessment rules and the local single-learner reference scope are fixed in Design Baseline 1. Implementation setup still chooses actual runtime/browser support and authorized model configuration. Session duration is a learner choice; fresh evaluation examples and acceptable loss when saving review time belong to later qualification/experiments. No Kubernetes pilot or mandatory hands-on workflow is assumed.

The [representation and adaptive-granularity decision](issues/10-knowledge-representation.md) has a [concrete proposal](representation-design.md) and an executable continuation. [Learner estimates and uncertainty](issues/11-learner-inference.md) has a [qualitative baseline and deferred model validation plan](inference-design.md), supported by research and a numerical assumption probe. [Exercise selection and compression](issues/12-adaptive-review-selection.md) has a [baseline policy and earlier executable comparison](selection-design.md). The [material-to-practice workflow](issues/09-learning-workflow.md) has a [concrete proposal](material-workflow.md) and an executable source-to-practice continuation. The [first-build plan](first-build-plan.md) now consolidates them into the finalized implementation sequence for the web application. Its first proposed slice is one saved learning encounter; starting it requires explicit implementation authorization, and live model integration requires authorized model setup. Current work remains design and planning. Broad model and empirical validation questions remain open; writing the plan does not settle them.
