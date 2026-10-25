# A staged plan for learning observability

Status: finalized observability plan for [Design Baseline 1](../skill-maintenance/design-baseline.md), 2026-10-16. The first descriptive release is part of the main learning-app slices; prediction audits and optimization experiments are deferred. Implementation and live experiments require separate authorization.

## What has actually been done

- The [integrated lifecycle](../skill-maintenance/learning-lifecycle-contract.md) and [tracking/calculation contracts](tracking-contract.md) now patch all seven second-audit gaps. The [closure traces](../skill-maintenance/cross-contract-closure.md) reconcile the fifteen audit scenarios plus additional boundary cases at the document level. No production behavior or learning effect was tested.

- The [everyday-learning continuation](../skill-maintenance/everyday-learning-design.md) connects observation to practice with explicit exposure, fresh-instance, stopping, backlog and return-navigation rules. Its 43 authored cases and two focused source reviews are design evidence; no runtime or learner benefit is claimed. Its record/policy additions and later audit patches are reconciled in Design Baseline 1 and must be implemented in the corresponding main-build slices.

- Four research reports cover measurement validity, sparse-history statistics, dashboard evidence and collection/reproducibility. Each links primary sources and describes access or generalization limits.
- Eight authored numerical cases were executed: missing outcome bounds, changing difficulty mix, duplicated evidence, exact matched-pair randomization, full-cost reversal, unplaced effort, improvement versus maintenance, and repeated peeking. [Script](spikes/analysis-probe.py), [outputs](spikes/analysis-results.json), [interactive explanation](spikes/analysis-prototype.html).
- Three dashboard arrangements share seven authored situations: partial improvement, maintenance, first use, help, correction, curriculum expansion and incomplete effort. [Prototype](spikes/dashboard-prototype.html).
- The selected C has a [detailed contract](c-dashboard-contract.md) and [logic walkthrough](spikes/c-walkthrough.html): computed population filters, formula/evidence dialogs, scenario controls, historical-correction snapshots and frozen reports in memory. The [calculation probe](spikes/c-probe.mjs) reproduces eight authored situations plus filtered and alternate-curriculum cases; the record mapping identifies remaining schema additions.
- Python calculations and JavaScript syntax were checked. Browser opening of `file:` URLs was rejected by browser security policy; no alternate route was used. Rendering, keyboard behavior, responsive layout and actual interactions remain unverified.
- No real learning outcomes, attention, retention improvement, time savings or dashboard usefulness were measured.
- The [data-contract audit draft](data-contract.md) reconciles saved records with the dashboard and compatibility contract: complete transaction receipts, uncertain occurrence times, timer authority after restore, bounded exposure, fixed endpoint assignments, criterion-to-unit attribution and immutable reports. Sixteen worked adversarial cases specify future persisted-system checks; no importer or telemetry implementation is claimed.
- The [deletion recommendation](deletion-design.md) defines archive, curriculum removal, managed-copy deletion, report consequences and fourteen future acceptance cases. The [readiness review](readiness-review.md) separates first-release product choices from runtime qualification and future optimization experiments. Neither document records implementation or deletion approval.

## Campaign decisions before building

| Work | Concrete outcome | State / dependency |
|---|---|---|
| Measurement, statistics, dashboard and collection research | Source evidence and bounded recommendations | Research complete; baseline records the adopted descriptive scope |
| Numerical assumption spike | Explain why the eight tempting conclusions fail or require assumptions | Calculations complete; live learner interpretation remains a qualification task |
| Dashboard spike | Select an everyday entry and appropriate depth of drilldown | User selected C as preferred default on 2026-10-15; retain A/B for their scenarios. Comprehension and browser qualification remain open |
| Metric contract | Approve exact claims, units, exclusions, unavailable states and priority | Finalized for the descriptive baseline; validity still requires real evidence |
| Experiment contract | Specify a future pilot's estimand, margins, burden, allocation and analysis | Open; not required to begin ordinary descriptive measurement |
| Data-contract audit | Resolve all proposed additions against compatibility/export rules | Finalized contract plus later audit patches; real persistence/replay qualification is required during implementation |
| Deletion and report retention | Define intentional deletion without silent loss or false replay guarantees | First-release scope accepted: archive plus whole-library deletion; individual answer/source erasure deferred; no runtime qualification claimed |
| Design readiness | Review scope, seams and remaining risks | Design Baseline 1 finalized; runtime measurement readiness and future experimental readiness remain separate |

