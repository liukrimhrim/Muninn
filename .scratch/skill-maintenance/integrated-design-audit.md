# Remaining gaps after the lifecycle and observability patch

Status: third design audit, 2026-10-15, responding to “do another pass to find out other gaps.” Baseline: research snapshot `2e679b8` and the corresponding user-visible documents. This inspection finds four substantive gaps. It does not patch their policy, implement the app or report live defects.

Follow-up: the user requested “patch them.” The [four-gap closure](integrated-design-closure.md) now supplies concrete proposed rules and outcomes for G01–G04 and all ten cases below. The original findings remain as baseline provenance; they are no longer an unresolved drafting backlog. Runtime correctness and policy value remain unverified.

The previous seven-gap patch supplied useful rules, but its closure cases do not establish that all combinations of those rules work. Two findings below concern edge cases in that patch itself. The other two connect existing learning and reporting contracts. These are document-level findings with authored counterexamples, not evidence of incident frequency, learner harm or an empirically ranked backlog.

| Finding | What is still missing | Evidence classification |
|---|---|---|
| G01 Historical corrections after subsequent checks | What happens to later real checks whose scheduling basis is invalidated | Missing transition across existing rules |
| G02 Being caught up after repair | Whether replaced checks remain in the completion denominator forever | Conflict under the literal completion rule |
| G03 Exposure across different learning targets | Which other targets a revealed answer helps, without transferring achievement | Missing scope-resolution rule |
| G04 Effort at a selected historical date | How the frozen cost window is capped by the report and selected check time | Display/query contract mismatch |

## G01. Correcting an old assessment can invalidate the basis of later checks

