# Evidence that supports a learning-progress claim

Research for [What evidence makes a learning-progress measure valid?](../issues/01-measurement-validity.md), 2026-10-14. This is a recommendation for the observability campaign, not an implemented assessor, validated instrument or learner study. Seven primary sources were directly inspected; access depth and limits are recorded below.

## Recommendation

Make every progress statement answerable to a **named capability, conditions, evidence and intended use**. Use a small, reviewable set of measurements first, with explicit boundaries for later statistical models. Sophistication should mean being able to distinguish competing explanations and change a decision responsibly; adding a latent mastery score would not solve the observed assessment ambiguities.

The [existing observability proposal](../../skill-maintenance/observability-design.md) already protects denominators, exposure history, corrections and effort. Its remaining measurement gap is a concrete contract for each claim and a repeatable procedure for qualifying an assessor. The [diagnosis design](../../skill-maintenance/diagnosis-design.md) already distinguishes demonstrated, error, not shown and cannot judge. Preserve these. The [retrieval ledger](../../skill-maintenance/research/conversation-retrieval.md) additionally requires goal-dependent fluency/reconstruction, connected application, useful granularity and separate grading/learner uncertainty (L02, L05, L08, L14, L20, L24, L38–L45).

## Primary evidence and its boundaries

**Assessment validity belongs to a particular interpretation and use.** The joint testing standards require explicit intended interpretations; reliability evidence must match relevant variations in tasks, raters and occasions. Their Standard 2.7 distinguishes agreement when scoring the same response from consistency across different performances. Standard 1.15 addresses interpretations of individual items or small subsets. These support scrutiny of fine-grained progress claims; they do not supply a universal pass count or acceptable error threshold for this app. Inspected the official PDF, printed pp. 11, 23–27, 42–44 and 90–92. [AERA/APA/NCME, 2014, Standards](https://www.testingstandards.net/uploads/7/6/6/4/76643089/standards_2014edition.pdf).

**Immediate performance and delayed retention can disagree, and measurement changes memory.** In two prose-learning experiments, restudying performed better at a five-minute test, while retrieval practice performed better at delayed tests; testing without feedback still affected later retention. These findings support separate time horizons and recording assessment as exposure. They do not establish the optimal horizon or practice policy for this general app. Inspected original article, abstract, methods and results. [Roediger and Karpicke, 2006](https://learninglab.psych.purdue.edu/downloads/2006/2006_Roediger_Karpicke_PsychSci.pdf).

**Transfer requires its own tasks.** Butler's four experiments used same-question retention, new inferences within a domain and new inferences in different domains at a one-week endpoint. Retrieval practice improved these outcomes relative to restudying. Rephrasing practice questions did not itself yield an additional advantage in the tested comparisons. Thus, a changed surface form is not a sufficient definition of transfer. Inspected the original paper, including methods and general discussion; this is a hosted copy of the original article. [Butler, 2010](https://andymatuschak.org/files/papers/Butler%20-%202010%20-%20Repeated%20Testing%20Produces%20Superior%20Transfer%20of%20Learning%20Relative%20to%20Repeated.pdf).

**Automated scoring needs more than agreement.** Williamson, Xi and Breyer's framework covers fit to assessment purpose, agreement with human scores, independent measures, generalization across tasks and consequences. It was developed around constructed responses and high-stakes uses; its numeric operational criteria are not adopted here. Verified the publisher's abstract and ETS publication record, not the paywalled full paper. [Williamson et al., 2012](https://onlinelibrary.wiley.com/doi/10.1111/j.1745-3992.2011.00223.x).

**Response duration mixes person and task properties.** Van der Linden's original hierarchical model separates person speed/ability from item time intensity/difficulty and makes conditional-independence assumptions. It is a model for calibrated testing data, not evidence that a slow answer implies weak knowledge. Inspected the original 2005 research report, executive summary and model assumptions; the later journal version is dated 2007. [Van der Linden, RR-05-02](https://ris.utwente.nl/ws/files/5129699/Linden05hierarchical.pdf).

**Knowledge-component boundaries are hypotheses that can be tested.** Liu and Koedinger interpreted a model discovery as a hidden square-root difficulty in backward area problems, checked its generalization on new data, then tested a revised tutor against a control. The intervention changed several features, including scaffolding and practice, so its benefit cannot be attributed solely to splitting labels. Inspected the original article's modeling, intervention and results sections. [Liu and Koedinger, 2017](https://jedm.educationaldatamining.org/index.php/JEDM/article/download/212/pdf_29).

**Assessment design can begin from an evidence argument.** Evidence-centered design separates claims about unobserved capabilities, observations and the tasks that elicit them; probability models sit within that larger design. This supports a contract-first approach without requiring a Bayesian engine. Verified the original report's publisher abstract and ETS record; full report access was unavailable through the attempted ETS PDF URL. [Mislevy, Almond and Lukas, 2003](https://onlinelibrary.wiley.com/doi/10.1002/j.2333-8504.2003.tb01908.x).

## Proposed claim contract

The following is this campaign's design recommendation. Reuse existing target, exercise, cohort and report records rather than introducing another service. A metric definition should identify:

- **Claim and decision:** what the display may say and what choice it supports; for example, whether to continue a focused repair or try a larger task.
- **Capability:** exact target revision and response mode, including required relationships or integration.
- **Conditions:** cueing, permitted references, task family, language, modality and any goal-relevant time constraint.
- **Opportunity and evidence:** assigned attempt, criteria, accepted assessment, relevant assistance and exposure, plus what was not observable.
- **Time meaning:** acquisition check, later check at a named interval, or a maintained performance under a recorded review policy.
- **Comparison rule:** baseline selection, comparable task forms, exclusions and target-population changes.
- **Validation scope:** which examples, subjects and response forms were reviewed; which interpretations remain untested.

Allow several claims from one episode, but preserve its identity. The same answer may demonstrate a fact and a relation without becoming two independent observations of reliability. An error in a larger task does not prove a missing prerequisite; diagnosis must find discriminating evidence or keep its cause unresolved.

Use these working meanings:

**Acquisition:** first observed independent performance, or observed error-to-success change under a comparable contract. The former cannot establish prior ignorance; neither establishes the app caused learning. **Maintenance:** previously demonstrated capability remains successful at a later opportunity, with practice and cost shown. **Retention:** successful access after an explicit interval and exposure history. **Transfer:** application under named changes to cues, context or demands that were not simply rehearsed. **Fluency:** accurate performance satisfying a goal-relevant access or execution constraint. These are overlapping descriptions of evidence, not five mutually exclusive learner states.

For fluency, keep correctness and duration separate. Report all eligible outcomes, then durations for correct attempts alongside errors, timeouts and missing timing. Restrict comparison to comparable input/output demands and devices. If a time constraint is chosen, count “correct within the agreed time” directly; do not average speed and correctness. A correct reconstruction can satisfy explanation while failing an explicitly chosen rapid-recall requirement. Ordinary browser foreground time cannot identify retrieval onset, hesitation, comprehension time or working-memory use.

## Methods and decisions

These choices are recommendations for this project's data situation, not universal rankings of statistical methods.

| Method | Decision it can support | Evidence it needs | Recommended boundary |
|---|---|---|---|
| Criterion audit and paired counterexamples | Is a proposed judgment defensible? | Reviewed prompts, acceptable alternatives, contrasting responses | Start here; successful fixtures establish behavior only on those cases |
| Fixed target/family outcome table | Which observed needs improved or persisted? | Comparable baseline/endpoint, help and missingness | Default for sparse personal histories; no causal label |
| Independent scoring plus confusion table | Which assessment mistakes matter? | Blind initial ratings, documented adjudication, category counts | Use before suppressing practice; agreement alone is insufficient |
| Matched fluency display | Is accurate access faster under these conditions? | Comparable task demands and trustworthy timing | Report accuracy and time jointly, with omissions visible |
| Generalizability analysis | Are tasks, raters or occasions driving instability? | Deliberately crossed repeated observations within a suitable stability window | Later study; learning between occasions confounds a simple reliability interpretation |
| IRT or hierarchical difficulty model | Can performance be compared across different items? | Connected item/learner observations, defensible construct and model checks | Defer production use; changing personal content and few responses do not identify a scale by themselves |
| Knowledge tracing or cognitive-model refinement | Which latent history or unit boundary predicts later responses? | Repeated histories, explicit opportunities/exposure and held-out evaluation | Research candidate; prediction improvement does not prove instructional benefit |

For the initial personal history, prefer specific observations over numerical confidence about a hidden skill. A credible Bayesian interval can still be driven by assumptions when evidence is sparse. A precise descriptive count remains useful without pretending its uncertainty is zero: “successful on these two checks” is different from “90% likely to know this tomorrow.” Neither descriptive tables nor heavier models justify a progress claim when the rubric is wrong, the comparison changed demands, or the outcome was never observed.

## Assessor qualification and monitoring

Propose a reference collection spanning factual recall, relationship explanation, reconstruction, independent method selection and a recorded procedure. Keep each task's rubric and valid alternatives explicit. Include correct paraphrases, correct outputs with faulty reasons, missing requested evidence, irrelevant extra content, answer-containing hints, misreads with supporting reasoning, incomplete traces and genuine ambiguity. These are cases for judging assessment behavior; they are not estimated population frequencies.

For an initial bounded audit:

1. Freeze the prompt, rubric, source, assistance and response before assessment. Separate development examples from a held-out review set; do not repair the rubric using held-out answers and still call those answers unseen.
2. Obtain independent initial judgments before showing the model output. A qualified reviewer and an independently judging second reviewer are preferable for contested semantic cases. Repeated model calls are not a substitute for independent human interpretation.
3. Preserve initial disagreement, then adjudicate with the rubric and domain evidence. The result may remain unresolved; human consensus is a reviewed reference, not infallible truth.
4. Report the full four-category confusion table and action consequences: unsupported credit, unsupported remediation, unnecessary clarification and missed required clarification. Also report refusal/abstention frequency. An assessor that abstains on everything should not appear perfect.
5. Review a sample of apparently successful judgments as well as learner disputes. A complaint-only sample cannot reveal silent mistakes. Track task family and assessor/rubric version so pooled agreement cannot conceal one failing format.
6. Repeat held-out checks after consequential assessor or rubric changes; preserve prior assessments and report cutoffs. Until scoped evidence exists, offer reviewable assessments without claiming validated autonomous diagnosis.

Do not invent a single acceptable agreement percentage. The relevant choice is which errors are acceptable for the consequence: an optional suggested exercise differs from removing a topic from future practice. A pilot must specify acceptable unsupported credit/remediation and maximum review burden beforehand. Sparse audits should show individual mistakes and denominators rather than a reassuring headline accuracy percentage.

Represent uncertainty in separate places: **assessment uncertainty** means the response or rubric is unclear; **learner uncertainty** concerns performance in unobserved future conditions; **measurement uncertainty** includes missing exposure/timing; **causal uncertainty** concerns whether the policy produced change. Fixing an ambiguous grade does not imply the learner improved, and a confident grade does not imply durable retention.

## Difficulty, granularity and reactive monitoring

Use a modest task-family blueprint recording required operations, selection demands, distractors/cues and response form. Match endpoints by those demands, not merely topic or an author's “easy/medium/hard” tag. Difficulty tags remain hypotheses until there are observations adequate to check them. Keep target and exercise-family revisions visible in trends.

Hold meaningful goal coverage fixed when units split. A graph edit from one relationship target to five linguistic facets must not multiply achievements. Conversely, do not conceal a persistent subproblem because its parent task usually succeeds. A proposed split should name different practice decisions and receive contrast cases; if all branches lead to the same practice, it may be unnecessary. Retain integrated-task evidence separately from component evidence.

Monitoring exposure needs one addition to the existing proposal: **answer-bearing evidence drilldown can itself rehearse material**. Opening a response, correction or worked example on the dashboard should register a bounded relevant exposure if the app knows what was shown. Browsing a target label is different from viewing its answer; avoid claiming exact cognitive effect from either. A report with no new retrieval is not a new success, while its review time still counts. Preserve the recorded exposure cutoff when interpreting a later endpoint. Additional tests require a measurement budget; do not repeatedly test until an uncertainty display looks comfortable.

## Proposed validation work and spike counterexamples

These are next decision tasks, not executed tests or authorization for a learner study.

**Contract audit:** author one claim contract in each of the five modes above, then find a response that should satisfy it and a near-miss that should not. Verify that every dashboard phrase can point to the specific distinction. This checks semantic scope before choosing chart forms.

**Assessor audit design:** produce the frozen reference-set manifest, blind-review form, adjudication rules and error-consequence table. Reuse existing reviewed learner examples where consent/scope permits; label authored cases separately. Decide whether the available reviewers can establish the intended reference at all.

**Synthetic analysis spike:** construct paired histories that differ in exactly one consequential feature and require the report to change appropriately:

- Same immediate success, but only one history has a delayed independent check.
- Same delayed pass, but one learner viewed the answer in dashboard drilldown yesterday.
- Same final answer, but one explanation contains a contradiction and the other is equivalent unconventional wording.
- A correct binary-search derivation with a corrected endpoint misread, versus an actual halving error.
- Faster correct responses because prompts now require one word instead of explanations, versus faster responses under unchanged demands.
- A target split that inflates counts without new attempts, versus genuine new coverage.
- Perfect rater agreement on an inadequate rubric, versus honest disagreement that triggers rubric repair.
- A higher overall pass fraction caused by more easy tasks, with no matched-target improvement.
- Components pass separately while the larger selection/integration task fails.

**Future real-use validation:** only after its scope is agreed, observe whether users understand the claims, whether sampled judgments hold up, and whether the evidence predicts the named later capability. Record monitoring/annotation cost. Synthetic passes cannot close this step, and one subject cannot validate arbitrary subjects or modalities.

## Human preferences still needed

The campaign should make concrete alternatives for: which capabilities need rapid access rather than reconstruction; which practical retention horizons matter; how much extra checking/review time is acceptable; which assessor errors are most costly; and who can adjudicate disputed domain answers. These preferences set validation targets, not mathematical truths. They need not block the research or counterexample preparation. They must be settled before claiming a measurement is sufficient to suppress practice or adopt an efficiency improvement.
