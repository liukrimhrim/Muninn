# From a learner's answer to useful practice

Status: first-release diagnosis contract finalized in [Design Baseline 1](design-baseline.md), 2026-10-16. Preserve the confirmed larger-exercise → supported-gap diagnosis → focused help → fresh-check sequence. Worked examples specify behavior; they do not establish general assessment accuracy.

The subsequent [answer-assessment trial](spikes/assessment-trial/README.md) runs these instructions through the current Codex chat on ten constructed answers and provides a page for separate human review. It checks input binding and quotation validity, not semantic accuracy. On 2026-10-13, the user reported completing the review and finding the judgment sensible. A subsequent [real learner attempt](spikes/assessment-trial/learner-trial.md) exposed an unnecessary follow-up for a trivial misread, recorded below. Independent assessment, remedial benefit, and retained learning remain unmeasured.

The aim is to find a sufficiently specific, supported practice target. An answer can show that the learner could not explain a relationship on this attempt. It cannot by itself establish whether they forgot it, never learned it, misunderstood the question, or made a slip.

## 1. Decide what evidence the exercise can produce

Before presenting a question, define the target, an observable criterion, acceptable alternative answers, and what would remain untested. These belong to the exercise content. They are not universal rules about every subject.

For example, a binary-search explanation can assess several distinct targets:

| Target | Evidence that supports it | Evidence that is insufficient |
|---|---|---|
| Ordered-search condition | Explains why the ordering permits eliminating a region | Mentions the word “sorted” without explaining its role |
| Elimination step | Correctly chooses which region to discard from a comparison | Merely says “divide the array” |
| Repeated halving | Produces a correct sequence and counts the reductions | Gives the final count without work |
| Meaning of a logarithm | Explains that `log₂(64) = 6` means `2⁶ = 64` | Recites “binary search is logarithmic” |
| Connection | Explains why the halving count is the exponent, using words, a diagram, or an equation | States both facts without relating them |

This example uses ideal halving until one candidate remains, not an implementation's exact comparison count. A complete exercise must ask for the explanation it intends to assess. If it asks only for a number, an omitted explanation is not a failed requirement.

Targets can overlap. A coherent derivation may provide evidence for several criteria at once; no preliminary quiz is required. Conversely, being a prerequisite or appearing in the topic graph is not evidence that a target was demonstrated. Do not force all subjects into the existing prototype's six-target shape.

## 2. Read the answer before diagnosing the learner

For each relevant criterion, preserve the original response and make one scoped observation:

| Observation | Meaning | Usual next action |
|---|---|---|
| Demonstrated here | The response meets the criterion under the recorded conditions | Reuse that evidence; do not immediately retest it without a reason |
| Error shown | A statement or action conflicts with the criterion | Practice the identifiable target, or distinguish causes if they require different practice |
| Not shown | The answer supplies no usable evidence for this criterion | Ask only if knowing this would change the next step |
| Cannot judge | The wording, assessment rule, or assessor cannot settle the result | Clarify the answer or review the assessment; do not record a learner failure |

An explicit “I don't know” on a focused question records unavailable recall on that attempt. An empty submission may instead be a skipped attempt or input problem. Neither establishes a permanent inability.

Every positive or negative observation must point to the relevant response span or recorded action and the criterion it supports. “Not shown” points to the unanswered requirement; it must not invent a quote. A quoted sentence still needs a valid interpretation: evidence extraction alone is not grading.

Separate answer completeness from the need for reinforcement. When the learner's reasoning already demonstrates the relevant knowledge and a small mismatch fits a misread, use that context: briefly point out the mismatch and move on. “Not shown” is not an obligation to ask another question. A likely-misread inference may justify skipping diagnosis without rewriting an omitted detail as directly observed. Record a learner's report of a misread alongside the response; if it fits their reasoning and correction, no remedial practice is needed. A substantive contradiction still needs attention even when the learner calls it a slip.

