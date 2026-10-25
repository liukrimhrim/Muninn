# C dashboard: calculations, interactions and evidence

Status: presentation contract included in [Design Baseline 1](../skill-maintenance/design-baseline.md), 2026-10-16. C is the selected default. Later everyday-learning, data and tracking rules override the original prototype's ranking and abbreviated calculations. Browser/accessibility/comprehension qualification remains outstanding.

[Open the self-contained walkthrough](spikes/c-walkthrough.html). Start at **Follow progress over time**; the displayed search example has eight skills checked on four dates. **Fix a grading mistake** demonstrates why saved reports and current history can legitimately differ. No subject exercise or checklist is required to explore it. All responses are invented, including the grammar and operations examples; the operations examples assess described actions, not actual execution.

The [campaign design](spec.md) supplies the research rationale and statistical boundaries. The [delivery plan](plan.md) supplies future implementation and qualification work. This contract makes the selected dashboard concrete.

Revision after user feedback, 2026-10-15: the user found the terminology difficult, the before/after bars unsuitable for time trends, and the walkthrough buttons unclear as workflow steps. These are observed usability problems in the earlier version. The revised source uses plain labels, a dated history chart and sequential steps. Whether this revision resolves those problems still needs user observation; the existing C preference is unchanged.

Subsequent feedback: the user says the revision “looks better” and requests flags for the five weakest knowledge units. This is positive presentation feedback, not a complete comprehension or accessibility result. The prototype now adds a shortlist with reasons and dated evidence.

After locating the new section, the user says “looks good. continue.” This supports the revised presentation direction and continuing design work. It does not establish real mastery estimation or a completed accessibility/comprehension study.

## 1. What the learner should be able to establish

The opening workspace answers five questions together: what changed on comparable targets, what was maintained, what evidence is absent or questionable, how much whole effort was accounted for, and whether an apparent improvement or saving survives inspection. A short statement above the evidence gives A's quick orientation; the target dialog gives B's detailed notebook. Practice remains directly reachable in the future app. The prototype has no practice route because it contains no actual learning system.

There is no universal mastery score. A target is a versioned capability under specified conditions and mode. Knowing a fact, connecting facts, explaining an integrated process and executing a procedure retain different meanings. The dashboard must not silently convert a described command into a demonstrated operational skill.

The learner-facing vocabulary is now explicit:

| Internal concept | Dashboard wording |
|---|---|
| Target | Skill — one thing you want to be able to do |
| Independent success | Correct without help |
| Assessment mode | Kind of question |
| Endpoint | Check on a named date |
| Comparable transitions | Became correct / stayed correct / became incorrect / still incorrect / cannot compare yet |
| Unresolved assessment | Not graded yet in the pending-grade example; use the actual reason, such as “grade needs review,” for other unresolved cases |
| Accounted effort | Time spent |
| Source cutoff, evaluation instant, manifest | Technical details, hidden until requested |

Use plain language in calculation explanations too. Retain exact definitions in this design and technical records, rather than requiring the learner to translate codes before understanding the main view.

An observed error is also not a diagnosis. The earlier conversation's binary-search misread is a relevant design requirement: a supported misread changes the interpretation of that response, not the learner's knowledge by decree. Retain the original response, supporting clarification, and accepted assessment interpretation; offer a fresh neutral check if evidence remains insufficient. Do not allocate remedial work solely because the first answer was wrong.

## 2. Population and observation rules

The [tracking contract](tracking-contract.md) now defines how the product creates these plans: useful ordinary history immediately, a previewed optional three-week same-skill comparison using regular reviews, and fixed membership/baseline/windows before answers. It also defines `claim-outcomes-1` for qualified metrics. The prototype and the raw examples below retain their version-1 definitions; they are not silently upgraded by this document patch.

Resolve exact curriculum and target revisions first. For progress, freeze the target set, mode/conditions, designated baseline, assigned endpoint and time window before observing the endpoint. The baseline cannot be selected retrospectively as the worst prior response; a later retry cannot replace the designated endpoint. A changed curriculum or mode produces a visibly different scope, not a continuation of an unlabelled trend.

Each matured planned endpoint has exactly one raw observation status. Delay/window/exposure qualification is a second axis, not a reason to relabel a graded answer U:

