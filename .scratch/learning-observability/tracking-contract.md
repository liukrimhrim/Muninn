# Useful history and honest planned comparisons

Status: comparison-plan lifecycle and claim-qualified calculation contract finalized in [Design Baseline 1](../skill-maintenance/design-baseline.md), 2026-10-16. This includes the lifecycle audit patches and named qualification ownership. Ordinary tracking adds no exercise solely for measurement; it is not an authorized optimization experiment.

This is the canonical extension for comparison-plan lifecycle and qualified aggregation. The [data contract](data-contract.md) still owns source cutoffs, time evidence, transaction closure and saved-report integrity. The [C contract](c-dashboard-contract.md) retains its raw-state formulas and presentation direction; new claims must use the separate definitions below. All constants are disclosed first-release defaults, not empirically optimal settings.

## 1. Ordinary history works before a tracking plan exists

The default dashboard starts with **Your practice history**: dated answers, corrections, helped/unknown outcomes, active and unstarted goals, current next actions and whole effort. Per-target timelines show actual attempts and dates; daily/weekly activity summaries show their changing population and episode count. Unknown dates remain in a separate group. Repeated attempts, question mix and shared episodes remain visible. These views need no experiment or fixed cohort.

Do not turn a rising rate over an evolving mix of tasks into “you improved on the same skills.” A learner who has practised for two weeks without making a tracking plan still gets useful history and evidence drilldown. Opening the dashboard cannot retrospectively invent a prospective comparison.

**Follow the same skills over time** is the planned comparison inside C, using ordinary review work. If no plan exists, show a compact invitation with its purpose and an explicit **Start tracking** action. Show it on the first progress visit after practice admission, or when the learner deliberately selects it. No modal, repeated prompt or extra test is required. Dismissing it preserves the ordinary history view.

The workflow is **Preview scope and dates → Start tracking → Use ordinary practice → Inspect each window's results**. Each step shows its current state. “Tracking” means recording a fixed observational comparison; it does not mean experimentally assigning a teaching policy.

## 2. A concrete default plan

Use baseline version `routine-tracking-1`:

