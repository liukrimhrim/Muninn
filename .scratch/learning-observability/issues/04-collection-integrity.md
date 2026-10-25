# How can measurement stay trustworthy through interruptions and revisions?

Type: research
Label: wayfinder:research
Status: resolved
Mode: AFK
Assignee: /root/obs_collection
Parent: ../map.md
Blocked by: none

## Question

Which browser and storage constraints affect collection of full learner effort and reproducible learning reports? Audit visibility, timing, sleep, crashes, retries, multiple tabs, background model waits, offline/late records, clocks, revisions and exports. Compare minimal local-record approaches with external instrumentation only where a concrete need justifies it. Define measurable quality indicators, collection failure probes and privacy/retention boundaries; do not equate foreground time with attention.

## Comments

Report owner: `../research/collection-integrity.md`. Ground browser claims in standards or official documentation; assess compatibility with the existing append-only logical-record proposal.

## Answer

Specify timer ownership/clock provenance and separate duration from placement. Reports need frozen evaluation time as well as source sequence, exact query manifests and fingerprints. Local versioned records suffice as a proposed foundation; browser behavior and data-contract reconciliation remain unverified. See [the source investigation](../research/collection-integrity.md). Bounded research completed on 2026-10-14; source-access limits are recorded in the report. Research artifacts will be captured on `codex/research/observability-campaign`.
