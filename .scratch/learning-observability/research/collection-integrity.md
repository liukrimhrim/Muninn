# Trustworthy collection and reproducible learning reports

Research for [How can measurement stay trustworthy through interruptions and revisions?](../issues/04-collection-integrity.md). Reviewed 2026-10-14. This is design research, not implemented instrumentation or a browser-test result.

## Recommendation

Keep the existing local append-only records, exact references, command receipts and portable export. They can support the required measurements without a warehouse, external analytics SDK or second event store. The concrete gaps are smaller: record who owned a timer, distinguish trustworthy duration from trustworthy calendar placement, preserve the complete report query, and expose unresolved collection gaps.

The [observability proposal](../../skill-maintenance/observability-design.md#8-collection-and-reproducibility-contract) already separates outcomes from activity and specifies unknown durations. The [compatibility contract](../../skill-maintenance/compatibility-design.md#2-identity-and-version-rules) already separates occurrence time from commit order. Neither contract presently carries every field needed to enforce its prose promises. The additions below are recommendations to the unreleased design, not claims that historical data exists.

## Browser facts and their consequences

**Clocks.** High Resolution Time distinguishes a monotonic clock from an adjustable wall clock. Same-origin-of-time `performance.now()` differences cannot decrease; callbacks may nevertheless be throttled or frozen. Wall-clock values can move backward or forward. A clock measuring elapsed duration does not establish that the learner worked throughout it. [W3C High Resolution Time](https://www.w3.org/TR/hr-time-3/).

**Visibility.** Visible means at least partly visible under the browser's rules, with accessibility accommodations. It does not measure attention, reading or comprehension. A quiet reader and an unattended visible window can present the same available signal. [W3C Page Visibility](https://www.w3.org/TR/page-visibility-2/).

**Interruption.** Chrome documents suspended tasks in frozen pages, non-observable discard, unreliable termination callbacks, and the possibility that a persistence callback never runs even though its transaction committed. Hidden-state persistence is useful preparation, not a guarantee against abrupt failure. [Chrome Page Lifecycle](https://developer.chrome.com/docs/web-platform/page-lifecycle-api).

**Multiple tabs.** Web Locks coordinates cooperating contexts sharing a storage bucket; it is not cross-device or cross-profile coordination. Its specification warns that stealing a lock does not guarantee that the former holder has stopped executing. [W3C Web Locks](https://www.w3.org/TR/web-locks/).

**Storage.** IndexedDB separates request success from transaction completion and offers durability hints, including stricter persistence behavior with a potential performance/power cost. Persistent browser storage protects against browser clearing policy subject to permission; it does not prevent user deletion. [IndexedDB 3.0](https://www.w3.org/TR/IndexedDB/), [WHATWG Storage](https://storage.spec.whatwg.org/).

**Connectivity.** `navigator.onLine` is explicitly unreliable as proof of Internet reachability. Successful acknowledgement by the chosen authoritative store is the evidence that a command was accepted. [WHATWG HTML system state](https://html.spec.whatwg.org/multipage/system-state.html#navigator.online).

## Minimal collection contract

Retain the proposed 30-second checkpoints and 60-second continuity threshold as initial, versioned engineering settings. They are not attention thresholds or proven optimal intervals. Thirty-second scheduling does **not** bound crash loss to thirty seconds: callbacks, storage or transport can stall.

A checkpoint measures a half-open interval `[start,end)` within one document run. Close at a phase change, explicit pause, loss of visibility or takeover when that transition is observed. Resume a new interval after interruption. Save elapsed monotonic endpoints together with wall-clock anchors; compare their deltas to detect inconsistent placement. A large callback gap or contradictory clock deltas invalidates continuity even if the eventual elapsed number looks plausible. Do not extrapolate the last category across the gap.

When a process dies, retain acknowledged spans. An open session without a clean close establishes an **unknown tail**, not an interval of work ending at the next login. Without observed endpoints there may be no finite defensible duration to display. A measured session envelope can bound missing *accounting time*, but not attention. Manual recollection remains separately labelled self-report.

Use one active learner timer per library, including when two different sessions are open. The authoritative store grants a generation token through an ordinary transaction and records a small `timing_run`; its session link may be null for material preparation outside practice. Explicit takeover advances the token and invalidates future claims by the old owner. The UI may use Web Locks for convenience after capability testing; the accepting transaction must still validate the token. This fixes duplicate time, without introducing a coordination service.

Already committed requests always return their original receipt on retry. A previously unaccepted old-owner interval arriving after takeover is preserved as unverified rather than accepted as measured effort. It may genuinely predate takeover, but a client timestamp alone does not prove that. No answer is rejected merely because its timer lost ownership.

| Existing record | Minimal proposed addition | Failure it prevents |
|---|---|---|
| New `timing_run` | `generation`, nullable `session`, start/end anchors, `active/closed/interrupted` status, collector version; at most one active run per library | Two tabs both claiming time, including preparation outside sessions |
| `activity_span` | `run_id`, `owner_generation`, `ordinal`, nullable monotonic start/end offsets, `placement: anchored/uncertain/unplaced`, `quality_reasons: text[]` | Inability to distinguish duplicate, stale-owner, discontinuous or clock-shifted intervals |
| `activity_span` | Keep raw wall anchors; do not require their difference to equal reliable duration after a clock anomaly | Throwing away useful duration or inventing reliable calendar placement |
| `operation` | Nullable execution start/end and monotonic duration, with collector version | Mistaking model request latency for measured learner waiting; inability to inspect actual service delay |
| `measurement_report` | Frozen query manifest, evaluation instant, snapshot fingerprint, included/excluded references with reasons, collection-quality counts | Same saved report label producing different populations, maturity decisions or values |

`run_id` references one granted collection period within a document lifetime, not a person or durable device fingerprint. Self-reports and historical spans may have no run. Ordinals order measurements within that run; domain `sequence` still orders accepted revisions. The single new ownership record uses the same append-only envelope; it does not create another event log. Raw timing offsets can use rounded integer milliseconds; submillisecond precision provides no learning benefit here. Older records lacking provenance remain unknown after migration.

## Cost arithmetic, offline delivery and late evidence

Compute total placed effort as the union of eligible intervals after applying effective revisions. Do not add session elapsed, attempt elapsed and span totals. Do not allocate a shared exercise to several targets and then sum those copies. Conflicting categories on overlapping intervals remain unattributed; do not resolve the conflict by selecting whichever produces a nicer cost comparison.

Separate known duration from known placement. A trustworthy ten-minute duration with uncertain placement can be shown in an unplaced bucket, but cannot automatically enter a Tuesday total or be unioned against another clock epoch. Self-reported outside time is additive only when non-overlap is supported. Otherwise show it beside the measured total.

A long model operation produces learner blocked-wait cost only while the learner is actually in a recorded waiting phase. If the learner reads another topic, that interval is reading; provider latency remains a separate operational diagnostic. If the tab is hidden, classify it as unknown or an explicitly reported break/outside activity, not waiting by default.

The storage deployment is not selected. If the browser database is authoritative, local transaction acknowledgement is acceptance. If a local or hosted backend is authoritative, browser persistence is a pending copy until that backend commits it. Do not imply that a local draft is already part of the accepted library. Offline answering is a separate product capability, not a prerequisite for honest instrumentation; an initial release can retain drafts and clearly mark submissions pending.

When delayed delivery succeeds, preserve occurrence time and add a later commit sequence. Do not backdate the commit. Out-of-order retry must not create another attempt or span. Inaccurate occurrence time remains flagged; report daily placement or minimum-delay eligibility as uncertain where necessary. The research recommendation is conservative eligibility, not silently replacing the timestamp with receipt time.

## Reproducible queries and immutable reports

A saved report needs two independent coordinates: **what was committed by sequence S** and **the instant T at which endpoints are evaluated**. `computed_at` is not T: recomputing tomorrow must not mature additional endpoints inside yesterday's saved report.

Resolve records in a consistent snapshot. For each identity, select the highest accepted revision whose sequence is at most S, then apply the domain's supersession, assistance and mapping rules at that cutoff. Do not fetch today's assessment before applying yesterday's cutoff. Only then evaluate eligibility at T and aggregate by the occurrence window. An observation committed after S is absent from that report, even if its occurrence time was earlier.

Freeze the resolved targets and enrollment revisions, mode/help filters, endpoint assignment rule, grouping timezone, explicit calendar boundaries, cost scope, exclusion reasons, metric version and parameters. Preserve exact included and excluded references. A timezone identifier alone is insufficient for indefinite replay if historical timezone rules change; saved UTC bucket boundaries make the grouping unambiguous without requiring a time database service.

Reuse the compatibility design's logical snapshot fingerprint for the source prefix, including library identity. Equal sequence numbers alone do not identify equal data on divergent copies. Store a digest of the canonical manifest/results as well. JCS defines a deterministic JSON representation suitable for hashing; hashing detects changed bytes, not truth, provenance or authorization. [RFC 8785](https://www.rfc-editor.org/info/rfc8785/).

Treat a saved report as immutable. A correction produces a new report linked to the earlier one; its current historical chart may change at the original learning time. Keep the old report readable. If old metric code is unavailable, disclose that replay is unavailable instead of claiming the newly computed result reproduces it. Report saving itself must not move its source cutoff.

## Quality, privacy and retention

Show separate quality indicators: placed estimated minutes, placed self-reported minutes, unplaced known duration, known unaccounted intervals, unknown-tail count, stale-owner/conflicting-span count, pending acceptance, and late/corrected records affecting the query. Counts need denominators when a meaningful opportunity count exists. Do not invent a percentage of attention captured or treat acknowledged checkpoints as a percentage of all real effort.

A known envelope permits an accounting-coverage fraction, explicitly labelled as such. An unknown session end makes that fraction unavailable. Missing cost that could reverse an efficiency comparison makes the comparison unresolved. Quality affects the strength of a claim; it must not turn an observed correct answer into failure or silently erase it.

Keep timing independent of answer text, keystrokes, screen capture and URLs outside the app. Store record references and coarse collection facts; progress inspection time is overhead. Optional subjective feedback stays optional. No external analytics transmission is required. Full library exports contain source material, answers and timing history; a dashboard-table export is a different, deliberately scoped artifact and should carry its manifest without copying response text by default.

Append-only history and intentional deletion conflict unless deletion has an explicit contract. Recommended first design boundary: no automatic expiry of evidence referenced by retained curricula/reports; rebuildable caches may be dropped. Keep local unsent transport copies only until acknowledged/reconciled, except unresolved conflicting records. Do not silently prune ledger intervals into daily totals, which would destroy correction and overlap analysis. Whole-library deletion and selective redaction need a separate reviewed design covering backups, copies and report replay; neither is implemented by retirement. Persistence status and export recency should be visible if browser storage is chosen.

## Future executable probes

These are proposed manual acceptance probes, not results. Run against each supported browser/OS and retain receipts, saved records and before/after report manifests.

| Probe | Action and required observation |
|---|---|
| Quiet reading | Read for two minutes without input; preserve foreground estimate, never infer attention or idle failure. |
| Hide, freeze, sleep | Hide the tab, use Chrome's `chrome://discards` freeze/discard controls, then suspend the machine; reopen and inspect boundaries. No gap becomes measured work. |
| Crash and acknowledgement loss | Kill the page before/after checkpoint commit; suppress the response and retry. Reopen the store to distinguish committed-without-callback from absent; exactly one accepted interval. |
| Clock jump | With an isolated test clock, move wall time both directions during one run. Monotonic duration survives where continuous; calendar placement and delay eligibility become uncertain. |
| Two-tab takeover | Freeze the first owner, take over in another tab, resume the first and deliver its pending spans. One owner; old accepted receipts remain valid; new stale claims cannot double time. |
| Concurrent work | Delay a model response while answering elsewhere, then wait explicitly. One union of learner intervals; provider latency is never added wholesale. |
| Offline and quota failure | Block the authoritative endpoint or force storage failure. UI distinguishes pending/failed save; restored delivery is idempotent and does not fabricate successful persistence. |
| Cutoff and correction | Save at S,T; later accept an old occurrence and correct a grade. Old report stays byte-stable; current report explains changed history and uses a new manifest. |
| Export and divergent copies | Restore offline and replay a saved report; compare two copies with equal S but different histories. Matching fingerprints reproduce; sequence equality alone is refused. |

The next collection decision should select the authoritative store and supported browser matrix. The evidence here specifies what that choice must prove; it does not justify a telemetry service or predict learner benefit.
