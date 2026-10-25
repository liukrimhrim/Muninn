# Four remaining interactions: design patch and verification

Status: proposed design patch, 2026-10-15, requested by “patch them.” This closes the four named findings in the [third audit](integrated-design-audit.md) at the document level. It does not claim the entire design is free of gaps, user acceptance of every default, implemented correctness or improved learning. The audit remains as the record of the earlier omissions.

## Decisions and rationale

| Finding | Proposed rule and canonical owner | Why this choice; alternatives not taken |
|---|---|---|
| G01 Descendants after correction | [descendant-correction-1](learning-lifecycle-contract.md#correction-after-later-checks): preserve actual offers/answers and separately recompute their effects; a still-qualifying formerly owned later capability answer can re-establish maintenance | Discarding later genuine evidence creates unnecessary rework; blindly preserving every later due date ignores corrected help/timing. Recheck conditions and retain the original ownership instead of rebinding an answer to another opportunity |
| G02 Completion after repair | [caught-up-1](learning-lifecycle-contract.md#counts-and-milestones): evaluate currently open obligations and unresolved needs in an explicit scope; keep failed/replaced history separate | Requiring every past obligation to succeed prevents recovery; calling a replacement a success falsifies history. A dated current-work indicator preserves both recovery and accountability |
| G03 Shared-answer exposure | [exposure-scope-1](learning-lifecycle-contract.md#shared-content-across-different-targets): checked presented-content-to-requirement relevance, with uncertainty and historical occurrence time retained | Target-ID-only lookup misses reversed directions/shared steps; graph-wide propagation overstates what was revealed and delays unrelated work. Scope judgments are evidence with provenance, not inferred achievement |
| G04 Historical effort | [cost-cutoff-1](../learning-observability/data-contract.md#historical-cost-boundaries): keep the frozen investment window, intersect it with evaluation/selected-check boundaries for each cost display | The entire frozen period can include future effort; changing the frozen window would change the comparison contract. A separate effective interval preserves reproducibility and honest historical views |

These are changes to existing records, replay and report queries. They introduce no new service, cache, queue, latent mastery score or review-optimization engine. Intervals retain the existing capability policy; the patch does not assert they are optimal.

## The ten audit cases

All rows below are authored **design traces**. They specify what an implementation must later demonstrate using the actual store, adapter and UI. The cost arithmetic was also calculated independently; no application path was executed.

| Case | Trace through the patched rule | Concrete result |
|---|---|---|
| I01 Completed descendant | September 30 study → October 1 A success → October 8 B owned success → October 10 correction makes A unusable. A's successor is invalidated; B remains an actual formerly owned qualifying later check | Re-anchor from B; successor due **October 15**. Preserve B/its offer; no new review. The study obligation becomes replaced by later evidence, not passed by A. One effective scheduling effect for B |
| I02 Open descendant | Apply the same ancestor correction before B submits, then separately after B submits but before its assessment | Unsubmitted affected slot loses effective reservation, retains draft, and can continue as extra practice or be replaced by a new bound check. Submitted B remains under a target-scoped hold until graded or explicitly released; valid later success then follows I01, released B never advances. Other target slots continue |
| I03 Repaired workload | A failed due obligation is replaced by completed teaching; a qualifying later independent check succeeds and clears the concern; next check is in the future | Selected active scope can show **Caught up on later checks as of [time]**. Old failure remains historically failed/unsatisfied and replaced, outside the current-open-work test |
| I04 Whole selected scope | Add an unstarted or paused selected goal to I03 | Whole-selected-curriculum indicator is withheld. A separately labelled active subset can be caught up; no removal of goals from its claimed denominator |
| I05 Reverse-direction reveal | T1 feedback shows “mavo means blue”; checked scope links the association to T2's blue→mavo requirement | T2's relevant exposure includes that occurrence. A check while the aid is available is helped; one shortly after closure cannot certify the delay. T2 earns no review or achievement from T1's result |
| I06 Related versus unrelated | A procedure explanation reveals a command; checked scope finds it relevant to command recall but not a separate vocabulary target | Command conditions are affected, vocabulary is not deferred. An unresolved candidate connection stays uncertain, without a false error or graph-wide postponement |
| I07 Target created later | T2 is accepted after the saved T1 feedback event | Candidate scan finds shared content; append a relevance revision linked to the original occurrence. Its old time/end bound governs eligibility. Mapping creation is neither a new exposure nor a fabricated T2 review |
| I08 Historical known cost | S contains October 5: 20m and October 15: 30m; T reaches October 22; selected cutoff October 8 | Selected cost **20m**. Separately labelled whole-period cost **50m**. Same investment scope, different declared display interval |
| I09 Crossing span | Add a disjoint, reliably placed October 8 11:58–12:03 span; selected cutoff 12:00 | Clip to two minutes: selected cost **22m**, whole-period cost **55m**. No entire-span inclusion or rounding to a full five minutes |
| I10 Earlier evaluation and uncertain placement | Use I09, set T to October 8 12:00 despite a later selected point/newer S; add unplaced 7m | Selected and period-to-date known cost are both **22m**; no later effort leaks through. The 7m stays separately unplaced/uncertain membership, not 29m of known earlier effort |

## Additional boundaries checked in this patch

| Case | Required consequence |
|---|---|
| R01 Correction reveals newer exposure | If relevant content ended October 8 09:00 and B answered 12:00, B cannot re-anchor a seven-day interval. Its own past retrieval counts for the next check: with no later reveal, next eligibility is October 9 12:00. Unknown timing holds qualification; no invented date |
| R02 Correction removes the only prior anchor | If B is now the first supported independent demonstration and there is known to be no preceding study/due anchor, schedule first later check at B+24h. Do not confuse that with an unknown possible earlier anchor, which holds the affected advancement |
| R03 Mixed larger exercise | A correction affects only one target slot. Retire/hold only that slot; other qualifying targets can settle once while the attempt remains partly pending. A whole-attempt status cannot release all targets or erase their evidence |
| R04 Replay, repeated correction and restore | Same effective inputs reuse the target/event/policy successor identity. Restore retains terminal dispositions, scoped effects and pending hold. Read-only validation creates no reviews, owners or checkpoints |
| R05 Extra or released answer | It stays evidence and can affect a concern, but cannot be promoted to the descendant exception. A previously released pending offer never regains scheduling credit merely because a correction now makes its answer look useful |
| R06 Due boundary and first-later evidence | Due exactly at evaluation time is not caught up. An exposure deferral cannot hide that debt. Immediate success after teaching does not meet the required later-check milestone; unknown due, missing current obligation or pending assessment also cannot produce an award |
| R07 Later error after a qualifying descendant | B may justify its historical schedule, but a later ordered error still leaves repair pending. Re-anchoring cannot clear later evidence or award caught-up status |
| R08 Relevance uncertainty and changed mappings | Missing candidate decisions with potentially disqualifying timing withhold the affected claim. Corrected scope uses original occurrence time. Report replay uses its saved source/definition and never performs a fresh model judgment |
| R09 Day boundary, empty window and unknown duration | Day selection uses saved next-local-midnight UTC, not a fixed 24h assumption. Span beginning at cutoff adds zero; a pre-start evaluation yields an explicitly empty interval, not an efficiency win. Unplaced durations cannot be proportionally assigned to the past |
| R10 Actual recall stream | An otherwise valid actual descendant rating remains in the corrected chronological stream; removed/disputed ratings stay in history but not effective replay. No capability interval or fabricated rating replaces the adapter. Unknown order or unavailable engine holds scheduling |
| R11 Earlier award and later history | New later work or the passage of time can make the live indicator false without falsifying its prior award. A correction affecting that earlier basis can mark it superseded while retaining its old scope/source/evidence and saved reports |

## Record, plan and verification ownership

The lifecycle contract owns obligation states, Practice-owned schedule correction effects, checkpoint scope/source/status and cross-target exposure behavior. The data contract owns exposure scope/relevance fields, report definition versions, effective cost windows and per-point cost provenance. Compatibility/export retains those additions and validates their constraints without invoking a model. The main build plan and observability plan carry the cases into the existing persistence, correction, scheduling and reporting slices.

The existing [everyday-policy investigation](issues/14-everyday-learning-policy.md) and [record/report investigation](../learning-observability/issues/09-data-contract.md) remain open for their broader policy and qualification dependencies. Their four named drafting gaps now have concrete rules and outcomes; this is not a claim that those entire tickets are resolved. No new learner exercise is needed to inspect this patch.

Verification checks: local link/anchor resolution; all four finding IDs, ten original case IDs and eleven added boundary IDs; independent interval arithmetic for 20/50, 22/55 and evaluation-capped 22 minutes; and a source reconciliation pass across the canonical contracts and readiness notes. These checks establish document consistency and the authored calculations only. Actual transaction atomicity, semantic relevance judgments, browser behavior, recall-engine replay and learning value remain later implementation/empirical work.
