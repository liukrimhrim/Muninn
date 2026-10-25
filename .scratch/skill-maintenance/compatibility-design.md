# Keeping curriculum progress through software changes

Status: compatibility contract finalized in [Design Baseline 1](design-baseline.md), 2026-10-16. Stable identities, retained progress, atomic corrections and portable history are required. Implementation, real migration fixtures and runtime verification remain outstanding.

## 1. What the learner can rely on

A software upgrade preserves saved curricula, selected goals, source material, exercises, answers, assistance, assessments and corrections, actual reviews, pending work and due dates. The learner continues the same work without a reset or an automatic regrading pass. A later algorithm can reach a different conclusion, but the history and the reason for the change remain inspectable.

“Saved” means the server committed the record and acknowledged its revision. Text still marked “saving” in a browser is not yet part of the portable history. The browser keeps that text through a failed request and offers to retry; it must not claim that an export contains unacknowledged edits.

The supported direction is **new software reads or migrates old saved data**. Every released data format must have a documented path to the current version, possibly through intermediate converters. Old software need not understand new formats and must refuse to write them. The first design assumes one learner library and one application writer. Moving that library to another host is supported through restore; synchronization and merging independently edited copies are outside this contract.

Keep three operations distinct: a technical upgrade preserves learning meaning; a curriculum revision can change what is being learned; a model/policy transition can change an interpretation or future schedule. Never bundle the latter two into a silent storage migration.

## 2. Identity and version rules

| Value | Exact role |
|---|---|
| `library_id` | Opaque UUID assigned once to the learner library; preserved by backup, restore and migration |
| `id` | Opaque UUID for a curriculum, target, attempt or other record identity; never derived from its title, text, row position or model output |
| `revision` | Positive integer starting at 1 within `(kind, id)`; changing a definition or saved state appends a revision, never overwrites the old one |
| `sequence` | Unique increasing positive integer assigned when a record revision is committed in this library; preserved on restore; orders commits, not the time learning happened |
| `format_version` | Integer describing the portable logical record format; starts at 1 |
| `store_schema_version` | Integer describing a particular database layout; starts at 1 and can change without changing the portable format |
| Algorithm identity | Name, implementation version, parameters and protocol/state-format version where applicable; independent of all the above |

Use these value types throughout the contract:

```text
Ref   = { kind: string, id: UUID, revision: positive_integer }
Time  = UTC string in YYYY-MM-DDTHH:mm:ss.SSSZ form
Record = {
  kind: Kind, id: UUID, revision: positive_integer,
  sequence: positive_integer, recorded_at: Time, payload: KindPayload
}
```

Integers must be exactly representable JSON integers, at most `9007199254740991`; reject overflow rather than round. Timestamps are instants, independent of display timezone. An occurrence time such as `submitted_at` remains separate from `recorded_at`. Missing historical information is represented by an explicit nullable field and its provenance, never by the migration time or an invented default observation.

Every historical reference uses an exact `Ref`. “Latest target” is a navigation query, never an assessment binding. Criterion and section IDs are opaque strings local to their enclosing exercise or curriculum revision. The next revision must name its expected base revision when written; stale edits fail with a conflict and preserve the submitted draft. Ordinary writes cannot reuse an existing `(kind, id, revision)` with different content.

Revisions are append-only snapshots in ordinary application tables, not a separate event-stream service. The application chooses current revisions through the rules below. Retiring content appends a status revision; records referenced by learning history remain present. Intentional user-requested deletion would need its own design and is not disguised as migration or retirement.

The [deletion design proposal](../learning-observability/deletion-design.md) now defines that separate operation: archive preserves history; whole-library deletion removes approved managed copies; selective erasure requires an explicit portable-format decision before support is claimed. It does not permit an upgrade to drop records or weaken ordinary import validation.

## 3. Portable logical records

The [module-review follow-up](module-design-review-response.md) removes duplicate duration/role fields and moves correction effects into `schedule` in this unreleased proposal. The portable data contract is public and versioned; repository code and physical layout are private. This is a proposal revision, not a migration already run on learner libraries.

