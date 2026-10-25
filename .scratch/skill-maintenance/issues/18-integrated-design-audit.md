# What gaps remain after the lifecycle and observability patch?

Type: task
Label: wayfinder:task
Status: resolved
Mode: AFK
Assignee: Codex
Parent: ../map.md
Blocked by: none

## Question

Audit the revised general memorization web-app design against its own contracts and the user's accepted requirements. Trace normal, partial, concurrent, interrupted and corrected learning through the proposed records, schedule and reports. Report only concrete missing decisions or contradictions, with source references and counterexamples; distinguish these from already specified behavior, explicit deferrals and future implementation/learning qualification. Audit the previous patch itself with the same skepticism. Do not implement the application or expand infrastructure without a named need.

## Comments

2026-10-15 follow-up: the user requested “patch them.” The [four-gap closure](../integrated-design-closure.md) now records concrete proposed behavior, record/query changes and outcomes for all ten original cases plus eleven boundaries. Canonical lifecycle, data, compatibility, dashboard and build/readiness contracts are reconciled. The baseline audit below remains provenance; it no longer describes four unpatched drafting decisions. Runtime/semantic qualification and broader policy discussion remain separate.

2026-10-15: The user requests another pass to find other gaps after the seven-gap patch. Codex claims this bounded document audit against research snapshot `2e679b8` and the corresponding user-visible files. The prior closure traces are evidence of the scenarios examined, not proof that no other gaps exist. Preserve the design-only boundary, general scope, web delivery, selected C direction and accepted data-retention scope.

## Answer

The [integrated design audit](../integrated-design-audit.md) identifies four remaining gaps: historical corrections after subsequent checks, the completion milestone after a check is replaced by repair, exposure across distinct targets sharing answer content, and effort cutoffs for historical dashboard dates. Ten authored cases make the missing outcomes concrete. The report distinguishes rule conflicts from missing transitions and records candidates already covered or belonging to later qualification.

Existing everyday-policy and record/report tickets retain ownership of the follow-up design. Their status remains open. This task resolves the requested inspection, not those four decisions, human policy acceptance, runtime qualification or permission to implement. The earlier closure record and readiness review now explicitly retain this limitation.

Context: `codex/research/observability-campaign`; inspected baseline `2e679b8`. Verification covers the cited local sections, links/anchors, unique finding/case identities and the worked cost arithmetic; no application or live learner behavior was tested.