**What is already specified.** The [ownership and event-order contract](learning-lifecycle-contract.md#4-one-due-opportunity-two-tabs-and-late-grading) preserves real answers, binds each owner to an obligation, prevents rebinding an old answer to today's opportunity and replays corrections in occurrence order. Its final replay step replaces an invalidated successor while retaining lineage. The [compatibility contract](compatibility-design.md#7-assessor-learner-model-and-scheduler-replacement) also requires recomputation at original learning times. These are necessary rules; this finding does not reopen duplicate submission or late grading in general.

**Counterexample.** A capability was taught on September 30, making its first later check due October 1. An owned answer A on October 1 is accepted as successful, consuming that obligation and creating the October 8 obligation. A genuinely independent answer B owns and successfully completes the October 8 obligation, creating a check due October 15. On October 10, a supported correction makes A's judgment unusable. B's real answer and accepted assessment are unchanged, and its conditions otherwise qualify.

The corrected history no longer supports the transition that created B's obligation. The current text says to replace that invalidated successor, but also says B may consume only its original bound obligation. It does not determine whether B retains its scheduling effect, is reconsidered through an explicit correction rule, or becomes extra evidence while a new check is required. Merely preserving the chain does not choose the current due date or visible next action.

**Decision needed.** Specify how already delivered, submitted and completed descendant offers are treated when an ancestor is corrected. Separate the immutable facts of what was offered and answered from their recomputed scheduling effect. Decide when a later genuine demonstration resolves the current need, how an uncompleted descendant is retired or held, and how the learner sees any changed due date. The rule must terminate in a current state rather than recursively creating fresh obligations on every replay.

**Bounded direction.** Retain B and its historical ownership; do not silently delete its achievement, invent a compensating review or bind it to a different opportunity. Add an explicit correction transition for descendant scheduling effects, with the actual resulting next action illustrated. Leaving an explained hold is possible, but that choice needs a recovery path and cannot masquerade as a fresh learning failure. The audit does not choose one of these policies on the user's behalf.

**Why the previous case missed this.** [Closure case X07](cross-contract-closure.md#additional-boundaries-checked-while-patching) asks for recomputation and preserved lineage, but gives no expected outcome after a descendant has already been completed. Relevant baseline passages: lifecycle lines 92, 118–127; compatibility lines 217–221.

## G02. A repaired mistake can prevent a completion milestone forever

**Conflicting rules.** The [milestone rule](learning-lifecycle-contract.md#1-selecting-goals-does-not-create-a-review-backlog) requires every obligation due through the selected time to be satisfied before showing “Later checks completed as of [time].” The [obligation rule](learning-lifecycle-contract.md#4-one-due-opportunity-two-tabs-and-late-grading) says completed teaching can replace an unsatisfied obligation, explicitly without satisfying it. Both are useful distinctions, but their interaction is unresolved.

**Counterexample.** A due check fails. The learner completes targeted teaching, which replaces the old unsatisfied obligation. They then pass the new independent later check, resolve the concern, and have no current due work. The old due obligation remains historically unsatisfied, as required. Under the literal “every obligation due through that time” rule, this learner can never earn the milestone, however much later progress they make.

An implementer could interpret “every obligation” as only currently effective obligations. That may be the intended behavior, but the contract does not say so. Treating replacement as success would resolve the contradiction by falsifying history.

**Decision needed.** Define the obligation set used for a current caught-up indicator, separately from lifetime completion/failure history. State the treatment of consumed, replaced, invalidated and still-open obligations. Preserve the existing requirement that selected unstarted or paused goals cannot disappear to earn a whole-curriculum award.

**Bounded direction.** Allow an appropriately scoped current-work indicator to recover after successful repair without rewriting the old failure. Retain historical missed/replaced checks and their waiting time in a separate history view. Save the exact effective scope and rule with any awarded checkpoint; a later correction must be able to supersede its basis. No new mastery score is needed.

**Why the previous cases missed this.** Admission cases check that importing 200 goals does not create 200 overdue tasks. Repair cases check future practice. They do not connect a replaced obligation to the all-selected-goals milestone. Relevant baseline passages: lifecycle lines 34–36 and 92.

## G03. Different targets can expose the same answer

**What is already specified.** The [representation and compatibility example](compatibility-design.md#worked-example-the-same-progress-under-three-changes) correctly treats opposite vocabulary directions as different targets: knowing “mavo → blue” does not prove “blue → mavo.” The [exposure payload](../learning-observability/data-contract.md#5-exposure-corrections-and-the-unit-behind-a-flag) has target and content references, and [ordinary learning](everyday-learning-design.md#exposure-no-help-answers-and-delay) records exposure at its actual scope without deferring an unrelated curriculum. Thus the storage can represent broader exposure. The missing part is how that scope is determined.

**Counterexample.** T1 asks for the meaning of the invented word “mavo”; T2 asks for the invented word meaning “blue.” The learner opens T1's feedback, “mavo means blue.” Immediately afterward the system offers T2 as an independent later check. If the exposure is tagged only to the inspected target T1, a T2-only scan misses it. Separate assessment histories are correct; ignoring the shared answer is not a valid basis for the claimed delay.

The same issue occurs when an explanation of a procedure displays a command that another target separately asks the learner to recall. Passing the explanation must not award command-recall achievement, but seeing the command can still affect the next recall check's conditions.

**Decision needed.** Define exposure relevance independently of assessment coverage and schedule ownership. Specify how the actual revealed content maps to other accepted targets, including direction, mode and requirement scope; what provenance supports that mapping; and what happens when relevance is uncertain. Define how current qualification finds an older exposure when another related target is introduced later. Exact target identity alone cannot answer these questions.

**Bounded direction.** Use the existing content/knowledge references and checked scope information to record which targets' answers the presentation reveals or materially supplies. Do not assume that every graph neighbor is exposed or learned. Preserve uncertainty for an unresolved relevant mapping and leave unrelated work usable. Showing shared content may change exposure qualification; it must never mint a success, a study completion or an FSRS review for the other target.

**Why the previous cases missed this.** The previous patch tests when exposure ends, uncertain timing, post-submission feedback and excluding the response from its own prior-exposure scan. Those cases do not test differing target IDs with overlapping answer content. Relevant baseline passages: compatibility lines 209–213; data contract lines 115–129; everyday learning lines 93–103; lifecycle lines 133–154.

## G04. An earlier dashboard date can include later effort

**Conflicting levels of specification.** The [C interaction contract](../learning-observability/c-dashboard-contract.md#4-controls-and-state-transitions) says choosing a plotted date updates course effort **through that date**. The [tracking default](../learning-observability/tracking-contract.md#2-a-concrete-default-plan) freezes cost over the whole 21-day period. The [cost query](../learning-observability/data-contract.md#4-timer-ownership-duration-and-placement) clips reliably placed spans to that frozen window, while the [report query](../learning-observability/data-contract.md#6-frozen-endpoints-and-deterministic-queries) explicitly excludes answers after evaluation time T but does not give the corresponding cost cutoff.

**Counterexample.** A plan starts October 1 and ends October 22. Its saved source snapshot includes 20 minutes on October 5 and another 30 minutes on October 15. Selecting the October 8 check must show 20 minutes through that check. Clipping only to the frozen plan window yields 50. This remains a problem if the source is legitimately newer than the evaluation date: S controls what evidence is known, while T and the selected check control when the displayed activity occurred.

**Decision needed.** Distinguish the frozen investment scope/window from the effective interval of each displayed cost. For “effort through this check,” specify the upper bound using both the selected check boundary and evaluation instant, including the exact boundary for a day label. Define clipping for a span crossing that bound. Apply the same rule to the headline, selected-date cards, chart points, saved report and replay. Do not quietly substitute the source snapshot's date.

**Bounded direction.** For a through-date display, intersect the declared cost window with the time interval ending at the earlier applicable report/check boundary, then apply the existing union and quality rules. A full-period cost display may coexist if separately labelled. Unknown or unplaced duration remains visible with its timing limitation; it cannot be placed before the cutoff merely to produce a complete total. No extra analytics service is needed.

**Why the previous cases missed this.** The prior historical-query case excludes future answers and the timer cases prevent duplicate or invented minutes. Neither checks future *effort* in a valid newer source snapshot. Relevant baseline passages: C contract lines 85 and 112; tracking line 32; data contract lines 106–108 and 151–158.

## Cases the next patch must settle

These are authored design counterexamples and acceptance obligations, not passing application tests. In the correction cases, the next patch must supply the currently missing specific outcome, not merely repeat “recompute.”

| Case | Input | Required closure evidence |
|---|---|---|
| I01 Completed descendant | G01's A → B → correction sequence | One explicit current due/need outcome, retained B evidence/ownership, and a reason for any changed scheduling effect |
| I02 Open descendant | Correct A after B's offer is reserved, then after B is submitted but ungraded | Exact continue/hold/retire behavior and disposition of B's later result; no silent rebinding or loss of the submitted answer |
| I03 Repaired current workload | Old failed obligation replaced by teaching; replacement later check succeeds | A reachable caught-up state for the appropriate active scope, with the old failure still historical and unsatisfied |
| I04 Whole selected scope | Same repaired target plus another selected unstarted or paused target | No false whole-curriculum completion through denominator shrinkage |
| I05 Reverse-direction reveal | T1's “mavo means blue” feedback precedes T2's check | Shared-content exposure considered for T2; no inherited achievement or fabricated review |
| I06 Related versus unrelated | Procedure explanation reveals a recalled command but not a separate vocabulary answer | Relevant scope affected; unrelated target remains usable; unresolved relevance is explicit |
| I07 New target after old reveal | T2 is created after the saved T1 feedback presentation | Relevance can be checked against retained content/time without inventing an old T2 review or assuming no exposure |
| I08 Historical known cost | Source includes October 5: 20m and October 15: 30m; selected cutoff October 8 | Through-check cost 20m; separately labelled full-period cost may be 50m |
| I09 Boundary-crossing span | Add a reliably placed span October 8 11:58–12:03; cutoff 12:00 | Add 2m before the boundary, giving 22m through the check; full-period total is 55m if all spans are otherwise eligible and disjoint |
| I10 Evaluation and unknown placement | Selected date is after T; another 7m has unknown placement within the plan | Never include known effort after T; retain the 7m as unplaced with uncertainty, not as known earlier effort |

## Candidates examined but not counted as new gaps

| Candidate | Disposition |
|---|---|
| A late grade clearing a newer failure | Already covered by occurrence ordering, extra-evidence concerns and the assessment-pending hold. G01 is specifically invalidation after descendant work, not the same late-grade example again |
| Ratings arriving after feedback | Already bound to the retrieval interval; later feedback is not retroactive help. Pending/disputed assessments are held and the adapter requires actual ratings. A concrete disagreement table would improve the implementation prefill, but this audit does not establish a fifth independent defect from the phrase “judgment/rating” alone |
| Short recall relearning versus capability delay | The contracts distinguish actual recall reviews from capability intervals and deliberately served practice. Reverify the selected FSRS binding and its adapter at implementation; the historical probe is not evidence about today's installed version |
| Tracking weeks without a scheduled review | Explicit consequence of using ordinary reviews without adding measurement debt; missing results retain their denominator and reason |
| New exercise families or changed curriculum meanings | Existing frozen-comparison and compatibility rules deliberately require a new plan or withhold comparability |
| Browser/provider/deployment choices, accessibility and semantic quality | Already named decisions or runtime qualification work; no new storage service or statistical model is justified by this document audit |
| Causal learning efficiency | Explicitly requires later authorized comparative evidence; authored arithmetic cannot settle it |

## Integration ownership and verification limits

The existing [everyday-learning policy investigation](issues/14-everyday-learning-policy.md) owns G01–G03's behavior. The existing [record and report contract investigation](../learning-observability/issues/09-data-contract.md) owns their saved representation/replay and G04's query behavior. Completion displays also need the same effective scope in the dashboard. No new campaign or implementation ticket tree is needed.

This pass inspected the relevant contract text and earlier closure cases, checked the local citations/anchors and case identities, and independently calculated the small cost example. It did not execute a scheduler, importer, dashboard, model or live learner session. Confidence is high that the cited text leaves these cases unresolved or inconsistent; this does not establish that a future implementation would choose the wrong interpretation. No severity or frequency ranking is asserted.

The audit task was completed by recording these findings and their ownership. Its four open drafting decisions are now addressed by the linked follow-up patch, which reconciles the cited contracts and traces concrete outcomes. Existing human preferences remain unchanged; the patch does not claim acceptance of every proposed default or require another learner exercise.
