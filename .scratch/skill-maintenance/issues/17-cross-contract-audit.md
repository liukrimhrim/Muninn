# Which first-release decisions still fall between the design contracts?

Type: task
Label: wayfinder:task
Status: resolved
Mode: AFK
Assignee: Codex
Parent: ../map.md
Blocked by: none

## Question

Audit the current design end to end after the everyday-learning continuation. Identify demonstrable contradictions, missing lifecycle transitions and unspecified first-release decisions an implementer would have to invent. Cite the actual documents and a concrete counterexample for each finding. Distinguish genuine missing design from already specified behavior, explicit deferrals, implementation choices and post-build validation. Record bounded recommendations and acceptance cases without implying user acceptance or starting production implementation.

## Comments

2026-10-15 follow-up: the user requested “patch those gaps.” The [closure record](../cross-contract-closure.md) links concrete proposed resolutions for all seven findings and checks all fifteen original cases. Main lifecycle, record, metric and build documents are reconciled. The original audit answer remains below as provenance; its then-unresolved integration work is now patched in the design. This does not change the meaning of audit resolution or claim runtime/learning validation.

2026-10-15: The user requests another pass to find missed details. This is a source audit of the existing design, not a request for another broad research campaign or new infrastructure. Preserve previous accepted scope and the design-only boundary. One audit ticket owns this pass; policy decisions remain in the existing everyday-learning and observability tickets.

## Answer

The [second-pass audit](../cross-contract-audit.md) identifies seven source-grounded gaps: initial independent-success scheduling; selected versus admitted learning; teaching/variant generation contracts; distinct competing attempts and late assessments; exposure timing and unknown-time recovery; prospective comparison-plan creation; and raw-versus-qualified metric aggregation. Fifteen counterexamples make the missing decisions concrete. The audit also records areas already specified or deliberately deferred, so they are not counted as new omissions.

The build-plan draft now includes the initial-success transition and separate initial error/unknown behavior. The everyday contract ties exposure eligibility to answer production/submission, preserving post-answer feedback as later exposure. These are proposed clarifications, not a production implementation or acceptance of an optimal interval. Remaining integration is assigned to existing policy/metric/data work, and the readiness review records it explicitly.

Verified the cited local sections, 107 local link targets, three new audit anchors, the seven finding IDs, fifteen case IDs and worked outcome arithmetic. No runtime, model-quality or learning-effect result is claimed. Audit resolution means the requested inspection is complete; it does not resolve the design choices it found. Context: `codex/research/observability-campaign`; baseline inspected at `8b744fb`.
