# Removing material without misleading the learner

Status: first-release scope accepted, 2026-10-15, and included in [Design Baseline 1](../skill-maintenance/design-baseline.md) on 2026-10-16. The user accepted archive plus whole-library deletion; individual answer/source deletion is deferred. This is a design document. No data is deleted, no retention job is created, and production implementation remains unauthorized. The [decision ticket](issues/11-deletion-contract.md#answer) records the scoped acceptance; future selective-erasure details remain proposals.

## 1. Recommended behavior

Use **Archive** when the learner wants to stop studying a curriculum while preserving progress. Use **Remove from this curriculum** when the outline should change. Reserve **Permanently delete** for an explicit request to remove stored information, with the resulting loss of evidence shown before confirmation. Correcting wrong material or a wrong grade remains a separate action.

The accepted first-release scope is archive plus whole-library permanent deletion; ordinary curriculum revisions remain the way to change membership. Individual answer/source deletion is deferred. Its future requirements are recorded below, but no selective-delete control is included initially. The current portable format requires complete historical records; silently blanking a field cannot satisfy that contract. Accepting this release boundary does not approve any actual deletion.

| Action | Learning material and progress | Scheduling and dashboard | Reversible? |
|---|---|---|---|
| Archive a curriculum | Preserve material, original answers, grades, corrections and reports | Stop requests originating from that enrollment; keep it available in archived history | Yes, reopen the enrollment |
| Remove a target from a curriculum | Append a curriculum revision; preserve the old definition and its history | Current scope changes visibly; a frozen comparison retains its original membership | Yes, restore membership through another revision |
| Correct material or grading | Preserve original evidence and accepted revision chain | Recalculate only justified current conclusions; saved reports retain their prior values | A further correction is possible; no silent overwrite |
| Permanently delete the library | Remove all learner content, progress, schedules, reports and identified app-managed copies for this library | No surviving personal dashboard or automatic restoration | No in-app undo after completion |
| Selectively delete material or answers, later | Remove approved content and its dependent copies; preserve unrelated learning evidence | Mark affected history unavailable and hold unsupported conclusions; do not manufacture failure or success | No in-app undo after completion |

Archiving one enrollment must not suspend a shared target still selected in another active curriculum. Its past time remains past effort. Archived membership is a display filter, not permission to improve an old trend by changing its denominator. Reopening preserves pending needs; overdue checks are visible and can be selected within a session budget, without inventing missed failures or completed reviews.

## 2. Scope and copies

The deletion preview distinguishes **managed copies the app can act on**, **known copies outside that control**, and **unknown copies**. A list of downloaded exports is not proof that those files still exist or that the list is complete.

| Location | Proposed responsibility |
|---|---|
| Authoritative store and its content-bearing auxiliary files | Include the library's records, drafts, operations, timing, reports and journal/WAL files in the approved scope; stop writers before removal |
| App-managed backups and recovery snapshots | Inventory and include copies containing the approved content; an inaccessible copy means cleanup is incomplete |
| Controlled browser storage, pending requests and open views | Invalidate the library session, clear its acknowledged caches/drafts, reject stale writes and clear connected views; an unreachable context is explicitly unconfirmed |
| Search indexes, generated previews, temporary exports and diagnostics | Remove content-bearing derivatives; do not treat “cache” as permission to retain them |
| User-downloaded exports, manually copied files and system backups | State that they are outside the app's deletion scope; identify known exports without claiming enumeration or removal |
| Material already sent to a model provider | State that local deletion does not confirm provider-side deletion; any provider-specific action needs its own supported capability and authorization |

Do not write answer/source text into operational logs merely to make debugging easier. This reduces extra copies; it does not justify asserting that no old copy exists. No keystroke logging, cross-site tracking or new telemetry provider is introduced.

For the proposed SQLite deployment, deleting rows is not a sufficient erasure claim. SQLite documents retained deleted content in free space, limitations of `secure_delete` for some virtual-table storage, and WAL as part of persistent database state. The implementation must qualify its actual file/storage cleanup path, including auxiliary files and app-managed backups. This design promises removal from the stated application scope, not forensic sanitization of physical media or independently managed backups. [SQLite VACUUM](https://www.sqlite.org/lang_vacuum.html), [secure_delete limitations](https://www.sqlite.org/pragma.html#pragma_secure_delete), [WAL state](https://www.sqlite.org/wal.html#the_wal_file).

## 3. Whole-library deletion workflow

The interface uses a separate settings action. Routine cleanup continues to offer Archive. The permanent action is not a side effect of account navigation, a failed migration, a curriculum edit or a blank dashboard.

1. **Prepare an impact preview.** Identify the exact library and current source cutoff; show counts of curricula, answers and saved reports, managed backup locations/copy counts, known external copies and unconfirmed locations. Show that all progress in this library will be lost. A temporary preview may show titles to the user, but the deletion log must not retain those titles or content.
2. **Confirm that specific scope.** No preselected permanent action and no hidden default to preserve a backup. “Export first” is an explicit separate option, with the warning that this creates a copy the deletion will not remove. If the content or managed-copy inventory changes after the preview, recalculate and require confirmation of the changed scope.
3. **Stop reintroduction.** Quiesce writes and exports, invalidate pending model operations and timer ownership, and revoke the current library session. A late assessment result or old browser retry cannot recreate the library. A new library receives a new identity. If the writer cannot be stopped, do not begin destructive cleanup.
4. **Record minimal recovery state, then remove approved copies.** The application keeps a content-free local operation marker outside the deleted store so interruption cannot look like success. It contains an operation ID, opaque library ID, approved scope version, phase and per-managed-location completion state. It contains no answers, titles, source hashes, graded results or command input digests. Do not create the usual pre-upgrade recovery backup during deletion.
5. **Verify and report scope accurately.** Verify each controlled location after cleanup and reopen the application. Report “deleted from this app” only when all in-scope managed copies are confirmed removed. List out-of-scope copies separately. Partial failure is “deletion incomplete” with the remaining locations, not success. Do not start a fresh populated library or restore a backup automatically.

The operation marker supports idempotent resumption, not a second learning ledger. Managed locations use opaque storage identifiers; do not copy a source title embedded in a filename into the recovery marker. Before any irreversible removal, cancellation can return to the unchanged library. Once removal begins, a retry resumes the same approved scope; it never rolls back by resurrecting deleted content. New locations/content require a new preview. The generic completion receipt can be dismissed; no long-term retention of learner content is needed to explain that a deletion occurred.

An unreachable browser profile cannot be silently counted as cleared. The proposed first release should minimize durable browser copies and make the authoritative-save state explicit, but “local app” does not by itself establish that all browser caches are controlled. Qualification must name the supported browser/storage setup. Do not offer a deletion promise stronger than that setup can meet.

## 4. Selective deletion: semantic contract and release gate

The future action is **delete this information and its affected copies**, not merely hide a row. Before it can ship, the application must calculate and show the actual impact against saved records. Start from selected record identities and all their revisions, then inspect every content copy and evidence dependency.

| Affected object | Required treatment |
|---|---|
| Original source or answer | Remove selected content across all revisions, drafts and pending transport copies |
| Quotes, assessor packets, raw model responses and generated feedback | Remove dependent content-bearing records, even if the copy is paraphrased or embedded in a larger packet |
| Shared exercise covering several units | Treat the answer and any combined feedback as one record; disclose the impact on every affected unit. Do not silently slice a free-text answer and assert that the remaining grade is unchanged |
| Knowledge, exercise or rubric containing deleted source material | Include dependent content in the preview; retain an independently sourced definition only when its continued use and lack of forbidden copied content are supported |
| Assessments, review ratings, projections and schedule state | Remove unsupported derived outcomes; retain an explicit evidence-unavailable state. Hold dependent scheduling where surviving evidence cannot safely reconstruct it |
| Saved reports containing affected material or results | Delete those reports under the proposed policy, rather than retain grades or a miniature copy of the content by default |
| An otherwise unrelated report whose complete source prefix included the erased record | Its displayed results may survive if they contain no affected content/results, but original full-prefix verification/replay cannot be claimed. Show that limitation; do not replace its old fingerprint with a new one and call it unchanged |
| Remaining independent curriculum progress | Preserve its identity, answers, judgments and pending work; no whole-library reset or blanket regrading |

The conservative recommendation is **do not keep affected grades or progress summaries merely to make the chart look continuous**. Those results are themselves information about the deleted work. Keeping a historical score without its source is a different user choice and would need explicit retention semantics. Archive already supplies the usual “keep my progress” path.

Dependency inspection is not a full-text search alone. An answer may appear in model input snapshots, assessment quotes, free-form explanations, report snapshots or exports. The schema must declare content-bearing fields and evidence dependencies. If a record cannot be safely separated, include the whole affected record in the impact preview; if the impact cannot be bounded, refuse the selective operation and offer archive or whole-library deletion. Do not use an unverified model paraphrase as a guarantee of erasure.

**Worked effect:** one larger answer supports three targets, and two other answers support two unrelated targets. Deleting the larger answer removes its response, copied feedback and all three unsupported results. The two unrelated results remain. The learner is not marked wrong on the first three targets, and the system does not describe two surviving successes as “100% of the original five.” A new check may establish new evidence; deletion itself does not.

For a retained fixed cohort, distinguish **evidence removed** from no answer, ungraded work and incorrect work. Keep the original planned denominator only where its membership is permitted to remain; expose the removed portion and withhold comparisons that need it. If the target definitions themselves were deleted, withhold that cohort report instead of preserving revealing labels or inventing anonymous comparable targets. Deliberate removal is not ordinary missing-outcome sensitivity analysis.

### Why selective deletion needs a format decision

The current [data contract](data-contract.md) requires complete revision chains, exact references, all records in receipt ranges and full-prefix fingerprints. The following shortcuts are invalid:

- A new “deleted” revision while old revisions still contain the answer is retirement, not deletion.
- Replacing an old payload with empty text under the same identity/revision falsely claims unchanged history.
- Dropping records while silently accepting broken references or receipt gaps weakens import validation for every library.
- Keeping original command input hashes or verbatim deletion manifests can retain information that the user intended to remove.

Before exposing selective deletion, specify a portable redacted representation that distinguishes intentionally unavailable records from corruption, preserves unrelated identities and receipt boundaries, and makes old-prefix replay unavailability explicit. It must also retire affected idempotency responses: an old request may be recognized and refused, but cannot return the deleted response or execute again. Normal records and genuine corruption keep the existing strict validation. Old readers must reject the unsupported representation.

This is a named unresolved format design, not an instruction to build a generic deletion framework now. A precise follow-on decision is: **what redacted record/receipt representation preserves unrelated history without retaining deleted information or falsely validating its old fingerprint?** It is required only if selective deletion is included in a release. The first-release recommendation avoids pretending that this decision has been resolved.

## 5. Backups, restoration and retention defaults

There is no automatic expiry of evidence needed by retained learning history or saved reports in this proposal. Do not invent a 30/90-day policy or silent deletion of old reviews. Disposable indexes can be rebuilt; a saved answer is not a cache. Unacknowledged drafts remain visibly pending and are not advertised as exported progress.

App-managed backup deletion is part of the explicitly approved permanent-delete scope. For selective deletion, any backup containing the erased information must be removed or replaced by a verified sanitized copy before declaring managed cleanup complete. Preserve unaffected history in the active store and verify a sanitized recovery path before destroying the last valid recovery copy. If that cannot be done, stop before destructive work; do not silently choose between losing unrelated progress and retaining deleted information.

A user-held export can reintroduce deleted data. The restore UI must distinguish technical restoration of retained history from deliberate import of an older copy that may contain removed material. Where a local deletion record identifies that library/copy, surface the conflict and require a separate explicit choice; do not automatically merge it or replay old commands. With no surviving record on a new installation, the app cannot reliably know that this data was deleted elsewhere. State that limit rather than promising global prevention.

The upgrade contract still preserves progress. Permanent deletion is an intentional exception with explicit scope; it must not become a justification for migration loss. Conversely, an upgrade's default backup behavior must not silently preserve material during an explicitly authorized deletion.

## 6. Acceptance cases

These are future qualification requirements, not tests reported as run.

The accepted first release requires R01–R09, R12 and R13. R10, R11 and R14 concern deferred selective erasure and do not block that release.

| ID | Case | Required observation |
|---|---|---|
| R01 | Archive one of two curricula sharing a target | History unchanged; the remaining enrollment can still schedule that target |
| R02 | Remove a difficult target from the current outline | New scope visible; old fixed-cohort denominator and saved report unchanged |
| R03 | Correct a source or grade | Revision path preserves the old evidence; no permanent deletion invoked |
| R04 | Preview library deletion, then another answer is saved | Confirmation becomes stale; new impact shown before any removal |
| R05 | Export first | Downloaded copy clearly excluded from the later managed deletion claim |
| R06 | Browser/model response arrives after deletion starts | No recreated records, new grades or resumed timer |
| R07 | Crash during cleanup | Content-free marker survives; next launch shows incomplete and resumes the approved scope without restoring deleted content |
| R08 | Managed backup cannot be reached | Status remains incomplete; no claim that all managed copies were removed |
| R09 | Verify the proposed SQLite deployment | Actual database, WAL/journals, controlled indexes/temp copies and managed backups checked through the qualified cleanup path; no claim about physical-media sanitization |
| R10 | Selectively delete one shared answer | All affected copied content/results removed; unrelated answers preserved; no failure grade or improved ratio fabricated |
| R11 | Unrelated report used a full source prefix containing erased data | Honest replay-unavailable status; no substituted original fingerprint |
| R12 | Restore an old user-held export | Explicit reintroduction path; no automatic restore, merge or command re-execution |
| R13 | Selective erasure representation is unsupported | No selective-delete control advertised; imports refuse it without weakening ordinary corruption checks |
| R14 | Selective deletion requested, impact cannot be bounded | No destructive attempt; explain the unbounded dependency and offer archive/whole-library alternatives |

Use distinctive synthetic content in future deletion fixtures, covering every declared copy path; inspect logical records and retained storage artifacts as appropriate. A substring scan can help locate a known test marker but cannot prove that all paraphrases or unknown external copies are gone. Qualification needs the dependency audit and copy inventory as well as execution/restart tests.

## 7. Accepted first-release scope

The user accepted archive plus whole-library deletion for the first release. Archive preserves progress; curriculum revision changes membership; permanent deletion requires its own explicit scope confirmation. Selective erasure and its format work are deferred. The proposed treatment of individual deleted grades/reports in section 4 is retained for future design review, not promoted to an accepted or implemented capability.

No personal retention deadline, provider policy, physical erasure guarantee or approval to delete has been inferred. The [readiness review](readiness-review.md) separates this product recommendation from later implementation tests and experiment choices.