The [module ownership contract](module-design.md#one-owner-per-rule-and-record) assigns each kind one ordinary writer, with semantic decisions supplied by the named domain owner. Application Workflows coordinates their changes in one Library command transaction; modules do not commit independently or use the portable schema to bypass another owner's public interface. Physical repositories may change while these logical identities and meanings remain stable. Read-only restore validation invokes each owner through the application and cannot create learning events.

The [integrated lifecycle contract](learning-lifecycle-contract.md) owns the additional admission, authoring, obligation/offer and exposure-recovery fields; the [tracking contract](../learning-observability/tracking-contract.md) owns plan lifecycle and qualified result objects. These named additions complete this unreleased format. Include `teaching`, `practice_offer` and `condition_checkpoint` in the portable registry; validate their exact references, transition rules and complete receipt membership. New report definitions separate raw and claim-qualified counts, while old saved reports keep their original schema/definitions.

The subsequent four-gap patch adds explicit obligation dispositions, Practice-owned schedule correction effects and checkpoint scope/status to those same records, plus exposure scope/relevance and declared-versus-effective cost intervals in the data contract. Preserve these fields through export/restore. Validate one effective obligation disposition and current obligation/need per target, no duplicate effective review effect, target-scoped reservation decisions, exact relevance/requirement refs, and a report's saved cutoff/definition. Historical invalidated consumption remains inspectable but cannot count as current work completed. No new service or storage family is required.

The [fourth-audit follow-up](journey-invariant-closure.md) additionally makes nested assistance time nullable with explicit evidence, and freezes a versioned effort-membership rule alongside cost scope refs. Export/import preserves the help fact even when its timestamp is unknown, and preserves the distinction between following an enrollment identity for cost and binding an outcome to an exact target revision. The data contract owns both resolution rules and their saved-report provenance.

The [everyday-learning payload delta](everyday-learning-design.md#7-record-changes-needed-for-this-behavior) additionally specifies concern continuity, exercise review, eligibility/presentation history, ordered multi-curriculum session scope, cost quality and due-versus-next-offer state. These are additions to the unreleased proposal, with their own acceptance cases; they do not fabricate a migration from an already shipped format.

The [observability data-contract addendum](../learning-observability/data-contract.md) completes this unreleased proposal. For the affected fields, use its transaction-membership receipts, occurrence-time evidence and nullable uncertain timestamps, explicit study completion status, criterion-scoped interpretation, requirement-to-knowledge bindings, timing/exposure records and saved-report payload. The tables below remain the base contract; the addendum explicitly supersedes their abbreviated forms where named. It is a design audit, not a verified importer or permission to implement.

The following is the logical persistence contract, independent of SQL table layouts. Fields listed below are required; `?` means the value may be `null`, not that a writer may omit the field. Lists may be empty unless a rule says otherwise. A `Ref[]` preserves order when order has meaning. Text and JSON values are data, never executable instructions. No record contains credentials.

| `Kind` | `KindPayload` fields and rules |
|---|---|
| `source` | `title: text`, `text: text`, `origin: text?`. Preserve literal captured text and every referenced revision. |
| `knowledge` | `form: fact/relation/group/procedure`, `statement: text`, `scope: text`, `sources: Passage[]`, `dependencies: {ref: Ref, role: text}[]`, `status: draft/accepted/disputed/retired`. A relation has one identity even if displayed as both a node and an edge. |
| `target` | `content: Ref[]`, `action: text`, `mode: recognition/recall/explain/reconstruct/select/describe_procedure/execute`, `conditions: text[]`, `evidence_requirements: {id: text, statement: text}[]`, `status: draft/accepted/disputed/retired`. Accepted targets have nonempty content and requirements. A target specifying execution does not claim the app can observe execution. |
| `curriculum` | `title: text`, `purpose: text`, `sections: {id: text, title: text, targets: Ref[]}[]`, `status: active/retired`. The same target may appear in several sections; progress counts it once per selected exact contract. |
| `enrollment` | `curriculum: Ref`, `goal_order: Ref[]`, `status: active/paused/archived`, `checkpoints: {label: text, achieved_at: Time, rule: Algorithm, basis: Ref[]}[]`. The goal list selects targets present in that curriculum revision. Its `practice` entries separately record unstarted/active/paused admission; selection alone creates no dated backlog. Checkpoints retain any actually awarded completion milestones and their criteria; no upgrade invents one. A single learner can keep several enrollments. |
| `exercise` | `family_id: UUID`, `prompt: text`, `targets: Ref[]`, `criteria: Criterion[]`, `reference_response: text`, `hints: Hint[]`, `expected_seconds: {setup: integer, answer: integer, feedback: integer}`, `status: draft/accepted/held/retired`. Criteria bind the exercise to exact target definitions. |
| `session` | `enrollments: Ref[]`, `budget_seconds: integer`, `started_at: Time`, `ended_at: Time?`, `status: active/stopped/completed`, `stop_reason: text?`, `next_action: NextAction?`. Enrollment refs are nonempty, unique and ordered by the selected session scope; shared exact targets still have one schedule. Measurement derives elapsed duration including breaks and the separate effort breakdown from qualified timing evidence; neither is a second session-owned duration field. Session completion is not curriculum mastery. |
| `attempt` | `session: Ref`, `exercise: Ref`, `follows: Ref?`, `purpose: initial/clarification/verification/practice`, `response: text`, `started_at: Time`, `submitted_at: Time?`, `assistance: Assistance[]`, `status: draft/submitted`. Purpose describes the encounter, never scheduling credit. Practice resolves owner/extra per target from the bound offer and its release/correction history; one larger attempt may have mixed roles. Measurement derives any pre-submission duration from qualified timing evidence. Draft revisions are retained; submission freezes this attempt's response and binding. Later learner responses receive new attempt IDs linked through `follows`. |
| `study` | `session: Ref`, `targets: Ref[]`, `kind: initial/repair`, `content: text`, `started_at: Time`, `completed_at: Time?`. Completion records actual study/help completion, not a demonstrated capability. Merely proposing or displaying help is insufficient to invent completion. |
| `assessment` | `attempt: Ref`, `assessor: Assessor`, `results: CriterionResult[]`, `interpretation: ordinary/supported_misread/unresolved`, `explanation: text`, `raw_response: text`, `supersedes: Ref?`, `revision_reason: text?`. Records here have passed acceptance validation. Invalid/unaccepted model results remain in `operation`. Reassessment of the same bound task appends a revision under the same assessment ID. |
| `schedule` | `target: Ref`, `type: recall/capability`, `policy: Algorithm`, `state_format: text`, `engine_state: JSON`, `due_at: Time?`, `need: initial/independent_check/repair/clarify/held`, `basis: Ref[]`, `previous: Ref?`, `reason: text`. Its stable ID is the recall stream or capability schedule identity; one active schedule per learner and exact target contract. Prior schedule decisions remain available. Practice owns the lifecycle contract's `resolution_rule` and `check_effects` on schedule revisions. Pin the qualification claim identity in `policy.parameters.qualification_claim` when a decision uses one; null means no qualification was performed, never a default claim. |
| `review` | `schedule_before: Ref`, `attempt: Ref`, `assessment: Ref`, `rating: again/hard/good/easy`, `occurred_at: Time`, `supersedes: Ref?`, `revision_reason: text?`. Used only for actual comparable recall ratings. A rating correction is another revision of the same review, not another retrieval. Capability checks use attempts/assessments/study directly. |
| `projection` | `target: Ref`, `rule: Algorithm`, `basis: Ref[]`, `as_of: Time`, `observations: Observation[]`, `hypotheses: {claim: text, alternatives: text[], evidence: Ref[], uncertainty: text}[]`. Preserve the last published interpretation; observations cite assessment criteria and shared episode identity. This is not a new source of learning evidence. |
| `selection` | `session: Ref`, `purpose: text`, `needs: Ref[]`, `candidates: {exercise: Ref, expected_total_seconds: integer}[]`, `chosen: Ref?`, `reason: text`, `policy: Algorithm`, `basis: Ref[]`. Retain the decision as made; do not replace it by rerunning a new selector. |
| `mapping` | `from: Ref[]`, `to: Ref[]`, `relation: equivalent/reorganized/split/merged/changed/retired`, `disposition: proposed/accepted/rejected`, `criterion_map: {from_exercise: Ref, from_criterion: text, to_target: Ref, to_requirement: text}[]`, `reviewer: text?`, `reason: text`, `supersedes: Ref?`. This explains compatibility; it cannot itself generate a success or recall review. |
| `operation` | `purpose: draft_material/assess_answer`, `inputs: Ref[]`, `input_snapshot: JSON`, `model: Assessor`, `status: pending/running/succeeded/failed/interrupted`, `outputs: Ref[]`, `raw_response: text?`, `error: text?`. Store the credential-free request snapshot and exact input bindings before an external request. Authoring additionally records `intent`, bounded request-group retries and acceptance disposition under the lifecycle contract. Application Workflows owns lifecycle and exact bindings; Content/Evidence supplies the typed accepted/rejected disposition and validated output refs. The coordinator does not reinterpret the result. |
| `transition` | `scope: Ref[]`, `category: curriculum/assessment/policy`, `before: Ref[]`, `after: Ref[]`, `actor: text`, `reason: text`. Records the coordination of an intentional semantic or policy activation atomically with its resulting revisions. It references Practice-owned schedule effects; it does not contain scheduling decisions. Technical migration receipts are separate metadata. |
| `activity_span`, `session_feedback`, `measurement_cohort`, `measurement_report` | Exact payloads are defined in the [observability contract](observability-design.md#8-collection-and-reproducibility-contract). They preserve measured/unknown effort, optional subjective feedback, fixed comparison scope and saved reports across architecture changes. |

The observability kinds are additions to this still-unreleased format 1 design, not an already performed migration. All their evidence and scope references obey the same revision/closure rules; saved reports reference a source sequence preceding the report's own commit. Technical upgrades preserve them, including unknown durations, original metric definitions and historical report values. Dashboard caches remain disposable.

Nested values have these exact fields:

```text
Passage = {source: Ref, start_utf8_byte: integer, end_utf8_byte: integer, quote: text}
Criterion = {id: text, requirement: text,
             covers: [{target: Ref, requirement_ids: [text]}]}
Hint = {id: text, text: text, criterion_ids: [text]}
TimeEvidence = {field: text, precision: exact/bounded/unknown,
  earliest_at: Time?, latest_at: Time?,
  basis: qualified_clock/self_report/unavailable/legacy_unknown,
  raw_client_at: Time?, explanation: text}
Assistance = {shown_at: Time?, time_evidence: [TimeEvidence],
  text: text, criterion_ids: [text], study: Ref?}
CriterionResult = {criterion_id: text,
  outcome: demonstrated/error/not_shown/cannot_judge,
  response_quotes: [{start_utf8_byte: integer, end_utf8_byte: integer, quote: text}],
  reason: text}
Observation = {assessment: Ref, criterion_id: text, attempt: Ref,
  outcome: demonstrated/error/not_shown/cannot_judge, assisted: boolean}
Algorithm = {name: text, version: text, parameters: JSON}
Assessor = {kind: human/model, name: text, version: text,
            protocol_version: text, parameters: JSON}
NextAction = {kind: answer/clarify/study/verify/review/unresolved,
              refs: [Ref], explanation: text}
```

Offsets are half-open byte ranges in the referenced literal UTF-8 text and must fall on character boundaries; the slice must equal the saved quote. Every exercise criterion has at least one covered target requirement. A target is demonstrated only when all its required criteria are demonstrated under its assistance conditions. Empty quotes are permitted for `not_shown`/`cannot_judge`; these outcomes are never converted into errors by import. `Observation.assisted` describes known relevant in-attempt assistance for its criterion, validated against the saved assistance entries, independently of whether their times are exact. False is not certification that no external aid existed. Overall independence additionally resolves scoped exposure under the data contract's [assistance rule](../learning-observability/data-contract.md#known-assistance-with-uncertain-time).

Each `Assistance.time_evidence` contains exactly one entry with `field: shown_at`. Exact precision requires equal non-null bounds and matching `shown_at`; bounded precision requires ordered non-null bounds and null `shown_at`; unknown requires null bounds and null `shown_at`. The entry records actual help during the bound response, not a proposed hint, uncertain display or feedback after submission. Preserve its text and criterion scope even when clock quality is unavailable. Nested entries are addressed by the exact attempt revision and zero-based assistance index; import retains their order. The data contract defines capture, qualification and correction behavior.

Every required target requirement must actually be covered by the exercise before it can establish that target; partial coverage remains partial evidence. An accepted mapping requires a non-null reviewer and a reason. Referenced kinds and local criterion/requirement IDs must match their declared roles, not merely resolve to some existing record. Duration/cost values are nonnegative; trusted domain end/submission/completion times on a common time basis cannot precede their own start times. Preserve anomalous raw client wall-clock anchors separately with explicit uncertain placement; they may reverse during a clock adjustment and must not be promoted into trusted ordering, daily placement or minimum-delay evidence. A reliable same-run monotonic duration can survive that anomaly. The [observability data-contract audit](../learning-observability/issues/09-data-contract.md) must reconcile these quality fields before collection implementation. A `submitted` attempt has a submission time; a `draft` does not. A replacement assessment or review must supersede the current revision of the same identity. Validate these rules at write and import boundaries.

One accepted assessment lineage exists per submitted attempt. Each replacement names the current assessment in `supersedes`; concurrent replacements conflict. A model-assessed submission commits the submitted answer, submitted-offer state, credential-free pending `operation` with exact submitted refs, and command receipt together. There is no committed submitted answer awaiting a model without a saved operation. This rule covers model-assessed submissions; a later human correction uses the existing assessment-correction command without a fabricated model operation. Accepted assessment revisions, affected projections and schedule decisions likewise commit atomically; no half-applied correction is visible. A changed exercise contract requires the mapping/reinterpretation procedure in section 6, not a revision pretending the old prompt asked something else.

A curriculum's current progress view joins its selected target refs to effective projections, schedules and unfinished sessions. A past completion checkpoint remains attached to the enrollment revision and evidence under which it was awarded. Changing a curriculum's requirements can change the current denominator, but must show the added requirements separately from that past achievement. Neither a checkpoint nor “session completed” means permanent retention. If a corrected assessment undermines a checkpoint, retain the historical award and mark its evidence superseded in the current view.

Retain idempotency receipts as a separate portable list: `{request_id: UUID, command: text, input_digest: text, result_refs: Ref[], committed_sequence: integer}` (`CommandReceipt`). The digest is 64 lowercase hexadecimal characters from SHA-256 of the RFC 8785 canonical logical command input, excluding transport credentials. Repeating the same request and digest returns the saved result; repeating its ID with different input is a conflict. Preserve these receipts across upgrades so a browser retry cannot create a second answer after restart. Imported receipts never re-execute their commands.

## 4. Snapshot and export format

The browser downloads one UTF-8 JSON file named `library-<library_id>-<export_id>.learning.json`. Its top-level shape is:

```text
{
  format: "memorization-library",
  format_version: 1,
  export_id: UUID,
  exported_at: Time,
  library_id: UUID,
  writer_release: string,
  through_sequence: integer,
  records: [Record],
  receipts: [CommandReceipt],
  integrity: {algorithm: "sha256-jcs", digest: lowercase_hex_string}
}
```

All keys are required. `through_sequence` is zero for an empty library, otherwise the maximum saved sequence. `records` includes **all revisions**, ordered by sequence; receipts are ordered by request ID. Current record selection is deterministic: the greatest revision of an identity, subject to assessment supersession and curriculum activation rules. References within earlier records remain fixed. An export of the entire library avoids missing transitive definitions; partial curriculum export and cross-library merges are deferred.

Compute `integrity.digest` over the UTF-8 canonical JSON of the top-level object with the entire `integrity` member omitted, using [RFC 8785 JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785/). Hashing neither normalizes learner text nor establishes that an assessment is correct. It detects accidental alteration, not malicious authorship; this is not a signed archive. Reject duplicate JSON keys, invalid Unicode, non-finite numbers and unsupported versions rather than silently converting them.

For migration/restore equality, use a separate **learning fingerprint**: SHA-256 of the canonical object containing only `format_version`, `library_id`, `through_sequence`, `records` and `receipts`. Export time, export ID and writer release necessarily change between exports and are excluded from this comparison. The archive integrity digest still includes them. When a format changes, compute the comparison fingerprint through the explicitly specified former-format view, not by pretending different formats have identical bytes.

Application Workflows drives export through fixed owner export functions over one Library read snapshot; owners serialize their public logical records from their private physical layouts. Library supplies receipts, sequence metadata, canonicalization and integrity checks. Import/staging and physical migration use the corresponding fixed owner functions and semantic validators; Library does not import domain modules or interpret their tables. No dynamic serializer registry is needed.

Export uses one consistent database read snapshot, including receipts and the sequence watermark. No record saved later may leak into that snapshot with an older watermark. It contains no API keys, authentication tokens, machine paths needed for operation, or external file dependencies. Model inputs/outputs stored under the credential-free contract remain data. Search indexes, render caches and database migration logs are excluded. Existing schedule state and published projections are included because their old algorithms may no longer be executable.

Import first parses and validates without changing the current library. Validate integrity, types, UUIDs, unique sequences, contiguous per-identity revisions, reference closure, source/answer quotes, target/criterion coverage, supersession lineages, receipt references and all schedule/projection bases. Each receipt's committed sequence must be within the snapshot watermark. Historical references to superseded judgments remain valid history; only current effective projections must reflect the accepted correction chain. Unknown record kinds or fields require a supported format conversion, not silent dropping. No model call or network fetch is part of import. Never manufacture new targets to satisfy missing references.

Restore into a separate empty store, preserving IDs, revisions, sequence numbers, timestamps, decisions and receipts. Validate it, close and reopen it, then compare its logical snapshot with the source archive. Activation replaces the whole local library only after that check; the previous library stays recoverable. An active library with a higher sequence than the archive is not overwritten through ordinary restore: open the older snapshot separately for inspection, or pursue an explicit recovery decision. Restoring an archive is not an algorithm upgrade.

A sequence comparison is valid only within the same uninterrupted library lineage. Before replacing an existing store, also compare its records and receipts with the incoming snapshot: any divergent record or local record absent from the archive blocks ordinary replacement, even if the sequence numbers happen to match. Two copies edited independently are a conflict, not a supported synchronization operation. Repeating the same restore is a no-op only after full logical equality is established.

The physical store may normalize these records into tables. For the proposed SQLite store, keep `library_id`, the next sequence and `store_schema_version` in metadata; keep a `migration_history` entry for each committed change. These structures and indexes may change without altering the portable record contract. The implementation must provide a read/export adapter for the pre-migration layout, so schema differences never become an excuse to compare only row counts.

## 5. Upgrade and recovery procedure

For the initial single-writer application, migrations run during maintenance before normal writes resume. There is no zero-downtime or distributed migration requirement. Every release declares its supported store schemas, export importers and browser command protocol. It checks compatibility before opening a writable application connection. An older browser with an unsupported protocol is asked to refresh while retaining its unsaved text; it cannot submit through a changed contract.

Each specific migration is identified by `{id, from_schema, to_schema, implementation_digest}` and has named preconditions, transformations and validation rules. It must be deterministic and local: no model calls, no learning timestamps set to “now,” no generated review events. Record the source snapshot fingerprint, source sequence, source/target application releases and verification result in its receipt. A new migration is written only when an actual layout change requires it.

### Normal path

1. **Quiesce.** Stop accepting new mutations and drain in-flight transactions. Save ongoing model operations as interrupted; do not wait for the provider or restart the request automatically. Already committed answers remain unassessed. Ensure no other application writer is active. Capture the source sequence `S`.
2. **Snapshot.** Produce a consistent restorable database backup and a logical snapshot for comparison. Open and validate the backup. If it cannot be created or verified, stop before changing the original. For SQLite, use its [backup API](https://sqlite.org/backup.html), not a copy of only the main file from an active database.
3. **Migrate.** With normal writes still disabled, run the complete pending migration chain in one database transaction. Schema-version updates and migration receipts commit with the transformations. Before commit, validate record meaning, references and the invariants below. A failure rolls back the transaction; a retry starts from the last committed schema.
4. **Reopen and verify.** After commit, close and reopen the store with the new application. Recheck structural integrity and the logical comparison, then read each enrollment's current progress, pending task and schedules through the application layer. Do not make model calls or mark a read as learning.
5. **Resume.** Enable writes only when verification succeeds. Preserve `S` in the migration receipt so recovery can tell whether later learning has occurred. Start new commands above the preserved sequence watermark. Keep the verified backup available until explicitly replaced by the backup-retention policy; this design adds no silent backup deletion.

For SQLite, structural verification includes both `integrity_check` and `foreign_key_check`; the former does not detect foreign-key violations. Application-level `Ref` and meaning checks remain necessary. An application-managed version can use `user_version`, rather than SQLite's internal schema counter. These are documented [SQLite behaviors](https://sqlite.org/pragma.html); the application's sequence, migration receipts and semantic comparisons are our design choices.

### Interrupted and failed paths

| Failure point | Required recovery |
|---|---|
| Before backup verification | Original is unchanged; discard only the incomplete backup created by this operation, then retry when possible |
| During the migration transaction | Let database recovery establish the committed state; read version/receipts instead of guessing whether commit happened. If the old version remains, retry the chain; if the new version committed, continue verification |
| After commit, before writes resume | Stay in maintenance. If verification fails, restore the verified backup while the old writer is stopped, open it with the compatible release, and verify before resuming |
| After new learning writes (`sequence > S`) | Do not restore the old backup over them. Preserve the current store and export if readable; use a forward repair or a specifically tested converter retaining those new records. Otherwise stay in recoverable read-only mode and report the affected library |
| Unknown newer schema or missing migration step | Refuse writable startup without changing the store; identify the required compatible release/converter |
| Corrupt backup, broken references or altered archive | Refuse activation and report the specific failing records; never replace the problem with an empty library or partial “successful” import |

Backup restore is not an inverse schema migration. A new layout may have information an old layout cannot express. If the old executable understands the portable format, a separately validated restore may be possible; otherwise fix forward. There is no blanket promise that every old binary can resume new work.

### Moving to a different storage engine or host

Use export/restore instead of pretending an SQL migration can cross engines. Quiesce the source at `S`, export it, restore into the empty destination, then verify the same invariants and application read paths. Keep the source read-only through cutover. Activation records one durable choice of the active store; startup must refuse writes if that choice is ambiguous. Only one store may accept learner writes. If interrupted before activation, the source remains authoritative; after activation, the destination does. Once the destination records new learning, switching back requires preserving those new records through the same recovery rules. Hosting selection and any external transfer still require separate authorization.

### Comparison invariants

For a technical upgrade, compare source and destination through the same logical format. Exact IDs/revisions, literal answers/source text, timestamps, criterion outcomes, assistance, correction chains, recall ratings, curriculum membership, pending work, engine state, due timestamps and command receipts must match. The domain sequence watermark does not advance merely because software was upgraded. Metadata about the migration may differ; disposable indexes may be rebuilt.

When the portable format itself changes, the release must specify a lossless field mapping and a comparison view back to the former format. Every old field must be retained or demonstrably recoverable; a new required field with no historical evidence is nullable/unknown until populated through a real action. If the proposed format cannot express the old meaning, that is a blocked release, not permission to reset the library. Database equality alone does not prove these invariants.

## 6. Curriculum revisions and evidence continuity

A new curriculum revision is available separately from the learner's active enrollment. Creating it does not switch an ongoing session. An enrollment activation records a `transition` from its old revision to its new one; the same transaction records mappings and the new selected target order. Previously completed sessions retain their exact enrollment and exercise references.

| Change | Identity, evidence and scheduling behavior |
|---|---|
| Rename a chapter or move an unchanged target | New curriculum revision, same target refs. Keep all evidence and schedule IDs/due dates. Resume the target by ID, not its old list index |
| Rewrite display wording while the exact evidence contract stays the same | Prefer a curriculum/exercise display revision without changing the target. If content refs change, require a reviewed `equivalent` mapping; spelling similarity alone is insufficient |
| Add a target | New selected/unstarted goal; its active initial need starts on admission to practice. Existing targets keep their state; show “one new target” rather than erasing prior completion |
| Remove a target from this curriculum | Keep its history. Stop presenting it for this enrollment; another active enrollment can still use it. Its due timestamp remains stored, so reactivation does not postpone an overdue check |
| Change conditions or the required performance | New target revision. Keep the old achievement visible under its old definition; the new revision starts unresolved until compatible evidence is explicitly established or a new check occurs |
| Split one target | New target identities and a `split` mapping. An aggregate old pass/fail is insufficient to grade each child. Retained criterion evidence may be reinterpreted explicitly; otherwise children remain untested |
| Merge targets into an integrated capability | New target identity and a `merged` mapping. Existing component evidence stays available, but an integrated success is not the sum of separate passes. A grouping-only change belongs in curriculum organization/practice bundles and needs no new target |
| Correct a wrong source claim | Retain the old source/knowledge revisions. Mark affected current definitions and dependent exercise mappings disputed/held; continue unrelated targets. Earlier observed responses remain historical evidence, not proof that the corrected claim was learned |

For a reviewed equivalent target revision, preserve the schedule identity and due date through an explicit schedule revision and mapping reference; do not add a review. Equivalence must cover meaning, action, conditions, required evidence and recall comparability. If any of these is uncertain, retain the previous schedule under the old target and hold the new target's compatibility decision.

For a split, merge or changed contract, a reinterpretation cites the exact prior attempt, assessment criterion and destination requirement in `mapping.criterion_map`. A new published projection cites those sources and the accepted mapping; it does not fabricate another attempt or alter the earlier assessment. Missing criteria stay `not_shown`/`cannot_judge`. All resulting facets retain the same attempt ID, so one historical episode never becomes several independent successes. A correction to the originating assessment invalidates/recomputes dependent projections and mappings before new progress is presented.

Reinterpretation does not backfill FSRS review events. New non-equivalent recall streams begin without a fabricated rating history. A new capability may display supported historical evidence while retaining a pending independent check; it does not acquire a seven-day interval from a newly created mapping. Only an accepted equivalent-contract mapping can carry an existing schedule forward unchanged.

The first release needs retained revisions, organization changes and explicit held mappings. This contract defines future split/merge semantics without requiring a general merge/split editor in that release. Unknown compatibility stays visible and local to affected targets; it is not a reason to reset the entire curriculum.

### Worked example: the same progress under three changes

This is an authored example, not the user's learning history. A vocabulary target asks for the meaning of the invented word “mavo,” whose supplied meaning is “blue.” Its saved answer is “blue,” its accepted assessment is unassisted, and its next due instant is `2026-10-21T16:00:00.000Z`.

1. Replacing the web framework or moving from SQLite to another store preserves that exact target, answer, assessment, schedule identity and due instant. There is no new attempt.
2. Moving the target from “Lesson 1” to “Colors” changes the curriculum revision and enrollment selection, but leaves the same target and schedule in place. An already open exercise stays bound to its original revision.
3. Adding “given blue, produce mavo” creates a different retrieval contract. The first achievement stays visible. The reverse-direction target is untested until it has appropriate evidence; it does not inherit a review or a seven-day interval from the original direction.

## 7. Assessor, learner-model and scheduler replacement

An assessor change applies to future answers by default. Existing accepted judgments remain effective. Requested reassessment of an old answer uses its original prompt, rubric, assistance and response, produces an explicit superseding assessment with a reason, and recomputes dependent state atomically. That computation uses the original learning time, not the date of the reassessment. Reassessing a historical prompt against a different target requires section 6's mapping, not pretending the learner answered a new exercise.

When a corrected transition already has later offered/answered descendants, apply [descendant-correction-1](learning-lifecycle-contract.md#correction-after-later-checks): retain original offers/answers, record effective scheduling consequences separately, and re-anchor only a still-qualifying real formerly owned check. Pending answers retain a scoped hold; unsubmitted invalidated slots become practice. Replay actual eligible recall ratings without altering historical `schedule_before` refs or inventing ratings. The [case traces](integrated-design-closure.md) specify the October 15 result and alternatives when conditions fail.

A learner-model change preserves the last published projections and produces candidate new projections from the same effective evidence. A recorded policy transition activates them with their model identity and explanation. Old and new outputs remain inspectable; forecasts are not converted to observations. If a model cannot interpret some old evidence, it labels the affected estimates unavailable rather than discarding the source or assigning zero mastery.

A scheduler upgrade preserves existing schedules unless a separate policy transition is activated. The transition names affected schedules, old/new algorithm versions and parameters, replay inputs, previous/new due dates and reasons. A compatible FSRS state upgrade may use the actual effective rating stream in original occurrence order; no invented reviews, use of today's timestamps or automatic replay of disputed ratings. Use the [ordinary occurrence-order resolver](learning-lifecycle-contract.md#effective-event-order-and-recomputation) here too: exact ties use original submission receipt sequence for deterministic processing but cannot establish recovery/streak order for conflicting simultaneous evidence. Uncertain order holds affected advancement; model completion/commit order cannot manufacture learner chronology. The simple capability policy uses the [existing event transitions](first-build-plan.md#evidence-diagnosis-and-reviews).

When an old engine is unavailable, retain its serialized state, policy identity, last due date and history. The application can display pending reviews and save a new answer, but it cannot silently advance that schedule with a substitute engine. Hold its next scheduling decision until a tested replacement is activated; unrelated supported schedules continue. This is a recoverable limitation, not a progress reset. A release replacing the only supported engine must include that transition before it qualifies as a working upgrade.

## 8. Browser continuity and unfinished work

Ordinary check ownership follows the [practice-offer contract](learning-lifecycle-contract.md#4-one-due-opportunity-two-tabs-and-late-grading), separately from timer and diagnostic reservations. Restore preserves submitted owners and unsatisfied obligations; two distinct answers are both retained, with at most one consumption of a given opportunity. Releasing a pending check is explicit and preserves its eventual result as extra evidence. No browser timeout silently transfers a submitted owner.

Saved attempt drafts are normal versioned records and appear in export. On reopening, the browser loads the same attempt and exact exercise revision. Repeated submission uses the original request ID and returns its receipt. A different answer under that request ID is a conflict, not an overwrite.

The UI distinguishes “draft saved,” “answer saved—assessment pending,” “feedback available,” and “needs review after a content change.” An interrupted authoring/assessment operation is shown for explicit retry using its retained input snapshot; restore never contacts the old provider automatically. Before accepting a late result, verify the exact input revision and the operation's current status. A result for an abandoned or superseded request is retained as an unaccepted result and cannot attach to new content or generate learning credit.

An unchanged historical exercise can be resumed after an architecture upgrade. If a curriculum change disputes its meaning, retain the draft and offer a fresh suitable exercise with a reason; the old draft is not graded as a failure. Switching curricula while an attempt is open does not change that attempt's target bindings.

## 9. Concrete acceptance cases

These are requirements for implementation, not tests reported as run. Use actual historical release stores when they exist. The first release creates the baseline fixture and proves export/restore; do not invent a fictional released schema merely to claim migration coverage.

The baseline fixture contains two subject curricula sharing one unchanged target, an independent success, a hinted attempt, an ambiguous answer, a supported misread correction, one superseded grade and recall rating, a pending repair, an overdue schedule, a saved draft, an unassessed submitted answer, a retired target and a request whose response was lost after commit. Record exact expected IDs, revisions, answers, assistance, schedule states and timestamps independently of the migration implementation.

| Case | Input/change | Required result |
|---|---|---|
| C01 Round trip | Export fixture, restore into empty store with network disabled, reopen | Same logical snapshot and receipts; same curricula, feedback, dates and saved drafts; no model calls |
| C02 Physical upgrade | Change actual released database layout while logical format stays unchanged | All section 5 invariants match; next answer appends once and continues the selected curriculum |
| C03 Multi-release path | Oldest retained fixture through every documented step | Every step validates; skipped direct paths are refused; oldest history remains accessible |
| C04 Crash before commit | Interrupt at each write in migration, then reopen | Entire old or entire committed new schema; no mixed revisions; safe retry |
| C05 Crash after commit | Interrupt before reopen checks or before enabling writes | New startup re-verifies before serving mutations; no migration replay or duplicate credit |
| C06 Failed verification | Introduce broken reference, altered quote or due-date drift | Upgrade stays in maintenance; original recoverable; error identifies the actual mismatch |
| C07 Recovery after use | Save an answer after upgrade, then request old backup restore | Ordinary rollback refuses to erase it; current store preserved for forward repair |
| C08 Future/invalid archive | Newer version, unknown field/kind, duplicate key/ID/sequence, bad digest, truncated data or missing reference | Import refuses before activation; current library untouched; no invented placeholders |
| C09 Reorder/shared target | Move target between sections and retain it in two curricula | Same evidence and schedule; no new review, duplicated target completion or changed due date |
| C10 Added/removed target | Add one new requirement, then retire an old membership | New need is explicit; prior achievement retained; another enrollment's target stays usable |
| C11 Split/merge | Split an aggregate target with partial criterion evidence; merge components into integration | Reuse only scoped evidence, preserve shared episode identity, leave unsupported child/integration claims unresolved; no backfilled reviews |
| C12 Correction after mapping | Correct a source assessment already used by an accepted mapping | Dependent projections/schedules update once, prior decisions retained, unrelated work unchanged |
| C13 Policy replacement | Replace assessor/model/scheduler with a different version | Existing history unchanged until an explicit transition; proposed date/estimate changes explained; no fake review |
| C14 Unavailable engine | Restore valid state without its old scheduler/model implementation | History and due dates remain visible; affected new decisions held; no fallback reset; working-upgrade gate fails if required continuation is unavailable |
| C15 Retry and stale client | Lose submit response, upgrade, retry same request; also retry with different text or unsupported client protocol | Same result for identical request; conflicts/refresh for the others; no duplicate attempt and no loss of browser draft |
| C16 Late model output | Upgrade with an unassessed saved answer; provider returns after request interruption or input revision change | Exact answer survives; late output cannot overwrite active state; explicit retry is a distinct operation |
| C17 Time and absence | Export in one timezone, restore in another with missing/ambiguous observations and overdue work | Same UTC instants, local display only; no missing-to-failure conversion or due-date rebasing |
| C18 Snapshot concurrency | Answer commits immediately before/after export's read snapshot | Archive contains a complete transaction or none of it; records, receipts and watermark agree |
| C19 Engine/host cutover | Import at `S` into another store, interrupt before/after activation, then record a destination answer | One authoritative writable store; full logical equivalence at cutover; later destination answer cannot be lost by switching back |
| C20 Divergent copies | Two restored copies receive different answers but reach the same sequence | Ordinary restore refuses replacement; neither answer is silently dropped or merged |

The upgrade smoke test additionally uses the real browser: resume the saved draft, submit a new answer, inspect the corrected judgment, and reopen a due curriculum after a process restart. Comparing only JSON, table counts or a startup HTTP status is insufficient. Grading quality and learning benefit remain separate evaluations.

## 10. Decisions and limits

This design chooses stable domain identities, append-only revisions, a self-contained versioned JSON snapshot, explicit semantic transitions, and maintenance-time transactional migration with a verified backup. The reasons are concrete: old target bindings must remain meaningful; retries must not duplicate episodes; interrupted upgrades must not discard saved answers; unavailable models must not prevent reading history.

Rejected alternatives are freezing the architecture, serializing framework/ORM objects as the portable format, restoring only completion percentages, automatically regrading all old answers, and creating a generic distributed compatibility service. Each either loses necessary evidence or adds machinery unrelated to the first single-learner workflow.

Exact SQL DDL and migration code depend on the implementation's actual schema and later changes; they are intentionally not fabricated here. The logical records, conversion obligations, activation/recovery rules and acceptance outcomes above are specified now. Hosted multi-writer rollout, account transfer, synchronization, intentional deletion and unsupported rich media need separate scope if later selected. Public deployment and implementation remain unauthorized.