The layout preference is settled: the user prefers comprehensive analytical C, while A and B retain useful scenarios. Do not ask for that choice again. A later usability check can ask, on the October8 example, “What changed, and what remains unknown?” The expected authored facts are three improved, two maintained, two repeated errors and one missing check. The revised opening view instead shows four dates and selects October22; it must not silently reuse the October8 expected answer. This tests clarity separately from preference. Do not require the user to review a long checklist, solve another subject exercise or choose statistical machinery.

If an explanation is needed during that usability check, record the first attempt as assisted; after revising the display, use a fresh equivalent example for verification. The preference already provided is not a comprehension result. Usability validation remains open, but does not block recording or developing the selected design direction.

## Proposed implementation slices

Follow the shared [module design](../skill-maintenance/module-design.md). Measurement owns collection, cost membership, tracking and reports, and reads Content, Evidence and Practice through their public interfaces at one declared context. It neither duplicates evidence qualification nor schedules exercises. Application Workflows passes measured budget input into Practice and coordinates prospective tracking assignment with offer creation; Practice does not import Measurement. Carry M01–M10 into the existing slices alongside the metric/collection cases.

### Slice 1 — Trustworthy history and one useful summary

Establish the lifecycle/obligation/offer/teaching identities and raw-versus-qualified evidence fields with the first store schema. Show selected-versus-admitted goals honestly, and preserve pending distinct attempts independently of timer ownership. The comparison-plan UI can follow, but later slices must not need to reconstruct lost provenance.

Include the [four-gap follow-up](../skill-maintenance/integrated-design-closure.md): obligation dispositions/checkpoint scope, descendant correction effects, captured exposure content and checked cross-target relevance. At reporting, apply `cost-cutoff-1` to every selected-date and per-point cost, retaining declared and effective windows and unknown membership. Carry all ten audit cases and the added boundary cases into correction, dashboard and restore qualification; their document traces are not runtime results.

Include the [fourth-audit patch](../skill-maintenance/journey-invariant-closure.md): `assistance-evidence-1` preserves known help without an exact clock, and `cost-membership-1` follows explicit enrollment identities for effort while outcome targets stay frozen. Capture known context at collection, preserve nullable timing and exact hint-entry references, and save membership rules and per-span scope decisions with reports. Carry W01–W08 and the additional boundaries through real correction, shared-cost, saved-report and export/restore qualification. This extends the existing store/query work, not the service architecture.

Build on the real persisted attempt/assessment/help path in the main plan. Add versioned metric definitions, the minimal measurement provenance, nonoverlapping timing with explicit unknown gaps, and a saved report manifest containing S and T. Show a session summary, fixed-target outcome rows, full accounted cost and unavailable later checks. Display meaningful first-use and failed-save states.

Apply the [accepted retention scope](deletion-design.md): archive keeps history, membership changes keep fixed historical comparisons, and whole-library deletion must cover the approved managed-copy inventory. Individual answer/source erasure is deferred beyond the first release; do not implement it by blanking historical records.

Verification uses a real answer through the actual persistence path, reopened storage, retried save, accepted grading correction and export/restore. Confirm that one shared answer remains one episode and that a dashboard view cannot create learning credit. Perform hide/crash/two-tab/clock probes against the selected browser and authoritative store. Completion requires real collection behavior; synthetic fixture arithmetic alone is insufficient.

### Slice 2 — Evidence exploration and useful presentation

