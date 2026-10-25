# How should intentional deletion affect learning history and saved reports?

Type: grilling
Label: wayfinder:grilling
Status: resolved
Mode: HITL
Assignee: /root
Parent: ../map.md
Blocked by: 04

## Question

Define the user-facing meaning of whole-library deletion and selective source/answer redaction before claiming either is supported. Which copies and backups are affected, which retained reports become nonreproducible, and how is intentional deletion distinguished from silent migration loss? Preserve the existing progress-survival promise without interpreting append-only history as a ban on deliberate deletion. Prepare a concrete recommendation; perform no deletion and add no retention service.

## Comments

2026-10-15: User authorizes preparing the deletion/report-retention recommendation and consolidating remaining design decisions. This is a design claim only; no deletion, implementation or external action is authorized. Record recommendations separately from accepted user choices.

Surfaced by [collection-integrity research](../research/collection-integrity.md#quality-privacy-and-retention). This is a design boundary, not evidence of a production privacy incident.

2026-10-15: [Removing material without misleading the learner](../deletion-design.md) now specifies archive versus curriculum revision versus permanent deletion, managed/external copy boundaries, confirmation scope, interrupted cleanup, backup/restore behavior, affected reports and fourteen future acceptance cases. It recommends archive plus whole-library deletion initially, with selective erasure gated on an explicit portable-format design. The scoped format question is now precise: represent intentionally erased records/receipts without retaining deleted information, resetting unrelated progress, accepting corruption or claiming unchanged old-prefix replay.

The first-release scope preference was asked explicitly: archive plus whole-library deletion, or individual answer/source deletion too. No answer has been recorded as of this drafting pass. Recommendations remain proposals; no user choice, deletion or implementation approval is inferred.

The [readiness consolidation](../readiness-review.md) separates ordinary measurement readiness from future policy experiments. Links, case numbering and tracker dependency targets were checked, and SQLite storage caveats were verified against linked official documentation. No deletion, browser cleanup, physical erasure or runtime acceptance test was performed. Preparation claim released; this human-dependent decision remains open.

## Answer

2026-10-15: the user replies “your recommendation makes sense” to the explicit first-release choice. Resolve that scope as **archive plus whole-library deletion**, with permanent deletion of individual answers/sources deferred. Archive preserves curriculum history and progress. Whole-library deletion uses the documented explicit impact confirmation and managed-copy scope; it is not an upgrade, a curriculum edit or an automatic cleanup action.

The [deletion design](../deletion-design.md) contains the workflow, backup/copy limits and future acceptance cases. Detailed selective-erasure semantics and its portable representation remain future proposals, outside this first-release decision; they are not claimed complete or accepted. No implementation, actual deletion, external operation or runtime qualification is authorized or reported. The decision is resolved within the agreed release scope, not the whole observability campaign.
