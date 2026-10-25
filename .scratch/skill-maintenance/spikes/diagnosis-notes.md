# Can a larger exercise lead to specific, revisable reinforcement across subjects?

Status: the user confirmed the overall sequence. The broader design decision remains open. The subsequent [answer-to-practice draft](../diagnosis-design.md) specifies how response evidence could select follow-ups; that assessment step is not implemented in this HTML prototype.

Open [Find the gap](diagnosis-prototype.html) directly in a browser. It is one self-contained HTML file with in-memory state, curated prompts, feedback, a readable evidence panel, free play, and nine guided walkthroughs. Nothing needs installation or a server. The prototype addresses the user's approved next step after the [comprehensive conversation retrieval](../research/conversation-retrieval.md).

## Start here

1. Select **A missing connection** and press its steps. Watch the relationship receive reinforcement while the other observed components stay supported.
2. Select **Revise the diagnosis**. A focused check passes, then the next larger exercise exposes a different gap. Watch the next repair change.
3. Switch to **English grammar** and repeat either case. The content changes; the decision rules do not.
4. Try **Uncertain: stop probing**. Three different inconclusive probes reach the explicit diagnosis limit. No component is declared failed from the overall result alone.
5. To answer freely, type your response in the exercise panel, compare it with the worked answer, and record what your original answer demonstrated. The next exercise is selected from those rubric judgments.

The free-play controls also allow changing the planning budget, changing the diagnosis limit, undoing a response, restarting, and simulating seven days passing after a fully demonstrated larger answer. Switching topics resets the session.

## Two small topic models

The model distinguishes components, a relationship, selecting an applicable pattern, and integration. Six assessable targets per topic are enough to expose the question without creating a full curriculum.

| Target | Binary search | English grammar |
|---|---|---|
| Condition/component | Explain the ordered-search condition | Identify the subject head |
| Procedure/component | Eliminate the correct half | Identify subject number |
| Principle/component | Interpret powers of two and logarithms | Recall singular/plural verb forms |
| Relationship | Connect halving to logarithmic growth | Connect the subject head to its verb |
| Selection | Choose where midpoint elimination applies | Choose do/does plus a base verb for a yes/no question |
| Integration | Combine conditions, elimination, and derivation | Produce and explain agreement and question forms together |

Each component has a criterion, two focused prompts, worked answers, and a feedback explanation. Five larger variants per subject elicit the combined targets. Typed relationships explain the content; they never assign automatic evidence. The two variants of a focused prompt and the five larger variants share solution patterns. They are not independent evidence of far transfer. Reused focused prompts are labeled; after all five larger variants are used, the model requests new content instead of calling a repetition unseen.

The content is deliberately bounded. Binary-search counts refer to an ideal halving model, not the exact comparison count of a particular implementation. Grammar uses standard written English, ordinary subject number, simple-present forms, and do/does questions; it does not cover collective nouns or dialect variation.

## What the model records and chooses

An attempt retains its topic, prompt, criteria, pre-feedback response, rubric judgments, overall result, assistance, source, simulated day, estimated cost, and selection reason. A criterion can be demonstrated, incorrect/unavailable, uncertain, or not observed. The latest observation is shown, while the full history remains inspectable.

There is no automatic natural-language grader. In free play, the learner judges the answer they supplied before viewing feedback. Guided cases inject explicitly authored evidence records; their response text describes the scenario action rather than claiming to be an independently graded learner transcript. No real learning process or hidden ground-truth ability is simulated.

The policy chooses in this order:

1. Start with a larger exercise.
2. Pause if rubric judgments and the overall result conflict.
3. Repair a directly observed component gap, preserving other gaps.
4. After feedback, ask for an independent focused check. Assistance does not close the gap.
5. After focused repair, return to a different larger example. A new component failure redirects practice.
6. With no localized gap, probe an unresolved component not already probed after this larger attempt. The fixed order is parts, relationship, then selection. It is inspectable but not an optimal information-gain calculation.
7. If component checks pass and integration explicitly fails, practice integration. If integration is merely unobserved or uncertain, check it before assuming it needs repair.
8. Stop at the diagnosis/time limit, repeated failed repairs, or exhausted content. Preserve uncertainty.
9. After a larger independent answer meets every criterion and the overall result, stop separate prompts for this session and reserve a later integrated check.

An earlier pass does not settle a later contradiction. A new larger attempt can leave earlier component evidence insufficient for explaining its result. The prototype then gathers current evidence instead of silently converting the whole failure into prerequisite failures.

## Replayed behavior

Run the experiment driver with Node.js:

```sh
node .scratch/skill-maintenance/spikes/diagnosis-replay.mjs
```

It loads the exact pure model from the HTML and executes the same authored steps as the walkthrough buttons. [Full traces and additional observations](diagnosis-replay-results.json) preserve the results.

| Walkthrough, repeated in both subjects | Observed behavior |
|---|---|
| One missing component | Probe → repair that component → independent check → integrated recheck |
| A missing connection | The same path targets the relationship, without repeating the supported components |
| Choosing the rule | A directly observed selection failure goes straight to focused reinforcement |
| Two gaps | Repair/check the first gap, then repair/check the second; only then recheck integration |
| Success hides a gap | Correct overall outcome does not suppress a needed relationship probe |
| Revise the diagnosis | After the relationship passes its check, a fresh larger failure redirects repair to another component |
| Uncertain: stop probing | Three distinct inconclusive probes stop; no exact cause is fabricated |
| Hints and later checks | Helped success requires independent integration; simulated delay creates a separate later check |
| The parts pass; the whole fails | Integration practice followed by a larger check; a slip remains an alternative explanation |

All 18 authored walkthroughs completed without an unexpected stop at the default budgets. Additional observations show that an insufficient budget pauses rather than substitutes an inadequate task; restoring budget permits the task; an unattributed failure creates no component observations; the pure transition leaves its input unchanged; contradictory overall/rubric grades pause; helped success does not mark the session's learning target demonstrated; and unobserved integration receives a check rather than automatic repair.

Both embedded JavaScript blocks passed syntax checks. HTML parsing found unique static element IDs and no external assets. Browser interaction and visual layout have **not** been verified. The browser tool previously rejected local-file preview in this conversation; no alternate browser route was used to bypass that restriction.

## What this makes concrete, and what it does not settle

The artifact implements distinct treatment of observed gaps, uncertainty, assisted practice, integration, and contradictory evidence. The replay establishes those authored transitions. It does not establish that a real learner can self-grade accurately, that the components are the right granularity, that the next question is maximally informative, or that reinforcement improves retention. Both topics deliberately fit the same six-target shape; broader representation flexibility remains untested.

Prototype constants are a three-question diagnosis limit, a twelve-minute planning budget, estimated costs of 120/30/45 seconds for larger/probe-or-check/feedback exercises, and a seven-day delayed-check interval. No actual elapsed study time, forgetting curve, calibrated uncertainty, transfer coefficient, or FSRS update is calculated. Two failed focused checks stop the available repair strategy; that threshold is also illustrative. The model cannot produce new content after its authored inventory is exhausted.

The useful next feedback is whether the selected question and reinforcement match the evidence in each case. Then the content mapping and assessment burden need a small real learner trial, with actual time and delayed retention measured separately. Representation, inference, selection, and prototype-acceptance decisions remain open.

Local source snapshot: `codex/prototype/diagnosis-loop`. This is experimental work, not a production module or completed product design.
