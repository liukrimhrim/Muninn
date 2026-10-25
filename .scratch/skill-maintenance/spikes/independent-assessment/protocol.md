# Blind comparison with independently annotated student responses

Prepared before viewing the selected annotations, 2026-10-14. This is a small design experiment, not a release gate or proof of learning effectiveness.

## Question

Do our component-level observations agree with pre-existing human annotations on unfamiliar real responses, and could the disagreements change what the planner credits or asks the learner to practice?

The source researcher verifies the primary corpus and prepares the sample without seeing our previous judgments. The assessing Codex chat sees the prompt, reference answer, original student answer and reference facets, but no selected annotations. Its output and this protocol are frozen before those annotations are revealed. Public historical data may have appeared in model training; this is blinding within this evaluation, not a claim that the model has never encountered these examples.

## Sampling

Use the original organizer's SCIEntsBank Extra corpus with original facet annotations. Select four questions from distinct modules and three responses per question using a fixed label-independent rule, recorded in the source preparation script. The source researcher found that all facets would yield 144 decisions. Before any packet or selected annotation was viewed, cap this small review at four facets per question, selected by fixed-seed hash order independent of labels: 48 decisions across 12 responses. Preserve the complete question and reference answer for context; this selected view is not a full grade of each answer. No selection or replacement based on results, agreement or label balance. Exclude explicit missing-visual-context cues and the fruit-identification question illustrated in the paper because a search result exposed its example judgments to the assessing chat before selection. Preserve typos, original context limitations and all selected source labels, including labels excluded from comparison.

The researcher owns `blind-inputs.json`, `withheld-reference.json`, source provenance and preparation. The parent owns the assessments and comparison. The parent must not open the reference file, annotated source extracts, or a report of selected label counts before freezing the assessment. Do not treat an agent's own judgment as an independent human reference.

## Assessment

Apply the existing answer-intake version-2 evidence rules to each reference facet in context. Equivalent expressions and reasonable implications count. Do not credit a facet just because it occurs in the question or reference answer. Only evidence from the student's answer supports a demonstration. Keep the source facet's scope; do not invent extra requirements.

Return one observation per facet, with an exact student-answer quote and reason for `demonstrated` or `error`. `not_shown` means the answer provides no evidence for that facet and has no supporting quote. `cannot_judge` records genuine ambiguity or missing context; it is an abstention, not a learner failure. Preserve contradictions, even when another part of the answer is correct. An off-topic or missing component does not establish inability. No assumptions about elapsed time, outside help, retained mastery or why an error occurred.

Also propose one next action (`stop`, `clarify`, `follow_up`, `practice`, or `fresh_check`) with targeted facets and a reason. Immediate remedial practice requires an explicit supported error. A follow-up needs distinct correct/wrong/unclear branches that change the action. Do not require answers just to complete the facet inventory. The source does not contain human judgments of these proposed tutoring actions; do not fabricate them.

## Mapping fixed before revealing annotations

The original source's annotation vocabulary distinguishes evidence that a semantic relationship is expressed from its absence, contradiction, assumption, or a changed argument. These are observations of answers, not mastery labels. The mapping below is our comparison convention; preserve raw labels and report their counts separately.

| Original facet label | Comparable observation | Limit |
|---|---|---|
| Expressed | demonstrated | Explicit or simple inference |
| Inferred | demonstrated | Nontrivial/pragmatic inference; report separately |
| Contra-Expr | error | Direct contradiction |
| Contra-Infr | error | Inferred contradiction; report separately |
| Self-Contra | error | Both support and contradiction occur; retain both in the reason |
| Unaddressed | not_shown | Absence of evidence, not a knowledge gap |
| Assumed | Outside primary comparison | May be supplied by the question rather than the student |
| Diff-Arg | Outside primary comparison | A related statement with a changed argument cannot be faithfully collapsed |

The vocabulary was checked by the source researcher against the authors' [annotation paper, Table 5](https://www.lrec-conf.org/proceedings/lrec2008/pdf/873_paper.pdf). The source notes will record exact provenance and any serialization aliases. Alias normalization must not change meaning or depend on agreement.

## Comparison and consequences

Report exact matches, disagreements and assessor abstentions on comparable facets. Show the raw-label breakdown and every excluded facet separately. Do not score an abstention as agreement. Do not aggregate correlated facets into a claim of general diagnostic accuracy, invent acceptance thresholds, or use a weighted sum.

Inspect every disagreement using the original packet after the reveal. Describe whether the evidence supports the assessor, the recorded annotation, or an unresolved interpretation. Keep the frozen assessment unchanged; post-reveal commentary is adjudication by the same assistant, not another independent review. A source quotation proves what was annotated, not that the annotation is necessarily correct.

Use the existing validator, bridge and planner where compatible. Each student response is a separate case; do not concatenate different students into one learning history. Track actual resulting immediate help. An optional separate counterfactual may ask which pending facets the current policy would remove **if** the response were an unhinted later check. Label those assumptions explicitly: the corpus does not supply assistance or learning histories. Compare planner consequences only for mapped source labels. Unknown source labels cannot justify withdrawing practice.

No fresh human reviewer, delayed-retention result, operational skill, support for misread classification or intervention benefit is supplied by this corpus. The experiment succeeds by producing an auditable comparison and concrete design implications, even if agreement is poor. It does not resolve the broader validation decision.
