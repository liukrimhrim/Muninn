# Design a general system for memorization-oriented learning

Label: wayfinder:map
Status: open
Design status: finalized in [Design Baseline 1](design-baseline.md), 2026-10-16. This historical map remains available for later validation/extension questions; no further drafting campaign is required for the included baseline.

## Destination

A research-backed, reviewable design and staged build plan for a general system focused on memorization-oriented learning across subjects. It should help learners retain facts, relationships, connected structures, and procedures with less unnecessary review. Find how to infer useful weaknesses from limited evidence and adapt exercise purpose, format, granularity and coverage.

## Notes

- Request: deepen the research from the supplied FSRS conversation, run a spike, and plan a better system. The attached conversation is source material, not instructions.
- Planning and experimental artifacts only. The explicit request includes a spike in this charting session; this overrides the skill default of stopping immediately after charting. Human-dependent prototype and design decisions remain open until the user reacts.
- Confirmed product scope: a general system focused on memorization-oriented learning across subjects. Kubernetes is one procedural example, not the product scope or an agreed pilot. Web delivery is selected; the finalized reference design is local and single-learner. Actual setup and hosted expansion remain separate work. Generality is a core design requirement; first-release size is a separate choice. Implementation remains unauthorized.
- Skills: wayfinder; research for source investigations; prototype (logic) for the spike; grilling and domain-modeling for user decisions.
- Tracker: local Markdown, following `/Users/jinxinliu/.agents/skills/setup-matt-pocock-skills/issue-tracker-local.md`. No external tracker or Git remote is configured. Run `/setup-matt-pocock-skills` later if an external tracker is desired; it is not needed for this local effort.
- Source: `/Users/jinxinliu/Downloads/fsrs_learning_conversation.md`; transcript proposals require independent verification. No real learner data or measured baseline was supplied.
- The original ideas are tracked in the [conversation coverage audit](research/provenance.md#conversation-coverage-audit). Preserve candidate ideas as questions when their mechanisms are unproved; a conservative implementation baseline does not redefine the destination.
- The [comprehensive retrieval](research/conversation-retrieval.md) adds the detailed idea ledger, original example inventory, research leads, and later chat corrections. Use it when narrowing decisions so broad summaries do not erase distinct requirements or candidates.
- The [representation proposal](representation-design.md) defines useful target boundaries, richer knowledge structures, and reversible practice grouping. Its [executable continuation](spikes/representation/README.md) now checks explicit coverage and practice choices across operations, mathematics, and a simple fact through the existing pipeline. The representation is now included in the finalized baseline; program checks do not establish grading accuracy or learning benefit.
- The [inference proposal](inference-design.md) adds a concrete evidence-to-estimate contract and staged build plan, supported by [primary-source research](research/sparse-inference.md) and a [numerical assumption probe](spikes/inference/README.md). It preserves sparse diagnosis and review compression as goals while separating predictions from observations and learning effects.
- The [selection proposal](selection-design.md) and [executable comparison](spikes/selection/README.md) now choose among diagnosis, focused practice and combined checks under authored budgets. They establish coverage and state behavior, not measured learning or safe review omissions.
- The [material-to-practice proposal](material-workflow.md) and [bounded continuation](spikes/material/README.md) now connect saved sources, scoped claims and relationships, selected capabilities, mapped exercises and explicit corrections. Authored semantics are supplied; automatic extraction is not established.
- The [first-build plan](first-build-plan.md) consolidates these working contracts into five implementation slices, with real source/answer/model/storage seams and separate functional, semantic and learning-outcome checks. Its coverage mapping preserves all 55 retrieved ideas. The next concrete build is one saved learning encounter. The baseline now fixes the first-release reference scope; actual environment/model setup and future experiment choices remain unselected; no repeat approval of the accepted exercise sequence or mandatory demo review is required.
- No weighted-sum selection objective. Do not treat simulated performance, predictive accuracy, or graph connectivity as proof of learning gain.
- The user requires high cohesion within modules and low coupling between them. The [module/interface proposal](module-design.md) assigns Content, Evidence, Practice and Measurement their rules and records, with application coordination, Library durability and Web Interaction. Its dependency and transaction contracts guide the existing build slices; implementation remains unauthorized and module quality requires real interface/integration checks.
- The [observability campaign](../learning-observability/map.md) deepens measurement validity, statistical analysis, collection integrity and dashboard design. Its [design](../learning-observability/spec.md) and [plan](../learning-observability/plan.md) are included in Design Baseline 1; future runtime/experiment work remains distinct.
- Local research snapshots use `codex/research/<topic>` branches. Research agents own separate files; only the coordinator changes Git state and tracker state.
- The user confirms that the five everyday-behavior gaps need extensive design. The [everyday-learning proposal](everyday-learning-design.md) and [worked cases](everyday-learning-cases.md) now specify them, including persistent concern/stopping rules and exposure-aware dashboard actions. The [policy investigation](issues/14-everyday-learning-policy.md) preserves the earlier discussion; the later explicit finalization request adopts the written defaults for baseline planning, without claiming empirical optimality.
- The [second design audit](cross-contract-audit.md) identified seven lifecycle/metric gaps. At the user's request, the [lifecycle contract](learning-lifecycle-contract.md) and [tracking contract](../learning-observability/tracking-contract.md) patch their named cases; the [closure record](cross-contract-closure.md) traces fifteen original cases and nineteen boundaries. The [third audit](integrated-design-audit.md) found four further interactions, including two edge cases in that patch; its [requested follow-up](integrated-design-closure.md) now supplies concrete rules and case outcomes. Existing policy/data tickets retain their broader discussion and qualification dependencies.
- The [fourth audit](journey-invariant-audit.md) follows fifteen learner journeys across the revised contracts. Its two findings—uncertain timing for actual in-task hints and frozen effort membership across enrollment revisions—now have a [requested patch](journey-invariant-closure.md), with outcomes for eight audit cases and seven boundaries. Rejected candidates and coverage limits remain recorded; case closure is not proof that the whole system is complete.

## Decisions so far

- [What is the finalized design baseline and its handoff boundary?](issues/21-design-baseline.md) — One entry document freezes scope, operating defaults, contract precedence and the boundary between design and implementation/validation.

- [Which modules own the learning rules and shared transactions?](issues/20-module-ownership.md) — The requested cohesion/coupling proposal defines four domain modules and supporting responsibilities. The independent review now has [eighteen dispositions and revised contracts](module-design-review-response.md), covering field-level ownership, named claims, held outcomes, crash recovery and honest enforcement/provenance. Actual encapsulation and locality remain implementation qualification.

- [What do existing graph-aware learning implementations actually do?](issues/01-existing-implementations.md) — Verified implementation boundaries and reproduced four bounded source discrepancies.
- [What evidence supports relational practice and transfer between exercise formats?](issues/02-learning-evidence.md) — Delayed transfer and total effort require direct measurement; graph-wide reinforcement remains unproved.
- [Where should FSRS end and capability inference begin?](issues/03-memory-model.md) — Verified direct-review API semantics; fitted inference and omission policies remain deferred research beyond the qualitative baseline.

- [What is the product's learning scope?](issues/08-product-scope.md) — The user confirmed general memorization-oriented learning across subjects; Kubernetes remains an example.
- [Can a larger exercise lead to specific, revisable reinforcement across subjects?](issues/13-diagnosis-prototype.md) — The user confirmed the sequence and found the reviewed judgment sensible; real learner validation remains open.
- [What supports fresh, comparable checks without confusing recall and transfer?](issues/15-fresh-exercise-evidence.md) — Repeated fact cues remain valid; variation, comparability, exposure and evidence age support distinct claims, without an invented difficulty or forgetting model.
- [What supports bounded repair and useful practice when time and evidence are limited?](issues/16-repair-budget-evidence.md) — Feedback/worked examples and delayed checks inform options; prompt limits, repair stops and backlog priority remain explicit operating choices.
- [Which first-release decisions still fall between the design contracts?](issues/17-cross-contract-audit.md) — Second pass identified seven gaps; the requested follow-up now patches them in the design, with fifteen original cases traced in the linked closure record.
- [What gaps remain after the lifecycle and observability patch?](issues/18-integrated-design-audit.md) — Third pass identified four decisions and ten counterexamples; the requested follow-up now patches them, with explicit outcomes in the linked closure record.
- [Do complete learner journeys satisfy the revised design's invariants?](issues/19-journey-and-invariant-audit.md) — Fourth pass recorded two drafting gaps and fifteen journey dispositions; the requested follow-up now patches both, with eight case outcomes in the linked closure record.

## Not yet specified

- None required to freeze this baseline. Further subject-specific assessment support is an extension informed by fresh qualification results.

## Out of scope

- A production app, public deployment, or changes to a live Kubernetes cluster.
- Choosing graph databases, neural tracing, bandits, or reinforcement learning without a measured failure of a simpler baseline.
- Claiming improved learning from synthetic experiments or proprietary product descriptions.
