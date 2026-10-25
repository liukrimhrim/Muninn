# From learning records to trustworthy reports

Status: saved-record and report contract finalized in [Design Baseline 1](../skill-maintenance/design-baseline.md), 2026-10-16. Metric definitions and the compatibility/lifecycle reconciliation are fixed for this design. Persistence, import and report replay remain implementation qualification; no live collection or experiment is authorized.

The learner should be able to answer “Why does the dashboard say that?” with the original question, answer, help, accepted judgment and date. A correction should explain a changed conclusion. An upgrade should preserve both the evidence and previously saved reports. Missing information should remain visible.

This addendum completes the [base portable records](../skill-maintenance/compatibility-design.md#3-portable-logical-records), [initial observability payloads](../skill-maintenance/observability-design.md#8-collection-and-reproducibility-contract) and [C display mapping](c-dashboard-contract.md#6-records-needed-behind-every-display). Where the initial payload sketches omit fields or conflict with the rules below, this is the proposed replacement for those specific details. The design is still unreleased format 1; these are design revisions, not migrations of existing learner data.

## 1. Audit findings and the smallest changes

The subsequent [lifecycle patch](../skill-maintenance/learning-lifecycle-contract.md) and [tracking patch](tracking-contract.md) complete admission, authoring, distinct-attempt ownership/order, exposure recovery, prospective plan creation and per-claim aggregation. They own the named payload extensions below. The [closure traces](../skill-maintenance/cross-contract-closure.md) check all fifteen second-audit scenarios at the design level.

| Observed design gap | Proposed change | Failure addressed |
|---|---|---|
| A receipt has only a final sequence and command results | Retain the complete transaction's record range and references | A report could otherwise include a corrected grade without the corresponding schedule/projection changes |
| An endpoint permits an initially null assignment, without a full revision rule | Freeze its measurement contract; allow only one assignment to an unsubmitted attempt | A later successful retry must not replace the original check |
| Required occurrence timestamps cannot express an uncertain client clock | Add explicit time evidence; permit null occurrence times when not exact | Avoid inventing a date, reversing time, or losing a valid answer |
| Timing spans lack accepted owner and clock provenance | Add one timing-run record and qualified span fields | Double counting, stale timer deliveries, false calendar placement |
| Viewing an answer is neither necessarily study completion nor absence of exposure | Add a presentation/outside-exposure record with bounded timing | A retention claim must account for possible intervening rehearsal |
| A metric name/version and sequence do not preserve a whole query | Freeze source fingerprint, evaluation time, definition, resolved population and reasons | Saved reports changing silently after corrections, midnight or upgrades |
| The prototype has one unit per target; real exercises can cover several | Bind requirements to units and preserve criterion-level interpretation | One composite error must not mark every participating unit weak |

All additions use the existing record envelope, ordinary application transactions and full-library export. No second event store, analytics service or new coordination service is needed by these findings.

## 2. Complete transactions and source identity

Extend `CommandReceipt` to:

```text
{request_id: UUID, command: text, input_digest: Digest,
 result_refs: Ref[], first_sequence: integer,
 committed_sequence: integer, record_refs: Ref[]}
```

`Digest` is 64 lowercase hexadecimal characters. `record_refs` lists every revision written by that command, in sequence order; `result_refs` is the response and need not contain all writes. The range is inclusive. Mutating commands commit at least one record, with consecutively allocated sequences; allocation rolls back with the transaction. Every domain record belongs to exactly one receipt, and committed ranges partition sequences 1 through the snapshot watermark without gaps or interleaving. A read-only no-op creates no new receipt; a retry of an already accepted command returns its original receipt.

An assessment correction writes its revised assessment, changed projections/schedules and transition in one transaction. The report source cutoff is either zero or the final sequence of a complete receipt. An arbitrary record sequence in the middle of this transaction is not a valid report source. Import verifies the partition, exact record membership, references and input-digest syntax; it does not re-execute a command or claim to reconstruct every original command input from the digest.

For a report at cutoff `S`, form exactly this logical prefix:

```text
{format_version, library_id, through_sequence: S,
 records: all revisions with sequence <= S, in sequence order,
 receipts: all receipts with committed_sequence <= S, by request_id}
```

Hash its RFC 8785 canonical bytes with SHA-256. The fingerprint is the compatibility design's learning fingerprint, applied to a complete prefix. Store `format_version`, `library_id`, `S`, `fingerprint_algorithm: sha256-jcs`, `snapshot_fingerprint` and `receipt_scope: complete_prefix` in the report. Two libraries with equal `S` are not necessarily equal. The saved report's own transaction is later than `S` and is excluded, avoiding self-reference. Earlier saved reports in that prefix remain ordinary historical records.

Canonicalization preserves string data and rejects duplicate keys or invalid Unicode. A general-purpose sorted-key JSON serializer is not a substitute for JCS; use the standard's serialization and ordering rules. The import parser also rejects negative zero, following the verified erratum. These choices detect inconsistent bytes, not truthful grading or authorship. [RFC 8785](https://datatracker.ietf.org/doc/html/rfc8785), [verified negative-zero erratum](https://www.rfc-editor.org/errata/eid7920).

Full-library archives retain all receipts, including report-saving receipts. A scoped dashboard table is not a restorable archive and must say so. A future legacy format lacking transaction membership cannot receive fabricated receipts: preserve its original view and report that a historical cutoff cannot be verified unless its actual provenance establishes the boundary.

## 3. Occurrence time is evidence, not a required guess

Payload owners validate time-evidence shape using the shared pure value validator. Practice records the session start/stop facts; Evidence owns their learning-order/delay interpretation, and Measurement owns duration/placement/cost interpretation. Keeping an observed instant in a session is not authority for Practice to calculate effort. The module-review revision removes `attempt.elapsed_ms` and `session.elapsed_ms` from the unreleased format: measured duration belongs to `activity_span`; elapsed display/budget summaries are derived views with source/quality provenance. Session elapsed includes breaks, whereas effort excludes explicit pause. Trustworthy session endpoints may establish an elapsed envelope, never attention or the category breakdown. Unknown timing remains unknown and cannot prevent saving an answer.

`recorded_at` and `sequence` describe acceptance by the authoritative store. They do not substitute for when the learner answered, studied or reviewed. Planned windows and due dates are explicit scheduling instants, not observations.

For observed lifecycle fields, add this payload member to `session`, `attempt`, `study` and `review`:

```text
time_evidence: TimeEvidence[]
```

`TimeEvidence` is defined in the compatibility contract. The allowed parent field names are `session.started_at/ended_at`, `attempt.started_at/submitted_at`, `study.started_at/completed_at`, and `review.occurred_at`, using the local field name inside each payload. Nested assistance has its own one-entry array for `shown_at`, as specified below; it is not another parent field. Every observed field has exactly one entry. An exact time has equal non-null bounds and the existing timestamp equals that value. Bounded time has ordered non-null bounds and a null timestamp. Unknown time has null bounds and a null timestamp. Raw client values remain evidence, never a second authoritative date. A clock is qualified by the declared collection protocol; being a server clock alone does not prove it accurate. Use `basis: unavailable` with an explanation for current observations lacking a usable timing source; reserve `legacy_unknown` for genuinely missing historical provenance. Both require unknown precision and null bounds; use a supported clock/self-report basis if real bounds exist.

This changes the base rule that every submitted attempt must have a non-null submission instant: **submitted status requires an accepted submission, not a fabricated exact occurrence time**. A submitted attempt always has submission time evidence, possibly unknown. An uncompleted lifecycle field has no time-evidence entry. To keep occurrence separate from completion, add `study.status: started/completed` and validate it together with its completion-time evidence. Session and attempt already have status fields; an actual review is itself evidence that the review occurred. Technical import must not infer completion from a nullable time alone.

Exact trusted start/end times on a common basis must be ordered. Raw clock anchors may disagree; that does not invalidate an otherwise accepted answer. For a minimum delay `d`, with anchor bounds `[a0,a1]` and answer bounds `[b0,b1]`, qualification requires `b0 - a1 >= d`. If only `b1 - a0 < d`, it is definitely too early; otherwise it is uncertain. Unknown bounds cannot establish the delay. For calendar grouping, an event enters a bucket only if all its possible times lie within that bucket; otherwise keep it in an uncertain-date group. Save UTC bucket boundaries as well as the display timezone.

### Known assistance with uncertain time

Use `assistance-evidence-1`. An assistance entry asserts a known presentation during this bound response; its `time_evidence` describes how precisely that presentation can be dated. These are separate facts. A confirmed hint-display acknowledgement before submission in the same live attempt lifecycle can establish in-task help even when the wall clock fails. Keep the acknowledged assistance in the draft and submitted snapshot, with text, criterion IDs and a timing explanation. Store acceptance time is not its display time. A mere request/reservation or uncertain browser presentation cannot assert known help; retain that uncertainty as exposure evidence under the existing presentation rules instead. Feedback first shown after submission is exposure for future checks, not an assistance entry for this answer.

For an unknown display instant, save `shown_at: null` and a single `time_evidence` entry with `field: shown_at`, `precision: unknown`, null bounds, the actual basis and explanation. For a bounded instant, keep both bounds and null `shown_at`; never choose a midpoint or one bound as an exact event. Unknown time does not empty the assistance list, clear an assisted flag or reject an otherwise valid answer. A known in-task entry whose supposedly exact time falls outside trusted attempt bounds is a timing contradiction to resolve before acceptance, not permission to drop the help; preserve the captured evidence and submit with uncertain time if that is what is actually supported.

Resolve each criterion/requirement using both (a) known in-attempt assistance and (b) relevant external exposure/aid availability at source cutoff S. A local `Observation.assisted` flag describes (a) only. The report, independent-success decision, concern resolution and schedule advancement use the combined conditions, not that flag alone. Known relevant help from either source makes a usable target judgment H/QH; retain timing limitations alongside it. An unusable judgment remains U/QU with the help annotation. Unknown availability/relevance alone retains the recorded raw judgment and makes the affected independent claim uncertain. Other requirements remain unaffected unless their own evidence establishes help or uncertainty. A local hint without a reliable timestamp is still known help; a definitely open relevant answer in another screen requires no fabricated local hint entry.

Keep the accepted assessment's correctness judgment separate from assistance qualification. Binding proves which criterion received a hint, not that the hint's content was actually relevant to every target in the exercise. Use the bound criteria/requirements and checked exposure relevance. The combined result cannot certify independent recovery or advance an independent-check obligation for an affected target. Subsequent delay checks use supported exposure end bounds or the existing prospective condition checkpoint; an unknown display time does not invent an end time or permanently prevent future practice.

Submission keeps its historical assistance snapshot. Later evidence about timing, relevance or outside help is linked through the existing exposure/correction path and recomputes current qualification, concerns and schedule effects atomically; it does not overwrite that snapshot or create another presentation. A linked exposure uses `related_occurrence` for the attempt and `related_assistance_index` to identify the assistance entry; report criterion bindings retain the exact attempt Ref and assistance index. Count one underlying reveal, even if both representations support it. Import validates the declared precision/null rules, criterion bindings and reference closure; it does not infer that help was absent from a null clock, invent display acknowledgements, or call a model. Saved older report definitions keep their original results.

## 4. Timer ownership, duration and placement

Use one library-wide active timer, even for preparation outside a session. Its durable grant is an ordinary new kind:

```text
timing_run = {
  session: Ref?, activation_id: UUID, document_run_id: UUID,
  generation: integer, collector: Algorithm,
  status: active/closed/interrupted,
  opened_at: Time, closed_at: Time?, close_reason: text?
}
```

These start/close instants describe store-side grant lifecycle, not measured learner effort. Generation is positive and monotone within one runtime activation. `activation_id` changes whenever the authoritative writer restarts or a restored store is activated. Its current token is operational metadata, not a rewrite of portable history. Each grant retains that identity in its record; neither ID is a durable device fingerprint or secret credential. The accepting transaction checks the current activation and generation before qualifying a new measurement.

Extend `activity_span`, retaining its existing scope, category and measurement fields:

```text
run: Ref?, ordinal: integer?,
monotonic_start_ms: integer?, monotonic_end_ms: integer?,
raw_wall_start: Time?, raw_wall_end: Time?,
placement: anchored/uncertain/unplaced,
duration_quality: continuous/self_report/unknown,
authority: accepted/stale/not_applicable,
continuity: closed/checkpoint/unknown_tail,
quality_reasons: text[]
```

`run` names the exact grant revision and carries its activation/generation; do not maintain a second conflicting token in the span. Ordinals are positive and unique per run/interval identity; a correction is a new revision of the same span. A new request reusing an ordinal with a different span identity conflicts. Self-reported or legacy spans may have null run/ordinal/monotonic fields and `authority: not_applicable`; they cannot claim a qualified foreground measurement. A retry with the same command ID returns the accepted result before checking today's timer ownership. A previously unaccepted old-owner delivery is retained with `authority: stale`, `measurement: unverified`; it cannot enter measured totals. Answer submission remains independent of timer ownership.

For a continuous qualified interval, monotonic offsets are integer milliseconds from the same document run, ordered, and their difference equals `duration_ms`. `started_at/ended_at` are the qualified placement, nullable, while raw wall anchors may run backward. `anchored` requires both trustworthy placement endpoints; `uncertain/unplaced` has null placement endpoints. A clock discrepancy can leave a reliable duration unplaced. A continuity gap leaves duration unknown unless other evidence supports a bounded estimate. Do not infer continuous attention from visibility or elapsed time.

An `unknown_tail` has null duration and no invented end time. On restart/takeover, if a previous run has no clean terminal observation, record a new unknown-tail span referring to its last acknowledged point through `context`. Do not modify prior intervals. Until that record exists, the report may derive an open-run warning from its saved source; deduplicate it by run identity. Historical queries never consult today's owner metadata: subsequent interruption notes affect only later source cutoffs. Restore validation itself is read-only. Any subsequent interruption note or new grant is a new command above the restored watermark.

For cost, select effective accepted spans at source cutoff S, resolve their scope under `cost-membership-1` below, clip reliably placed in-scope intervals to the **effective display interval** and union them once. Exclude explicit pause from effort. Segment overlaps at their boundaries: if included effort categories disagree, count the overlap once as `unattributed`; if a pause/unaccounted claim conflicts with an effort claim, withhold that segment from known effort and show it as disputed. Categories plus unattributed effort must sum to the reported known union. Show foreground estimates and self-reports distinctly; an overlap is not two minutes of work per minute.

Unplaced known duration, stale claims, disputed segments and unknown tails remain separate. Do not add an unplaced duration to a day's union unless non-overlap and membership are supported. Filtering to one target retains the shared encounter's full cost and labels that scope; it never divides a larger exercise's minutes by its target count. Model request latency is not learner waiting time: only a qualified `blocked_wait` span contributes to effort. Operation latency instrumentation is optional and is not a prerequisite for this dashboard contract.

### Historical cost boundaries

Use `cost-cutoff-1` for new product report definitions. Keep the declared scope and frozen investment window `W=[cost_start,cost_end)` unchanged. Derive a separate effective interval for each displayed cost:

- **Through the selected check:** `upper = min(cost_end, evaluated_at, selected_check_cutoff)`.
- **Period to date:** `upper = min(cost_end, evaluated_at)`. Label it “Whole period” only once evaluation reaches the period end; a newer source snapshot cannot make future effort part of an earlier evaluation.
- The effective interval is `[cost_start,upper)` when `upper > cost_start`; otherwise it is empty. Store the requested upper bound and the empty result explicitly. A pre-start empty interval means “Tracking has not started at this date,” not a measured zero-cost learning achievement.

The selected cutoff is an explicit UTC instant, not a date string parsed at display time. A planned plot point uses its frozen check-window end; an exact ordinary check can use its supported occurrence boundary. A calendar-day selection uses the **next local midnight** in the saved display timezone, converted to and saved as UTC. Do not assume every local day is 24 hours. Save the day label and UTC bucket; an uncertain occurrence that cannot be placed in a day cannot manufacture a dated check point. Its evidence remains separately visible. Merely viewing the report in another timezone does not recalculate a frozen cutoff; a changed query creates a new calculation.

For a reliably placed span `[a,b)`, include `[max(a,cost_start), min(b,upper))` only if its end exceeds its start, then apply the existing union/category/dispute rules. A span beginning exactly at the cutoff contributes zero. Clip a crossing span before summing; do not allocate uncertain calendar placement proportionally to make it fit. Retain unplaced/unknown/disputed spans with the reason they might belong to this effective interval. A span known to lie wholly after it is excluded with that reason, even if its record is in S. A duration with possible times on both sides remains uncertain membership, not known earlier effort. Known membership without reliable placement still cannot be added to the union without established non-overlap.

Apply this function to selected cards, each history point, any full-period panel and saved/replayed cost results. Skill filters preserve the same whole-encounter scope; date controls change its time interval. Each result retains its own effective window, so selecting one point cannot overwrite other points' cutoffs. Source S determines which facts/corrections are available; evaluation T and the selected boundary determine which occurrence time is included. Never use record creation/acceptance time as effort time.

Example: S contains 20m on October 5 and 30m on October 15. With T at/after October 22, an October 8 selected cutoff yields 20m, while the separately labelled whole-period view yields 50m. A further reliably placed October 8 11:58–12:03 span adds 2m to a 12:00 cutoff, yielding 22m versus 55m for the whole period. If T is October 8 12:00, even period-to-date remains 22m regardless of a later selected date or newer S. An additional unplaced 7m remains separate.

### Frozen cost membership across revisions

Use `cost-membership-1`, saved as an `Algorithm` with `name: cost-membership`, `version: "1"` and `parameters: {scope: roots/library}`. A cohort uses `scope: roots`: freeze this as `measurement_cohort.effort_membership` with the existing exact `effort_scope: Ref[]`. New saved queries carry the same algorithm as `query.cost_membership` with `cost_scope`. In roots mode the roots must be nonempty, unique enrollment, target or source refs from the same library and available when the scope is fixed; unsupported root kinds are rejected. Do not silently turn a curriculum title or today's selection into a new root. Roots and algorithm are immutable within the plan; changing either requires a new comparison.

An explicitly selected whole-library ledger uses `scope: library` with empty roots and includes all that library's accepted spans before applying time/quality rules, including unallocated preparation. It is labelled as library effort and cannot masquerade as a cohort's curriculum cost. Empty roots in roots mode are invalid; an empty filtered selection cannot silently widen to the library. This preserves ordinary effort inspection before a curriculum or tracking plan exists.

Root matching is explicit and limited:

| Root kind | What is followed | Supported attribution on an effective span |
|---|---|---|
| Enrollment | The same `(kind, id)` across its revisions available at S, retaining the exact frozen revision as provenance | `span.enrollment` and enrollment refs explicitly in `span.context`; if neither supplies an enrollment, the exact `span.session` may supply its single enrollment. These are the only enrollment paths |
| Target | That exact target Ref | A direct match in `span.targets` or target refs explicitly in `span.context`; preserve whole shared-encounter cost |
| Source | That exact source Ref | A source ref explicitly in `span.context`, for preparation even before an accepted target exists |

Explicit span enrollment attribution takes precedence over the session fallback. Known work shared by several enrollments records their exact refs in `context` (plus `enrollment` when applicable). Do not infer sharing merely because a session lists several curricula: without explicit attribution, those enrollments are candidates with uncertain membership. A single-enrollment session is sufficient inherited context; record that session Ref as the basis. A shared target, the curriculum's present membership, arbitrary reference traversal, or an accepted equivalence mapping does not pull all connected work into an enrollment scope. Target/source roots do not follow revisions or mappings automatically.

The collector saves known enrollment context for preparation, inspection, correction and learning work when the span is recorded, even if its target list is empty. It does not guess a context from the grade. With explicit enrollment context outside the selected roots, record out-of-scope work; with unresolved or absent attribution, retain potentially relevant library overhead as uncertain, not zero or silently discarded. For a target/source-only scope, explicit nonmatching attribution to other targets/sources is outside that narrow scope, while missing relevant attribution remains uncertain. A possible match can never certify known in-scope minutes. Across multiple roots use OR: one supported match suffices; otherwise retain uncertain candidates or supported exclusion reasons. Several matching roots still identify one span, not several copies of its duration.

For routine tracking, the roots are the selected enrollment refs, **not** a replacement target-only cost filter. Continue following those enrollment identities through goal additions/removals, admission, pause, archive and checkpoint revisions within the frozen cost window. Include actual attributed work on new or removed goals and curriculum overhead; none of this changes the fixed outcome-target set. A new enrollment identity, even for the same curriculum or a similar title, is outside the old scope unless it was itself frozen as a root. Previously unallocated source work enters an enrollment scope only through explicit supported attribution/correction; an incidental content link is insufficient. Narrow target/source views are labelled as such and show other curriculum/unallocated overhead separately; they cannot be presented as full curriculum investment.

After resolving scope, apply `cost-cutoff-1` and the timer quality/union rules. In-scope does not mean reliably placed, before T, or additive: scope, placement, authority and overlap are independent checks. Shared minutes may appear in several drilldowns with a shared label; a combined view unions the actual spans/intervals, never the displayed subtotals. Scope-uncertain effort remains separately visible with its timing quality and may make a cost comparison incomplete; no arbitrary allocation or weighted score resolves it.

Save each considered span's scope decision in the cost result:

```text
ScopeResolution = {span: Ref, state: in_scope/out_of_scope/uncertain,
  roots: Ref[], basis: Ref[], reason: text}
```

`roots` identifies matched or possible frozen roots; it is empty for explicit library mode and may be empty for unsupported context/outside scope. `basis` retains exact span/context/session refs establishing the decision. `CostResult.membership_rule` is the frozen Algorithm and `scope_resolutions` is this list, separate from temporal and quality exclusions. Use the effective span revision at S, its original occurrence evidence and the referenced historical session revision; do not substitute today's enrollment/session or a correction's acceptance date. An accepted attribution correction may change a **new** report's included spans under the same rule, with its reason, while an old saved report retains its source, manifest and value. Restore/replay preserves these distinctions. A missing older membership rule is not silently upgraded to `cost-membership-1`; retain the old definition or state that reproduction is unavailable.

Worked scope result: E@1 contributes 20m, a checkpoint creates E@2 with the same goals, and E@2 contributes a disjoint 30m within the effective window. The frozen E@1 enrollment root follows E's identity and yields **50m**. If that 30m explicitly belongs to E and F, E's view includes 50m, F's includes the shared 30m, and their combined view is still **50m**. An unrelated F-only span does not enter E merely because their curricula share a target.

## 5. Exposure, corrections and the unit behind a flag

Add one `exposure` kind:

```text
{session: Ref?, targets: Ref[], content_refs: Ref[],
 kind: answer_presented/review_content_presented/outside_report,
 timing: {precision: exact/bounded/unknown,
          earliest_at: Time?, latest_at: Time?},
 basis: app_presentation/self_report,
 presentation_id: UUID?, related_occurrence: Ref?,
 related_assistance_index: integer?, details: text?}
```

Add the [availability/end-bound and condition-checkpoint fields](../skill-maintenance/learning-lifecycle-contract.md#5-exposure-has-an-end-and-uncertainty-has-a-prospective-recovery). An open view is ongoing availability, not an exposure that ended at its opening time. A justified prospective end bound can enable a future check without rewriting historical unknown timing.

Also add the following fields for [shared-content exposure](../skill-maintenance/learning-lifecycle-contract.md#shared-content-across-different-targets), under `exposure-scope-1`:

```text
scope: {presented_text: text?, knowledge_refs: Ref[],
        content_complete: boolean, basis: Ref[]},
relevance: [{target: Ref, requirement_ids: text[],
             decision: relevant/not_relevant/uncertain,
             basis: Ref[], reason: text,
             reviewer: Assessor?, protocol: Algorithm}]
```

App presentations preserve the literal shown text or content refs resolving to exactly the shown excerpts; a whole source chapter does not stand for the small excerpt actually displayed. `content_complete` describes whether the presented content was fully captured, not expert certainty. Outside reports can have null text/incomplete scope with their explanation. Knowledge refs identify supported content, not inferred learner achievement. Relevance rows for one target have disjoint nonempty requirement sets belonging to that exact revision; a positive/negative checked decision requires its reviewer, rule and supporting text/refs. A generated/unreviewed candidate or missing candidate row is uncertain. Full-target irrelevance requires covering all candidate requirements; absence of a row cannot mean a negative finding.

Before target admission/delivery and when applying corrections, resolve candidates by the lifecycle rule, including existing attempts/studies with related content. For such an occurrence, an exposure record may retain the new scope decision through `related_occurrence`; the underlying occurrence is still counted once. Append a new exposure revision to add/correct relevance for a later-created target; preserve the original presentation ID, captured text and occurrence/end time unless those facts themselves are explicitly corrected. Relevance acceptance time is not exposure time. Concurrent revisions validate their predecessor and preserve other accepted scope entries. Recomputing a report never authors mappings: a missing candidate decision produces qualification uncertainty where relevance could change that claim's result. If supported timing puts the occurrence outside every relevant interval for that claim, retain a scope-quality note without withholding an otherwise supported result. Store the exact exposure revision, requirement scope and relevance decision in endpoint eligibility evidence. An older saved report retains its own recorded decisions/definitions.

Timing follows the same bound invariants as section 3. An app presentation uses a presentation ID created once for that display occurrence; retry/repaint of the same display does not create another exposure. A later reopening is a new possible exposure. Bounds cover the possible visible presentation interval, not an assumed reading instant. Outside reports may have unknown timing and no content record; their subject must still be scoped to known targets or explicitly treated as unscoped uncertainty. Do not make a knowledge unit merely to fill a missing reference.

Attempts, scoped assistance and completed study already supply exposure evidence. `related_occurrence` identifies a duplicate representation when applicable; reports count the underlying occurrence once and retain all supporting refs. A counts-only page does not expose answers merely because it names skills. An answer-bearing dialog may affect later retention eligibility, but never creates a success, completed study or FSRS review. Unknown outside activity is not known absence of outside learning. A saved report may therefore claim “no recorded intervening exposure” without claiming that none occurred.

For exposure representing an existing in-attempt hint, `related_occurrence` is the exact attempt revision and `related_assistance_index` is its zero-based assistance entry. Validate that the entry exists and the captured content/scope refers to that hint. The index is null for a whole attempt's retrieval, a study, or a separate presentation; a non-null index requires an attempt ref. This distinguishes several hints and the answer retrieval in one attempt; excluding the current answer's own retrieval from prior exposure must not exclude its indexed hints. Identity for this deduplication is the attempt identity plus the preserved entry position, with exact revisions retained as evidence; an appended linked exposure is not another reveal. Draft assistance entries are append-only facts: preserve existing entries and their positions, and freeze the list on submission; later interpretation uses the linked correction path. If association is uncertain, retain the uncertainty rather than merging separate presentations by matching text.

For a claim that requires no exposure after its anchor, a bounded exposure overlapping that interval makes eligibility uncertain, and a definitely intervening exposure disqualifies it. For a claim requiring a minimum gap after any relevant exposure, compare the answer's earliest possible time with the latest possible exposure time. Do not use the earliest exposure bound to make the gap look longer. The definition states which interpretation is intended.

Complete the assessment payload with `interpretation_criteria: text[]` and `interpretation_basis: Ref[]`. The existing `interpretation` applies only to the named criteria; ordinary uses an empty scope. A supported misread or unresolved interpretation requires a nonempty scope and its explanation; supported misread also requires the saved supporting clarification/evidence. All criterion IDs belong to the bound exercise. Other criteria retain their ordinary interpretation. This represents a mixed larger exercise without treating one misread as a defect in every part. If evidence needs different nonordinary interpretations per criterion, retain the affected result as unresolved until an explicit schema extension supports that distinction; do not silently collapse it.

The misread remains visible as an observed response, but cannot contribute an error-based weakness flag. It also does not become demonstrated knowledge merely because the learner says “misread.” A fresh neutral check can supply separate evidence. Accepting a correction appends an assessment revision with exact support, supersession and transition, using the original attempt's occurrence. A changed prompt or rubric needs the existing mapping process, not a grading revision disguised as the same task.

Extend each `target.evidence_requirements[]` entry with `knowledge_refs: Ref[]`, restricted to that target's exact `content` refs. This is a declared coverage binding, not a diagnosis. A requirement can name a relation or procedure as its own knowledge unit. If a failed requirement covers several units and does not localize the failure, show “needs diagnosis” with that evidence; do not flag all units as weak. Partial or disputed coverage likewise does not become an error.

For an eligible flag, preserve the exact unit revision, target, requirement, mode, criterion, attempt and accepted assessment refs. Group the display by stable knowledge identity, but never concatenate incompatible revision histories. In the absence of an accepted comparability mapping, show old/new contracts separately inside the unit. Order checks by their predeclared check sequence or supported occurrence order, not by delivery order. Ambiguous temporal order cannot establish a latest result or a consecutive streak and stays separately unresolved. Rank each comparable requirement/mode stream with the already proposed rule, then display each unit once at the priority of its most urgent eligible stream, showing all its flagged streams. Equal evidence is tied; stable identity is only a deterministic final display order. No averaging across modes or multiplication of shared episodes. A unit can have both a valid error flag in one mode and an unknown result in another; show both.

This extends the single-mode prototype, whose rule remains a descriptive proposal. It is not a validated mastery model, evidence of a diagnosed cause, or an instruction to assign extra practice.

## 6. Frozen endpoints and deterministic queries

A `measurement_cohort` freezes target refs, baseline rule and exact baseline refs, nullable anchor with reason, windows, required mode, eligible exercise families, exposure rule, effort scope/membership algorithm and metric definition before its endpoints are observed. The [tracking lifecycle](tracking-contract.md#2-a-concrete-default-plan) supplies the ordinary preview/freeze/assignment/closure workflow and defaults; routine history without a cohort remains available. Each `(cohort identity, endpoint id)` binds one target and one planned check; date labels are not identifiers. Multiple targets may use the same attempt.

Allowed cohort revisions are the [tracking contract's assignment and lifecycle transitions](tracking-contract.md#3-plan-creation-closure-and-changes). An assignment changes `assigned_attempt` and `assignment_offer` from null to the initial draft/offer pair before presentation. Commit assignment with draft/offer creation in one transaction; it must precede submission. Lifecycle can move active→stopped/completed without changing frozen windows or populations. Assignment to an already submitted identity is rejected even if an earlier draft Ref is supplied. The other cohort fields and already populated assignments remain unchanged. Later draft/submission revisions keep that attempt identity. Changing the selected exercise contract retires/replaces the plan visibly; it cannot silently replace the measured endpoint. A cohort revision records all assignments so far, and historical reports use the effective assignment revision at their own cutoff.

Late delivery cannot prove a prospective assignment retrospectively. An answer saved without an accepted prior assignment remains ordinary descriptive evidence and can prompt a new future check; it does not repair the trial protocol after the outcome is known. A technical restore preserves assignments exactly. Endpoint windows are half-open `[start,end)`; they mature at `evaluated_at >= end`. The displayed scheduler reminder alone is not this boundary.

The shared report query follows this order:

1. Open a consistent complete-transaction snapshot, capture source identity `S` and frozen evaluation instant `T`, and validate its fingerprint. Source records, receipts and definitions all come from that view.
2. Resolve accepted revisions at or before `S`. Apply existing supersession/activation rules. Never fetch today's assessment and then try to filter it backward.
3. Resolve the exact population and every planned check, including checks without answers. Freeze inclusions/exclusions and explicit UTC buckets. Cohort membership cannot be filtered by its observed outcomes.
4. Resolve each assigned attempt identity to its submitted revision, if any, and the accepted assessment at `S`. Also establish that the submission occurred by `T`: a late commit can qualify when its occurrence evidence supports that, but an answer known to occur after `T` cannot appear as an earlier result. If temporal eligibility is uncertain, retain the candidate's raw grade with its uncertain date, and mark the as-of claim uncertain (QX for an otherwise usable unaided S/E); do not turn an already graded answer into U just to represent chronology. Withhold an exact by-T completion fraction when occurrence by T is unresolved. Evidence definitely after `T` is excluded from its displayed answers/grades; the endpoint stays M if no submission was available by T. Retain separate reasons for no assignment, no submission, pending judgment, disputed interpretation and insufficient criterion coverage. Never search for the best or latest successful retry.
5. Classify observed results as S/E/H/U/M/N under the C contract. N takes precedence until the window matures. For matured endpoints, missing submission is M; submitted but unusable judgment is U; usable relevant help is H; otherwise supported independent success/error is S/E. Scoped misread interpretation cannot produce an ordinary E. Preserve the underlying response and grade even when the claim cannot use it.
6. Separately calculate eligibility for each claim: occurrence-window membership, delay, exposure, mode, coverage and baseline comparability. Use `eligible/ineligible/uncertain` plus reasons. An observed correct answer with uncertain time can remain “correct without help” in descriptive history while retained-performance qualification is unknown. Use the [claim-outcomes-1 mapping](tracking-contract.md#4-two-axes-for-every-endpoint): QN, QM, QU, QH, then QX for otherwise graded S/E with a failed/uncertain condition, otherwise QS/QE. Keep all reasons independently of partition precedence. A delayed-outcome metric uses QS with the full matured denominator; it never inherits raw S.
7. Compute transitions only for supported comparable pairs. Compute the dated trend from the same fixed population. Weak-unit history stops at the selected check time even when later points are visible elsewhere in that report. Count distinct targets, units, attempts and exercise families separately; none is automatically a statistical sample size.
8. Compute each cost display with its frozen `cost-membership-1` rule and `cost-cutoff-1`: resolve scope from effective span/context evidence at S, retain the declared full scope/window, derive the effective interval from T and the selected check boundary, then clip/union using the quality rules. Preserve per-point windows and unknown membership. Produce values, reasons and evidence refs. Highlights and what-if scenarios never change the recorded population or grades.

An interactive dashboard and a saved report use this same interpretation. There is no second implementation of “effective grade” inside a chart. The initial release can compute directly from the ordinary store; derived caches are disposable and require no new architecture until a measured limitation exists.

## 7. Saved report payload and replay

Replace the abbreviated `measurement_report` payload with these logical fields. Optional values are explicit nulls; lists may be empty. Nested objects are specified below or in the linked C metric dictionary.

```text
{source: SourcePrefix, evaluated_at: Time, computed_at: Time,
 supersedes_report: Ref?, definition: Algorithm,
 definition_snapshot: {contract_version: text, implementation_digest: Digest?,
   metric_contracts: JSON, status_rule_version: text,
    focus_rule_version: text, timing_rule_version: text,
    exposure_scope_rule_version: text, assistance_rule_version: text,
    cost_rule_version: text, cost_membership_rule_version: text},
 query: {curriculum_refs: Ref[], target_refs: Ref[], cohort_refs: Ref[],
   modes: text[], selected_check: text?,
   baseline_rule: text, endpoint_rule: text, exposure_rule: text,
   history_start: Time?, history_end: Time?,
    cost_scope: Ref[], cost_membership: Algorithm,
    cost_start: Time, cost_end: Time,
    cost_view: through_check/period_to_date, selected_check_cutoff: Time?,
   display_timezone: text, utc_buckets: [{label: text, start: Time, end: Time}]},
 exclusions: [{ref: Ref, reason: text}],
 endpoint_resolutions: EndpointResolution[],
 results: MetricResult[], history: JSON, focus: JSON,
 cost: CostResult, quality: JSON,
 inspection: {highlight: text?}, scenarios: JSON[],
 content_digest: Digest}
```

`SourcePrefix` is section 2's six fields. `EndpointResolution` contains cohort Ref, endpoint ID, target Ref, baseline refs, assigned draft Ref or null, submitted Ref or null, accepted assessment refs, criterion/requirement bindings, observed state, state reason, per-claim eligibility/reasons, comparability/reason, time-evidence sources and exposure refs. Criterion bindings retain underlying judgments, exact local assistance entries (attempt Ref plus index), their time evidence and relevant exposure refs; not just a derived success bit. Freeze `assistance-evidence-1` for new definitions and resolve local help together with external aid conditions. Add the tracking contract's per-claim buckets/qualification/reasons and separately named raw/qualified count objects. Freeze `claim-outcomes-1` in the definition snapshot for new definitions; saved older reports retain their original schema.

`CostResult` retains scope, `membership_rule: Algorithm`, `scope_resolutions: ScopeResolution[]`, declared window, view, requested upper bound, effective window or explicit empty interval, and the evaluation/selected-cutoff basis. Validate agreement among the cohort/query/result membership algorithm and the saved definition version; scope proofs use only refs available at the saved source cutoff. It also retains included span refs and clipped segments, excluded or disputed span refs and reasons, union duration or null, category durations, unplaced known duration, uncertain-membership refs/reasons, unknown-tail run refs, and the accounting envelope or null. Conflicting segments retain supporting span refs and their boundaries. `selected_check_cutoff` is required for `through_check` and null for `period_to_date`; validate it against the selected check or saved day bucket. `history` stores an equivalent cost result per plotted point. `quality` contains separately named counts and limitations, never a weighted quality score. Pending local drafts/measurements are not accepted source records; a live page may show a separately timestamped local pending count, but it cannot pretend that count is reproducible from the library prefix. Existing saved reports keep their original schemas/rules; do not rewrite them as `cost-cutoff-1` outputs.

`metric_contracts` freezes the complete claim definitions from the campaign metric dictionary: units, denominators, exclusions, assumptions and withholding rules. `history` preserves check identities, observed dates/bounds, fixed population and per-date resolutions/counts. `focus` preserves the unit grouping, streams, lexicographic ordering keys, ties, cutoff, reasons and supporting refs. `scenarios` preserve a named hypothetical assumption and its separate result, never a substituted actual endpoint. These are versioned report-output objects, not new independent learning records.

`content_digest` hashes the canonical payload with that member omitted. It includes `computed_at`, source fingerprint, full query, definitions and output. A saved report is immutable: no revision updates its query or results. A new calculation gets a new report ID and may link `supersedes_report`. Reopening shows the stored report; recomputing creates a comparison, not a silent overwrite.

Replay has three distinct results:

| State | Meaning |
|---|---|
| Stored report readable | The saved values and their explanations are present and intact |
| Source verified | The complete referenced prefix and definitions match their fingerprints |
| Calculation reproduced | The compatible calculation implementation, same S and T, and same query produce the same semantic output |

Semantic output comparison excludes a new computation timestamp and the outer report ID; it compares source, definitions, frozen query, resolutions, counts, reasons, history, focus, cost and scenarios. Do not require the new report's entire bytes to equal the old report's bytes. Conversely, byte integrity alone is not calculation reproduction. An unavailable historical implementation permits reading the old result but withholds replay. Import never runs archived code, contacts a model or accepts a current metric as a substitute.

## 8. Export, restore and upgrades

Add `timing_run`, `exposure`, `teaching`, `practice_offer` and `condition_checkpoint` to the portable kind registry. Validate the lifecycle contract's admission, offer ownership, obligation consumption, teaching provenance and prospective boundaries, plus the tracking contract's immutable cohort fields, permitted lifecycle revisions and assignment-before-presentation rule. Include the extended spans, receipts, time evidence, cohort assignment revisions and saved report payloads in full archives. Validate exact-ref closure recursively, including report endpoint resolutions, definition-owned refs, exposure content and timing grants. Revisions referenced historically stay valid even when no longer effective. Empty arrays and unknown values preserve their meaning; they are not missing fields to fill from current defaults.

Validate report source S against receipt boundaries and recompute its prefix fingerprint within the archive. All learning evidence used by the report must exist at or before S. Its referenced definition must be embedded or available within that source; its own report record/receipt occurs after S. A report may contain planned future windows, but not future answers or assessments. Recompute its content digest; validate semantic output only with a supported implementation, otherwise retain an explicit unverified-replay state.

Restore into the existing separate empty store and compare the portable snapshot before activation. No history revision or timer grant is written during that comparison. After activation the operational owner is empty and receives a fresh activation ID. Historical `active` timing-run records remain readable but confer no authority. An old accepted request still returns its receipt; a newly arriving old-activation span is stale. New learning and timer commands begin above the preserved sequence watermark.

Technical upgrades preserve previously missing/unknown facts, source text, answers, assignment identity, accepted correction lineage, timing quality, report definitions/results and receipts. They must not replace unknown time with migration time, reopen a completed task, regrade answers or multiply progress after a target split. New claims needing absent provenance are unavailable for that history. Curriculum changes and model transitions remain explicit semantic changes under the compatibility design, not hidden migration work.

Deletion is separate. The [deletion design](deletion-design.md) specifies archive versus permanent removal, managed-copy cleanup, interruption and report effects. The user accepted [archive plus whole-library deletion](issues/11-deletion-contract.md#answer) for the first release; selective erasure and its format work are deferred. This draft promises neither permanent replay after removing required evidence nor support for a redacted archive format. No deletion, expiry process or external transfer is authorized by this audit.

## 9. Worked adversarial cases and expected outcomes

These are design examples, not real learner histories or an executed storage test. Short labels stand for valid exact refs in a future acceptance fixture.

| Case | Input | Required outcome |
|---|---|---|
| D01 Transaction cut in half | Earlier transaction ends 100; a correction writes assessment101, projection102, schedule103, transition104 in one receipt | S100 and S104 allowed; S101–103 refused. Omitting record102 or the receipt fails import |
| D02 Same S, different history | Two copies have same library ID and S104 but different accepted assessment bytes | Different fingerprints; sequence equality cannot authorize restore or certify replay |
| D03 Late answer | Check window closes Oct9 00:00Z; report S100,T=Oct9 12:00Z contains M; the designated answer occurred Oct8 12:00Z but commits later at110 | Old report stays M. New report may show S/E if judgment and time qualify; timing remains uncertain if supported only by an unqualified client claim |
| D04 Correction, not new learning | Before: 3 improved,2 maintained. Accepted correction recognizes an earlier success | New historical view:2 improved,3 maintained; old report remains3/2. No new attempt or review |
| D05 No best retry | Draft A assigned before submission; A is wrong; fresh verification B succeeds | Endpoint retains A. B is separate verification evidence; substitution rejected |
| D06 Raw clock reversal | Same-run monotonic offsets10000→70000; raw wall time12:00→11:59 | If continuity qualified:60000ms known duration, uncertain placement. No negative duration, fabricated day or established delay |
| D07 Bounded exposure | Outside study Oct7 00:00–Oct8 00:00; answer Oct9 12:00; required gap48h | Possible gap36–60h, so qualification uncertain; using60h to certify it is invalid |
| D08 Two tabs and restore | Old activation A/generation7; new activation B grants1; unaccepted A span arrives | Old receipt retry returns unchanged; new A span stale; answer still accepted; no extra measured time |
| D09 Overlapping effort | Study[0,10), feedback[8,13), setup[13,15) minutes; all qualify as effort | Union15; study8,feedback3,setup2,unattributed2. Sum15, not17 |
| D10 Selected date versus visible trend | Full history contains Oct22; user selects Oct8 for weak-unit flags | No Oct15/22 evidence affects shortlist; full chart can still display later points |
| D11 Misread in a larger exercise | Criteria1–2 ordinary, criterion3 supported misread with saved clarification | Only criterion3's interpretation changes; no error-based flag from it and no automatic success; other evidence survives |
| D12 One unit, several modes | Same knowledge unit has recall E, explanation S and execution U | One flagged unit, recall evidence shown; execution uncertainty retained; no averaged mastery |
| D13 Failure not localized | One criterion covers two units without evidence isolating either | “Needs diagnosis”; do not create two weak-unit flags |
| D14 Same report tomorrow | Reopen same source S and evaluation T after another endpoint matures | Original N remains N; a current report needs a new T and ID |
| D15 Unknown occurrence | Submitted answer accepted, its occurrence time unknown, judgment correct without help | Descriptive success retained with uncertain date; delay/calendar claims withheld |
| D16 Missing historical calculator | Archive passes structural/digest validation, old implementation absent | Stored report readable, source verified, calculation replay unavailable; no model request or substituted values |

Future product qualification must execute these through the actual command handler, persisted records, reopened store and export/restore adapter, in addition to the real-browser interruption probes. The authored C model covers portions of D04/D10/D14 only; it does not qualify transaction closure, timer authority, multi-unit grouping or import. This audit checks the proposed contracts against the cited design files and provides expected outcomes; it does not make those future checks green.

## 10. Readiness and next decision

The [everyday-learning payload delta](../skill-maintenance/everyday-learning-design.md#7-record-changes-needed-for-this-behavior) now adds proposed concern continuity, explicit teaching-to-verification bindings, diagnostic presentation reservations, ordered session scope, cost/priority provenance and exposure-based next-offer eligibility. Its report rule `observed-concerns-2` is a new definition, not a rewrite of the prototype or frozen reports. Reconcile these additions at the same complete-transaction, time-quality and export/restore boundaries; the [acceptance pack](../skill-maintenance/everyday-learning-cases.md) includes concurrency, uncertain presentation and restored repair cases. No new store or service is implied.

The draft and [integrated patches](tracking-contract.md) now specify the missing record roles, source closure, prospective plan creation, assignment/lifecycle rules, qualified count mapping, time quality, ordered correction interpretation and replay behavior. All seven second-audit gaps have concrete design dispositions; no persisted execution is claimed. The metric contract still owns which claims and prioritization rules the product promises. The deletion contract owns deliberate removal. Deployment/store choice and the supported browser matrix remain product implementation decisions, with explicit acceptance requirements above.

The [deletion/report-retention recommendation](deletion-design.md) and [readiness consolidation](readiness-review.md) are now prepared. Review the concrete remaining product choices; do not reopen dashboard layout selection or ask the learner to approve field names. A real policy experiment additionally needs user-selected outcome/cost tolerances; none are inferred here. This audit does not authorize production implementation.