Implement the selected analytical workspace as the default dashboard, with A's quick summaries and B's capability notebook available for their specific scenarios. Include target timelines, scoped help and criterion drilldown, a correction path and inspection effort. Add potential-exposure records for answer-bearing views without pretending they were completed study. Preserve filter/context on return and keep practice directly accessible. Analytical comparisons whose data is not yet available must show their prerequisites, not fabricated results.

Verify keyboard navigation, screen-reader relationships, 320 CSS pixel page reflow, visible focus and legible noncolor states in the real browser. Observe a few named interpretation tasks with the learner; record confusion and time rather than calling a coached walkthrough a pass. No population usability or motivation claim follows from one learner's preference.

### Slice 3 — Comparable progress and repair histories

Implement the [routine tracking workflow](tracking-contract.md): preview baseline/population/windows, freeze before answers, assign ordinary offers atomically before presentation, close windows, and stop/replace plans visibly. Provide ordinary history before any plan exists. Use QS/QE/QH/QU/QM/QX for each qualified claim, retain raw grading coverage, and withhold missing-only bounds when its assumptions fail. No silent extra reviews are added.

Once actual delayed history exists, add paired transition tables, maintenance, repair-stage attrition, fixed-cohort trends and exposure-aware retention labels. Show scope revisions and metric/assessor changes. Saved reports remain immutable, while corrected current histories explain what changed.

Replay late arrivals, distinct attempts graded in reverse order, rejudgments, target split/reuse, missing/unresolved/assisted endpoints, ongoing answer views and prospective recovery from unknown exposure. Carry CCA01–CCA15 and the closure boundary cases into the real command/store/query tests. Check each denominator from original eligible cohort to final stage. Compare the report at identical S,T before/after restore; changing T is a new evaluation, not a replay.

### Slice 4 — Investigation of effort and data quality

Add effort breakdowns, paired outcome/cost comparisons, completeness and exclusion inspectors, scenario bounds and tipping points. Show actual versus expected total effort, including preparation/correction/waiting. An analyst can save a reproducible query and scoped table. Known defects can be fixed without awaiting a causal trial.

Verify the eight numerical counterexamples through real report queries. A changing task mix must not appear as comparable learning gain; a missing-cost reversal must remain unresolved. Audit report exports for exact scope and absence of unnecessary answer text. Confirm that chart computation, source correction and saved reports use one effective-history interpretation.

### Slice 5 — Optional prospective prediction audit

Only if a numerical learner model is selected, record frozen forecasts and forward outcomes, benchmark on the same endpoints, compute proper scores and inspect calibration with dependence and horizon explicit. Keep forecasts separate from observed capability and direct FSRS review records.

Qualification includes leakage checks, benchmark comparison, family-aware uncertainty feasibility and sensitivity to plausible model assumptions. Too little evidence produces “calibration not established.” A better score does not automatically change scheduling or permit review omission.

### Slice 6 — Bounded efficiency comparison

Choose one named limitation and one candidate change. Before a trial, agree on relevant retained outcomes, cost, meaningful savings, allowable loss, extra assessment burden and stopping rules. Qualify the actual assignment/analysis through a simulation feasibility study; this campaign's exact toy probes do not replace it.

A prospective comparison retains all assigned units and missingness, includes the cost of evaluation, uses fresh designated endpoints and reports both harms and benefits. Adoption requires the prespecified retained-performance and cost decision, not merely significance or a shorter answer time. Inconclusive remains inconclusive; preserve the baseline. No automated policy promotion is in this plan.

## Acceptance scenarios

These are future product qualification requirements. Only the authored numerical counterparts named above have been calculated.

