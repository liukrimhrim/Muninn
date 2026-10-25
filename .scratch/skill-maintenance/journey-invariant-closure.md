# Known help and continuous effort: design patch and verification

Status: proposed design patch, 2026-10-15, requested by “patch them.” This closes the two named drafting gaps in the [fourth audit](journey-invariant-audit.md). It does not assert that the entire design is complete, implemented, empirically effective or that every proposed policy is user-approved. The audit remains provenance for baseline `a11431b`; this patch continues from snapshot `2c78d6c`.

## Decisions and rationale

| Finding | Rule and canonical owner | Rationale and alternatives |
|---|---|---|
| G01 Known help, uncertain display time | [assistance-evidence-1](../learning-observability/data-contract.md#known-assistance-with-uncertain-time), with the exact nested type in [compatibility](compatibility-design.md#3-portable-logical-records) | Keep the help fact and its clock quality separate. Requiring a fabricated timestamp or deleting the hint loses evidence. An exposure record supplements a captured hint; it does not replace the in-attempt fact. Use the existing time-evidence shape and current exposure/correction path |
| G02 Curriculum effort across revisions | [cost-membership-1](../learning-observability/data-contract.md#frozen-cost-membership-across-revisions) | Routine tracking follows explicit enrollment identities within the frozen time window, while its outcome targets remain exact and fixed. Exact-enrollment-revision equality loses later work; arbitrary graph traversal pulls in unrelated work. Explicit target/source scopes remain available as narrower, separately labelled views |

No new service, storage family, scoring model or app code is required by these changes. They refine the existing records, collection contract and deterministic report query.

## A known hint with no reliable clock

This is an authored nested `Assistance` value, not a real learner record or an executed importer result. Its criterion ID must belong to the bound exercise in a real record. It represents an acknowledged hint during the answer, with no trustworthy display timestamp:

```json
{
  "shown_at": null,
  "time_evidence": [{
    "field": "shown_at",
    "precision": "unknown",
    "earliest_at": null,
    "latest_at": null,
    "basis": "unavailable",
    "raw_client_at": null,
    "explanation": "Hint display was acknowledged before submission in this attempt; no reliable display time was available."
  }],
  "text": "Use the relationship between the two quantities.",
  "criterion_ids": ["A"],
  "study": null
}
```

The saved observation for A can be assisted even though `shown_at` is null. A usable correct judgment remains correct and helped (H/QH), with date uncertainty disclosed separately. It cannot resolve an independent-recovery need or advance the affected independent-check obligation. Unusable grading remains U/QU with a help annotation. B's separate unexposed requirement can still supply independent evidence when its own conditions are satisfied.

The actual assistance array is append-only through drafts and frozen at submission. Later evidence is linked through exposure/correction; the exact attempt revision and assistance index identify the old entry. A hint and a linked exposure are one underlying reveal, while two actual presentations remain two occurrences. External aids qualify the answer without creating a fictitious local hint. Historical report definitions and results remain immutable.

## All eight audit cases

These are authored **design traces**. Each row now has a specified representation and result. Real save/import, browser capture, assessment, scheduling and report execution remain later qualification work.

| Case | Trace through the patch | Concrete result |
|---|---|---|
| W01 Known hint, unknown time | Save the nested value above in the bound attempt; accept the answer with its own supported time evidence | Preserve the help, text and criterion scope with null display time. Usable target judgment is H/QH. Save/import/replay must retain that distinction without inventing a timestamp |
| W02 Bounded hint time | Set precision to bounded, retain supported lower/upper instants and their clock or self-report basis, keep `shown_at: null` | Neither endpoint nor midpoint becomes the display instant. Group only where all possible times fit; subsequent minimum-delay decisions still require supported availability/end information, not merely the opening bound |
| W03 Scoped larger answer | A received the hint; B did not. The attempt's own time/other conditions are sufficient for B | A is helped; B can be independently demonstrated. Unknown hint time does not contaminate B automatically. Whole-target independence is withheld only where a required criterion is affected |
| W04 Help in another screen | Local assistance list is empty and local assisted flag is false; a checked relevant answer view was known available during response production | Combined qualification gives H/QH for the affected target. Keep local hint history empty, preserve exposure refs, and block independent advancement. Unknown availability instead preserves raw judgment with uncertain qualification |
| W05 Same goals, new enrollment revision | Scope root E@1; effective spans are 20m against E@1 and disjoint 30m against E@2 after a checkpoint; both lie in the effective interval | `cost-membership-1` matches E's identity: **50m**. Scope proof retains root E@1, actual span refs and E@2 attribution; no latest-ref rebinding |
| W06 Goals change | Freeze outcome target A and enrollment root E@1. E@2 adds B; E@3 removes A. Work is 20m on A plus disjoint 30m on B, explicitly attributed to E | Curriculum cost is **50m**. Outcome population remains **one target, A**; B is listed as added outside that comparison, and unavailable A checks retain their missingness. Removed/paused status does not erase actual work |
| W07 Shared work | E-only span 20m; one 30m span explicitly attributed to E and F | E view **50m**, F view **30m**, combined view **50m**, not 80m. An F-only span is outside E even if their curricula share a target; no arbitrary cost split |
| W08 Corrected attribution and replay | At S1 both W05 spans belong to E; report R1 saves 50m. At S2 a supported correction changes only the 30m span's attribution to F | New E report R2 is **20m** with the attribution-change reason; R1 stays **50m**. Original span time, exact revisions, both saved definitions and scope proofs survive restore. A correction's receipt date does not become the effort date |

## Additional boundaries checked

| Case | Required consequence |
|---|---|
| B01 Invalid or unknown hint time | Non-null `shown_at` with unknown/bounded precision fails validation. Unavailable/legacy-unknown timing basis cannot carry invented bounds. Preserve raw anomalous clocks as raw evidence; a captured hint is not discarded to make validation pass |
| B02 Uncertain display versus known display | A reservation/request without a display acknowledgement is uncertain exposure, not a known assistance entry. Feedback after submission is not retroactive help. No null timestamp alone can distinguish these facts |
| B03 Several hints in one attempt | Entry indices identify separate preserved presentations. A linked exposure with `related_assistance_index` names one existing entry; a whole-answer retrieval has null index. The checked answer's own-retrieval exclusion cannot accidentally exclude its hints |
| B04 Inherited versus ambiguous scope | A span with no explicit enrollment inherits its exact single-enrollment session. A multi-enrollment session without explicit attribution supplies uncertain candidates, not fabricated known sharing. Explicit span context takes precedence |
| B05 New enrollment and narrow roots | A new enrollment ID with the same curriculum/title does not match E. Exact target/source roots do not follow later revisions or semantic mappings; narrower views disclose excluded/uncertain overhead. An explicitly selected library ledger uses library mode and no roots; empty roots in a scoped comparison are invalid, never an implicit expansion to the whole library |
| B06 Scope does not override time or quality | In-scope future, unplaced, stale or disputed work still follows existing cutoffs/quality rules; explicit pauses do not become effort. Adding reliable F-only 10m to W07 gives E=50m, F=40m, combined=60m, not 90m |
| B07 Frozen definitions and old reports | A plan cannot edit roots or membership algorithm after outcomes. A supported attribution correction changes evidence under the same rule, not the scope. Older reports without this rule retain their definitions or explicit replay-unavailable status; no silent upgrade |

## Integration and verification

The base compatibility type and validator now agree with the time-evidence addendum. The lifecycle and tracking contracts use the combined assistance/exposure conditions. The base cohort shape, tracking freeze, report query/manifest, cost result, collection context and dashboard wording all name the same cost-membership rule. The two build plans carry W01–W08 and these boundaries into the existing persistence, correction, reporting and restore work.

The [record/report investigation](../learning-observability/issues/09-data-contract.md) retains its broader metric-policy and actual qualification dependencies. This patch completes its two requested drafting gaps and releases the drafting claim; it does not close the whole investigation or require another learner exercise.

Verification: inspect the canonical declarations and their consumers; parse the authored hint value and check its precision/null constraints; verify local links/anchors and unique case IDs; independently calculate the 50/30/50, 50/40/60 and corrected 20-minute examples; inspect the scoped document diff. These checks establish document consistency and arithmetic only. They do not establish collection accuracy, atomic replay, model quality or learning benefit in a running application.
