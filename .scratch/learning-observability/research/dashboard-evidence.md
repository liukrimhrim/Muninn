# Dashboard evidence, alternatives and comprehension probes

Research for [Which dashboard designs support understanding and useful action?](../issues/03-dashboard-evidence.md), 2026-10-14. This is a design investigation; no dashboard implementation, learner study or live measurement was performed. It extends the [existing observability proposal](../../skill-maintenance/observability-design.md). All proposed prototype histories below are authored examples.

## Finding

The dashboard should help the learner make a small number of defensible decisions: recognize a demonstrated improvement, distinguish maintenance from stagnation, find the specific unresolved capability, and inspect whether preparation or repeated repair is consuming time without established benefit. More charts do not establish these abilities. Test interpretation and navigation before testing whether the dashboard changes retained learning per unit of effort.

Keep four outcomes separate: **understanding the display**, **wanting to continue**, **taking a useful action**, and **remembering or performing better later**. None is a substitute for the next. This is the organizing design judgment of this report, informed by the different outcome measures in the studies below.

## Primary evidence and its limits

The search targeted controlled learner-dashboard studies, experiments on visual encoding/uncertainty, and the applicable accessibility standard. Eight primary sources were directly inspected. This is a targeted design review, not a systematic review or an estimate of the average dashboard effect. Null results below do not establish equivalence.

