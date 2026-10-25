# Independent audit of the annotation comparison

Completed 2026-10-14 by the source-preparation agent, after the parent explicitly reported the assessment frozen and authorized reference reveal. This is a separate agent's source, arithmetic, and execution audit. It is not independent human adjudication of student understanding or an independent model evaluation.

**Result: the calculations and reproduced output conflict check out. One overstatement about erosion was corrected; no remaining correction is required within this audit's scope.** Disputed meanings remain unresolved.

## Freeze and source integrity

- All five files listed in `freeze.json` match their committed digests. The reference file matches the digest supplied before reveal: `b34ff37773ac556c07fa3b149a7d1dd6ac43cd12b9240892c206f9f15372f81c`.
- Directly re-reading the pinned ZIP confirmed all 48 selected labels and every blind reference-facet attribute against source XML. No selected source category was normalized or reinterpreted during extraction.
- The bridge, trial, and planner dependency files have no diff from freeze commit `f397ef8`. No frozen assessment, protocol, input, adapter, or validation file was edited during this audit. Exact source license and README copies remain unchanged.
- Audited `comparison.json` SHA-256: `72ecd1a89ac927d3dfc4cdbb8964315d47afa49ace985c47f003d183cf1bc074`.
- Audited revised `review.md` SHA-256: `845f3273f3cba849851c46e6ea942ce499894a4ee52830c0277d6e6b23ca33f1`.

## Mapping and calculations

The comparison implements the frozen mapping exactly. It is compatible with the original authors' distinctions in [Table 5 of the annotation paper](https://www.lrec-conf.org/proceedings/lrec2008/pdf/873_paper.pdf): assumptions are separated from response evidence, inferred and explicit expressions are retained as distinct source categories, and contradictions are not collapsed into absence. Mapping these categories to this prototype's statuses remains an evaluation convention. It does not transform annotation agreement into verified correctness.

An independent Python calculation joined observations to annotations by response and facet IDs. It checked exact key coverage, every row's source label/status/outcome/reason/quotes, per-label counts, excluded records, and all counterfactual set differences. It did not invoke the parent's comparison program to obtain its expected counts.

| Result | Count |
| --- | ---: |
| Matches | 23 |
| Disagreements | 10 |
| Abstentions | 3 |
| Excluded Assumed annotations | 12 |
| Comparable / total | 36 / 48 |

The six Inferred-to-not_shown differences are policy-sensitive pragmatic-inference disagreements, not six established assessor mistakes or learner deficits. Comparable coverage is uneven: 12 thermometer, 9 units, 3 circuit, and 12 erosion judgments. The protocol's exclusions leave only one selected circuit facet per response in the comparison.

The review's disagreement table contains each of the 13 nonmatching comparable rows exactly once. The 12 exclusions remain individually identifiable in `comparison.json`. All eight possible source categories are preserved in the mapping even though not every category occurs in this sample.

## Planner consequences

Independent set calculations confirmed the simulated differences: two additional pending checks removed, seven retained, one additional help target, and two help targets absent relative to the mapped reference. Assumed annotations are excluded on both sides of this simulation. These counts overlap; they are neither independent errors nor counts of teaching sessions. They depend on the explicit hypothetical later, unassisted check and pending-target state, neither of which the corpus establishes.

I separately executed the actual adapter → trial → bridge → planner path for `SE.27b.333.1` without writing its files. It accepted the frozen record with zero validation errors. The assessment proposes a follow-up covering `SE_27b_f2` and `SE_27b_f4`, while `plan.now` returns immediate help for `SE_27b_f2`. The returned channels therefore expose a real action-precedence conflict. The finding does not depend on accepting the historical science labels, and does not show that any learner received harmful or unnecessary instruction.

The proposed bounded change addresses that observed integration conflict. Its pedagogy remains a design hypothesis: this corpus cannot establish that clarification is the optimal intervention. Preserving observations, keeping unrelated clear errors eligible for help, and testing target-specific action precedence are appropriately narrower than changing a general memory model.

## Claim-strength correction and limits

The first review version described `LF.13b.737.1` as a confirmed conflation and unsupported credit. I requested a correction because a recorded Unaddressed label cannot by itself settle whether removal reasonably implies wearing away. The revised review now calls this a possible overbroad reading relative to the annotations and explicitly leaves semantic adjudication unresolved. The two simulated removals remain factual consequences of the differing mappings.

The revised report separates observed program outputs, simulated policy differences, and disputed semantic interpretation. It does not claim grading accuracy, human approval of next actions, learner harm, mastery, retention, or teaching benefit. Reusing this sample for regression discussion is appropriate; using tuned performance on it as a new blinded evaluation would not be. Broader subject coverage, a fresh human review of disputed meanings, and real learning outcomes remain outside this audit.
