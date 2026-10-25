# How should the system represent details, relationships, and larger knowledge structures?

Type: grilling
Label: wayfinder:grilling
Status: open
Mode: HITL
Assignee: unassigned
Parent: ../map.md
Blocked by: 08

## Question

Define assessable knowledge components, typed relationships, reasoning chains and groups. Separate the content graph from learner state and exercise coverage. Decide how an exercise spans several targets and how review granularity changes with familiarity or failure while preserving diagnostic detail. Include fact recall, relational retrieval, reconstruction and derivation in more than one subject. Distinguish readily recalled knowledge from a correct result reconstructed slowly.

## Comments

The user's failure-diagnosis requirement makes exercise-to-component mapping necessary: specify which assessment criteria can reveal each component or connection and preserve enough detail to return from a failed large exercise to focused practice. Include integration as an assessable target; knowing the parts does not establish the ability to combine them. [Diagnosis design](../spec.md#diagnose-failure-before-choosing-reinforcement).

Transcript anchors: lines 204–316, 380–552, 658–701, and 982–1008. Existing records are a draft, not a settled representation. The question is precise enough to investigate now rather than remain unspecified.

Context: [conversation coverage audit](../research/provenance.md#conversation-coverage-audit).

The [comprehensive retrieval](../research/conversation-retrieval.md) distinguishes recalling a relation, reconstructing why it holds, deriving a new consequence, and choosing it from situational cues. Include applicability conditions, contrasts, shared generalizations, and constraints across several relations. Decide which targets need fluent retrieval versus acceptable reconstruction. Preserve these assessment distinctions without assuming each needs a separate fitted state variable.

The [two-subject diagnosis prototype](13-diagnosis-prototype.md) now makes a six-target representation concrete in binary search and English grammar. It includes components, relationship, selection, and integration criteria. These are authored examples for discussion, not validated universal granularity.

The [independent annotation comparison](../spikes/independent-assessment/review.md) adds concrete representation questions. A linguistic facet such as ownership of the finger in a thermometer answer need not become its own memorization target. Conversely, credit for material moving cannot automatically establish the separately requested wearing-away relationship. Preserve evidence at useful diagnostic granularity while allowing one coherent exercise to address connected targets. These are design implications from selected examples, not a validated universal representation; three of four selected circuit facets were excluded as `Assumed`, so that comparison does not validate complete circuit explanations.

## Proposed representation, 2026-10-14

The user authorized continuing this design question after the clarification-before-practice change. The [representation proposal](../representation-design.md) now supplies useful-unit criteria, distinctions between capabilities and rubric criteria, semantic groups versus temporary practice bundles, and worked contrasts across operations, mathematics, grammar, science, and simple facts. It preserves applicability, reconstruction versus fluency, joint constraints, shared principles, overlapping coverage, and refinement of content over time.

The live prototype provides a specific reason to refine the model: `ops.list` and `ops.logs` combine choosing evidence with producing a command, although recorded answers can distinguish those performances. Its singular `group` field selects a future exercise; it is not a semantic knowledge-group model. The proposal explicitly preserves old IDs, assessments, and rubric meaning; no historical grades were split or new learning outcomes inferred.

The bounded deliverable is a source-checked design and counterexample walkthrough. No runtime code or frozen assessment changed. The broad HITL decision stays open pending the user's response to this representation. The next implementation slice is described in the proposal; inference policies, compression thresholds, delayed validation, and the content-entry workflow remain separate open questions.

## Executable continuation, 2026-10-14

The user authorized making the proposed distinctions executable in the existing prototype. The [walkthrough](../spikes/representation/index.html) and [implementation notes](../spikes/representation/README.md) now exercise goal-selected capabilities, explicit version-bound criterion mappings, scoped observations, and focused or combined practice through the existing validator, bridge, and planner. Operations distinguishes evidence choice from command production; mathematics distinguishes component reasoning from integration; a simple fact uses one target. The new examples are authored, not reassessments of the user.

The initial replay exposed the old one-criterion/one-target restriction. The current replay passes 40 checks, including shared evidence, partial answers, hints, clarification, alternate paths, overlapping bundles, retained-record snapshots, and version changes. The existing 84 behavior/CLI checks also pass. The prior accepted plan and frozen independent assessments retain their original judgments; the new mappings do not migrate their grades. Browser rendering and learning outcomes remain unverified.

This establishes the bounded representation path, not universal component granularity or optimal practice selection. The broad HITL question remains open to user reaction and fresh learner evidence. The next useful validation concerns the correctness of judgments and practice choices on new answers, rather than additional representation infrastructure.
