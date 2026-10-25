# Live learner trial

Started 2026-10-13. Status: first live attempt complete; learner-reported misread consistent with the response and correction, no knowledge gap identified. This is a chat-assisted trial, with no background job or new application. It supports the still-open [validation decision](../../issues/05-pilot-outcome.md).

## Question and conditions

Can an actual larger answer support a specific practice choice, and does a fresh larger answer after that practice show the targeted knowledge? If no gap is observed, stop without forcing remedial practice.

The user authorized starting the trial with “go”. Binary search is a provisional first example drawn from the existing work, not a restriction on the general product or a confirmed choice of every validation subject. The user is the learner for this round. Codex is the assessor and tutor, not an independent evaluator.

The conversation has already discussed binary search, repeated halving, logarithms, and example solutions. Record that prior exposure. Ask for the learner's current understanding without looking up an answer, but do not assert they complied unless they say so. This attempt cannot establish pre-teaching ability. Chat timestamps are not measurements of active learner effort.

## First larger exercise — L01

Exact prompt to present:

> You have an alphabetically sorted list of 1,024 different names and want to find “Mira”. You can inspect any entry, one at a time.
>
> 1. How would you search efficiently? Describe how you choose an entry and decide where to look next.
> 2. Why is it safe to rule out the other entries?
> 3. If the list grows to 65,536 names, roughly how many more inspections would you need in the worst case, and why?

Ask for a few sentences in the learner's own words. “I don't know” is acceptable; do not encourage deliberate mistakes or a fictional learner response. Show no solution before this answer.

## Assessment prepared before the answer

Use the [existing evidence rules](assessor-prompt.md), accepting equivalent language. Keep observations tied to exact response spans. Do not require the term “logarithm” or code.

| Target | Evidence sufficient for this task |
|---|---|
| Search procedure | Inspect near the middle of the remaining range, stop on equality, otherwise repeat in the remaining possible range. An omitted equality case is not automatically an error. |
| Safe elimination | Use alphabetical comparison to select the correct side and explain why ordering rules out the discarded entries. |
| Growth estimate | About six additional inspections when the list grows by a factor of 64. Accept consistent exact bounds or reasonable approximate counts. |
| Connection | Explain how repeatedly reducing the possible range by about half makes each doubling add about one inspection, or give equivalent reasoning. A memorized complexity label alone does not explain the connection. |

The prompt asks for an approximation. Ideal-halving estimates of about 10 versus 16 and consistent binary-search worst-case bounds of 11 versus 17 are both acceptable here. Do not manufacture an off-by-one error. An alternative efficient algorithm needs assessment against the stated access and data assumptions before assigning any failure label.

## Continue only from the real answer

1. Preserve the exact answer and any help the learner reports. For each relevant target, record demonstrated, error, not shown, or cannot judge, with evidence and unresolved alternatives. Explain the salient finding to the learner in plain language.
2. If the evidence already supports a useful practice target, go directly to focused practice. Otherwise ask one short follow-up at a time, only when its correct, wrong, and unclear branches change the next action. Write those branches before asking. At most three diagnostic or clarification prompts per larger attempt; stop earlier when a target is clear.
3. Give one focused explanation and retrieval opportunity for a supported gap. If diagnosis remains uncertain, label any worked example as support under uncertainty. Keep other observed gaps and correct components intact.
4. After help, give a different larger task that requires the targeted knowledge without supplying its solution. Do not reveal that task before it is needed. A separate focused check can be skipped when the new larger answer directly shows the target. Record recent teaching even when no hints accompany the new task.
5. Compare evidence before and after. If the new task still fails, preserve the result and reconsider the target; do not claim the gap was repaired or loop indefinitely. If the initial answer already supports every target, end immediate diagnosis; this trial then supplies no evidence about remedial benefit.

Record follow-up count, help supplied, diagnosis revisions, and performance on the fresh larger task separately. Immediate improvement is an observation, not proof that this method caused learning or saves review time. Delayed retention needs a later attempt; no reminder or delayed run has been scheduled. Independent assessment and contrasting subjects remain outside this first attempt.

## Attempt log

- L01 prompt: presented in chat as written above.
- Learner response: received verbatim below.
- Assessment: search procedure, safe elimination, and halving-to-logarithm connection demonstrated in the larger answer; comparison demonstrated in the follow-up. The learner reports a misread, consistent with both responses. No knowledge gap identified.
- Final action: stop immediate diagnosis. One comparison follow-up was asked; user feedback identifies it as unnecessary for this minor mismatch.
- Practice and fresh larger check: skipped because no remedial need was established.
- Delayed check and learning benefit: unmeasured.