| Code | Meaning | Boundary |
|---|---|---|
| S | Independently judged success | Required target evidence is present; no relevant help disqualifies independence |
| E | Supported independent error | Accepted evidence supports an error under the target contract; this alone does not identify its cause |
| H | Usable judgment with relevant help | Show the underlying judgment in evidence; neither independent success nor independent error for this comparison |
| U | Submitted, but no usable target judgment | Pending, disputed, insufficient coverage or cannot-judge evidence stays unresolved |
| M | No submitted endpoint answer available | Include in the matured planned population; never manufacture a failure grade |
| N | Endpoint not yet mature | Outside the matured denominator; remain visible as planned future checks |

For a production endpoint, maturity uses its closed observation window and trustworthy time basis, not merely the scheduler's due reminder. The fixture uses a single authored due instant as shorthand for that boundary. An absent assignment and an assigned-but-unsubmitted attempt may both aggregate to M, but their reasons remain distinct in drilldown.

The unit of target coverage is not the unit of independent evidence. The main fixture has eight target contracts, seven submitted target results from four later exercise episodes, and one authored person. The first three larger episodes each support two target rows. A count of seven judged targets must never be presented as seven independent participants or used to justify a narrow sampling interval.

## 3. Exact displays and withholding rules

These are the raw observation calculations used by the authored walkthrough. Product claims requiring delay, exposure or other conditions must instead use the [qualified partition and formulas](tracking-contract.md#5-exact-calculations-and-sensible-withholding). For example, raw 5S+2E+1M with one too-early S remains 5/7 raw correctness and 7/7 grading coverage, but yields 4/8 qualified success coverage, one QX and one QM. No raw missing-only range is presented as a delayed-performance range in that case.

Let P = S + E + H + U + M, J = S + E, and C = P − M. Symbols in this section are endpoint counts; source cutoff S in a report manifest is a different, explicitly named field.

The following numerical examples use the October 8 check. The revised opening view selects October 22; selecting October 8 reproduces these examples.

| Display | Calculation | October 8 example | When to withhold or qualify |
|---|---|---|---|
| Correct without help, out of all planned skills | S of P; keep other statuses visible | 5 of 8 skills | This describes observed correct coverage, not a failure rate for the remaining skills. P=0 → unavailable |
| Independent success | S/J | 5/7 = 71.4% | J=0 → unavailable. Always show helped/unresolved/missing counts beside it; it is conditional on usable independent judgments |
| Check completion | C/P | 7/8 = 87.5% | P=0 → unavailable. A completion rate is not a learning outcome |
| Assessment coverage | (S+E+H)/C | 7/7 = 100% | C=0 → unavailable. Helped checks count as assessable, not independent successes |
| Comparable transitions | Counts E→S, S→S, S→E, E→E, plus incomplete pairs | 3 improved, 2 maintained, 0 regressed, 2 repeated errors, 1 incomplete | Unsupported pair comparability stays incomplete, with reason; do not relabel these as app-caused gains |
| Missing-only sensitivity range | [S/P, (S+M)/P] | [5/8,6/8] = [62.5%,75%] | Only the simple otherwise-judged, unaided case: P>0 and H=U=0. This is not a confidence interval |
| Accounted effort | Duration of the union of eligible placed intervals, with category reconciliation | 6+12+5+8+4+2+3 = 40 minutes | Unknown duration/placement remains separate. No coverage fraction without a known accounting envelope |
| Full-cost comparison | Show each outcome vector and each full cost separately | A=40 minutes; B=32 | Cost difference alone is not efficiency superiority. Withhold comparative retention claims for mismatched endpoint contracts |
| Task-mix comparison | Counts and rates within each predeclared stratum, plus population sizes | Easy 80%→70%; hard 20%→10%; pooled 26%→64% | Changed composition defeats a pooled progress interpretation. No weighted utility sum is substituted |

The transition display uses counts rather than percentages of only complete pairs. Every incomplete target stays visible, so missing checks cannot make a small set look fully improved. A chart can report an exact descriptive fraction without claiming precise knowledge about future performances.

Supported maintenance is a useful outcome: a maintenance example shows zero improved and five maintained. It is not failure because the number of newly improved targets is zero. Conversely, a repeated independent error is a prompt to inspect the underlying response and diagnosis; it does not establish that all practice was wasted.

The original one-pair fixture could only show a before/after comparison. In response to the user's trend feedback, the revised fixture explicitly adds repeated authored checks on October 1, 8, 15 and 22. It does not manufacture intervening observations from the old pair. The main chart counts correct-without-help results on the same eight skills: **2 → 5 → 4 → 6**. A dashed line shows helped, ungraded or missing checks together, with those categories separated in the accessible data table. It has values 0 → 1 → 1 → 1 in the main example.

The vertical scale is zero to the full selected skill count, never only the answered subset. Selecting a date updates that date's cards, skill rows, earlier-versus-selected comparison, missing-answer exploration and course effort through that check. Recorded course effort is 40, 62 and 80 minutes through October 8, 15 and 22 respectively; filtering skills preserves the full corresponding course cost. The old five-category comparison remains a secondary count summary, not the time-trend chart.

For product reports, [cost-cutoff-1](data-contract.md#historical-cost-boundaries) makes “through that check” exact: intersect the frozen investment window with the evaluation instant and saved selected-check boundary, clip crossing spans, then union once. A separate whole-period view requires evaluation at/after period end; otherwise label it period-to-date. Show unplaced duration separately. Each point and card keeps its own effective window. The authored walkthrough's numbers remain illustrations under its original definition.

Only available check dates appear. An early report contains one point and explicitly withholds a trend; no line extends into future results. Old report versions contain only dates and grades available then. Correcting an October 1 grade changes that historical point with an annotation; it does not create a new time point. Saved reports freeze the available series as well as the selected-date calculation.

For real history, retain fixed population, mode, check timing, exposure context and metric definition. Missing scheduled periods must not be silently skipped; no interpolation or fitted memory curve is implied by connecting observations. This fixture illustrates dated observed performance, not a standardized retention curve: later dates have different elapsed times and intervening practice is not controlled. Model predictions, calibration and causal effects remain separate panels with their own qualification rules.

### Five weakest knowledge units: an inspectable review order

The section below describes the **implemented authored prototype rule, version 1**. The [everyday-learning contract](../skill-maintenance/everyday-learning-design.md#baseline-shortlist-observed-concerns-2) specifies baseline `observed-concerns-2` for the product: unresolved difficulty, recovery awaiting a later check, and missing evidence have separate groups; age/due state remains visible without invented decay. Its [dashboard-to-practice flow](../skill-maintenance/everyday-learning-design.md#6-from-dashboard-to-practice-and-back) also specifies answer revelation, corrections, stale-report actions and return navigation. C's placement and analytical direction remain selected. The policy is adopted in Design Baseline 1 but is not implemented in the walkthrough; version-1 reports retain their original definition.

The user's request is implemented as an **up-to-five shortlist from observed checks**, not an estimated mastery percentage. Each entry shows its unit name, question type, current recovery status, dated correct/incorrect history, why it is flagged, and whether to inspect the mistake, check a recent recovery or simply continue normal practice. The main skill table repeats the flags, and “See why” opens the actual saved answers used. All results still refer to the invented example learner.

Rule `observed-review-order-1` is a proposal for descriptive triage. Use accepted effective judgments available at the chosen source cutoff and only check dates through the selected date (or the report evaluation date if earlier). Currently incorrect units come first; within that group, a longer current run of incorrect checks takes precedence. Then consider units currently correct but with earlier errors, ordering fewer consecutive correct checks first. This is a lexicographic rule, not a weighted sum, calibrated mastery model or causal scheduling policy. Single mistakes remain single observations; repeated difficulty requires repeated recorded mistakes. Units with no recorded error are not added merely to fill five positions.

Equal evidence remains tied; alphabetical order only makes the display deterministic. If a tie extends beyond the five-item display, name the omitted tied units. Latest missing, ungraded or helped checks are listed separately as needing a check or grading review, with the last known unaided result retained. Missingness is not a zero-mastery score, and a past error is not erased by a missed later check. Supported misreads and disputed/unaccepted assessments must not create an error-based weakness flag; the current fixture contains accepted ordinary errors, with the correction scenario demonstrating removal of an invalid earlier error.

The October22 example flags Boundary handling first; Depth versus total work and Stopping condition tied next; Choosing a search strategy next; and Work across branches last. Their recent records explain the order: four incorrect checks; one correct after a recent error; two correct; and three correct respectively. The last two are explicitly improving/holding up and do not trigger extra remedial work just to fill the list. Ordering assumptions is separately marked for a fresh check because its later answers are missing. Correcting the earlier Work across branches grade removes it from the October8 shortlist; only four eligible units remain.

In this bounded prototype each named skill represents one knowledge unit in one mode. In the full system, group flags by stable knowledge-unit identity and identify the weak requirement/mode inside each unit; do not count the same unit five times or average recall, explanation and execution into a single score. No diagnostic or scheduling action runs from this prototype. The rule, scope, cutoff, ranks/ties and supporting checks are retained in its saved report copy.

## 4. Controls and state transitions

For new product definitions, show **“Help received; time unknown”** when the hint is known but its clock is not; keep the usable judgment and helped status. Explain **“Relevant answer was available in another view”** for known external aids, without inventing an in-task hint. Apply the shared [assistance resolver](data-contract.md#known-assistance-with-uncertain-time) to progress, recovery and scheduling decisions.

The whole-curriculum effort card follows [cost-membership-1](data-contract.md#frozen-cost-membership-across-revisions) and says **“Time spent on this curriculum”**, with the selected interval and the explanation **“Includes work on skills added or removed since tracking began.”** Keep the fixed outcome population visibly separate. Drilldown shows included context, uncertain/unallocated overhead and shared encounters; combined totals count shared time once. A target/source-only view is labelled **“Time linked to these skills/source”**, never whole-curriculum effort. Scope, rule, exact evidence and attribution corrections are inspectable; saved historical reports retain their original definition and value. These rules extend the design, not the existing prototype's implementation.

| Action | Changes the calculation? | Required behavior |
|---|---|---|
| Choose curriculum | Yes | Resolve its exact selected targets; reset incompatible mode selection; identify the new population |
| Choose assessment mode | Yes | Recompute outcomes and exclusions. Keep full shared encounter cost; do not invent per-target cost allocation |
| Choose source/evaluation snapshot | Yes | Resolve only available revisions through the source cutoff, then evaluate endpoint maturity at the selected instant |
| Choose a plotted check date | Yes | Keep the whole fixed-set history visible; update the selected check, paired comparison and course effort through its saved UTC boundary, capped by evaluation time; preserve each other point's own cost interval |
| Highlight successes/errors/missing | No | Keep all rows and denominators; use an explicit highlight. This is inspection, not an outcome-based eligibility filter |
| Open a calculation | No | Show formula, actual counts, population, interpretation and withholding rule |
| Inspect target evidence | No outcome change | Show exact criterion, submitted answer, scoped help, effective judgment, revision chain and shared episode identity. In the product, record possible answer-bearing exposure |
| Change missing-outcome what-if | No recorded change | Show scenario result separately; do not impute a grade, alter the scheduler or overwrite a saved report |
| Change cost scope in comparison | Only the separate comparison | Expose answer-only omission; the original curriculum totals remain intact |
| Save report | No history change | Freeze scope, source identity, evaluation instant, evidence, definition and reported values. Subsequent controls do not edit this copy |
| Accept a judgment correction | Changes current historical interpretation | Append accepted revision with reason and provenance. Keep the original event time and old report; create no additional attempt or learning event |

The prototype supplies population filters, row highlighting, formula/evidence dialogs, what-if controls and an in-memory frozen report. It uses predefined snapshots to illustrate accepted corrections; it has no editable correction submission, durable saving, storage, telemetry, scheduler or export/restore path. Closing/reloading loses saved prototype state.

Each walkthrough tab resets to a known search fixture and displays an ordered, numbered step list with completed/current/upcoming states. Only the current step has its action exposed. Running it changes the example, displays “What changed,” and enables Next. Back restores the state before the previous action; Start again resets the story. Finish visibly marks the workflow complete. The grading-correction story follows original report → save copy → apply correction → inspect old copy. There is no arbitrary row of executable future-step buttons.

Free-play filters and date buttons pause the guide explicitly, so changing to grammar cannot leave a search-specific instruction pretending to describe the current view. Restart restores the guide's known state. Merely inspecting a formula or answer does not pause it. The two comparison panels remain separate authored populations. Their labels, own denominators and controls prevent their 100 task opportunities or method groups from being mistaken for extra observations on the main eight skills.

Product navigation should preserve selected scope, expansion and focus on return. Accessible implementation requires labelled controls, keyboard tab navigation, visible focus, named dialogs with focus return, text as well as color, table headings/captions and a reflowing page around scrollable tables. The source includes these affordances; actual browser and assistive-technology behavior remains unverified.

## 5. Worked cases and permitted conclusions

| Case | Result to inspect | Conclusion that must not appear |
|---|---|---|
| Opening four-date history | 2→5→4→6 correct of the same8; October22 has4 became correct,2 stayed correct,1 incorrect,1 missing | An interpolated memory-strength curve, or claiming6 newly learned skills |
| October8 progress | 3 improved, 2 maintained; 5/7 conditional success; 1 missing | “Five new skills learned” or “71% mastered” |
| Explain-only population on October8 | 6 selected targets, 5/6 judged successes, 3 episodes, 2 excluded targets; still 40 whole-encounter minutes | “The learner improved because the filter raised the rate” or an invented subset cost |
| Missing outcome succeeds in a scenario | Scenario fraction 6/8; recorded counts remain 5 S, 2 E, 1 M | A new success event or claim that 6 outcomes were actually observed |
| Maintenance | 0 improved, 5 maintained | “No worthwhile outcome” from the zero-improvement count alone |
| Correction | Original: 3 improved,2 maintained. Revised: 2 improved,3 maintained. Later grades unchanged | A new acquisition today, or a silently changed saved original report |
| Relevant help and pending judgment | 3 S,2 E,1 H,1 U,1 M; success3/5; completion7/8; assessment coverage6/7 | Independent credit for the helped target, an error for U, or the simple missing-only bound |
| Checks not due | 8 N, P=0; outcome rates unavailable | Zero knowledge, eight failures or eight missed checks |
| Full-cost reversal | Answering: A12,B20. Full: A40,B32 | Choosing A on answer speed alone; claiming B preserves retention from matching counts |
| Unplaced cost | A27 placed plus0–20 potentially additional; B32. More than5 additional minutes reverses the ranking | A measured full total, probability of superiority or settled cost winner |
| Mismatched horizon | A at7 days, B at1 day | Direct comparative retention or a policy recommendation |
| Changed task mix | Pooled26%→64%, both stratum rates down10 points | Comparable learning gain from the pooled increase; causal deterioration from the strata alone |

The pure model's [calculated outputs](spikes/c-calculation-results.json) record these checks. They verify arithmetic and model behavior on authored data. They cannot validate assessor quality, actual retention, live timer behavior, user interpretation or motivational benefit.

## 6. Records needed behind every display

The existing [logical record contract](../skill-maintenance/compatibility-design.md#3-portable-logical-records) and [observability payloads](../skill-maintenance/observability-design.md#8-collection-and-reproducibility-contract) already carry much of the necessary history. The table preserves the original foundation/addition distinction; the linked data and tracking contracts now specify those additions, including the subsequent seven-gap patch. No separate analytics service is implied.

| Display / interaction | Existing source records | Required completion of the design |
|---|---|---|
| Selected targets and exclusions | `curriculum`, `enrollment`, exact `target` refs, `measurement_cohort.targets`, endpoint mode | Saved query must include resolved targets and exclusion reasons, not only free-text filters |
| Success and transitions | Bound `attempt`, accepted `assessment.results`, scoped assistance, endpoint baseline and assignment | Per-endpoint resolution must retain eligibility reason, exact submitted/assessment refs, judgment status and comparability result; no best-retry lookup |
| Dated history and date selection | Repeated planned endpoints, occurrence times, exact attempts/assessments, source cutoff | Persist available check-date series, fixed resolved target set, selected endpoint/date, per-date statuses and evidence. Do not create a weekly trend by repeatedly displaying one answer |
| Completion and not-yet-due | Endpoint window, designated attempt's submission, report source cutoff | Add frozen evaluation instant; preserve no-assignment vs no-submission vs pending judgment in the result details |
| Misread and corrections | `assessment.interpretation`, `supersedes`, `revision_reason`, response/criterion quotes, `transition` | Show supporting clarification and provenance; reconstruct effective judgment at each source cutoff without moving the attempt time |
| Shared exercises | `attempt` identity, exercise family, criterion-to-target coverage | Keep distinct target, endpoint, attempt, family and person counts; declare intended inference unit separately |
| Effort breakdown | `activity_span` category, scope, duration, measurement and collector | Add run/owner/generation, monotonic duration provenance, raw clock anchors, placement confidence and acknowledgment/unknown-tail state. Category overlap needs explicit resolution before per-category totals sum to the union |
| Answer-bearing inspection | Existing `study` cannot truthfully represent merely viewing an answer | Proposed possible-exposure record: exact content/target refs, surface, shown time/bounds, visibility provenance. No automatic study completion or FSRS review |
| Outside learning | No structured interval-quality exposure payload in the original table | Proposed exposure evidence with reported interval/bounds or unknown timing, source and target scope; distinguish not recorded from known absent |
| Reproducible saved report | `measurement_report`, algorithm definition, results, refs, source sequence | Extend with transaction-complete source identity/fingerprint, evaluation instant, frozen query, endpoint resolutions and cost-quality summary. Scope closure must include required receipts and definition representation |
| Hypothetical scenarios | No learning record required | Store separately as report annotations only if the user saves them; never insert an assessment for a what-if |

Proposed report additions, expressed as logical fields rather than SQL DDL:

```text
source = {library_id, through_sequence, snapshot_fingerprint,
          fingerprint_algorithm, receipt_scope}
evaluated_at = Time
query = {curriculum_refs, target_refs, cohort_refs, modes,
         baseline_rule, endpoint_rule, selected_check, history_window,
         time_window, display_timezone}
endpoint_resolutions[] = {cohort_ref, endpoint_id, target_ref,
  baseline_refs, submitted_attempt_ref?, assessment_refs,
  state, eligibility_reason, comparability_reason, exposure_refs}
exclusions[] = {ref, reason}
cost = {scope_refs, window, placed_span_refs, unplaced_span_refs,
        union_duration_ms?, unknown_tail_count, conflicts, limitations}
inspection = {highlight}                 # no effect on metric eligibility
scenarios[] = {assumption, result}        # separate from recorded outcomes
```

These are the display's information requirements. The [data-contract draft](data-contract.md) now supplies receipt membership, source-prefix canonicalization, bounded exposure, timer authority, assignment revisions, time-quality and correction rules. It also extends the one-unit/one-mode example to real multi-unit evidence without assigning every error to all participants. Design Baseline 1 settles the metric/data design dependency; the [audit ticket](issues/09-data-contract.md) retains the earlier discussion and runtime qualification concerns. The initial base payload table must be read with the addendum. The prototype's short IDs, synthetic sequences and relative minute spans are explanatory shorthand, not valid production import records or proof that an importer exists.

The report read order is fixed: obtain a consistent complete-transaction snapshot and its identity; resolve accepted revisions through that cutoff; resolve the frozen population and assigned attempts; evaluate windows against `evaluated_at`; classify each endpoint with its reason; aggregate counts and eligible effort; retain exact evidence and calculated values. Late answers and corrections belong to a newer report. Restoring the same records with the same source identity and evaluation instant must reproduce the old result; equal sequence numbers alone do not establish equal source data.

Exports should be scoped: a normal table includes counts, definitions, scope, reasons and references without answer text by default. A full-library archive follows the compatibility contract. A saved fixture report here includes authored responses for inspection; that choice is not the production export default. Apply the accepted archive/whole-library-deletion scope; do not promise replay after removing required evidence.

## 7. Stop conditions and next design work

This continuation finishes the concrete C walkthrough and calculation/data mapping promised after the layout choice. It does not close the whole observability campaign. The later data/tracking/deletion contracts and final baseline settle the design reconciliation. Actual browser/comprehension and runtime measurement qualification remain outstanding. A real efficiency experiment additionally needs explicit retained-performance/cost tolerances, burden and analysis choices; none are selected on the user's behalf here.

The user's readability/trend/workflow feedback is now incorporated in the revision, not recorded as approval. Syntax and authored model calculations can verify counts, date cutoffs and correction history; they cannot establish that the revised workflow is understandable or visually accessible.

The saved-record and query drafting pass is captured in the [data-contract audit](data-contract.md). The [deletion/report-retention recommendation](deletion-design.md) and [readiness consolidation](readiness-review.md) are incorporated in Design Baseline 1. More dashboard variants or extra statistical machinery are unnecessary until a named unresolved question calls for them. Production implementation remains a separate decision.
