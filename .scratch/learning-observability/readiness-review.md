# What is ready, and what remains to decide

Status: design finalized in [Design Baseline 1](../skill-maintenance/design-baseline.md), 2026-10-16. The ledger below separates the adopted design from implementation setup, runtime qualification and future experiments. Historical audit notes describe the path to this baseline; their old pending-review wording no longer blocks included design behavior.

## 1. Preserve the decisions already made

| Requirement or preference | Where it appears in the proposed system |
|---|---|
| General memorization learning across subjects | Facts, relations, connected explanations and procedures share the evidence model; operational examples do not define the product |
| Web-based app | Browser intake, practice and progress; the reference design is local and single-learner, with hosted expansion outside this baseline |
| Larger exercises with exact-gap diagnosis | Criterion/requirement/unit bindings; ambiguous composite failure stays unlocalized until supporting evidence exists |
| A trivial misread is not a knowledge gap | Scoped interpretation, saved clarification, correction history and separate fresh checks |
| Progress survives architecture evolution | Stable identities, preserved evidence and schedules, explicit semantic changes, versioned export/restore |
| Progress motivates and effort must be justified | Observed improvement, maintenance, later checks and full effort shown together; no universal mastery/efficiency score |
| Comprehensive analytical dashboard C | Selected default; quick orientation and capability detail retain A/B's useful roles |
| Clear language, time trends and sequential guidance | Revised C prototype and display contract; user responded “looks better” and later “looks good” |
| Five weakest knowledge units | Dated evidence, ties, recovered/unknown distinctions, mode-specific streams and no automatic blame for every unit in an exercise |

The last two user reactions support the presentation direction. They are not evidence of valid mastery estimation, learning benefit or complete accessibility. No preference is reopened here.

## 2. First usable observability scope

The baseline adopts an initially descriptive product: accepted answers and corrections, scoped evidence drilldown, fixed-target history, improvement/maintenance, visible help/missing/unresolved outcomes, full effort with timing-quality limitations, and saved reports. The weak-unit shortlist is a transparent review aid, not an automatic remediation or review-omission policy. Meaningful later-check displays wait for actual qualifying history.

