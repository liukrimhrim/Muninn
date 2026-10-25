# From learning material to useful practice

Status: first-release workflow finalized in [Design Baseline 1](design-baseline.md), 2026-10-16. Assisted, editable source-to-practice authoring is the baseline. Automatic extraction quality remains to be qualified across subjects.

## The learner's path

The [admission contract](learning-lifecycle-contract.md#1-selecting-goals-does-not-create-a-review-backlog) makes selection and active practice distinct: importing 200 selected goals and starting three leaves 197 visible unstarted goals, not overdue reviews. “Start this curriculum” previews work within the session budget and admits only the chosen new targets; shared exact targets reuse history and schedules.

The learner supplies material and says what they want to retain or be able to do. The system proposes a short learning outline, keeps the supporting passages accessible, and prepares an initial useful exercise. The learner can change the outline or begin practice. They should not have to build a graph, write rubrics, or approve every extracted sentence.

1. **Bring material and a purpose.** For example: “I want to explain why binary search is logarithmic” with a short passage. Offer a purpose inferred from the material when the learner has not stated one; label it as a suggestion. Remembering a definition, explaining a connection, choosing when to use it, and carrying out a procedure can require different targets.
2. **Preview what will be learned.** Show meaningful claims, essential connections, conditions, and a representative exercise in ordinary language. Include omissions that matter to the stated goal. Keep IDs, graph edges, and rubric plumbing behind an inspect view. A ready outline is editable; known content doubts remain visible and hold only affected targets.
3. **Begin useful practice.** For familiar material, start with the larger exercise that can reveal what is missing. For unfamiliar material, allow reading an explanation or worked example first. Do not impose a universal understanding → memorization → application sequence. Record help and do not mistake a copied explanation for independent recall.
4. **Respond to evidence.** A specific observed gap can receive focused practice. Ambiguous failure can receive a short discriminating question. An omitted explanation calls for evidence, not an automatic failure label. Supported misreading remains distinct from a knowledge gap. After repair, use a fresh integrated task, then arrange later checks separately.
5. **Correct content at the point of use.** From an exercise, the learner can say “this claim is wrong,” “these are the same idea,” “this question tests something else,” or “I only misread it.” Content correction, assessment correction, and learner practice are different operations. Preserve the original response and show what the correction changes.

The important product ask is the source and intended use of the knowledge. Internal content review belongs primarily to the authoring process. Do not turn this workflow into mandatory per-node homework for the learner.

## What the chat requires us to preserve

The [retrieval ledger](research/conversation-retrieval.md) distinguishes the user's requirements from earlier assistant proposals. The user's [context and topology concern](../../sources/fsrs_learning_conversation.md "Source line 204") and [atomicity versus excessive review concern](../../sources/fsrs_learning_conversation.md "Source line 610") mean that splitting text is insufficient. The later requirement to identify the specific missing knowledge after a large exercise also requires explicit evidence mappings.

The original discussion additionally proposed attaching new material to existing knowledge, typed relationships, shared structures, progressive graph refinement, and LLM assistance. These remain useful design candidates. They do not prove that a model can extract or assess any subject accurately. [Unresolved workflow tensions](research/conversation-retrieval.md "Source line 182") include authoring burden, curated versus generated content, and how much representation to expose.

## Choose assisted authoring, with inspectable output

| Approach | Useful property | Cost or limitation | Proposed place |
|---|---|---|---|
| Manual authoring | Explicit control over meaning, conditions and assessment | The learner becomes a curriculum author | Expert correction and a reference baseline |
| Curated packs | Content and exercises can be checked together before use | Someone must maintain the pack; coverage is limited | Initial validation examples and reusable starting material |
| Assisted authoring | A model can propose units, connections and exercises from supplied material | Plausible omissions, overstatements and bad rubrics still need detection | Proposed default for personal material, with inspectable drafts |
| Generate questions directly from text, retaining no explicit knowledge representation | Low initial authoring ceremony | Harder to preserve identity, locate a recurring gap, reuse knowledge or explain correction impact | Comparison baseline, not the proposed main representation |

The proposed first build accepts pasted or uploaded plain text plus a title and optional source location. That is a small implementation slice, not a claim that books, diagrams, webpages or PDFs are unnecessary. Add each format when its extraction can preserve the meaning needed by its targets; do not treat flattened tables, equations or figures as successfully ingested simply because text was returned.

The present spike genuinely captures literal text and source versions. Its semantic drafts are authored examples. It does not call an LLM, parse a PDF, fetch URLs or test arbitrary extraction. The next implementation must make the assisted-draft boundary real and inspect its output against new material.

## How to break material into useful units

Work backwards from what the learner needs to remember and do. Propose the smallest **meaningful** distinction that could change diagnosis or practice. Sentence boundaries and token counts are not the rule.

For each proposed unit, retain its claim, scope and conditions, source passage, identity/version, and any known doubt. A definition may be one unit. A relationship may also be one unit. A procedure can initially remain a meaningful whole, with steps separated when failures at those steps require different help. A detail that matters only to grading can remain an assessment criterion instead of becoming a permanent learning target.

Preserve the explanation that joins units. A binary relation should say what the connection means, not merely list two related topics. A larger knowledge group should retain the shared argument, sequence, contrast or joint constraint. Derived claims explicitly name supporting claims. Those dependency references express content provenance; they are not automatic learner prerequisite credit or a requirement to test every dependency separately.

Use this concrete distinction:

| Source meaning | Proposed knowledge | Practice implication |
|---|---|---|
| Repeated halving from `n = 2^k` to 1 takes `k` reductions | Halving and logarithms are connected under those conditions | Ask the learner to reconstruct the relationship |
| Constant local work occurs in every call | Total work counts calls across all continuing branches | Check whether the learner counts more than depth |
| One continuing branch and two continuing branches can have equal depth but different work | A composition claim depends on both preceding ideas | A larger comparison can reveal a missing connection even when the parts are known |

With size-1 termination, the examples have `k+1` and `2n−1` calls respectively. Both have one call when `n=1`. The meaningful contrast is that equal depth does not establish equal total work. “The algorithm halves its input, therefore its total work is logarithmic” drops essential conditions. This is exactly the sort of plausible overstatement an authoring process must detect.

Keep direct recall and reconstruction distinct when the goal requires it. The mathematics example selects explanation targets; it does not quietly add a timed complexity-label drill. The invented vocabulary example selects only recalling “blue” from “mavo”; it needs neither a reasoning chain nor a separate graph review.

## Sources, existing knowledge and uncertainty

Capture the supplied source immutably. Anchor each claim to an exact passage and source version. Store derived content as derived, with its supporting claims and reasoning. A valid quote establishes that the passage was captured correctly; it does not establish that the claim follows, that the source is true, or that the source is current.

Search existing knowledge before creating duplicates. Present candidate matches with their meaning, scope and sources. Exact meaning under the same conditions can reuse an identity after an explicit mapping review. Similar wording under different conditions may need a contrast, narrower claim or separate identity. A contradiction needs resolution or an unresolved status, not an automatic merge. Attaching another source never creates a learner observation or proves prior mastery.

The spike supports only explicit exact claim/scope/dependency matches. It rejects flagged matches, preserves both sources, revises dependent identities, and holds affected exercises for review. Semantic similarity search, general merge/split editing and automatic conflict detection are not implemented.

## From knowledge to exercises

Use the [authoring intent and teaching contract](learning-lifecycle-contract.md#3-authoring-is-a-checked-operation-before-delivery) for initial outlines, fresh variants and targeted explanations. All three save bounded inputs and checked candidates before delivery. Accepted teaching is a definition; actual study completion and its later verification are separate records. Stale/cancelled generation cannot serve a newly edited meaning.

The [detailed exercise contract](everyday-learning-design.md#3-exercise-families-freshness-and-comparability) develops this boundary: repeated fact cues, surface variants, new instances and changed demands; semantic acceptance and bounded regeneration; answer exposure; comparability without calibrated difficulty; and held-out check handling. Its [worked cases](everyday-learning-cases.md) state what the proposed first release must preserve.

For selected content, specify the observable action, mode and conditions. Build an exercise with a prompt, required criteria, permitted help, and explicit criterion-to-capability coverage. Include setup, answer and feedback time in the illustrative cost. Keep the conditions needed to answer in the prompt: a fragment such as “compare the branches” is insufficient on its own.

An exercise records the capability definition it was authored to assess. Compilation resolves the content and dependency versions and refuses a stale mapping. It must not silently stamp a recall prompt with a newly edited recognition contract. Before use, content review checks both directions: the source supports the intended claim, and the exercise can elicit the intended capability without supplying its answer.

An integrated answer can support several targets, but each target requires its mapped evidence. A missing integration criterion does not erase evidence for the parts; it also does not prove the learner cannot integrate them. Relationships remain assessable targets rather than unobserved edges that automatically receive credit.

Keep the proposed target list visible even when some targets are held. “No eligible exercise” may mean a content problem or an authoring gap, not completion of the learning goal. Usable content without a suitable exercise remains unserved.

## Correction and versioning

| Change | What follows |
|---|---|
| Capture a revised source | Keep the previous source version and require new anchors where appropriate |
| Correct a claim or its applicability | Create a new unit version; flag transitive dependent claims, affected capabilities, prompts and rubrics |
| Change an action, mode or condition | Require a new capability definition and review the exercise mapping; do not borrow evidence from the old mode |
| Reuse a canonical claim | Preserve source provenance; version dependent references and review affected mappings |
| Split or merge meanings | Preserve old identities and explicit replacement mappings; reassess the affected exercise coverage before any history migration |
| Correct an assessment | Preserve the response, former judgment and correction reason; recompute only the justified learner conclusions |

The spike implements local claim revision, source versioning, exact reuse and exercise review. It detects target edits that leave old exercise mappings behind. It preserves snapshots; it does not implement a production revision store, a full capability editor, general splits/merges or evidence migration.

Old answers remain attached to what was actually asked and judged. A content dependency change may require new practice definitions without invalidating every historical observation. Deciding which old evidence still applies needs an explicit mapping; blanket reset and blanket transfer are both unjustified. The existing bridge therefore stops on contract drift while leaving history intact. Unaffected work can be designed to continue; the current conservative bridge stops the affected dataset rather than implementing that finer continuation.

## What this investigation establishes

The [bounded experiment](spikes/material/README.md) connects actual source capture and content resolution to the existing assessment bridge and exercise selector. It includes a connected mathematics explanation, one invented association, an unsupported proposal, reuse, and correction impact. The examples show:

- Compiling an outline does not create learner credit.
- A larger answer with a connection error leads to connection practice, then a fresh integrated check.
- A missing explanation remains unobserved, rather than becoming an observed failure.
- Changed claims or target definitions cannot silently reuse the old exercise mapping.
- A flagged contradiction cannot disappear through reuse, and old content versions remain intact.

An independent audit identified the target-mapping and reuse defects; those were fixed and exercised in the replay. These are program-behavior results on authored examples, not evidence of accurate extraction, accurate semantic grading, saved learning time or retained learning. The optional page needs no user review to complete this design step.

## Next build boundary

Consolidate this workflow with the [representation](representation-design.md), [inference](inference-design.md) and [selection](selection-design.md) contracts into one minimal end-to-end implementation plan. The next useful build is a single path from new text to a saved, editable learning outline, one genuine learner attempt, a justified response, and a revisitable history. Reuse the same path for a fact and a connected explanation. Keep estimates separate from observations and use a simple practice policy until evidence warrants more.

Before claiming assisted ingestion works, compare new generated outlines with a manually checked reference: missing claims, lost conditions/connections, unsupported additions, incorrect reuse, broken exercise coverage, and the editing effort required. Count authoring and correction time separately from practice time. Before claiming fewer reviews are better, use the delayed-outcome evaluation already specified; no amount of successful compilation establishes that result.

The delivery environment, actual learner time budget and acceptable retained-performance trade-off remain product/evaluation choices. They do not block finishing a concrete minimal build plan. No new learner exercise or repeat approval of the accepted diagnosis sequence is required now.