1. **Hellings and Haelermans — programming course experiment.** Random assignment offered dashboard access and weekly linked emails to approximately half of 556 students. Results distinguish access from self-selected use: some online exercise/quiz outcomes improved, but the overall final-exam and passing outcomes did not show a statistically detectable effect. Comparing dashboard users with non-users exaggerated some associations. This is evidence for keeping practice behavior, final performance and selection effects separate. It does not show that a self-directed memorization dashboard will improve delayed retention, nor isolate our proposed interface features. Verified abstract, empirical strategy and results. [Original article, published online 2020](https://link.springer.com/article/10.1007/s10734-020-00560-z).

2. **Valle et al. — predictive versus descriptive dashboards.** In an online statistics course, 179 completing participants were in predictive, descriptive or control conditions. Motivation and anxiety were measured with questionnaires alongside interviews. The predictive dashboard's effect on intrinsic goal orientation depended on initial motivation; some anxiety effects also depended on starting levels. The study does not justify claiming that a prediction or an upward curve universally motivates learners. Our implication is to avoid treating affective benefit as an inherent chart property. Verified abstract, design, participant description and instruments; no new effect-size calculation. [Original full-text article, 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8153529/).

3. **Giorgashvili et al. — personalized feedback and reflection.** A controlled field study analyzed 1,251 reflection texts from 417 students across three occasions. Personalized dashboard feedback changed the aspects learners said they intended to work on; perceived helpfulness related to incorporating suggested changes. The measured endpoint here is reflection content and intention. It is not proof of subsequent action, retained knowledge or time savings. The useful design inference is to attach a concrete, evidence-linked suggestion to a finding, then verify whether the learner understands and uses it. Verified methods, outcome definitions and results. [Original article, 2025](https://onlinelibrary.wiley.com/doi/10.1111/jcal.70073).

4. **Borrella and Ponce-Cueto — MOOC experiment.** The three-arm trial enrolled 8,745 learners: no dashboard, dashboard with generic messages, and dashboard with actionable motivational feedback. Feedback increased purchase of the certification track; engagement findings were mixed, and no final-grade difference was detected. Payment is a behavioral outcome, not a direct measure of motivation or retained learning. Only verified learners could access graded work, limiting a simple interpretation of final-grade comparisons after verification itself changed. Dashboard-use frequency was not recorded. Verified the institutional abstract and publisher methods/results text; direct publisher opening was rate-limited. [MIT copy and metadata, 2025](https://dspace.mit.edu/entities/publication/76c4d252-16f2-4953-809e-9654c9584f05), [publisher methods](https://www.mdpi.com/2076-3417/15/21/11493).

5. **Heer and Bostock — graphical perception.** Their experiments replicated and extended quantitative comparison tasks. Common-scale position judgments outperformed length judgments; angle and circular area were less accurate than position in the tested tasks. This supports trying aligned dots/bars for comparing counts and minutes. It is not an empirical ranking of every chart for every learning task. Verified experiment methods and results. [Author-hosted CHI paper, 2010](https://idl.cs.washington.edu/files/2010-MTurk-CHI.pdf).

6. **Fernandes et al. — uncertainty and decisions.** A preregistered analysis used 408 participants in simulated, incentivized bus-catching decisions. Several uncertainty displays, including quantile dotplots and cumulative distributions, supported better decisions than point estimates; performance varied by encoding and practice. Those results concern supplied predictive distributions and a specified payoff, not learner mastery. A dotplot is a candidate only if our system later has a defensible distribution and a matching decision; it cannot manufacture statistical meaning for missing checks. Verified full paper, methods, results and limitations. [Author-hosted CHI paper, 2018](https://www.mjskay.com/papers/chi2018-uncertain-bus-decisions.pdf).

7. **Song et al. — visible missing values.** Eighteen graduate students explored hypothetical stock portfolios. Showing imputed points with error bars, versus hiding incomplete points, changed observed decision processes; reported mental demand and frustration did not significantly differ. The small, domain-specific study supports inspecting how missingness changes interpretation. It does not endorse imputing learner grades, prove superior decisions, or validate our scenario bounds. We retain missing outcomes explicitly without imputing them. Verified full paper and limitations. [Author paper, IEEE VIS 2021](https://faculty.cc.gatech.edu/~john.stasko/papers/vis21-missvalues.pdf).

8. **W3C WCAG 2.2** supplies the accessibility requirements below. It is a normative standard, not evidence of learning benefit. [W3C recommendation](https://www.w3.org/TR/WCAG22/).

## Three different information architectures

These are alternatives for the primary organizing structure, not cosmetic skins. Test them with the same eight-target history so differences do not come from favorable data.

| Architecture | First screen and navigation | Strength to test | Main failure risk |
|---|---|---|---|
| **Decision-first briefing** | A short dated account of what changed, what remains uncertain, and one suggested next action. Open a claim to inspect its targets, evidence and cost. | Learner understands what to do with little dashboard time. | A polished narrative hides exclusions or overstates what caused the change. |
| **Capability notebook** | Curriculum capabilities form the main list. Selecting one reveals its observation timeline, help, repair, later checks and shared effort. Cross-target summaries are secondary. | Learner sees exactly which relationship or procedure needs reinforcement. | A long list obscures patterns and preparation costs across the curriculum. |
| **Investigation workbench** | Choose a saved target cohort and question; paired outcomes, cost categories and completeness appear together. Filters and evidence tables drive navigation. | Learner can challenge an efficiency conclusion and compare like with like. | Analytical burden exceeds the value of the answer; easy filters accidentally change the population. |

**Proposed starting arrangement:** briefing as the everyday entrance; notebook as its evidence destination; workbench opened deliberately for a specific comparison. This is a design hypothesis, not a settled preference. The prototype should expose all three structures briefly before combining them. A knowledge graph may help navigate relationships inside a selected capability, but a graph's node size or centrality must not stand in for achievement.

## Method and decision matrix

The following encodings are proposed applications of the evidence and existing metric contract. They have not been validated with this learner.

| Question | Initial encoding | Decision and constraint |
|---|---|---|
| What changed on the same targets? | Named rows with baseline and later outcome columns; date, mode and assistance labels | Count improved/maintained/gap/unresolved transitions. For eight targets, show the eight rows instead of hiding them behind a percentage. |
| What happened to this capability? | Dated event strip with distinct marks and readable labels for independent check, helped work, error and unresolved observation | Select an event to read the exact answer and correction lineage. No line connecting categorical outcomes into a smooth mastery curve. |
| Where did the time go? | Horizontal bars on one minutes scale, exact values, grouped into learning work, overhead and blocked waiting | Show the full accounted total alongside missing/unplaced time. Shared exercise minutes count once; a per-target panel labels shared cost. |
| Where did repair stall? | Stage table: gap, targeted help, fresh integrated check, later check; original cohort count and current outcomes at each stage | Keep missing and unresolved cases visible. A decorative funnel or Sankey must not imply that all starters were assessed or that dropout means forgetting. |
| Is method B more efficient? | Paired outcome table plus side-by-side full-cost bars and comparability checklist | No single ratio, weighted score or automatic winner. Explain mismatched delay, target contracts, exposure or cost boundaries before interpreting differences. |
| Could missing results change the answer? | Explicit scenario endpoints with text and counts | Five successes, two errors, one missing gives 5/8–6/8 under the two possible missing-result scenarios. This is not a confidence interval; neither endpoint is written as a grade. |

For larger inventories, grouped rows and search can reduce navigation. A matrix may use symbols plus labels, with colour as redundancy. Grouping preserves the exact target count and identity. Avoid a mastery pie: evidence status, assistance, historical milestones and due status overlap and are not a single partition. Avoid peer leaderboards, unrelated-subject “targets per minute,” and dual axes that visually suggest a relationship between arbitrary scales.

Every visible result opens the included and excluded records, not just successful examples. Returning preserves filters and scroll position. Show scope and date in plain language; technical definition versions and cutoffs belong in an expandable explanation or saved-report detail. A correction updates historical interpretation with an annotation, never a celebratory jump today.

## Sparse data and uncertainty states

The dashboard needs useful behavior before it has a trend:

- **Fresh curriculum:** “No independent checks yet,” followed by the first relevant check; no 0% mastery.
- **Only helped work:** show completed practice and the pending independent check separately.
- **One or two observations:** show those events and their dates; do not fit a curve just to fill the panel.
- **Checks not yet due:** state when the later observation becomes possible; no implied failure.
- **Missing or unresolved check:** name the absent evidence and keep previous achievements visible.
- **Unknown time:** show measured minutes with an incomplete-total label; unknown is neither zero nor an invented upper bound.
- **Changed curriculum or grading:** separate series or explain the reviewed equivalence; a new requirement does not erase an older achievement.

Use distinct phrases for **not observed**, **ambiguous assessment**, **measurement gap**, **scenario bound**, and eventually **model uncertainty**. A generic confidence badge would conflate problems requiring different actions.

## Mobile and accessibility constraints

Target WCAG 2.2 AA: keyboard operation with visible focus; meaningful text alternatives and table relationships; no colour-only states; ordinary text contrast at least 4.5:1 and required graphics/UI boundaries 3:1. Reflow the surrounding page at 320 CSS pixels; the standard permits exceptions for intrinsically two-dimensional content. Pointer targets need 24×24 CSS pixels or a permitted exception; prefer larger primary controls. Tooltips must support the applicable hover/focus behavior. [WCAG 2.2, criteria 1.1.1, 1.3.1, 1.4.1/3/10/11/13, 2.1.1, 2.4.7/11, 2.5.8](https://www.w3.org/TR/WCAG22/).

Our proposed implementation of these constraints is a stacked mobile briefing, a readable row/card alternative to wide charts, persistent evidence buttons, and the same actions through a semantic table. Never require dragging, hovering or deciphering red/green to investigate a result. Disable nonessential animation when reduced motion is requested. Designers must perform keyboard, zoom, contrast and screen-reader checks; these are not homework for the learner.

## Prototype scenarios and five plain-English tasks

Build authored scenarios that expose materially different conclusions:

| Scenario | Required distinction |
|---|---|
| Eight targets, 40 minutes | Three improved, two maintained, two persistent errors, one unchecked; full effort includes preparation and corrections. |
| Successful repair, later check pending | Immediate success supports the repaired performance; retention is still unknown. |
| Repeated later success with no new targets | Maintenance is visible; no unsupported claim that the time was wasted. |
| A corrected misread | Historical assessment changes; no new knowledge gained at correction time. |
| Apparently cheaper method, missing time or mismatched endpoints | The comparison remains unresolved, with the reason visible. |

Present one short task at a time. The learner answers naturally or selects something; they do not grade the interface or enumerate bugs. Keep the answer key out of the initial display.

1. **“What changed since the earlier check?”** Expected: three improved and two remained successful; no claim that all five were newly learned.
2. **“What can we say about the unchecked capability?”** Expected: its later outcome is unknown, not a failure or assumed success.
3. **“Show me why the app says this relationship needs practice.”** Expected: reach the relevant exercise, response and criterion evidence, with help visible.
4. **“Where did the 40 minutes go?”** Expected: find the full accounting, including preparation/correction/waiting, rather than answering time alone.
5. **“Would you switch methods based on this comparison?”** Expected: with missing cost or incompatible checks, explain why no superiority conclusion is established. Continuing the baseline or gathering the missing evidence are both reasonable responses.

The facilitator records interpretation, whether assistance was needed, navigation obstacles and approximate task time. Stop and clarify when the display produces a consequential misinterpretation; change it and use a fresh equivalent scenario for verification. Do not count a coached repeat as independent comprehension. An optional final “Was this useful enough to revisit?” addresses preference, not learning efficacy.

One learner's successful walkthrough resolves local design confusion, not population usability or retention benefit. Follow-up evaluation should measure actual useful actions, total monitoring burden and delayed performance separately. The remaining human decision is which structure feels useful in ordinary study; research cannot answer that on the learner's behalf.