Record assistance separately. Naming the target narrows the task; supplying a rule or intermediate result supplies answer content. A correct focused response can support that focused target without establishing independent selection or whole-task performance. Preserve feedback and hints in the same attempt history. Follow-ups are further learning opportunities as well as observations, so do not describe them as revealing an unchanged hidden state.

## 3. Choose a question only when its answers change the next step

Use the response to list the few plausible explanations relevant to the current goal. Include multiple simultaneous gaps when supported. Use the graph to find relevant prerequisites, not to test every ancestor.

For each candidate follow-up, write its branches before asking it: what would a correct answer, an error, or an inconclusive answer change? Reject a question if every branch leads to the same practice. When the response already identifies a useful target, go directly to that practice.

Different hypothetical branches alone do not justify a question: there must also be an unresolved learning concern supported by this answer. Do not invent a plausible gap merely because any extra question could be answered incorrectly. If a brief correction handles a minor task-reading mismatch and the underlying reasoning is sound, prefer that correction to a new assessment turn.

For the first trial, prefer a question that distinguishes the competing practice choices and fits the remaining time. If several do, use the shorter authored question; break remaining ties by the author's explicit order. This is an inspectable baseline, not a claim of optimal information gain. It uses no weighted score.

Reuse relevant prior evidence with its date, task conditions, and assistance visible. A later contradiction reopens the affected target; it does not erase earlier success or invalidate every other component. A historical pass with different cues does not settle an unaided recall question today.

## 4. Worked example: the facts are present, the explanation is missing

**Larger exercise:** “Explain why binary search can discard candidates in a sorted array. Then use ideal halving from 64 candidates to one to explain why the number of halvings grows as `log₂(n)`.”

**Learner:** “If the target is bigger than the middle value, all values at or below the middle can go because the array is sorted. Repeat on what's left. The halving sequence is 64, 32, 16, 8, 4, 2, 1: six halvings. `log₂(64) = 6` means `2⁶ = 64`.”

This answer supports the stated elimination case, the specific halving calculation, and the meaning of this logarithm. It does not explain the general connection. The system should not yet say that the learner *cannot* connect them.

**Follow-up:** “Why does `log₂(n)` give the number of halvings needed to reach one candidate?”

| Possible learner answer | What it establishes | Next step |
|---|---|---|
| “After `k` halvings there are `n/2ᵏ` left. Set that to one: `n = 2ᵏ`, so `k = log₂(n)`.” | The connection is demonstrated on a focused question | Complete the larger explanation or use a fresh larger check; skip remedial practice for this link |
| “I remember those two facts, but I cannot explain why the numbers match.” | The learner reports inability on the requested connection; the earlier facts remain supported within their scope | Explain the link, practice it, then check a different larger example |
| “One halving leaves `n/2`, so it takes `n/2` halvings.” | The response confuses candidates remaining with number of reductions; it also conflicts with the earlier correct count | Ask: “With 32 candidates, list the remaining counts and label how many halvings have occurred at each point.” Correct counts redirect to connecting the count to the exponent; repeated counting errors redirect to repeated-halving practice |
| “Because it gets smaller.” | Too little evidence to judge the connection | Ask once in simpler terms: “If the starting number doubles, how does the number of halvings change? Explain.” An answer without its reason still leaves the connection unresolved |

For the second branch, the focused explanation can use reversing the sequence: six doublings take one to 64, so six halvings reverse that process. Then use 32 in a focused check and 128 in the next larger exercise. Success immediately after feedback is evidence of current performance; retained learning still needs a later check.

The learner-facing reason is: **“You showed the halving steps and explained the logarithm. Let's check why they describe the same count.”**

## 5. Worked example: the same wrong sentence, different practice

**Larger exercise:** “Complete ‘The key near the cabinets ___ missing’ with ‘is’ or ‘are’, and explain your choice.” The scope is standard written English with ordinary singular and plural nouns.

**Learner:** “The key near the cabinets are missing.”

The verb choice is incorrect for this sentence. That alone does not identify whether the problem is finding the subject, recognizing its number, remembering the verb form, or applying agreement in context.

**First follow-up:** “Which thing is described as missing?”