### L01 response — original text

```text
1. begin with the one in the middle, and there could be 3 possibilities: i. we found "Mira"; ii. the name is alphabetically smaller than "Mira", then we truncate everything before and the name from the list, and repeat the process; iii. the name is alphabetically greater than "Mira", then we truncate everything after and the name from the list, and repeat the process. \
   2\. the truncation is safe because the list is sorted. if the current name is smaller/greater than "Mira", then it must be true that every before/after is also smaller/greater than "Mira"\
   3\. log2(65,536). At every round, we discard half of the list. in the worst case, we have to keep halving the list until there is one name left. So the question is: how many times we have divided the number by two until the result is 1? And by definition that's log2(n)
```

### L01 assessment — Codex judgment

| Target | Observation | Exact evidence and interpretation |
|---|---|---|
| Search procedure | Demonstrated | “begin with the one in the middle” and “i. we found "Mira"” identify selection and equality. The two subsequent cases correctly discard the inspected entry and the impossible side, then repeat. |
| Safe elimination | Demonstrated | “the truncation is safe because the list is sorted” is followed by “every before/after is also smaller/greater than "Mira"”, which explains the ordering relationship rather than merely naming sortedness. |
| Growth estimate | Not shown | No evidence quote is assigned to this observation. The answer supplies the expression for the larger list, but does not state the extra inspections relative to 1,024. This is an omitted comparison, not an observed calculation error. |
| Connection | Demonstrated | “how many times we have divided the number by two until the result is 1? And by definition that's log2(n)” connects the halving count to the logarithm, together with “At every round, we discard half of the list.” Equivalent verbal reasoning meets the criterion; an equation derivation is unnecessary. |

Accept the ideal-halving approximation under the prepared rubric; do not introduce an off-by-one failure. The user has not reported whether they used outside help. Earlier conversation exposure remains recorded, so these observations are not an independent baseline before teaching. No human assessor has independently scored this response.

### L01-F1 — comparison follow-up

Exact question to present:

> Using your reasoning, how many more inspections would the 65,536-name list need than the 1,024-name list?

Purpose: complete the requested comparison without repeating supported prerequisites. No numeric solution, logarithm values, or subtraction formula is supplied before the response. The accompanying feedback confirms the three supported targets and identifies the omitted comparison; this cues the follow-up.

Branches prepared before asking:

- Correct: record the comparison as demonstrated after a focused prompt and stop immediate diagnosis. No observed gap requires reinforcement, and no remedial benefit can be measured from this path.
- Wrong: preserve the error exactly. If the shown working identifies an error in evaluating powers/logarithms or comparing counts, practice that operation; otherwise ask for the two counts to distinguish those possibilities. Preserve the earlier correct reasoning.
- Unclear or unavailable: ask one simpler question to establish which part of the calculation is unavailable. If it remains unclear at the three-prompt limit, retain uncertainty and offer a worked calculation without claiming an exact diagnosis.

### L01-F1 response and design feedback — original text

```text
log2(65,536) - log2(1,024). I misread the question. This is a good case to show you where you should tell that it is just a trivial misread and not a real knowledge gap
```

The expression `log2(65,536) - log2(1,024)` correctly gives the requested increase; it evaluates to six. The learner supplied the expression, not its numeric evaluation. Accept the mathematically equivalent expression without another arithmetic prompt. The report “I misread the question” fits the original correct reasoning and this correction. Record a task-reading issue, with no diagnosed knowledge gap and no need for focused reinforcement.

The initial assessment preserved correct knowledge and did not label the omission as an error. However, the additional completion check was too literal for the learning goal. Before this follow-up, the better response would have been: “Your reasoning is correct. It looks like you answered the total rather than the increase; the difference is 16 − 10 = 6 extra inspections.” If that correction had been supplied, record it as feedback, not as an independently demonstrated subtraction. This alternative response is a design revision, not a rewrite of what happened.

This case updates the [diagnosis rules](../../diagnosis-design.md): distinguish answer completeness from practice need; use the surrounding reasoning to recognize likely misreads; do not ask merely to fill every rubric cell. Preserve explicit contrary evidence when there is a substantive error. One live example does not establish a general diagnostic accuracy rate.

Diagnostic/clarification prompts actually asked: 1. Focused remedial exercises: 0. This attempt demonstrates the no-remediation path and supplies interaction feedback; it does not test successful repair of a knowledge gap or later retention. No exercise duration is inferred from chat timestamps.
