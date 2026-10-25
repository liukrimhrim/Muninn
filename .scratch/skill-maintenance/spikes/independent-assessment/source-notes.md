# Independent response-assessment source notes

Prepared 2026-10-14. This is a small, selected-facet comparison against pre-existing human annotations, not a complete grade or evidence of durable learning. No assessor output was used to select records. Selected labels and label counts are confined to `withheld-reference.json`; the assessor must also avoid the annotated ZIP in `source/` until freezing its judgments.

## Provenance and permission

The repository owner's profile identifies [Myroslava Dzikovska](https://github.com/myrosia), first author of the [2013 task paper](https://aclanthology.org/S13-2045/). The repository [README at the pinned commit](https://github.com/myrosia/semeval-2013-task7/blob/5157c69f914e8c581045c03e98f96398d40a91b8/README.md) attributes the corpora to Dzikovska and Rodney Nielsen. This supports treating it as an author-maintained distribution, rather than an unrelated mirror.

The release explicitly supplies [CC-BY-SA 3.0 Unported](https://github.com/myrosia/semeval-2013-task7/blob/5157c69f914e8c581045c03e98f96398d40a91b8/LICENSE). The license was read before downloading responses. The unchanged notice is retained at `source/LICENSE`, with the original README at `source/README.md`. The JSON selection/reformatting of dataset material is likewise offered under CC-BY-SA 3.0; this notice does not relicense unrelated repository code. Attribution, source links, and transformation disclosure are embedded in both packets. No endorsement is implied.

Pinned commit: `5157c69f914e8c581045c03e98f96398d40a91b8` (2022-01-17). Download: [semeval-5way.zip](https://raw.githubusercontent.com/myrosia/semeval-2013-task7/5157c69f914e8c581045c03e98f96398d40a91b8/semeval-5way.zip), 12,983,203 bytes, SHA-256 `57c14e5c260d8cfd774f3fb954985d94bcfa3407029bfe585179650b907dbf9b`. The ZIP is only a local cache, excluded by this folder's `.gitignore`. `source-manifest.json` pins its selected XML members and the license/README hashes.

## What the annotations mean

The original corpus used grade 3–6 science responses. Seven college-student annotators participated. The authors report 78.4% agreement for eight labels, and 86.2% for a coarser five-label grouping; neither figure establishes this sample's correctness. Table 5 defines the released vocabulary as follows. [Nielsen et al. 2008, §§3.1–3.3, Table 5](https://www.lrec-conf.org/proceedings/lrec2008/pdf/873_paper.pdf).

| Source label | Meaning | Proposed comparison treatment |
| --- | --- | --- |
| Expressed | Explicit content or simple inference | demonstrated |
| Inferred | Pragmatic or nontrivial inference | demonstrated, report separately |
| Assumed | Presumed beforehand, often from the question | Outside primary score |
| Contra-Expr | Direct contradiction | error; retain subtype |
| Contra-Infr | Inferred contradiction | error; retain subtype |
| Self-Contra | Both support and contradiction | error; retain subtype |
| Diff-Arg | Same relation, different modifier/argument | Outside primary score |
| Unaddressed | Facet not addressed | not_shown |

The right column is our comparison convention, not the authors' ground truth about mastery. `cannot_judge` is assessor abstention. Assumed is not evidence supplied by that response; Diff-Arg cannot safely be forced into error. All source categories remain intact in the withheld packet. No category was used as a sampling filter.

Facets encode low-level semantic relationships. Linked propositions refer to other facet IDs; their meaning requires the full reference answer. The original representation also marks assumptions supplied by the question. [Nielsen et al. 2008, §2](https://aclanthology.org/P08-2061.pdf). The blind packet strips `isAssumed` along with response annotations, but retains every other reference facet attribute and token ID.

## Upstream restrictions and limitations

The 2012 SRA preparation excluded questions with over 80% of responses in one answer category or fewer than three correct responses, alongside unsuitable question forms. Therefore this release is already shaped by label-based upstream selection. [Dzikovska, Nielsen and Brew 2012, §3](https://aclanthology.org/N12-1021.pdf).

The 2013 organizers removed questions requiring insufficiently supplied outside material and some with unrelated alternative answers. Their partial-entailment pilot further retained only Expressed/Unaddressed, excluded problematic relation types and linked propositions, and removed relation names. **Our sample uses the richer Extra XML in the five-way archive, not that filtered pilot.** Its original eight-category annotations and relation structures remain available. Educational judgments are not identical to strict textual entailment. [Dzikovska et al. 2013, §§3.2–3.4, 5](https://aclanthology.org/S13-2045.pdf).

The archive directly verifies the eight label names and the presence of `facetEntailment` records in `sciEntsBank/test-unseen-questions/Extra/`. These are historical human judgments, not newly verified student states. This exercise can test agreement on selected response relationships and, where present, contradiction judgments. It cannot establish memory retention, durable mastery, reasons for omissions, prompt misreading, teaching effectiveness, or transfer beyond these questions. It cannot rule out model pretraining exposure to this public corpus. Closely related decisions within an answer are not independent observations.

## Deterministic selection and blinding

`select_sample.py` uses only Python's standard library. Run it from any directory; it downloads only the three pinned source files when missing and verifies their hashes.

1. Pool: the 15 Extra XML question files in `sciEntsBank/test-unseen-questions/Extra/`.
2. Before ranking, exclude any question mentioning `fruit`, because the assessor had encountered a labeled fruit/seeds example in the task paper; none of this pool's questions matched. Exclude multiple-reference questions; none matched. Exclude questions matching the case-insensitive whole-word regex `diagram|picture|table|graph|shown|below|above|drawing|chart|illustration|figure|image|photograph` to avoid missing context. This removed `ME_74b`, `MX_11b`, `VB_5c`, and `LP_16c`.
3. Rank IDs by ascending SHA-256 of UTF-8 `mem-graph-independent-assessment-v1|<question_id>`, taking the first four distinct modules. Within each, choose the three responses with smallest hashes of `mem-graph-independent-assessment-v1|<response_id>`.
4. Choose four facets per question by ascending SHA-256 of `mem-graph-independent-assessment-v1|<question_id>|<facet_id>`. Break hash ties by exact ID. Preserve every original facet in `context_facets` to resolve linked propositions, but score only `facets`.

The four-facet cap was requested before the assessor saw packets or labels. A preparer-only inspection of the initial unlabelled packet caught a missing illustration cue; the regex was expanded before release, and the same hash ordering was rerun. No label-driven replacements or balancing occurred.

Final shape: **12 responses, four questions/modules, 16 selected facets, 48 decisions**. Questions concern thermometer handling (`SE_27b`), standard units (`MS_50b`), circuit arrangements (`ME_36`), and erosion (`LF_13b`). This is deliberately small, not a representative sample or a full-answer evaluation.

## Files and verification

`blind-inputs.json` has top-level `questions[]`. Each question carries `question_id`, `module`, `source_path`, `question`, `reference_id`, `reference_answer`, `reference_tokens`, four `facets`, all `context_facets`, and three `responses[{response_id,response}]`. Each facet retains its source `id`, `govNum`, `modNum`, `reltn`, `govText`, `modText`, and any `childProp...` links. No generated glosses or repaired wording were inserted.

`withheld-reference.json` preserves selected `facet_annotations[{facetID,label}]` and original whole-answer categories, separately from the blind inputs. Whole-answer categories are provenance only and are not valid targets for this selected-facet comparison.

Verified: selected response/reference text is identical between Core and Extra XML; each selected facet has exactly one source annotation per response; erasing every `label`, `accuracy`, and `isAssumed` value in memory produces the identical blind selection. The selector prints hashes and sample size, never label counts.

- Blind inputs SHA-256: `d76a87c6a297cbcbd67f91a72894ca782adf7e9812bd81e0f1b33672a952f993`.
- Withheld reference SHA-256: `b34ff37773ac556c07fa3b149a7d1dd6ac43cd12b9240892c206f9f15372f81c`.

Assessment, protocol, comparison, and review outputs belong to the parent and were not created or consulted here.
