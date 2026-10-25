# Observability design: claims, analysis and useful decisions

Status: observability design finalized in [Design Baseline 1](../skill-maintenance/design-baseline.md), 2026-10-16. Research and numerical counterexamples support the decisions and their limits. Browser behavior, learner comprehension and empirical learning benefit remain unverified; production implementation is not authorized.

This document extends the [existing observability contract](../skill-maintenance/observability-design.md) and [compatibility contract](../skill-maintenance/compatibility-design.md). It does not replace their episode identities, target-scoped help, outcome categories, correction rules, full-effort accounting or optimization gates. The [campaign map](map.md) owns decision status; the [delivery and validation plan](plan.md) owns proposed sequencing.

## 1. Destination and newly exposed gaps

The everyday learner needs to see what changed, what was maintained, what remains unknown and a useful next action. The analytical view must explain the outcomes and full effort of a fixed learning goal before recommending a policy change. A successful dashboard is understood and useful at an acceptable inspection cost; dashboard visits are not proof of learning.

| Existing foundation | Gap exposed by this campaign | Proposed response |
|---|---|---|
| Metric formulas and evidence links | A correct formula can summarize an invalid interpretation | Claim-specific validity contracts and independent assessor qualification |
| Cohort comparisons | Dependence, adaptive task choice and carryover can invalidate inference | Separate descriptive, predictive and causal analysis contracts |
| Uncertainty labels | Missingness, grading dispute and sampling uncertainty have different meanings | Typed uncertainty with method-specific unavailable states |
| Full-effort ledger | Unknown timer ownership and unreliable calendar placement | Timing-run provenance, acknowledged intervals and separate placement quality |
| Saved report cutoff | The same cutoff can mature more endpoints tomorrow | Freeze evaluation instant T as well as source sequence S |
| Evidence drilldown | Viewing an old answer can rehearse the target | Record potential answer-bearing exposure without inventing study completion |
| Dashboard content list | Layout and interpretability had no concrete artifact | Three contrasting layouts and interpretation tasks |
| Optimization gates | Statistical significance does not establish acceptable retained performance | Prespecified effect/cost margins and a qualified decision procedure before adoption |

These are design findings from [measurement research](research/measurement-validity.md), [statistical research](research/statistical-methods.md), [dashboard research](research/dashboard-evidence.md) and [collection research](research/collection-integrity.md). They establish what to investigate or build, not how effective the future app will be.

## 2. Every metric needs a claim contract

A metric definition contains its name/version, intended user decision, exact capability/mode/conditions, observation unit, endpoint assignment, baseline selection, numerator/denominator, time/exposure requirements, exclusions, dependence assumptions, interpretation, validation evidence and withholding rule. A chart title is generated from that contract, not from a generic template such as “mastery.”

