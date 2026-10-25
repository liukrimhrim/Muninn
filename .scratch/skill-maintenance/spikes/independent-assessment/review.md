# Independent annotation comparison

Completed 2026-10-14. The small comparison found both semantic disagreements and a concrete mismatch between the assessor's proposed next action and the planner's output. It does not establish grading accuracy or learning benefit.

The practical next step is to reconcile clarification with corrective practice in the existing bridge, then review how assessment criteria map to useful learning targets. Adding a more elaborate memory model would not address either observed problem.

## What was compared

The current Codex chat assessed 12 real student responses across four science questions, using four selected semantic relationships per question: 48 judgments. The source researcher selected the sample without using our assessments or the source labels. The assessor saw the questions, reference answers, original responses and reference relationships, but did not open the selected human annotations until its judgments and mapping were committed at `f397ef8`. This was procedural blinding within this session, not access-control isolation or a guarantee against model training exposure.

The reference consists of historical human annotations from the author-maintained [SCIEntsBank release](https://github.com/myrosia/semeval-2013-task7/tree/5157c69f914e8c581045c03e98f96398d40a91b8), described in the [SemEval task paper](https://aclanthology.org/S13-2045/). No new human reviewer participated. See [source notes](source-notes.md) for licensing, upstream filtering, annotation definitions and the deterministic sampling rule.

The [protocol](protocol.md) and [assessment](assessment.json) remain unchanged. [Comparison output](comparison.json) preserves every raw label and judgment. All five frozen file hashes and the reference digest committed before reveal match. The independent research agent checked the selected labels directly against the pinned source XML and separately recomputed the comparison and planner consequences; [its audit](independent-audit.md) does not substitute for human adjudication of disputed meanings.

## Result

| Outcome | Facet judgments |
|---|---:|
| Matched the mapped human annotation | 23 |
| Disagreed | 10 |
| Assessor abstained because meaning was uncertain | 3 |
| Excluded by the predeclared mapping: source label `Assumed` | 12 |
| Total | 48 |

There are 36 comparable judgments. These are correlated judgments within 12 responses, not 36 independent learners. No acceptance threshold or accuracy claim follows from these counts.

| Original annotation | Total | Matches | Disagreements | Abstentions | Excluded |
|---|---:|---:|---:|---:|---:|
| Expressed | 3 | 2 | 1 | 0 | 0 |
| Inferred | 16 | 10 | 6 | 0 | 0 |
| Contra-Expr | 1 | 1 | 0 | 0 | 0 |
| Contra-Infr | 3 | 1 | 1 | 1 | 0 |
| Unaddressed | 13 | 9 | 2 | 2 | 0 |
| Assumed | 12 | 0 | 0 | 0 | 12 |

Six disagreements concern what the answer reasonably implies. They do not establish six learner deficits or six assessor mistakes. The protocol accepts reasonable implications but excludes facts merely supplied by the prompt; that boundary needs more precise examples. Some source annotations are also disputable.

## Findings that affect the design

**Credit must stay within what an answer supports.** In `LF.13b.737.1`, the learner describes material being taken away from particular places. I credited both movement and wearing away. The source credits movement and marks wearing away unaddressed. My reading may be overbroad relative to that distinction; whether the phrasing reasonably supports wearing away remains unresolved. A later-check simulation shows my reading would remove both wear-related checks, whereas the mapped reference would retain them. This is one answer and two related facets, not two independently established knowledge gaps. The annotation does not prove that the learner lacks the knowledge it marks unaddressed.

**The system needs one coherent next action.** For `SE.27b.333.1`, the frozen assessment records an apparently wrong prediction but proposes a follow-up to clarify awkward wording before choosing help. The real adapter → validator → bridge → planner path accepts the record, returns that follow-up as `proposal`, and simultaneously returns immediate help for the prediction in `plan.now`. The bridge intentionally exposes these separately, but no rule resolves which action takes precedence. This is a reproduced integration limitation, independent of whose science annotation is right. It does not show that a learner actually received unnecessary practice.

**A small linguistic relationship is not automatically a useful memorization target.** Some selected facets encode whose finger touches the thermometer or how many bulbs the question already supplies. They help analyze a sentence, but creating a separate review obligation for each would need a learning purpose. The useful target may instead be explaining the direction of heat transfer and its consequence together. Likewise, a causal relationship may be independently assessable even when its component facts are known. Granularity should preserve diagnostic distinctions without turning every parsing detail into a drill.

**Partial coverage cannot become a whole-answer pass.** Three of the four selected circuit facets were `Assumed` and excluded for every response. Only the one-path facet was compared. One circuit response also asserts a disconnection, outside the selected facet's precise scope. Neither agreement on that single facet nor credit on the parallel explanation establishes a correct complete circuit model. Keep scope visible and preserve concerning statements outside the selected criteria for review without inventing a target failure.

## Every disagreement and abstention

This is post-reveal interpretation by the original assessor, not fresh independent human adjudication. Frozen judgments are not revised to improve the score. Facet suffixes below identify the exact rows in `comparison.json`.

| Response and facet | Frozen assessment → source mapping | Interpretation and practical consequence |
|---|---|---|
| `SE.27b.116.1`, `f3` | not shown → demonstrated (`Inferred`) | Ownership of the contacting finger is supplied by context. A pragmatic reading can recover it, while the protocol forbids credit from the prompt alone. Do not create a separate ownership drill. The simulation retains this check only on the assessor side. |
| `SE.27b.313.1`, `f3` | not shown → demonstrated (`Inferred`) | Same context boundary in another answer. I accept contextual heat-source inference elsewhere in this answer, so the differing treatment needs an explicit rationale rather than a vocabulary requirement. The simulation retains only this check on the assessor side. |
| `SE.27b.116.1`, `f6` | error → demonstrated (`Expressed`) | The response predicts cooling and removal of heat; the reference facet concerns warming. The source's positive label is questionable. Preserve both records for adjudication; do not reverse the assessment merely to match it. The mapped-reference simulation differs by one help target and one retained check. |
| `SE.27b.333.1`, `f6` | not shown → error (`Contra-Infr`) | The source infers a mechanism contradiction from the answer; I treat the mechanism as unshown despite an incorrect overall prediction. The source mapping adds help for this facet. An overall wrong result alone should not populate every related component with errors. |
| `SE.27b.333.1`, `f4` | cannot judge → error (`Contra-Infr`) | The explanation about air and the thermometer is unclear. The source maps it to a contradiction. Clarification remains a defensible proposal, not a confirmed best intervention. The source mapping adds help here; both simulations retain the check. Together with the recorded prediction error, this case exposes the action conflict above. |
| `MS.50b.136.1`, `f4` | not shown → demonstrated (`Inferred`) | Consistent units and measurements may imply shared understanding, but the answer does not state the communication benefit. Interpretation unresolved; no demonstrated misconception. The assessor simulation retains this check. |
| `MS.50b.136.1`, `f5` | not shown → demonstrated (`Inferred`) | The second facet of that same interpretation disagreement. One concrete application question could distinguish the readings; two separate drills are unjustified. The assessor simulation retains this check too. |
| `MS.50b.311.1`, `f5` | not shown → demonstrated (`Inferred`) | The generic statement about knowing the best way to do something has an unclear referent. The source's positive inference is disputable. Resolve meaning before deciding on help; the simulation retains the check only on the assessor side. |
| `ME.36.214.1`, `f4` | not shown → demonstrated (`Inferred`) | Sharing energy may imply a common path, but does not necessarily establish that topology. This is an inference-policy disagreement, not evidence of a specific misconception. The assessor simulation retains one path check. The broader causal explanation was excluded from comparison. |
| `LF.13b.478.1`, `f3` | cannot judge → not shown (`Unaddressed`) | Making new land could suggest transported material or reshaping in place. Both interpretations leave movement unestablished; the two simulations choose the same actions. |
| `LF.13b.478.1`, `f5` | cannot judge → not shown (`Unaddressed`) | Same ambiguous movement event, now its relation to erosion. Do not count it as a second independently evidenced weakness. Both simulations retain the check without immediate help. |
| `LF.13b.737.1`, `f2` | demonstrated → not shown (`Unaddressed`) | Removal was credited as wearing away as well as transport. The reference keeps these distinct. This is a possible overbroad reading, with semantic adjudication unresolved. The simulation removes this check relative to the reference; it does not prove a learner gap. |
| `LF.13b.737.1`, `f4` | demonstrated → not shown (`Unaddressed`) | The same disputed interpretation also credits wearing during erosion. The simulation removes this related check too; it is not another independent incident or a separately confirmed assessment error. |

## Planner consequences and their limits

For each response, the comparison executes the existing connected components with an empty learner history. Students are never combined into one history. The clarification/help conflict above is an actual returned-output mismatch on a real response, though no intervention was delivered.

A separate, explicitly counterfactual probe gives every comparable facet a pending check and treats the archived response **as if** it were a later answer without help. It then compares what the same planner does with the frozen observations versus the mapped source annotations:

| Difference relative to the mapped reference | Facets |
|---|---:|
| Additional pending checks removed | 2 |
| Additional pending checks retained | 7 |
| Additional help targets | 1 |
| Help targets absent | 2 |

These counts can overlap and must not be added into an error total. The extra help target is precisely the disputed warming annotation; calling that help unnecessary would assume the disputed label is true. The seven additional retentions include pragmatic and questionable-source disagreements. The corpus supplies no human judgments about what to teach, no assistance history, and no later learning outcome. These are policy differences, not measured inappropriate practice, missed practice, retention or harm.

## Next bounded change

First, reproduce `SE.27b.333.1` as a regression case and make the existing connected output select a coherent immediate action. A supported proposal to resolve an interpretation that could change practice should hold off corrective practice for the affected target, while preserving the original observation. Resolving that question should then allow focused help, credit, or an explicitly unresolved outcome. Unrelated clear errors should remain eligible for help. Whether to represent the original prediction as provisional or to block only its action is a small design choice to test; this review does not silently settle it.

Verify this against the original misread case, clear command errors, mixed success and target-scoped assistance. Do not clear a pending check merely because clarification was proposed. Preserve the user's accepted combined later exercise. No additional learner exercise or timing commitment is required for this implementation experiment.

Second, use the wearing/movement and thermometer examples when defining meaningful learning targets and acceptable implication boundaries. Retain the frozen set for regression discussion, but use a new independently judged sample to evaluate a revised assessor; tuning against this set would no longer be a blinded evaluation. A new memory model, a graph-wide transfer rule, or additional storage is not justified by these results.

## Reproduce and remaining uncertainty

From the repository root:

```sh
python3 .scratch/skill-maintenance/spikes/independent-assessment/select_sample.py
node .scratch/skill-maintenance/spikes/independent-assessment/compare.mjs
```

The selector downloads only pinned source files if needed and reconstructs the same packets. The comparison verifies the frozen digests, validates all 12 records through the real bridge, checks 48-row coverage and writes `comparison.json`. The source packet includes the entire reference context even though only four facets per question are scored. This is not a whole-answer benchmark.

The sample is small, clustered within four elementary science questions and drawn from an already filtered public corpus. Public model-training exposure cannot be ruled out. Neither label agreement nor the source's own annotator agreement establishes truth. No new human assessor, general-subject diagnostic accuracy, learning gain, durable retention, measured learner burden, or reliable misread classifier was established. Broader validation choices, representation and inference remain open.