| ID | Scenario | Required observation |
|---|---|---|
| A01 | No practice / no matured checks | Unavailable outcomes with useful next action; no zero mastery |
| A02 | Five later successes, two known earlier | Three improvements and two maintained; no five-new-skills claim |
| A03 | One missing endpoint | Visible original denominator and scenario bounds; no imputed grade |
| A04 | Help applies to one criterion | Only affected target evidence loses independent status |
| A05 | Same episode supports several targets | Coverage preserved; independent sample count not inflated |
| A06 | Task mix shifts toward easy checks | Strata and changed composition visible; no pooled gain claim |
| A07 | Misread or grading correction | Old evidence retained; history corrected at original event time |
| A08 | Curriculum adds/splits targets | New needs visible; old achievements neither multiplied nor erased |
| A09 | Integrated repair succeeds; delayed check absent | Immediate repair separated from unknown retained repair |
| A10 | Full costs reverse apparent savings | Preparation/correction/waiting included; no answer-time winner |
| A11 | Overlapping or unplaced time | Union counts once; unknown overlap stays separate |
| A12 | Crash, freeze, ownership takeover | Acknowledged intervals survive; unknown tails and stale claims visible |
| A13 | Wall-clock jump | Reliable duration retained separately from uncertain calendar placement |
| A14 | Recompute saved report tomorrow | Same S,T, manifest and fingerprint reproduce unchanged maturity/results |
| A15 | Late answer / accepted revision after cutoff | Old report unchanged; new report explains historical change |
| A16 | Answer inspected on dashboard | Potential exposure retained; no fake study completion or FSRS review |
| A17 | Keyboard/mobile/accessibility use | All essential evidence/actions available without color or hover dependence |
| A18 | Forecast after outcome or leaked training data | Excluded from prospective forecast evaluation with reason |
| A19 | Repeated fixed-sample significance peeking | No premature adoption; declared analysis/stopping rule enforced |
| A20 | Four favorable randomized pairs | Sharp-null result distinguished from effect precision/noninferiority |
| A21 | Unsupported assessor interpretation | Abstain/review without inventing a learner deficit |
| A22 | Referenced data intentionally removed | Explicit policy and invalidated replay claims; no silent reconstruction |
| A23 | Repeated checks and date selection | Same selected skills on every plotted date; visible missing/helped/ungraded counts; selected-date details and cost agree; old report contains no later dates |
| A24 | Guided workflow and free exploration | Current numbered step and one action; result shown before Next; Back/Restart restore known state; free filters pause the guide instead of leaving mismatched instructions |
| A25 | Five weakest knowledge units | Explainable dated evidence and recovery status; ties visible; no future-date leakage; unknown/helped/ungraded evidence separate; corrections remove invalid flags; fewer eligible units do not cause padding or automatic remedial work |

## What remains open, and when to stop

The source investigations, default-dashboard preference and first-release deletion scope are complete within their scopes. Design Baseline 1 closes drafting/review for the included scope. Comprehension/browser validation and real persistence/report correctness remain qualification work. A real optimization experiment additionally needs the user's concrete trade-offs and a qualified statistical decision method. It is acceptable for the first app to provide trustworthy descriptions while causal efficiency remains unestablished.

Stop expanding analytical machinery when it does not change a named learner or design decision. Add a fitted model, sequential method, graph visualization or separate service only when a measured limitation justifies it. Do not turn “sophisticated” into more screens, more metrics or more infrastructure than the question needs.

The saved-record/query reconciliation after C is now a [detailed draft](data-contract.md), traced from the [display-to-record mapping](c-dashboard-contract.md#6-records-needed-behind-every-display). The baseline adopts the descriptive metric/data contracts; the [audit decision](issues/09-data-contract.md) preserves its history and remaining runtime concerns. The [deletion scope](deletion-design.md) is accepted for the first release. The [readiness review](readiness-review.md) identifies implementation setup and qualification work. Claims/ranking are baseline defaults; selective-deletion scope stays deferred. Design finalization does not authorize implementation. More layout selection is unnecessary.

The user subsequently reported three concrete problems with C: terminology, absence of a useful time-trend representation, and unclear workflow steps. The prototype and contract were revised for those problems first. Record that feedback as a failed clarity observation in the previous version; do not call either version usable from arithmetic checks alone.
