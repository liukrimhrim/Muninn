# Make learning progress and efficiency observable

Label: wayfinder:map
Status: open
Design status: finalized in [Design Baseline 1](../skill-maintenance/design-baseline.md), 2026-10-16. Open historical child metadata retains later qualification and experiment questions; it is not a request to restart design review.

## Destination

A research-backed observability design and staged plan for the general memorization-learning web app: defensible progress metrics, explicit statistical methods and limits, trustworthy collection, and concrete learner/analysis dashboard designs. Completion requires traceable decisions and inspectable spikes; it does not require or authorize a production app or a learner experiment.

## Notes

- Confirmed purposes: help the learner see meaningful progress and discover whether learning outcomes justify the entire effort spent. Scope spans subjects, facts, relations, integrated explanations and procedures; Kubernetes is an example.
- Existing [observability proposal](../skill-maintenance/observability-design.md), [compatibility design](../skill-maintenance/compatibility-design.md), [system design](../skill-maintenance/spec.md), [build plan](../skill-maintenance/first-build-plan.md) and [conversation retrieval](../skill-maintenance/research/conversation-retrieval.md) are inputs, not evidence of empirical validity.
- The user's explicit request includes research, brainstorming and spikes in this campaign. It overrides stopping immediately after charting: prepare bounded numerical and UI prototypes, clearly marked synthetic, while leaving human-dependent decisions open. Do not stand in for the learner's judgments or claim the design is complete because files exist.
- Skills: wayfinder; research for the source investigations; prototype for numerical behavior and dashboard alternatives; grilling and domain-modeling for unresolved user choices. Existing user answers settle the destination; do not re-interview about general scope, the two observability purposes or web delivery.
- Tracker: local Markdown following `/Users/jinxinliu/.agents/skills/setup-matt-pocock-skills/issue-tracker-local.md`. Read child metadata for the live frontier. Only the coordinator changes tracker/Git state; research agents own separate reports. Capture artifacts on `codex/research/observability-campaign` with the required saved design inputs in a separate checkout; preserve the original checkout's existing uncommitted edits.
- No universal mastery or weighted efficiency score. Distinguish observation, estimate, causal effect and user preference. Missing checks are not failure, assistance is scoped, corrections do not create new learning, and facets of one answer are not independent trials.
- A small first release and a sophisticated long-term design are separate questions. Every proposed method must name the decision or known failure it addresses, its data requirements, its assumptions, its simpler fallback and a condition for withholding a conclusion.
- Do not select a real pilot's retention-loss tolerance, burden budget or experimental assignment on the user's behalf. Do not transmit private learner material, start monitoring, or modify production scheduling.
- The [readiness review](readiness-review.md) records the finalized descriptive scope and distinguishes runtime measurement qualification from future optimization. The deletion release-scope decision is recorded below; selective-erasure details remain future proposals.
- The [everyday-learning design](../skill-maintenance/everyday-learning-design.md) develops evidence age, the proposed successor shortlist and progress-to-practice actions alongside session/repair rules. Its [policy investigation](../skill-maintenance/issues/14-everyday-learning-policy.md) preserves drafting history; the final baseline adopts the written first-release defaults and resolves that design dependency. The current C prototype remains version 1.

## Decisions so far

- [What is the finalized design baseline and its handoff boundary?](../skill-maintenance/issues/21-design-baseline.md) — The shared baseline adopts descriptive claims, analytical C, record/tracking contracts and their qualification gates; future causal optimization remains deferred.

- [What evidence makes a learning-progress measure valid?](issues/01-measurement-validity.md) — Use claim-specific validity arguments, independent assessor reference review and separate acquisition, maintenance, retention, transfer and fluency interpretations.
- [Which statistical methods can support a sparse personal learning history?](issues/02-statistical-methods.md) — Separate exact descriptive history, prospective prediction audit and randomized policy comparison.
- [Which dashboard designs support understanding and useful action?](issues/03-dashboard-evidence.md) — Research supports testing a daily briefing, capability notebook and occasional investigation workspace, with direct counts, evidence and missingness.
- [How can measurement stay trustworthy through interruptions and revisions?](issues/04-collection-integrity.md) — Specify timer ownership/clock provenance and separate duration from placement.
- [How should the learner explore progress, effort and uncertainty?](issues/06-dashboard-spike.md) — User prefers analytical C as the default; retain A for quick orientation and B for capability detail. Comprehension remains unverified.
- [How should intentional deletion affect learning history and saved reports?](issues/11-deletion-contract.md#answer) — User accepts archive plus whole-library deletion initially; individual answer/source erasure is deferred.

## Not yet specified

- None required for this baseline. Subject-specific validity, interaction changes from real usability checks and a concrete optimization experiment belong to later qualification or explicit extensions.

## Out of scope

- Production app implementation, deployment, external analytics setup, live telemetry collection and automatic policy optimization.
- Claims of improved retention, motivational benefit or measured learner time savings from authored data.
- Population rankings, clinical assessments, a universal mastery score, or infrastructure chosen without a named need.
- Selective permanent deletion and detailed redacted-format work for the first release, per the [accepted deletion scope](issues/11-deletion-contract.md#answer). Future requirements remain recorded, not implemented or declared resolved.