The testing standards frame validity around intended interpretation and use, and distinguish agreement on the same response from consistency across different performances. That is why “the model and another model agree” cannot qualify a learning claim. [AERA/APA/NCME testing standards](https://www.testingstandards.net/uploads/7/6/6/4/76643089/standards_2014edition.pdf).

Use this metric dictionary as the working recommendation:

| Measure | Exact quantity / unit | Required disclosure and withholding |
|---|---|---|
| First observed independent demonstration | Distinct target contracts with their earliest accepted unaided demonstration in the window | Prior ignorance and app-caused learning are unestablished; split targets cannot multiply an old achievement |
| Comparable observed change | Error→success, success→success, success→error, error→error on the designated comparable pairs; incomplete pairs separate | State the original cohort, complete-pair denominator and baseline rule; no substitution of best retries |
| Delayed independent outcomes | `P=S+E+H+U+M`; report counts first, conditional fraction `S/(S+E)` second | Actual horizon, last relevant exposure and completion/assessability visible; zero denominator is unavailable |
| Maintenance | Previously successful targets still successful at the designated later opportunity | Include practice/exposure and effort; zero new targets is not zero value |
| Integrated repair | Counts at observed gap → help → fresh integrated check → later check, always retaining original eligible cohort | Completion, outcome and unknown count at every stage; local corrected success cannot stand for integrated retention |
| Transfer | Outcomes under a declared change in task context, cues or demands | A reworded question is not automatically a transfer measure; define what was unpracticed |
| Fluency | Accurate responses meeting the goal's time constraint, plus correct-response duration distribution | Errors, timeouts and missing timing remain visible; input demands/devices must be comparable; no speed/accuracy weighted score |
| Effort | Union of eligible placed intervals by activity, plus separate unplaced/self-reported time | No summed per-target copies, no provider-latency addition, no invented attention percentage |
| Assessment quality | Consequential error counts, confusion table and abstention/coverage on independently reviewed reference cases | Scope and reference limitations visible; routine dispute rate is not overall accuracy |
| Prediction quality, later | Frozen forecast loss on declared same endpoints, compared with a simple benchmark | Temporal leakage, dependence, selection policy and horizon explicit; insufficient data can preclude calibration assessment |
| Policy effect, later | Prespecified delayed-outcome difference and full-cost difference under a defensible allocation | Generalization, missingness and interference assumptions explicit; no causal label for ordinary practice logs |

The three improvements and two maintained successes in the [sample dashboard](spikes/dashboard-prototype.html) describe paired observations. They are not five new concepts learned. A content correction alters the effective history at the original occurrence time; it does not appear as today's learning gain.

## 3. Statistical analysis is chosen by the question

### Recorded history

Default to exact counts, comparable paired transitions, dates, effort and missingness. A finite inventory of eight target outcomes does not need a sampling confidence interval merely to report its own count. A report generalizing to future retrieval or other tasks must state a sampling or response model.

For complete comparable pairs, let `b` be error→success and `c` success→error. `(b-c)/N_complete` is net observed change on those pairs. Always retain the incomplete pairs and transition counts: a net value can conceal improvements and regressions of different capabilities. Do not reinterpret this net fraction as a utility score or a causal effect.

Compare stable task/mode/family strata. The numerical probe has pooled success rising from 26% to 64% while both difficulty strata decline ten percentage points. The product must show composition changes rather than normalize them using invented difficulty values. Keep different task strata separate when a common comparison is not defensible.

### Uncertainty has separate causes

1. **Unobserved outcomes:** finite scenario bounds and tipping points. With five successes, two errors and one missing endpoint, the all-endpoint fraction is compatible with 5/8–6/8. Neither endpoint is stored as a grade. This simple bound applies to otherwise assessed unaided endpoints plus missing outcomes, not automatically to assisted/ambiguous categories.
2. **Assessment uncertainty:** disputed criteria, alternatives and independent reference review. Show the range of conclusions under specified plausible rejudgments; do not assign an arbitrary error probability.
3. **Collection uncertainty:** unknown tails, unplaced effort, clock disagreement and absent exposure history. Preserve useful reliable duration separately from unreliable placement.
4. **Sampling/model uncertainty:** a declared statistical method under its assumptions. A confidence interval, posterior interval and sensitivity range must never share an unlabeled “confidence” band.

For independent comparable Bernoulli trials, a Wilson interval is a candidate; [NIST gives its formula](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm). The [statistical contract](research/statistical-methods.md#2-descriptive-analysis-and-conditional-statistical-intervals) states the assumptions. The probe demonstrates that duplicating 8/10 episode outcomes into 80/100 criterion rows falsely narrows the interval. Episode IDs prevent literal duplicates but do not prove independence across episodes. No ordinary row bootstrap or invented effective sample size repairs this automatically.

### Forecast audit, after a numerical model exists

Freeze probability, capability/mode, horizon, exposure assumptions, selection policy, model version and training cutoff before the answer. Compare candidate and simple benchmark on the same eligible outcomes. Begin with Brier loss `(p-y)^2`; optionally include log loss under a declared handling of extreme probabilities. Aggregate and assess uncertainty at the declared episode/family level. Proper scores evaluate prediction, not learning improvement. [Gneiting and Raftery](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf).

Use forward temporal evaluation with related task variants kept together. Show actual forecast/outcome pairs before decorative calibration curves; two outcomes in a bin do not establish calibration. No numerical mastery model is selected by this campaign.

### Policy comparisons and sample sufficiency

Ordinary A/B crossover on the same knowledge is a poor default because learning carries over. The candidate is prospective allocation of suitable matched knowledge families, keeping shared prerequisites together and assigning before outcomes. Eligibility, baseline, target contracts, fresh endpoints, delay/exposure, cost boundaries and analysis time are frozen. Generalization remains limited to this learner and enrolled families unless separately justified. Cluster allocation requires an explicit interference assumption; semantic family names do not establish it. [Imai et al.](https://imai.sites.fas.harvard.edu/research/files/cluster.pdf).

The exact four-pair sign-flip probe gives `p=0.125` even when all four observed differences favor the candidate. It tests a sharp no-effect null under the specified randomization. It does not establish equivalence, noninferiority or an acceptable retention loss. No adoption decision uses this p-value alone.

Before a real comparison, specify meaningful savings, allowable retained-performance loss and the uncertainty/decision rule. Then run a feasibility analysis over plausible family correlation, effects, grading mistakes, missingness, transfer and timing noise. Report false adoption, interval behavior, inconclusive probability and evaluation burden. Use aims, data-generating mechanisms, estimands, methods and performance measures; report Monte Carlo error if simulation is used. [Morris et al.](https://discovery.ucl.ac.uk/10066118/1/2019%20-%20Morris%20-%20simulation%20studies%20tutorial%20-%20stat%20med.pdf).

There is no universal “30 answers” gate. If available independent allocation units cannot support the required decision, label the study feasibility-only or do not run it. Fixed-horizon analysis is the starting recommendation. The exact peeking counterexample produces 10.66% false rejection versus 4.14% with one planned look in its invented model. Sequential methods require their own valid assumptions and qualification, not repeated fixed-sample testing.

**Open:** a concrete retained-performance noninferiority/effect-interval procedure cannot be selected responsibly until the actual assignment units, outcome and user margins are specified. That is an explicit dependency of [the experiment contract](issues/08-experiment-contract.md), not a hidden promise that “statistics” will solve adoption later.

## 4. Assessor qualification precedes optimizing grades

Build a reference set spanning facts, relations, integrated explanations and described procedures, including alternate valid answers, omissions, real errors, hints, supported misreads, contradictions and unknown causes. Do not claim execution competence from textual description. Freeze prompts/answers and assessor versions; reviewers initially work independently of the candidate judgment. Adjudicate disagreements with reasons while retaining the original ratings.

Report a confusion table over the four criterion outcomes and a separate teaching-action table. In particular, track false demonstrations, unsupported repairs, unjustified review deferral, missed supported errors and appropriate abstention. Denominators include the opportunities for each error class; aggregate agreement cannot conceal a consequential subset. Agreement is evidence about consistency, not proof that the reference is true.

Use held-out cases and fresh equivalent verification cases after a rubric correction. Inspect performance by subject, mode, ambiguity and help; do not optimize on the same cases used to judge improvement. User tolerance of consequential errors and acceptable review burden remain decisions for the concrete pilot. Until qualification exists, disputed outcomes can be reviewed/corrected, and unsupported interpretations remain unresolved.

## 5. Dashboard architecture and interactions

The [three alternatives](spikes/dashboard-prototype.html) use identical synthetic histories:

| Alternative | Entry point | What to test |
|---|---|---|
| Daily briefing | What changed, what remains unknown, one useful next action | Can the learner understand the situation without opening every chart? |
| Capability notebook | Select a named capability, inspect earlier/later evidence and effort | Can the learner locate the exact relationship or step behind a judgment? |
| Analysis workspace | Fixed-cohort rows, completeness, cost and assumptions | Can the learner challenge an apparent gain or efficiency claim? |

Selected direction for this learner, 2026-10-15: **C, the comprehensive analysis workspace, is the default dashboard.** Keep A for quick orientation and session summaries, and B for a capability's detailed evidence and history. The user prefers analytical depth while explicitly retaining the other views' use cases. This supersedes the earlier briefing-first recommendation; it does not establish that every learner prefers C. Keep a direct route into practice from any view. See [the dashboard decision](issues/06-dashboard-spike.md#answer).

Use named outcome rows for small cohorts, dated categorical event strips for capability histories, aligned horizontal bars for minutes, a stage table for repair attrition, and paired outcome/cost panels for comparisons. Avoid smooth mastery curves unsupported by a fitted model, pie charts mixing overlapping states and probabilistic graphics for nonprobabilistic missingness. Graph topology may aid navigation later if the capability list fails a concrete use case; it is not required as the default dashboard.

User feedback on the detailed C, 2026-10-15: terminology was difficult, the before/after bars did not show time trends, and walkthrough buttons did not read as a workflow. The revised C uses “skills,” “correct without help,” and “checks answered,” with provenance behind optional details. Its main chart follows the same skills over explicit check dates; selecting a date updates the evidence and cost scope below. The old paired breakdown is secondary. Guidance now has numbered completed/current/upcoming steps, a single current action, its result, and Back/Next/Restart controls. These revisions respond to actual negative usability feedback; their usability is not yet confirmed.

The full product interaction contract is:

1. Choose curriculum and purpose. The first screen retains scope, last update and data sufficiency visibly.
2. Open any claim to see its exact target set, inclusion/exclusion rules and original denominator.
3. Open a target to see the assigned exercise, submitted response, scoped help, criterion evidence, assessment revision and relevant exposure.
4. Return to the same filters and scroll/selection state. A changed filter visibly changes the population and invalidates incompatible comparisons.
5. Propose a correction with its reason; retain old records, preview affected claims, and recompute current history after acceptance. Saved earlier reports remain unchanged.
6. Save a report with its complete manifest or export a scoped table with counts, definitions and references. Full-library export remains separate; answers are not copied into a table export by default.

The original three-layout mockup exercises arrangement, scenario switching and authored evidence drilldown. Filter persistence, real correction submission, report saving, task execution, repair-stage interaction and exports are specified future work, not working controls in that original mockup.

Continuation, 2026-10-15: the selected C now has a [detailed calculation and interaction contract](c-dashboard-contract.md) and a [separate logic walkthrough](spikes/c-walkthrough.html). It calculates from authored target/endpoint records, provides curriculum/mode filters, denominator-preserving row highlights, formula/evidence inspection, missing-outcome scenarios, correction snapshots and an in-memory frozen report. Separate panels expose full-cost and task-mix reversals. These controls extend the original arrangement mockup; durable storage, real correction submission, collection and product integration remain future work. The contract maps every display to existing records and explicitly proposed additions without claiming the data-schema audit is complete.

States requiring deliberate design include: no practice yet; no matured delayed checks; helped-only evidence; pending/disputed assessment; missed endpoint; successful maintenance; repeated repair without later verification; changed curriculum; unknown effort; model failure; pending persistence; changed metric definition; and inability to reproduce an older saved report. Unknown values are labeled unavailable, never encoded as zeros. First use offers a useful action without a fabricated trend.

Target WCAG 2.2 AA: keyboard access, visible focus, meaningful headings/table relationships, readable text alternatives, no color-only status, no hover-only evidence, and responsive page layout at 320 CSS pixels. Prefer large controls. The prototype source follows basic structures but has not passed a browser or accessibility audit. [WCAG 2.2](https://www.w3.org/TR/WCAG22/).

## 6. Monitoring can change the thing measured

Independent tests themselves can affect later retention; original experiments support recording tests as exposure rather than passive measurement. [Roediger and Karpicke](https://learninglab.psych.purdue.edu/downloads/2006/2006_Roediger_Karpicke_PsychSci.pdf).

Design inference: an answer-bearing drilldown can also offer rehearsal. Record that the target-specific content was presented; do not infer that it was read or learned. A conservative unpracticed-retention analysis must treat such presentation as possible intervening exposure. A counts-only overview is not automatically exposure to every capability. Record progress inspection time as overhead either way. Outside practice remains self-reported or unknown.

This is a real schema distinction: the existing `study` record means initial/repair study and records completion; it must not be repurposed to assert completion every time an answer is displayed. Proposed `exposure` records use the same envelope with `targets`, `content_refs`, `kind: answer_presented/review_content_presented/outside_report`, `timing: {precision: exact/bounded/unknown, earliest_at: Time?, latest_at: Time?}`, `session?`, `basis: app_presentation/self_report`, and `details?`. Exact timing has equal non-null bounds; bounded timing preserves the reported interval; unknown timing has null bounds. “Sometime yesterday” must not become an invented exact timestamp. Minimum-delay eligibility uses the conservative possible exposure time, or remains unresolved when timing cannot support the claim. Domain attempts/help/study remain their original exposure sources; deduplicate the underlying occurrence rather than adding a second synthetic practice event. No exposure record produces learning credit or an FSRS review.

## 7. Collection and report contracts

No analytics warehouse or external tracking service is justified by the current need. Use ordinary versioned records in the chosen authoritative application store. UI clicks do not mint learning results. Capture only the operational facts needed for measurement: no keystroke logs, screenshots or cross-site browsing history.

| Record / query | Required design addition | Reason |
|---|---|---|
| `timing_run` | Library-scoped ownership generation, nullable session, document-run identity, start/end anchors, collector version, status | Preparation and practice must not acquire duplicate timers in two tabs |
| `activity_span` | Run reference/generation, ordinal, nullable monotonic offsets, raw wall anchors, placement quality, quality reasons | Reliable elapsed duration is different from reliable day/interval placement |
| `measurement_report` | `evaluation_at`, complete query manifest, logical source-prefix fingerprint, manifest/results digest, included/excluded references | Source sequence alone cannot reproduce maturity, filters or a divergent library |
| Report manifest | Exact target/cohort revisions, estimator/version/parameters, estimand, observation/allocation units, filters, denominator and exclusion rules, exposure policy, cost scope, UTC grouping boundaries | A report must preserve the entire calculation, not just its number |
| Later forecast evaluation | Before-answer probability/model/training cutoff and same-endpoint benchmark references | Prevent retrospective “predictions” and mismatched score comparisons |
| Selection when randomized | Actual assignment probability and allocation unit, in addition to reason/candidates/policy | Do not reconstruct probabilities later from a changed selector |

Sampling time settings remain provisional engineering choices, not psychological facts. Thirty-second scheduling does not guarantee at most thirty seconds lost in a crash; callbacks may stall. A monotonic clock prevents wall-clock adjustment from corrupting a same-run duration, but does not prove attention or uninterrupted work. [High Resolution Time draft](https://www.w3.org/TR/hr-time-3/), [Chrome page lifecycle guidance](https://developer.chrome.com/docs/web-platform/page-lifecycle-api).

One transactionally granted timer generation owns each library's measured activity. Takeover invalidates new claims by the old generation, while already-committed retries retain their original receipts. Unaccepted late old-owner spans remain unverified, not silently discarded or accepted as certain. Learning answers remain valid independently of timer ownership. A browser lock may help cooperating tabs, but it does not replace accepting-store validation. Restore/cutover preserves timing history but never revives authority for an old document: the new runtime begins without an active owner and grants a fresh activation generation on resumption. Historical `active` records describe their snapshot, not present authority; late old-runtime claims remain unverified. This runtime activation must not rewrite the restored learning history or manufacture elapsed work.

For any report, first resolve effective records at committed sequence **S** within the identified library prefix. S must be a complete transaction-boundary watermark returned by a consistent snapshot, including associated receipts; an arbitrary record sequence that bisects an assessment/correction transaction is ineligible. Then evaluate endpoint maturity at frozen instant **T**, select the frozen population/filters and aggregate occurrence times into explicit UTC buckets. Recomputing tomorrow must not mature new checks inside yesterday's report. Late arrivals and accepted corrections can change a new report but not the saved old one. Rebuildable derived views are not another source of truth.

Show collection quality as separate counts/durations: placed foreground estimates, placed self-reports, unplaced known duration, known unaccounted intervals, unknown tails, conflicting/stale claims and pending persistence. A coverage fraction exists only when its total accounting envelope is known. Hashes detect changed bytes; they do not prove the truth of an assessment.

These additions belong to the still-unreleased format proposal; they are not a migration from nonexistent production data. The [data-contract draft](data-contract.md) now reconciles the payload additions, transaction membership, occurrence-time uncertainty, endpoint-assignment revisions, criterion-to-unit interpretation, source-prefix fingerprints and replay. It includes sixteen adversarial acceptance examples. The baseline settles the metric/data design dependency; the [audit ticket](issues/09-data-contract.md) retains its history and later qualification concerns. Persisted behavior and import are not qualified by this document.

Intentional deletion/redaction is not solved by append-only history. The [deletion design](deletion-design.md) specifies archiving, curriculum removal, whole-library deletion, managed/external copy boundaries and interruption. The user accepted archive plus whole-library deletion for the first release; individual answer/source erasure and its format work are deferred. No retention service or actual deletion is authorized.

## 8. Readiness and open decisions

The [consolidated readiness review](readiness-review.md) now maps settled user requirements, concrete recommendations, implementation qualification and future experimental choices. Ordinary descriptive measurement does not depend on choosing a live experiment's tolerances; causal efficiency and policy adoption still do.

Measurement readiness requires a defensible claim, qualified assessments, functioning collection and reproducible reports in real use. Optimization readiness additionally requires a specified comparison, acceptable retention/cost margins, an appropriate analysis procedure and adequate evidence. Prediction fit and attractive dashboards satisfy neither gate by themselves.

The campaign has produced source-backed options and counterexamples. The user selected C as the preferred default, retaining A/B for their scenarios, and accepted archive plus whole-library deletion for the first release. A real pilot's tolerances, burden and statistical feasibility remain open. Browser/comprehension and real data-contract qualification remain outstanding. The single-learner local reference deployment and descriptive claims are fixed for design; actual setup and any hosted extension are separate work. Those are named in the [local decision tickets](issues/10-design-readiness.md) and [plan](plan.md); future selective-erasure details remain deferred proposals.
