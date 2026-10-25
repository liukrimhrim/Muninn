# Do complete learner journeys satisfy the revised design's invariants?

Type: task
Label: wayfinder:task
Status: resolved
Mode: AFK
Assignee: Codex
Parent: ../map.md
Blocked by: none

## Question

Audit the general memorization web-app proposal at research baseline `a11431b`, including the latest four-gap patch. Trace complete learner journeys across authoring, delivery, assessment, repair, review, correction, reporting and preserved history. Check that promised actions are reachable, saved records can express them, and reports use consistent evidence. Record coverage and explicit counterexamples for actual contradictions or missing decisions; reject already-covered cases and known implementation/empirical dependencies. Do not force a finding count, introduce infrastructure, patch policy during the audit or implement the app.

## Comments

2026-10-15: The user notes that every round has found new gaps and asks for another pass. Codex claims this bounded journey/invariant audit. Earlier per-case closure is evidence for the cases checked, not a complete system proof. The design-only boundary and previously accepted scope/preferences remain in force. Keep the diagnosis of our own design and audit method subject to the same source checks.

## Answer

The [fourth audit](../journey-invariant-audit.md) records fifteen journey dispositions and two remaining design gaps: nested assistance still requires an exact display timestamp despite the uncertain-time contract, and frozen effort scope has no membership rule across later enrollment revisions. Eight closure/qualification cases make the required behavior concrete. Suspected conflicts already covered by other rules are explicitly excluded from the finding count.

The inspection is complete. The user subsequently requested the [two-gap patch](../journey-invariant-closure.md), which now reconciles the canonical contracts and supplies all eight case outcomes plus seven boundaries. The existing record/report ticket retains its broader policy and qualification dependencies. Verification is source inspection, baseline comparison, document references and authored arithmetic, not execution of the application. No new learner review, infrastructure or production implementation was required. Context: `codex/research/observability-campaign`, inspected baseline `a11431b`.
