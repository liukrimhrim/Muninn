# Seeing learning progress and the effort it costs

Status: measurement requirements included in [Design Baseline 1](design-baseline.md), 2026-10-16. Progress must motivate the learner and make outcomes versus full effort inspectable. Read this foundational design with the later observability, data and tracking contracts, which control their explicitly revised rules. No telemetry collection or recurring monitoring is authorized.

Follow-up: the [observability campaign](../learning-observability/map.md) now supplies four focused research reports, numerical counterexamples, dashboard alternatives, an [expanded design](../learning-observability/spec.md) and a [staged plan](../learning-observability/plan.md). Its proposed claim/statistical contracts, potential dashboard exposure, timer provenance and frozen report evaluation time extend this baseline. Read both under Design Baseline 1; the later data/tracking contracts and review patches reconcile the design, while actual browser/collection/report behavior still needs qualification.

## 1. Two questions, one evidence base

The learner should be able to answer **“What can I do now, what have I kept, and what should I work on next?”** The efficiency view should answer **“What outcomes did this work produce, how much did it cost, and what should we change?”** Both read the same saved learning records. Neither treats time spent, questions answered or a model's confidence as proof of learning.

Progress monitoring is a reasonable motivational hypothesis: a meta-analysis of randomized monitoring interventions found an average improvement in goal attainment. That broad result does not establish that this dashboard improves memorization, or that more statistics are always better. Test its usefulness with the learner and retained outcomes. [Harkin et al., 2016, author repository and abstract](https://eprints.whiterose.ac.uk/id/eprint/87431/).

Four distinctions govern every display:

- **Activity:** material studied, attempts made and time spent. Useful context, not learning gain.
- **Demonstrated performance:** what a response actually supports, with assistance and assessment uncertainty visible.
- **Later performance:** a check after a stated interval and intervening exposure history. An immediate correction is not this.
- **Change and maintenance:** improvement from a comparable earlier check, continued successful performance, or a new gap. Maintaining knowledge is valuable even when no new target is added.

The app must not maximize a universal progress score. Keep performance, coverage, effort, delay and data quality separate; no weighted sum. Metrics describe the learner's work in context, not a ranking against other people.

The user further requires good metrics and analytical tools **before optimization**. Measurement is therefore a product foundation, not reporting added after an adaptive policy is built. The sequence is: collect trustworthy evidence → establish a baseline → investigate a specific limitation → test one bounded change → verify its benefit. A dashboard looking better is insufficient to promote a learning-policy change.

## 2. What appears in the web app

Use the existing **Progress and corrections** area, with two views: **Learning** and **Time and results**. Show a small summary at the end of practice; do not require a new review questionnaire after each answer.

| Surface | What the learner sees | Interaction |
|---|---|---|
| Session summary | Specific independently demonstrated capabilities, work completed with help, remaining questions, time breakdown and next due check | Open the actual response/feedback; resume one clearly named next action |
| Curriculum overview | Selected goals; each target's latest interpretable evidence, previous achievements, assistance, last check date and due status | Inspect how the conclusion was reached; correct a judgment; see added/changed requirements |
| Weekly learning view | New demonstrations, successful later checks, maintained capabilities and repaired difficulties, with dates and sample counts | Filter by curriculum and mode; compare the same target set across time |
| Time and results | Comparable outcomes beside learner time, preparation/correction overhead, blocked waiting and measurement gaps | Inspect repeated repair loops or excessive overhead; propose a specific adjustment |

The default headline uses capabilities: “You explained why half the search space can be discarded,” not “You earned 200 points.” When no delayed checks have matured, say “Practiced today; later recall not checked yet.” A corrected misread is reported as a correction to the assessment, not as a newly learned concept.

Use a target list or map with separate evidence and schedule labels. For the latest comparable accepted attempt, the evidence label is independent demonstration, demonstration with help, observed error, or unresolved. A pending assessment is an overlay; it does not erase earlier evidence. Untested means no qualifying observation. Previous independent success and previous delayed success remain dated milestones even if the latest check exposes a gap. These labels are not mutually exclusive percentages to put in a single pie chart.

Show three simple trends when sufficient data exists: outcomes for a fixed target cohort, effort by category, and paired results versus effort for comparable cohorts. Unknown periods are gaps, not zeros. Draw curriculum revisions and assessment/policy changes as annotations. Do not extrapolate a rising line into a promised completion date. Routine practice days can be shown as optional activity context; losing a streak must not erase achievements or create overdue penalties.

An optional end-of-session prompt can ask “How demanding did this session feel?” and “Was it useful?” It is skippable, never a mastery rating and never required to continue. The app's motivational benefit remains unconfirmed until the learner finds the display useful; extra dashboard interaction itself counts as overhead.

## 3. Metric definitions and denominators

Every result carries its curriculum/target scope, definition version, time window, evidence cutoff, assistance/mode conditions, sample size and links to underlying records. A target key is its exact versioned contract, or an explicitly reviewed equivalent contract under a recorded mapping policy. A content split cannot inflate progress by turning one old success into several new achievements.

| Metric | Definition | Interpretation boundary |
|---|---|---|
| First independent demonstrations | Number of distinct selected targets whose earliest qualifying unassisted demonstration occurred in the period; inspect prior history, not just the period | First observed here does not prove the app taught it; the learner may already have known it |
| Current observed needs | Distinct target counts for latest comparable errors, unresolved observations and pending initial checks; show held/unassessed cases separately | Never treat `not_shown`, `cannot_judge` or no answer as an error |
| Successful later checks | Successes on the preselected endpoint opportunities satisfying the stated delay, mode and assistance conditions | Report successful, error, assisted, unresolved, missed and not-yet-matured separately; do not select the best retry |
| Endpoint completion and assessability | Completed endpoints / matured planned endpoints; judged endpoints / completed endpoints | Always visible beside a success fraction; missing outcomes cannot disappear from the denominator silently |
| Observed change | On the same comparable targets: prior error → later success, success → success, success → error, error → error, and pairs with unavailable evidence | Label these improved on checks, maintained on checks, new observed gaps, persistent gaps and unresolved pairs; no automatic causal attribution |
| Repair outcomes | For a supported gap: targeted help → first fresh integrated check, then the designated later check; report success/error/assisted/unresolved at each stage | A narrow corrected answer is not an integrated or retained repair; no check means pending |
| Reliance on help | Attempts using task-specific help / all presented attempts in the comparable cohort, with unsubmitted/pending attempts shown; facet assistance remains scoped | A fall is useful context only when task difficulty, mode and content remain comparable |
| Practice volume | Distinct submitted attempt IDs, study completions and practice days | Revisions/retries are not additional trials; this remains an activity metric |
| Effort | Recorded foreground time and separately reported outside time by category, blocked waiting, pauses and unaccounted time | Time estimates are not direct measures of attention or mental effort |
| Friction and assessment quality | Pending/failed model operations; judgment disputes and accepted corrections; time spent resolving them | Correction rate is not overall grading accuracy: unreported mistakes are unknown; disputes are not automatically model errors |
| Forecast calibration, later | Frozen before-answer forecasts versus subsequent eligible direct outcomes, stratified by target and horizon | Only when a real numerical model exists; prediction quality is separate from policy benefit and learning gain |

For a cohort's raw observation layer, define `P` as matured planned endpoints and partition it into independently successful `S`, supported errors `E`, assisted `H`, unresolved completed `U`, and missing/uncompleted `M`. Then `P = S + E + H + U + M`. Show these counts first. A conditional unaided success fraction is `S / (S + E)` only when the denominator is nonzero, explicitly labelled “among judged unaided checks.” It must be accompanied by all five counts and endpoint completion/assessability; it is not a success rate for every selected target. Assessability is `(S + E + H) / (P - M)` when the denominator is nonzero. A missing assessment for a submitted answer belongs in `U`, not `M` or `E`.

An assisted endpoint with no usable assessment belongs in `U` with an assistance annotation; `H` means an assessed endpoint disqualified from independent evidence by help on that target's required criteria. A hint for another target does not disqualify unrelated evidence. For otherwise independent endpoints, any supported required-criterion error makes the target outcome `E`; all required criteria demonstrated makes `S`; incomplete/ambiguous coverage is `U`. An episode may still support different outcomes for different targets. Preserve that episode ID and report both distinct target and distinct episode counts; do not treat ten facets of one answer as ten independent trials for confidence calculations.

Target counts are scoped inventories, not comparable units of cognitive difficulty. Do not rank vocabulary against mathematical proofs by “targets per minute.” Integration capabilities are assessed separately from their parts. A target checked successfully today is not guaranteed to be retrievable indefinitely; display the date and elapsed interval instead of “permanently mastered.”

## 4. What qualifies as improvement or retention

Routine dashboards use saved practice as observational evidence. They can show demonstrated progress and the effort accompanying it, but cannot by themselves establish that the adaptive policy caused improvement. New easy items, prior knowledge, changed grading and selective practice can all raise an apparent pass rate.

The [tracking contract](../learning-observability/tracking-contract.md) now supplies the routine-history/optional-plan workflow and a separate qualified outcome partition. Raw S/E/H/U/M describes grading and recorded help; use QS/QE/QH/QU/QM/QX for claims with timing/exposure/comparability requirements. Correct-but-ineligible evidence remains graded, visible and inside the planned denominator.

For a defensible comparison, freeze a **measurement cohort** before seeing its endpoint answers: exact targets and conditions, baseline evidence, designated endpoint opportunities, delay windows, task families and intended exposure policy. Use the first prospectively assigned eligible offer for each target/window; later help, invalidity or failure does not permit reassignment; retries remain useful practice but cannot replace the failed/ambiguous/missed measurement. An assigned draft abandoned before submission stays missing. Outcomes not yet due remain not-yet-matured and are not counted as failures.

Record both time since the planned learning anchor and time since the most recent known relevant exposure. Hints, feedback, extra early checks and reported outside study can rehearse the target. Do not call an endpoint “seven-day unpracticed retention” if the learner saw the answer yesterday. Keep its observed outcome and mark the exposure deviation; do not quietly restart the horizon until a favorable outcome appears. Broad routine displays may say “successful on a later day” with the actual interval. A controlled horizon claim needs the predeclared exposure rules and a visible record of exclusions.

Report outside exposure as self-reported/unknown; the app cannot observe all learning. One earlier delayed test is itself practice, so use distinct endpoint subsets for different research horizons when the evaluation requires unpracticed retention. Speech, real execution and fluency appear only if their corresponding evidence is actually collected; text answers cannot fill those metrics by inference.

When testing efficiency, compare a fixed recall baseline or equivalent capability practice against one proposed change, holding subject/target scope, assistance, assessment mode and delay comparable. Use the [existing evaluation decision](issues/06-evaluation-contract.md) to settle acceptable retained-performance loss and meaningful time savings before a pilot; this design does not choose that trade-off for the learner. Keep related families together where shared learning would contaminate comparisons. Report paired outcomes and costs first; do not declare causal improvement or equivalence from sparse personal data or overlapping observations.

Routine scheduled checks may supply observational endpoints. Additional evaluation prompts cost time and require the selected pilot scope; monitoring is not permission to add an unlimited testing burden. No review is omitted automatically because a dashboard looks favorable.

## 5. Time and effort accounting

The system needs an effort ledger from the first real encounter; timestamps on answers alone cannot recover preparation, feedback, corrections or waiting. Use the existing application store and session records, with the small measurement records in section 8. No separate analytics platform is needed for the initial single-learner app.

Within a measured session, assign each recorded interval to one category: setup, answering, diagnosis, studying/repair, feedback, authoring/editing, assessment correction, progress inspection, blocked waiting, pause, or unaccounted. Diagnosis answering is counted under diagnosis, not also answering. Overall cost counts an interval once even when one exercise covers several targets or two curricula share a target. Per-target drilldowns may show shared time, but those numbers must not be summed as independent costs.

Show learning work, authoring/correction/inspection overhead and blocked waiting separately. Total accounted session cost is their union, excluding explicit breaks; session elapsed time also shows breaks and unaccounted gaps. Preparation before practice and recurring maintenance outside sessions are included in curriculum-level cost, with one-time setup separate from recurring cost. An outside-time report with no trustworthy interval is displayed separately and not silently added to a potentially overlapping total. A long model request overlaps other productive work unless it actually blocks the learner; backend request latency is not an extra additive learner cost.

Preparation that never produces an accepted target, abandoned drafts and unresolved grading work still cost time. Keep them as unassigned library overhead until their context can be linked; do not drop them because there is no successful learning outcome. A comparison discloses shared and unallocated costs outside its frozen scope. If unresolved attribution could change which method appears cheaper, report the cost comparison as incomplete rather than divide shared minutes arbitrarily.

Browser timing is an estimate. [Page Visibility](https://www.w3.org/TR/page-visibility-2/) describes whether a document is visible; it does not establish attention. Use a [monotonic clock](https://www.w3.org/TR/hr-time-3/) for intervals within one document lifetime and UTC timestamps for placement. Do not infer concentration from typing speed, screen visibility or mouse activity. No keystroke contents or screen recordings are collected for timing.

Proposed collection rule for the first app: one timing owner per active session; start a span on explicit practice or a phase change, close on pause/navigation, and persist bounded checkpoints while visible. Use 30-second checkpoints and mark gaps longer than 60 seconds without a valid checkpoint as unverified. These are versioned engineering defaults for loss detection, not attention thresholds. A tab hidden or a device suspended cannot silently accumulate “active learning” time; hidden time is unaccounted unless the learner explicitly identifies outside study or a break. Quiet reading in a visible, running session remains foreground-estimated time and is labelled accordingly.

Each checkpoint closes a nonoverlapping span with a unique ID. Retry delivery is idempotent. Refresh/restart keeps acknowledged spans; an unacknowledged tail is marked unaccounted rather than extended to the next login. A second tab must explicitly take over the session timer; otherwise it cannot count another copy of the interval. Clock anomalies, missing telemetry and unavailable duration stay unknown, never zero. An optional correction appends a new span revision and reason, preserving the recorded original. Measurement derives the pre-submission and whole-session elapsed views from qualified timing evidence, with breaks and unknown gaps shown separately. There are no duplicate `elapsed_ms` fields on attempts/sessions. The span ledger owns measured durations; elapsed views are never added again as effort, and its accounting window includes post-answer feedback.

Subjective effort is independent of duration: a ten-minute difficult explanation may feel harder than twenty minutes of easy recall. Collect an optional easy/moderate/hard rating once per session, with missing feedback retained as missing. Use it alongside outcomes and time; it neither grades knowledge nor forms a composite efficiency score.

## 6. Detecting unproductive work and choosing a response

The app recomputes observations when an assessment/time correction is accepted, a session ends, or the learner opens Progress. It shows a short, evidence-linked suggestion; no background notification service is implied. Collapse repeated notices for the same unresolved issue and keep the learner able to continue or stop.

| Signal | Trigger and what it actually establishes | Suggested response |
|---|---|---|
| Repeated repair without independent use | Three completed repair episodes for the same unchanged target, each followed by an eligible check, with no independent success | Inspect the explanation, missing prerequisite and assessment criteria; try a different worked example or pause. This identifies a repeated pattern, not learner inability |
| Assisted success without later evidence | Repair/initial study has completed, but matured scheduled independent endpoints remain missing or unresolved | Show “later recall not established” and the pending check; do not call the practice ineffective or count a failure |
| High process overhead | In three consecutive measured sessions, authoring/correction/progress-inspection time exceeds answering + diagnosis + studying + feedback time | Show the actual minutes; inspect source preparation and grading burden. Up-front investment may still pay off later |
| More effort, unchanged observed outcomes | Two completed comparable cohorts show the same paired outcome counts while total recorded effort increases | Show the comparison and uncertainty; consider a simpler method. Maintenance and differing difficulty/exposure must be examined before calling it waste |
| Unexpected time cost | An exercise's actual accounted cost exceeds its saved full-cost estimate | Revisit that estimate and the budget; one overrun is a cost discrepancy, not a general trend |
| System-caused friction | Saved answers remain unassessed, authoring/assessment operations fail, or accepted grade corrections recur | Repair the app/content/assessment path before prescribing more learner practice; show pending/failed/corrected counts separately |
| Insufficient evidence | Too few comparable outcomes, changing curriculum/conditions, missing time or no matured delayed checks | State exactly what cannot yet be concluded; do not fabricate a percentage or demand broad remedial work |

The three-episode/session thresholds are proposed triage defaults, not validated cutoffs for inefficiency. Cost comparisons require comparable accounting scopes and complete interval placement; missing time or unplaced outside reports yield an incomplete-cost notice instead of a confident overhead flag. Foreground estimates remain labelled estimates even with complete interval coverage. A flag records its metric version, underlying record IDs and suggested next action. It never changes grading, resets progress or suppresses reviews. Numerical predictions are not required for any first-release flag.

Flags are derived view results, keyed by their rule version, scope and evidence references so the same evidence produces one notice. They are not another learner observation or a new recurring automation. A saved measurement report can retain the notice and its explanation without adding a separate monitoring service.

An improvement loop is: identify the cost or repeated difficulty → inspect the actual evidence → change one bounded aspect → compare the next suitable outcomes and cost. Keep the old policy/assessment versions and selection reasons so a later comparison can distinguish a product change from a learner change. If measurements themselves take too much time, reduce the dashboard/survey burden and record that adjustment.

## 7. Worked example and learner wording

This is an authored example, not measured user data. A fixed cohort has eight targets. Baseline: two pass, six have supported errors. At the designated later checks: the original two still pass, three formerly failing targets pass, two still show errors, and one has no completed check.

| Result | Count |
|---|---:|
| Improved on comparable checks | 3 |
| Maintained on comparable checks | 2 |
| Persistent observed gaps | 2 |
| Follow-up still missing | 1 |

The effort ledger contains 12 minutes answering, 5 diagnosing, 8 studying/repair, 4 reading feedback, 6 preparing material, 2 correcting assessments and 3 blocked waiting: **40 accounted minutes**, including 8 minutes of preparation/correction and 3 waiting. The designated checks are included, not treated as free.

The Learning view says: “Three targets improved on later checks; two stayed successful. Two need focused work, and one still needs checking.” The Time and results view shows the outcome counts beside the full 40 minutes and its breakdown. It may show “5 of 7 completed, judged unaided checks passed” only alongside “7 of 8 planned checks completed.” It does not claim 5 new concepts learned, 100% completion or proven superiority over another method.

If another 40 minutes later maintains the same five successes, the dashboard records maintenance. That may be useful; the counterfactual of what would happen with less practice is unknown. A fair comparison requires an agreed alternative and comparable later checks, not an assumption that flat target counts mean wasted effort.

## 8. Collection and reproducibility contract

Read these initial payload sketches together with the [completed data-contract draft](../learning-observability/data-contract.md), which supplies their missing timing provenance, exposure kind, endpoint-assignment constraints, complete-transaction receipts and report source/query/replay contract. Its named replacements take precedence in the proposed design. The existing sketches alone are not implementation-ready, and the metric/deletion decisions remain open.

Reuse the [compatibility record envelope](compatibility-design.md#2-identity-and-version-rules) for four additional kinds. `Ref`, `Time`, `Algorithm`, revisions and command receipts retain their existing meanings. These fields extend the still-unreleased format 1 proposal; they do not pretend a production format migration has occurred.

| Kind | Required payload fields |
|---|---|
| `activity_span` | `session: Ref?`, `enrollment: Ref?`, `context: Ref[]`, `targets: Ref[]`, `category: setup/answer/diagnosis/study/feedback/authoring/assessment_correction/progress_inspection/blocked_wait/maintenance/pause/unaccounted`, `started_at: Time?`, `ended_at: Time?`, `duration_ms: integer?`, `measurement: foreground_estimate/self_report/unverified`, `collector: Algorithm`, `revision_reason: text?` |
| `session_feedback` | `session: Ref`, `effort: easy/moderate/hard/null`, `usefulness: useful/mixed/not_useful/null`, `note: text?`. Optional record, never required to finish a session. |
| `measurement_cohort` | `name: text`, `purpose: observational/evaluation`, `enrollment: Ref`, `targets: Ref[]`, `frozen_at: Time`, `definition: Algorithm`, `endpoints: Endpoint[]`, `exposure_policy: text`, `effort_scope: Ref[]`, `effort_membership: Algorithm`, `cost_window_start: Time`, `cost_window_end: Time`. Effort scope names exact roots whose membership follows the data contract's `cost-membership-1`: enrollment identity across revisions, or explicitly narrower exact target/source work. Record known enrollment attribution on spans, including preparation/inspection without a target. Freeze the membership algorithm with the roots. Target set, cost scope, membership rule and eligibility cannot be revised after outcomes to improve the result; a changed design gets a new cohort ID. |
| `measurement_report` | `cohorts: Ref[]`, `definition: Algorithm`, `source_through_sequence: integer`, `computed_at: Time`, `window_start: Time`, `window_end: Time`, `display_timezone: text`, `results: MetricResult[]`. Persist only when saving a report/checkpoint; normal dashboard refresh need not append a report. |

```text
Endpoint = {
  id: text, target: Ref, baseline: [Ref], anchor: Ref?,
  window_start: Time, window_end: Time, minimum_delay_ms: integer,
  exercise_families: [UUID], required_mode: text,
  assigned_attempt: Ref?, exposure_notes: text
}
MetricResult = {
  metric_id: text, status: available/insufficient/unavailable,
  numerator: number?, denominator: number?, unit: text,
  counts: {success: integer, error: integer, assisted: integer,
           unresolved: integer, missing: integer, not_matured: integer}?,
  evidence: [Ref], time_spans: [Ref], limitations: [text]
}
```

Assign an endpoint before its answer is known, recording the attempt's initial draft reference. Resolve that same attempt identity's submitted revision at the report cutoff and retain the exact submitted/assessment references in the result. Updating that assignment from null to the first draft/offer pair is allowed only atomically with creation before presentation; replacing it after an unfavorable outcome is not. The tracking contract also permits active→stopped/completed lifecycle revisions, without changing population/windows. Its baseline-state, anchor-reason, plan/source and qualified-count fields complete these abbreviated sketches. A pre-existing baseline answer is selected by an explicit rule before the endpoint, never by choosing the worst prior performance retrospectively. Cohorts cannot independently count the same shared attempt as independent participants.

For routine charts without a frozen cohort, return the query's target set, curriculum revision, time window, grouping timezone, metric-definition version, assistance/mode filters and source sequence with the result. Label changing populations as observational activity/outcomes; do not manufacture a cohort trend from them. Metrics without endpoint categories use `counts: null`. A scalar uses `numerator` with `denominator: null`; a fraction declares both. An unavailable metric keeps both values null and explains why. Absence of measurement is never encoded as a zero outcome.

Accepted domain records are the source of truth for attempts, help, grades, reviews and checkpoints; UI clicks never mint learning outcomes. Commit critical domain records first/atomically with their relevant receipt. Timing delivery may retry without blocking answer submission; missing measurements lower cost-data completeness, not learning credit. Collect in the same local store, with no third-party analytics transmission. Raw source text and answers need not be copied into telemetry; `Ref` links supply authorized drilldown.

Foreground spans with reliable endpoints must not overlap for the same active timing owner. Total effort uses a union across owners/sessions rather than summing overlaps; conflicting categories remain explicitly unaccounted until corrected. Self-reported duration without interval placement is shown separately, never silently added to an overlapping interval. Unknown duration is null. No attribution divides one shared exercise into invented per-target minutes.

Version metric definitions with application code. Saved reports retain their definition, filters, source sequence and evidence so the result can be reproduced. Current charts use corrected effective assessments at the chosen cutoff; “as reported then” uses the original cutoff. An accepted misread/grade/time correction changes the current historical series at the original event time and adds a correction annotation—it is not new learning today. New metric definitions and curriculum changes start a labelled series or an explicit comparable-cohort view; do not silently rewrite the old baseline.

All four kinds export/restore with the library. A technical architecture migration preserves the raw ledger, cohorts, saved reports, definitions and their references. Derived dashboard caches may be rebuilt. If a prior metric implementation is unavailable, the saved report remains readable with that limitation; do not replace it with an unexplained newly calculated value. Before releasing a changed metric, replay the retained worked cases and inspect how conclusions change.

## Analytical tools and the optimization gates

The learner overview stays concise. A deeper analysis workspace within Time and results supports the following questions using the same records and metric definitions, rather than a separate source of truth.

| Tool | Question it answers | Required interaction and output |
|---|---|---|
| Evidence explorer | What supports this progress claim? | Drill from an aggregate to target → exact exercise/answer → assistance → accepted assessment/corrections. Show excluded and missing records as well as included ones; return to the same filters |
| Target trajectory | Is this capability improving, being maintained, or repeatedly failing? | Timeline of attempts, help, feedback, independent/delayed checks, outside-exposure notes and revisions. Overlay effort without converting attempts into independent subjects; unknown intervals remain gaps |
| Cohort comparison | Did the same kind of learning improve for the effort spent? | Select saved cohorts and show paired outcome transitions, completion/assessability, elapsed delays and full cost side by side. Display mismatched modes, target versions, task families, exposure rules and policy versions before a comparison can be labelled comparable |
| Repair-path analysis | Where does a repair attempt stop producing useful evidence? | Follow observed gap → targeted help → fresh integrated check → later check. At each stage show the original eligible count, completed count, unresolved/missing cases and accumulated cost; allow inspection of cases that stopped. Do not report only successful finishers |
| Effort breakdown | Where is time going, and what could be simplified? | Breakdown by activity, curriculum and policy version, with observed versus estimated/unplaced time and shared work visible. Compare expected versus actual full costs; keep abandoned preparation and correction work in scope |
| Measurement-quality view | Can we trust the conclusion? | Show assessment disputes, confirmed corrections, missing timing, endpoint coverage, repeated/shared episodes and cohort deviations. Recompute the conclusion under explicit sensitivity scenarios without rewriting recorded outcomes |

All tools support explicit curriculum/target, mode, assistance, time-window, delay and policy-version filters; preserve those filters and the evidence cutoff in a saved report. A comparison reports the intersection and exclusions when target sets differ; it cannot silently restrict itself to easy shared targets. Data-table export of a report includes definitions, counts, denominators, filters and record references, so the displayed result can be independently reproduced. The existing complete library export remains the way to preserve the underlying evidence.

For a concrete sensitivity view, a cohort with five successes, two errors and one missing endpoint has observed outcomes `5/7` among judged checks and `7/8` completion. The unresolved population-wide success fraction could be `5/8` or `6/8` depending on that missing result. Show that range as a scenario bound, not a confidence interval or an imputed grade. If missing endpoints, disputed judgments or unallocated costs could reverse the preferred choice, the analysis must say the decision is unresolved. Statistical intervals, if later introduced, must respect shared episodes and related target families rather than pretend every criterion is independent.

### Gate A: measurement ready for a bounded comparison

Before using a metric to optimize the learning policy, verify the parts needed for that claim:

1. **Meaning:** the metric states the capability, conditions and horizon it measures. Delayed recall, explanation, selection and execution are not substituted for one another. Known contrasting cases produce the expected distinction.
2. **Assessment validity:** inspect a reference set covering success, real error, help, missing evidence, alternate valid answers and misreads. Independently review the interpretations; schema validity or agreement between models alone cannot certify the outcome measure. Known consequential grading defects block the affected comparison.
3. **Collection integrity:** the actual saved path captures attempts, assistance, revisions, full effort and missingness without duplicates. Observe it in real use as well as deterministic cases; working arithmetic over invented data is not sufficient.
4. **Comparability:** freeze baseline/cohort scope, first endpoint selection, delay/exposure rules, cost boundaries and the candidate change before seeing its outcomes. Disclose outside learning and shared families. Agree on acceptable retention loss, meaningful savings and stopping rules for the particular pilot.
5. **Reproducibility:** a saved report reproduces from its definition version and source cutoff, including after correction and export/restore. Unknown measurements cannot become zeros or disappear from its denominator.

Record each gate result with its supporting report and unresolved limitations. A check passes only within the evaluated scope; it does not certify every subject or exercise format. These requirements gate policy experiments and optimization claims. Ordinary learning under the explicit baseline and fixes to clear defects do not have to wait for a claim of improved learning efficiency.

### Gate B: evidence sufficient to adopt the change

Passing Gate A permits a bounded prospective comparison, not a claim that the candidate is better. Keep a before-answer record of the hypothesis, affected policy/content versions and predicted outcome. Compare the candidate with the baseline under the agreed scope, including intervention, authoring, correction and measurement costs.

Adopt a change as an efficiency improvement only when it meets the agreed retained-performance constraints and improves the chosen cost/outcome trade-off, with missingness and assessment uncertainty unable to undermine that conclusion within the agreed decision rule. Report improvement, maintenance, regressions and unresolved cases separately. If evidence is sparse, conditions changed, or the comparison cannot distinguish benefit, retain an inconclusive result and the inspectable baseline; do not infer equivalence or silently promote the candidate.

Evidence that a metric or assessor itself is wrong first calls for measurement repair and reanalysis, not tuning the learner policy to that faulty signal. Numerical learner-model fit, faster model responses and fewer questions are useful diagnostics but cannot substitute for the retained-performance and total-effort check. No automatic optimization loop is part of the first release.

## 9. Acceptance cases and delivery scope

These are design requirements, not executed product tests.

| Case | Required behavior |
|---|---|
| O01 Activity versus learning | Ten retries and a helped correct answer do not become ten new targets or an independent/delayed success |
| O02 Partial/ambiguous evidence | Missing or unclear criteria stay unresolved; target, episode and endpoint counts remain distinct |
| O03 Delayed-check denominator | Worked cohort produces 3 improved, 2 maintained, 2 persistent errors, 1 missing; reports 5 judged successes without hiding the eighth target |
| O04 Exposure and first endpoint | An early hint/extra check is recorded; first failed/assisted endpoint cannot be replaced by a successful retry or relabelled as unpracticed retention |
| O05 Maintenance | Repeated later success is visible as maintained knowledge even when new-target count is zero |
| O06 Time ledger | Worked example sums to 40 minutes; shared exercises and model latency overlapping productive work are counted once |
| O07 Timing failure | Hidden tab, suspension, two tabs, lost checkpoints, clock anomaly and outside-time report do not fabricate precise active time; gaps stay visible |
| O08 Corrections | Correcting a grade/misread updates current historical metrics once, preserves original reports and never creates a new learning episode |
| O09 Curriculum evolution | Reorder leaves metrics unchanged; additions/splits start explicit new requirements; fixed-cohort trend and past achievements remain intact |
| O10 Efficiency signal | Repeated qualifying repair/overhead cases show the underlying evidence; sparse, incomparable or incomplete cases cannot assert waste |
| O11 Restore and metric version | Raw measurements, cohorts, receipts and saved reports survive export/restore and metric upgrades with reproducible cutoffs |
| O12 Browser comprehension | Learner can identify one capability gained/demonstrated, one maintenance result, one unresolved need, and where time went; can reach evidence and correct a result without guessing what “progress” means |
| O13 Measurement burden | Feedback is skippable, Progress has no effect on mastery, and time spent reviewing metrics is included in overhead |
| O14 No data | Fresh curriculum, no delayed checks or missing timing shows “not measured yet”/unknown, never 0% mastery or infinite efficiency |
| O15 Analysis trace and cohort mismatch | A chart opens its precise evidence and exclusions; changed contracts, modes or delay/exposure rules cannot silently become a comparable cohort |
| O16 Repair-path attrition | Cases missing integrated or delayed checks remain in their stage denominators, not dropped to make repair look successful |
| O17 Sensitivity and incomplete evidence | The authored missing-endpoint case shows the scenario range `5/8`–`6/8`; scenarios do not change stored grades, and a comparison that missing outcomes could reverse remains unresolved |
| O18 Optimization gates | Faulty measurements block the affected policy comparison; passing measurement checks alone cannot mark an untested or inconclusive candidate as an improvement |

First release: capture effort spans from initial intake, show session/curriculum evidence and time summaries, expose missing/assisted evidence, and compute dated later-check counts when real time has passed. Provide evidence drilldown, target trajectories, effort breakdown and measurement-quality inspection as the first analytical tools; add cohort and repair-path comparisons as their real histories become available. Add the small evidence-linked flags once their qualifying histories exist. Include saved reports and cohort contracts so later comparisons have stable denominators. Baseline performance floors, experiment allocation and research comparisons remain part of the evaluation decision, not an automatic consequence of opening a dashboard. Gate A precedes learning-policy optimization experiments; Gate B precedes claiming and adopting an efficiency improvement.

No leaderboard, global mastery number, reward economy, external monitoring stack or causal “learning per minute” optimizer is needed. The named problem is that the learner must see meaningful progress and the system must account for the effort needed to achieve or maintain it. Any later measurement machinery must improve one of those decisions.