| Decision | Default and reason |
|---|---|
| Population | All admitted, active exact targets in the selected curriculum at freezing; deduplicate shared targets. Preview unstarted/paused/held targets separately and include held admitted targets with their reason, so authoring trouble is not hidden |
| Goal coverage | Still show all selected goals alongside this smaller tracked set; “3 tracked of 200 selected” cannot become whole-curriculum completion |
| Baseline | Last submitted attempt for each exact target/contract known at freezing, regardless of result/help; never search backwards for a more favorable or worse answer. Preserve missing/pending/helped/ambiguous baseline as such |
| Duration | Three consecutive seven-day windows starting at freeze F: `[F,F+7d)`, `[F+7d,F+14d)`, `[F+14d,F+21d)` in UTC. These are observation windows, not new due dates |
| Review burden | Assign only an ordinary scheduled check the learner would otherwise receive; no extra prompts, changed interval, suppressed feedback or delay to manufacture an endpoint |
| Endpoint within a window | The first qualifying *offer* of an ordinary owned check for the target in that window, bound before presentation/submission; include its result even if it later becomes helped, invalid, missing or unjudgeable |
| Allowed exercises | Accepted family IDs declared at freeze, under the same exact capability/mode/conditions and accepted authoring review. New instances in those families may be generated normally; a new family or changed demand needs a new future plan |
| Primary claim | Comparable recorded performance, under named conditions; intervening learning is allowed and disclosed, so this is not retention without rehearsal or a causal effect |
| Optional later-check claim | At least 24h after the frozen learning/condition anchor and after any subsequent relevant exposure, in a later session; otherwise withhold that claim while retaining the primary observation |
| Cost | Freeze the selected enrollment ref as the whole-curriculum effort root, `effort_membership: cost-membership-1`, and investment window `[F,F+21d)`. Follow that enrollment identity across revisions, including attributed work on added/removed goals, shared episodes, setup/feedback/correction and unknown timing; keep outcome targets frozen separately. Each display intersects that window with its evaluation/selected-check cutoff under [cost-cutoff-1](data-contract.md#historical-cost-boundaries); a frozen window does not include future effort in an earlier report. Show prior investment separately; never allocate shared exercise time across its target rows |

“Qualifying offer” tests pre-answer facts only: current ordinary need/ownership, exact target/mode, accepted compatible family, window and requested conditions. Outcome, confidence of a later grade and whether the learner succeeds cannot influence assignment. Help requested after assignment remains that endpoint. Draft abandonment also remains that endpoint. A suitable check that is saved without a prior assignment stays ordinary history; no retrospective repair of the plan.

The preview lists actual targets, baseline dates/statuses, three windows, known scheduled reviews and any windows likely to have none. Say “We will use your normal reviews. Some windows may have no check.” Choosing tracking must not make review debt, change selection priority or demand performance on a calendar deadline. The learner can narrow scope before freezing; save that chosen scope, even if self-selected. It does not justify population-wide or causal claims.

If no targets are admitted, show ordinary goal coverage and the start-practice action; do not save a zero-population comparison. If a target has no usable exercise family, keep it in the planned set with empty family eligibility and `authoring_unavailable`; future missingness stays visible. A future plan can include the newly accepted family. Fixed windows are a simple first-release default; a new plan is required to change them. No automatic extension until the chart looks better.

### Baseline and anchors are different

The baseline is the last submitted target-bound attempt before F, with its exact submitted ref and accepted assessment at the source cutoff. If supported ordering cannot identify a unique latest attempt, save the candidate refs with `baseline_state: order_uncertain`. Missing baseline uses an empty list; never infer failure. Pending/helped baseline cannot yield an independent transition merely because an older response was usable. A later correction can revise that same chosen attempt's interpretation in a new report; a later answer cannot replace its identity. Old reports retain their old interpretation.

For the optional later-check metric, freeze a separate `anchor` per target: the most recent supported learning/study/exposure occurrence or an explicit prospective condition checkpoint already recorded before F. Its timing must be bounded enough for the stated comparison. If it is missing or order-uncertain, set anchor null, retain the reason and withhold this claim for that target in this plan. A future plan can use new known history. The primary observational claim does not require an old learning anchor and remains useful with an unknown baseline.

The later-check rule tests the frozen anchor **and** any more recent recorded relevant exposure before/during the answer. Exclude the checked response's own retrieval occurrence from prior exposure; actual hints/answer views during that attempt still count. It cannot infer a controlled exposure-free interval. “No recorded exposure after anchor” is a different stricter metric, not the default. Feedback after submission applies to future checks only. A plan must name its exact claim; no generic “mastery” or “retained” label covers all of these meanings.

## 3. Plan creation, closure and changes

Preview is disposable UI state. **Start tracking** commits the cohort, exact baseline bindings, current source cutoff, definitions, targets, windows, cost roots and membership algorithm in one command before any endpoint assignment. Freeze time F is this plan decision time, not a fabricated learning event. Refreshing or retrying this command returns the same cohort.

At ordinary offer creation, atomically assign a still-null endpoint to its initial draft. Offer ownership, cohort assignment and draft creation use one complete receipt. If an attempt was already created/presented or submitted, it cannot be attached later through an old draft revision. If two plans share an eligible ordinary check, both may reference that same draft prospectively, but it remains one attempt/episode and one actual cost. Reports disclose this dependence.

The window closes at its end, not when the user opens the report. Endpoints remain N until `T >= window_end`, even if a provisional response is already available. Show such early responses in ordinary history or explicitly as provisional, outside matured aggregates. A missing assigned response, or no suitable offer at all, becomes M with the actual reason. An answer after the window cannot be substituted into a closed point; its stored result is visible as late/unqualified when the report's T includes that answer. A late *commit* of an answer genuinely produced inside the window can qualify in a later-source report, with time provenance. The earlier saved report does not change.

Add these fields to `measurement_cohort`:

```text
creation_source: SourcePrefix,
plan_rule: Algorithm,
lifecycle: active/stopped/completed,
stopped_at: Time?, stop_reason: text?,
predecessor: Ref?,
baseline_rule: text,
claim_definitions: Algorithm[]
```

`claim_definitions` contains the complete named/versioned qualification identities resolved by Evidence, including validated parameters, under the [module claim contract](../skill-maintenance/module-design.md#named-qualification-claims). Measurement selects supported variants and labels them; it does not implement its own independence/delay evaluator. The report definition retains the resolved identities even without a cohort. Reporting precedence, window maturity and arithmetic remain Measurement-owned. Unknown older definitions make reproduction unavailable, never trigger a silent fallback.

`creation_source` is the complete prefix preceding creation, so baseline/anchor/definition refs already exist there. The cohort's own transaction is later. `predecessor` links a deliberately changed/restarted plan. Extend each `Endpoint` with `baseline_state: selected/missing/order_uncertain`, `anchor: Ref?`, `anchor_reason: text?`, `assignment_rule: text`, and `assignment_offer: Ref?`. The original nullable `assigned_attempt` remains. Non-null assignments name the initial draft and exact offer revision; both refer to the same attempt identity/target. New exercise instances are not new target contracts.

Allowed cohort revisions are now: (a) null assignment fields become their first draft/offer pair before presentation; (b) lifecycle moves active→stopped or active→completed, retaining a reason/time for stop. All definition, population, baseline, anchor, window, cost-root/membership and populated assignment fields are immutable. Completed is allowed only after all frozen windows close; it means the tracking period ended, not that checks succeeded. Lifecycle writes may combine with assignments in one transaction where valid. Reopening never reactivates a stopped plan; start a successor instead. Creation refs stay frozen across lifecycle revisions.

Stopping prevents new assignments. It neither deletes future endpoints nor matures them early: they remain planned/not-yet-matured until their original end, then missing with `plan_stopped` if unanswered. Already assigned responses keep their bindings and can still be interpreted under the original rules. The UI shows stopped prominently; it must not treat abandoned tracking as evidence of a learner's failure. Saved before-stop reports retain their original lifecycle.

Added curriculum targets are shown under “Added since tracking began,” outside the frozen comparison and inside ordinary goal/history views. Removed/paused targets remain inside the frozen population; no new practice is forced there, and unavailable checks show the reason. Changed meanings are incomparable, not reassigned to new definitions. New relevant exposure can disqualify an endpoint without removing it or requesting a compensating test. Corrections change effective evidence at the same identities; they do not refreeze the baseline or remove inconvenient targets. The whole-curriculum cost continues to follow the frozen enrollment identity under [cost-membership-1](data-contract.md#frozen-cost-membership-across-revisions), including work on changed goals without adding them to the outcome denominator. A successor plan may explicitly change scope or contracts; its chart starts a separately labelled series.

## 4. Two axes for every endpoint

Keep the existing raw outcome axis `S/E/H/U/M/N`: usable correct/error without recorded relevant help, usable helped judgment, unusable target judgment, missing answer, or not mature. Separately save each claim's `eligibility: eligible/ineligible/uncertain`, all reason codes and the refs supporting them. A correct answer that is too early remains graded and correct in its raw evidence. It is not U, E or dropped from the planned population.

Time-uncertain raw observations must say “date/conditions uncertain.” Raw S/E means the recorded response meets that judgment under the recorded aid information; it is not certification that no unrecorded aid existed. Known available task-specific aids violate a no-aid condition and produce H when the judgment is usable. Under [assistance-evidence-1](data-contract.md#known-assistance-with-uncertain-time), known in-task help remains H with an unknown display time; resolve external aids too, rather than using the local hint flag as certification of independence. Unknown availability retains its raw judgment and causes uncertain claim eligibility. Never show that candidate as an unqualified independent success.

For an as-of report, a submission definitely after T is not an answer by T: its endpoint is M and no future grade appears. If occurrence could fall on either side of T, retain the candidate's raw grade separately with that temporal limitation, and make the as-of claim uncertain. Do not change a perfectly usable grade to “not graded” to represent uncertain chronology. A later report with adequate time evidence can resolve this without changing the answer.

### One mutually exclusive qualified partition per claim

Version the mapping as `claim-outcomes-1`. For each endpoint, evaluate every applicable reason, then choose exactly one bucket using this precedence:

| Precedence | Bucket | Rule | Learner-facing label |
|---|---|---|---|
| 1 | QN | Window not mature at T | Planned for later |
| 2 | QM | No submitted answer available by T; definitely-after-T answers do not count yet | No answer for this check |
| 3 | QU | Submitted but target judgment unusable | Not enough grading evidence; show the actual reason |
| 4 | QH | Usable judgment with relevant help | Answered with help |
| 5 | QX | Otherwise S/E, but any claim condition is ineligible or uncertain | Does not establish this result; show why |
| 6 | QS / QE | Otherwise raw S / E and all claim conditions eligible | Correct / incorrect under this check's conditions |

QN is outside the matured denominator. QH wins over QX for the partition when both help and a timing violation exist; drilldown retains **both** reasons. QU wins when no target judgment is usable, even if help was shown. This is reporting precedence, not causal attribution. Within QX, retain known-ineligible versus uncertain counts separately: any confirmed violation makes the claim ineligible, otherwise an unresolved required condition makes it uncertain. List all reasons in fixed order: content/contract mismatch, occurrence window, aid availability, minimum delay, relevant exposure, mode, coverage, baseline comparability. Do not pick only the most flattering reason. Reason counts can overlap and must be labelled non-additive; bucket counts cannot overlap.

Qualification is **claim-specific**. A valid delayed endpoint with no usable baseline may count QS for endpoint performance, while its change-from-baseline claim is incomparable. The absence of a baseline must not disqualify an otherwise valid endpoint-only claim. Conversely, raw S cannot be inherited as QS for every claim. Supported misreads and disputed judgments retain their existing non-error interpretation.

Extend `EndpointResolution` with `claims: [{claim_id, eligibility, reasons, bucket, baseline_qualification, comparison_state}]`. Each reason has its code, eligible/ineligible/uncertain result and evidence refs. Unneeded baseline qualification is explicitly `not_required`. Preserve underlying criteria, raw grade and assistance separately. A new report definition snapshots this mapping; old reports/prototype version 1 retain their recorded definitions.

## 5. Exact calculations and sensible withholding

For matured endpoints, `P = S+E+H+U+M = QS+QE+QH+QU+QM+QX`. Raw counts and qualified counts are separately named output objects. No variable named merely `success` may supply both metric families without its definition. Zero denominators yield unavailable, not zero percent.

| Question | Formula and conditions |
|---|---|
| How many recorded answers were correct under their recorded aid information? | Raw `S/(S+E)` with H/U/M and uncertain-condition counts beside it. A time-uncertain candidate is labelled separately, not plotted as a known event on that date |
| How many submitted checks received a usable grade? | Raw `(S+E+H)/(P-M)`; a fully graded but timing-ineligible answer still counts as graded |
| How many planned checks established the named result? | `QS/P`, with QE/QH/QU/QM/QX shown beside it and QN outside P. This is qualified observed coverage, not a failure rate for every other target |
| How often were qualifying independent judgments correct? | `QS/(QS+QE)`; disclose the full P and all excluded/unknown buckets. The smaller denominator cannot stand in for the whole plan |
| How complete is the checking? | Raw `(P-M)/P`, plus the explicit count whose occurrence by T is uncertain. If such timing ambiguity exists, label this stored-submission coverage and withhold an exact by-T completion rate |
| What changed on the same targets? | Counts of qualified E→S, S→S, S→E, E→E, plus every incomplete/incomparable pair. Each pair must pass the declared phase-specific contract; do not omit incomplete pairs from the fixed target denominator |
| How sensitive is this to missing answers alone? | `[QS/P,(QS+QM)/P]` only when `P>0` and QH=QU=QX=0, with comparable population and all remaining independent judgments eligible. This is a scenario range, not a confidence interval |

The raw missing-only range remains valid only for its **raw** descriptive question under the old H=U=0 assumptions. It must not be labelled a qualified later-performance range when QX>0. With helped/ungraded/ineligible/uncertain outcomes, default to the full partition and reason inspection. Optional explicit what-if scenarios may ask what would happen if named unusable endpoints had instead yielded qualifying successes/errors; save the hypothetical assumptions separately. They are counterfactuals requiring different or newly established evidence, not bounds on observed learning or an imputation of grades. No general statistical interval is claimed.

For eight matured endpoints with raw 5S,2E,1M and one S known too early: raw correctness is 5/7, raw grading coverage 7/7, and qualified counts are 4QS,2QE,1QX,1QM. Qualified coverage is 4/8; conditional qualified correctness is 4/6. The raw missing-only scenario 5/8–6/8 cannot answer the delayed question. The qualified missing-only range is withheld because QX is nonzero. If an analyst explicitly assumes both the too-early case and the missing case would pass a different qualifying check, that separate counterfactual is 6/8; it is not recorded progress.

`MetricResult` gains `raw_counts` and `claim_counts` (both nullable when inapplicable) and `claim_id: text?`. The previous generic `counts` is retained only for old report definitions, not reused ambiguously by new ones. `claim_counts` includes qualified_success, qualified_error, helped, unresolved, missing, ineligible_or_uncertain, not_matured, plus the QX eligibility split and non-additive reasons. Query/report definitions identify which axis feeds every numerator. Cost remains a separate result with its quality limitations; there is no weighted learning-efficiency score.

## 6. Presentation and verification

In C, show the primary same-skill series by its window label and the date range; do not imply every answer happened at the midpoint. Each point has the fixed population and visible nonqualifying categories. Raw practice history remains a different selectable view. A later-check toggle uses its own qualified counts and explanatory sentence, not a renamed raw chart. A counts-only quality panel can explain “One correct answer was too soon” without revealing that answer before a check.

The initial point can show an incomplete baseline. Do not interpolate knowledge during missing windows or join separate scopes into one continuous improvement line. New-source/assessment corrections receive annotations; frozen reports remain as recorded. A/B's quick orientation and detailed evidence views retain their existing roles inside C.

The [closure traces](../skill-maintenance/cross-contract-closure.md) cover ordinary history with no plan, frozen membership, absence/help, late answers, stopped plans and two-axis arithmetic. Arithmetic enumeration is a design check, not an implemented query. Real qualification must run the actual offer/assignment/save/reopen/report path and compare source fingerprints, populations, reasons and formulas after correction/restore. These additions belong to the existing collection/dashboard slices and require no analytics service.