| Learner answer | Follow-up or practice |
|---|---|
| “The cabinets.” | Practice finding the noun the sentence is about. Do not also declare verb-form knowledge weak |
| “The key.” | Ask “Complete ‘The key ___ missing’ with ‘is’ or ‘are’, and explain.” This removes the nearby plural noun |
| “I'm not sure what the sentence means.” | Clarify the sentence meaning before inferring a grammar gap |

On the second branch, “are, because key is plural” points to the number of “key.” “Are; key is singular” points to the singular verb form. “Is, because key is singular” supports the simple form, leaving application around the intervening phrase or a slip unresolved.

If the simple form passes, ask a third question: **“Complete ‘The label on the boxes ___ torn’ and explain.”**

- “Are, because boxes is plural” supports focused practice in applying the subject-to-verb connection around the intervening phrase.
- “Is, because label is singular” supports this contrast case. Keep the original error in history and avoid declaring a stable gap or a confirmed slip; return to the larger task.
- An unclear answer leaves the cause unresolved at the question limit. Offer a worked example or assessment review, labeled as support under uncertainty.

These questions narrow the task and cue attention. Passing them does not establish unaided performance on the original larger exercise.

## 6. Worked example: selecting, doing, and checking a procedure

Use a fictional archive tool to avoid assuming product-specific behavior. Its taught rules are: copy a document, open the copy, compare its contents with the original, and report success only when they match. A successful copy message confirms only that the copy operation finished. Archive only documents marked ready.

**Larger exercise:** Archive one ready document in the toy tool and report the result. Observation comes from a supplied action trace, not from guessed actions.

| Observed response or action | Supported target for follow-up or practice |
|---|---|
| Selects a document marked draft | Recognizing when the procedure applies |
| Selects the ready document but uses move instead of copy | Executing the copy step; do not infer inability to choose a ready document |
| Copy succeeds; learner says “That message proves the contents match” | Interpreting what the success message establishes |
| Correctly says comparison is required, then reports success without comparing | Applying the verification step; a one-off omission remains possible |
| Trace shows an error returned by the toy tool | Inspect the tool failure before attributing a knowledge gap |

If only a written plan is available, assess the plan. Do not claim that execution or verification was observed. This example shows how the same evidence rules can apply to procedures without treating a final success flag as evidence for every step.

## 7. Stop diagnosis and start useful learning

Stop asking diagnostic questions when a supported target is specific enough to choose practice. The system need not settle “forgotten versus never learned” if both currently call for the same short explanation and retrieval attempt.