The application remains one coherent learning loop with observation built into it. Do not build an analytics platform before an answer can be saved, assessed, corrected and resumed. Use the [six observability slices](plan.md#proposed-implementation-slices) alongside the [main build plan](../skill-maintenance/first-build-plan.md), not as a separate product.

Archive and curriculum removal fit the ordinary revision model. The user has accepted [archive plus whole-library deletion](deletion-design.md) for the first release. Individual answer/source erasure and its format work are deferred. Runtime qualification and confirmation of any actual deletion remain required; the release-scope choice is settled.

## 3. Decision ledger

| Topic | Current state | What is actually needed next | Does it block the first descriptive release? |
|---|---|---|---|
| Scope and C layout | Settled by the user | Preserve them | No new choice |
| Descriptive metrics and weak-unit rule | Baseline adopts the [C contract](c-dashboard-contract.md) and `observed-concerns-2` | Implement the stated meanings and qualify real inputs; keep the ranking advisory | Design settled; runtime/validity claims still need evidence |
| Saved records and query semantics | Finalized [data contract](data-contract.md), lifecycle/tracking extensions and review corrections | Implement and qualify correction, exposure, cost, historical reads and real persistence | Design settled; a checked document does not establish runtime correctness |
| Archive, deletion and report retention | [First-release scope accepted](issues/11-deletion-contract.md#answer): archive plus whole-library deletion; selective erasure deferred | Qualify the documented managed-copy cleanup and interruption behavior when implemented | Scope settled; runtime qualification still required |
| Reference deployment | One local single-learner application and SQLite are the baseline | Select actual environment during authorized setup; hosted/multi-user operation needs an amendment | Setup gates execution, not design finalization |
| Model integration | Bound inputs and acceptance rules designed; provider/model not selected | Choose an authorized endpoint and credentials before any live private-material request | Yes for live intake/assessment; no transmission authorized here |
| Browser support and accessibility | Source affordances/probes specified; local prototype inspection previously blocked | Select supported browser matrix; execute real keyboard/reflow/focus/interruption tests | Release qualification, not another layout vote |
| Learner comprehension and assessment validity | Positive presentation feedback; no complete semantic/usability qualification | Observe named tasks on fresh examples and review assessor judgments on real accepted scope | Required before claiming validity/usability; not grounds to ask for a large checklist now |
| Predictive mastery model | No fitted model selected | Add only for a named decision and qualify forecasts prospectively | No; remain unavailable initially |
| Policy optimization experiment | Existing [comparison decision](issues/08-experiment-contract.md) remains open | For a concrete future trial, agree retention loss, meaningful saving, burden, allocation and stopping rules | No; it gates causal efficiency/adoption claims, not ordinary progress reporting |

This avoids treating every open question as a reason to block every part of the product. In particular, no learner must choose a statistical noninferiority margin just to see correct answers, maintained skills or recorded minutes. Conversely, those descriptive screens cannot establish that the learning method is more efficient.

## 4. Qualification by seam

The [module/interface proposal](../skill-maintenance/module-design.md) now assigns each record and shared rule an owner, declares acyclic dependencies and defines atomic workflows across owners. Measurement consumes qualified evidence and historical practice views; it does not implement a competing grader, scheduler or chronology rule. These architectural contracts add M01–M10 to implementation qualification. The [review response](../skill-maintenance/module-design-review-response.md) additionally resolves named claim ownership, duration ownership and correction holds, and strengthens crash/conflict checks. Portable records are public data with single-writer ownership; static access checks do not constitute runtime isolation. Documented modularity is not yet enforced encapsulation or measured maintainability.

| Boundary | Evidence required before it is called working |
|---|---|
| Answer → accepted assessment → learner state | A real bound answer through the actual save/accept path; scoped help, misread/abstention, correction and retry; no duplicate learning episode |
| Accepted state → current dashboard | Same effective-history resolver; exact denominators, supported unit attribution, no later-date leakage and no outcome-based cohort trimming |
| Timer → effort totals | Real hide/crash/two-tab/clock probes and reopened records; unknown tails, stale claims and overlapping time remain visible |
| Saved report → export/restore | Complete receipt boundary, exact S/T, original definition, matching source identity and honest replay-unavailable states |
| Content change → continued curriculum | Unrelated work and due needs preserved; mappings do not multiply progress; incomplete evidence remains incomplete |
| Archive/delete → retained or removed history | The [fourteen retention cases](deletion-design.md#6-acceptance-cases), with actual managed-copy cleanup for advertised deletion capabilities |
| Display → learner interpretation | Fresh, limited interpretation tasks; no coached answer recorded as independent comprehension; accessible operation checked in the supported browser |

The existing numerical probes establish authored arithmetic and model behavior only. No runtime test result is invented to complete this table. Production implementation needs its own authorization; qualification then proceeds on the actual application rather than on fake-green fixtures.

## 5. Remaining campaign work and stopping point

The pass-by-pass notes below are design history. Their old pending-review statuses are superseded for baseline behavior by the user's finalization request and the current ledger above. They remain accurate about unperformed runtime/empirical work.

### Fourth pass: known help and effort continuity patched

The [journey and invariant audit](../skill-maintenance/journey-invariant-audit.md) found two drafting gaps across fifteen journeys. The user-requested [follow-up](../skill-maintenance/journey-invariant-closure.md) now preserves known in-task help with bounded/unknown display time and defines frozen effort membership across enrollment revisions. The outcome population stays fixed while whole-curriculum cost follows explicit enrollment identity; shared work counts once, and corrected attribution changes new reports without rewriting saved ones. All eight cases and seven boundaries have concrete design outcomes. Canonical records, tracking, display and build plans are reconciled. The existing [data-contract investigation](issues/09-data-contract.md) keeps its broader policy/qualification dependencies. Several other suspicions were rejected as already covered; this bounded patch is not proof that no further gaps exist, and the runtime/empirical boundaries below still apply.

### Third pass: four interactions patched with concrete outcomes

The [integrated design audit](../skill-maintenance/integrated-design-audit.md) found four gaps after the earlier patch. The user requested their correction, and the [follow-up closure](../skill-maintenance/integrated-design-closure.md) now specifies descendant correction, recoverable caught-up status, shared-content exposure and historical effort cutoffs. A valid October 8 later answer keeps its October 15 review after an earlier grade is invalidated; replaced failures remain history without permanently blocking current completion; cross-target reveals affect conditions without awarding achievement; and earlier cost displays exclude later work. All ten original cases and eleven additional boundaries have design traces. The existing policy/data tickets remain open for their broader dependencies, not because these four outcomes are still unspecified. No production work or new learner experiment was performed.

### Second pass: lifecycle and integration gaps patched

The [cross-contract audit](../skill-maintenance/cross-contract-audit.md) found seven specific gaps. The requested patch addresses their named cases in the [lifecycle contract](../skill-maintenance/learning-lifecycle-contract.md) and [tracking contract](tracking-contract.md): initial success, selected-versus-admitted goals, checked teaching/variant generation, owned/ordered attempts, prospective exposure recovery, comparison-plan creation and separate qualified aggregation. The [closure traces](../skill-maintenance/cross-contract-closure.md) cover all fifteen audit cases and additional boundary cases. The third pass and its follow-up above demonstrate why coverage of those original cases was not complete integration proof.

A correctly graded but timing-ineligible answer now has raw S/E plus QX for the affected claim, preserving grading coverage and the full planned denominator. The proposed defaults are concrete and reviewable; runtime correctness and their practical learning value still require later qualification. The C prototype remains an authored illustration with its own declared rules and was not changed by the patch.

### Everyday learning behavior was still underspecified

The subsequent user challenge correctly identified that a final consistency review was not the only work left. Five substantive areas now have a [detailed proposal](../skill-maintenance/everyday-learning-design.md) and [43 authored acceptance cases](../skill-maintenance/everyday-learning-cases.md): meaning and age of weakness evidence, genuine exercise variation/comparability, daily priorities/backlog, persistent bounded repair, and dashboard-to-practice actions. Two focused primary-source reviews constrain the design. Review found and corrected method-reuse rejection, exposure bypass on reopen, answer leakage through summaries, correction-preview errors, assisted-repair loops, chained-concern preemption, unknown-time starvation, uncertain browser presentation and ambiguous repair-cycle binding.

These are now drafted behavioral contracts, not validated learning policies. The three-prompt/two-cycle limits, 24-hour exposure deferral, waiting-time order and new shortlist remain explicit proposals. The existing browser prototype still uses its original ranking; no product code or new learner experiment was run. The everyday-learning ticket remains open for the concrete policy discussion, and its record changes belong in the consolidated data audit. The subsequent integration patch completes the seven named omissions; that is distinct from qualification of the whole product.

The research reports, C design, data draft, accepted deletion release scope and everyday-learning continuation now provide a reviewable proposal. The finalization request now adopts the written claims/ranking, practice-priority, exposure/stopping defaults and first-release reference scope. Actual implementation/setup and model use still require authorization; future experiment trade-offs wait for a named candidate change.

The readiness ticket should track ordinary measurement readiness separately from future optimization readiness. Its first-release dependency on the experiment-contract decision is removed; that dependency remains for any future claim that a changed policy saves effort without unacceptable learning loss. This changes dependency scope, not the experiment's unresolved status.

Stop expanding dashboard variants, statistical methods or infrastructure unless an unresolved requirement calls for them. Selective deletion and its format question are explicitly deferred beyond the first release. Preserve the finalized baseline. Revisit a concrete policy only for a named requirement, implementation failure or observed outcome; do not default to another broad research campaign.