The [everyday-learning proposal](everyday-learning-design.md#5-diagnosis-and-repair-that-can-stop) reconciles the earlier per-attempt/per-session inconsistency: at most three diagnostic prompts per persisted session, and three on the same unresolved concern across sessions. Clarification and slip checks count too; reopening does not reset the allowance. Stop earlier if continuing would consume the time reserved for feedback and a check. Three is a provisional burden limit, not a research-derived optimum. Historical prototypes retain their original behavior; this is the proposed product rule.

If the cause remains unclear, say so and offer a worked example covering the unresolved part, assessment review, or a pause. Mark this as support under uncertainty; do not write an invented precise diagnosis to learner history. If several gaps are observed, retain them all and address the one blocking the next meaningful attempt first. If a new larger answer exposes another gap, revise the practice choice.

After feedback, check the focused target without supplying the answer and then check its use in a different larger exercise. The focused check is unnecessary when the fresh larger task itself provides clear evidence for the repaired target. Keep delayed retention separate from immediate success. Repeated failure should change the explanation or revisit the target boundary, not restart an unlimited repair loop.

## 8. How an assessor would supply this evidence

The [detailed stopping policy](everyday-learning-design.md#repair-cycles) proposes a changed teaching approach after one supported unsuccessful repair cycle and assessment/content review after two. Missing or unjudgeable checks do not become failed cycles. The linked policy specifies resumption, uncertainty and preserved effort; these limits are proposals, not established learning thresholds.

The current HTML uses learner-entered judgments or authored walkthrough judgments. Its free-text box is not an automatic grader. Keep the response-assessment step explicit rather than hiding it behind the existing pass/fail controls.

For the first implementation trial, an assessor receives the exact prompt, original answer/actions, reviewed criteria, acceptable alternatives, and assistance history. It returns criterion-level observations with supporting spans, unresolved alternatives, and an explanation of why the proposed follow-up would change practice. The original response remains unchanged. The learner can inspect and correct a mistaken interpretation.

An LLM is a candidate for proposing these assessments, not an established source of reliable diagnoses. In the first trial, compare its proposals with independently made human assessments before using them to suppress practice. Exact span matching can catch invented quotations; it cannot establish that the quoted text satisfies a criterion. Do not substitute keyword matching or model-reported confidence for that check. The assessment method remains an open decision.

The existing attempt and observation records can hold this information. A diagnosis is a revisable explanation tied to those records, not a new permanent mastery label. No new service, database, or fitted probability model is needed to evaluate the proposal.

The 2026-10-14 [independent annotation comparison](spikes/independent-assessment/review.md) adds two concrete cautions. An answer about material being carried away was credited as also establishing wearing away, although the source annotations distinguish these. Separately, the connected components returned both a clarification proposal and immediate corrective help for an awkward thermometer answer. The subsequent [clarification continuation](spikes/answer-intake/clarification-notes.md) resolves which action proceeds for affected targets while retaining the original evidence. Unclear replies can leave assessment unresolved without restarting corrective practice. The semantic dispute remains open; neither issue is fixed by adding a memory model. Linguistic facets also need an explicit mapping to meaningful learning targets rather than automatically becoming review obligations. These findings do not settle the general assessment or representation decisions.

## 9. Counterexample review

This is a manual design review against constructed cases. It is not an automated grading benchmark or a measurement of real learner benefit.

| Challenge | Required result from these rules |
|---|---|
| Same wrong grammar answer, two different follow-up answers | Select different practice targets, as in section 5 |
| Correct “is” with the reason “use is whenever any noun is plural” | Preserve the correct selection and flag the incorrect stated rule; overall success does not erase it |
| Correct answer, explanation omitted | Record “not shown”; ask for it only if explanation is a learning target |
| Correct derivation in unfamiliar words or a diagram | Accept equivalent reasoning; exact vocabulary is not required |
| Missing ordering condition plus faulty logarithm explanation | Keep both gaps; repairing one does not clear the other |
| Halving and logarithm checks both pass, but the link fails | Practice the connection; do not infer it from isolated successes |
| Blank submission or broken tool | Resolve whether an assessable attempt occurred before diagnosing |
| Correct answer after a worked example | Record feedback exposure; do not rewrite the earlier attempt as unaided success |
| Fresh answer contradicts an old pass | Reopen the affected estimate and preserve both observations |
| Correct outcome with hesitation | Do not infer a specific gap from elapsed time alone; check fluency only when it is a stated goal |
| Three follow-ups do not distinguish the cause | Stop and retain the alternatives; no forced component label |
| Assessor quotes the answer accurately but applies the wrong rule | Review the assessment; quote fidelity does not establish judgment validity |
| Sound general reasoning with a minor omitted comparison | Treat a misread as a plausible explanation, briefly point out the mismatch, and skip diagnosis when no substantive learning concern remains |
| Learner calls an explicit wrong rule a misread | Keep the contradictory evidence; use clarification only if it changes whether or what to practice |

The review changed the proposal in three places: omissions require a distinct observation, a possible slip must remain provisional, and uncertainty in grading must not be stored as learner weakness. It also exposes a limitation of the existing prototype's fixed component-probe order: the next question should depend on which answers would change the next practice choice.

Later feedback from the real learner trial adds a fourth adjustment. The learner correctly explained binary search and why halving leads to a logarithm, but gave the larger list's count instead of the increase. After a follow-up they supplied `log2(65,536) - log2(1,024)` and said they misread the question. Accept that symbolic comparison; another arithmetic prompt would add no useful evidence for the learning goal. The earlier assessment did not label a knowledge failure, but it still imposed an avoidable completion check. The improved response is a brief correction and an end to diagnosis. This is one observed interaction and user correction, not a measured error rate or proof of learning benefit.

The [Kubernetes chat trial](spikes/assessment-trial/kubernetes-trial.md) subsequently completed the larger-task → focused-practice → fresh-task sequence with real learner responses and simulated operational evidence. Two command forms needed correction, were recalled in focused practice, and were then selected correctly in the fresh incident. A different step—locating an unsupported argument before choosing a code/image repair—used a tutor hint. The learner later explicitly distinguished Running from application function and chose logs to check completed work, after earlier teaching of that distinction. These observations belong to separate targets with separate assistance histories; a whole-exercise pass/fail would conceal them. Stop this bounded trial rather than inventing more gaps from shorthand or incomplete checklists. This is one learner's immediate application, with no independent assessor, delayed test, real cluster execution, or causal evidence of learning benefit.

On 2026-10-14, the user accepted the [concrete next-session proposal](issues/04-evidence-spike.md#agreed-next-session-proposal--2026-10-14) with “all agree”. That proposal is now the agreed worked example for translating these observations into practice choices; preserve its scope and shared-exercise structure when developing the learner records and selection behavior. The acceptance is product feedback on the specified choices, not validation of the whole learner model or a retention result.

The [next-session prototype](spikes/next-session.html) now executes those choices from supplied chat assessments. Its [replay notes](spikes/next-session-notes.md) distinguish real excerpts from hypothetical later outcomes and show how the plan changes for a local error, uncertainty or missing observations. It demonstrates the record-to-choice boundary; interpretation of unseen answers and ordinary long-term scheduling remain outside the executable example.

The [answer-intake continuation](spikes/answer-intake/README.md) connects the preceding assessment boundary: exact prompt, answer, context and scoped assistance travel with each judgment. It reuses the original validator, then sends only demonstrated/error observations to the planner. Missing evidence and uncertainty in grading stay in the assessment, with any proposed clarification separate. The chat remains the semantic assessor; automated checks establish record integrity and planning behavior, not reliable interpretation of unseen answers. The version-2 protocol incorporates the misread feedback without changing the historical protocol or claiming independent validation.

## 10. Research basis and remaining verification

Evidence-centered assessment design separates extracting evidence from a particular work product from accumulating beliefs about learner capabilities. That supports keeping the original answer, criterion observation, and diagnosis distinct. This is a design application of the framework, not validation of our grader. [Mislevy, Almond, and Lukas, 2004, pp. 9–11](https://cresst.org/wp-content/uploads/R632.pdf).

Knowledge-space assessment models allow response errors and guesses while updating possible knowledge states across questions. This supports treating one result as uncertain evidence. We have not selected or fitted a knowledge-space model, and the authors' assessment lengths are not a target for our short repair loop. [Doignon and Falmagne, sections 9–10](https://arxiv.org/html/1511.06757).

Research on procedural knowledge assessment also considers solution paths. Its experiments include simulations and a simulation based on existing Tower of London task data. That makes it a relevant alternative for later investigation; it does not establish accurate diagnosis of our prose answers or improved retention. [Algorithms for the adaptive assessment of procedural knowledge and skills](https://link.springer.com/article/10.3758/s13428-022-01998-y).

These sources were checked on 2026-10-13. The design also preserves the [conversation retrieval](research/conversation-retrieval.md), especially L19–L29 and the original halving example: response-specific evidence, successful attempts with local weaknesses, uncertainty, competing knowledge states, and diagnosis distinct from reinforcement.

The historical-annotation comparison provides a limited independent reference for observations, with disputed interpretations and no human teaching-action judgments. The next empirical check remains actual attempts in contrasting subjects with independent assessment of both observations and proposed follow-ups. Record assessor disagreement, unsupported failure labels, follow-up count/time, unnecessary practice, and performance on fresh larger exercises separately. Later retention is a separate outcome. The constructed cases establish what the proposed rules require; neither they nor annotation agreement establish assessment accuracy or useful learning gains. Acceptance thresholds remain in the evaluation decision.
