# Answer-assessment trial

This trial records AI judgments of written answers and supports a separate human review. The AI assessor is Codex in the current chat. The page does not run a model: it shows saved assessments and prepares requests for new ones. There is no API service, server, installation, network request, or learner-memory update.

## Review the results

Open [the standalone review page](review.html). Your role is **reviewer**, not learner:

1. Read the exercise and the example learner's answer.
2. Record what the answer shows for each criterion, and what you would ask or teach next.
3. Click **Save my review and reveal the AI** to compare. Download your reviews before closing the page.

**Show AI without reviewing** is available for inspection. Any subsequent human judgment for that case is marked as made after reveal. The page freezes submitted reviews. Its ordering is a convenience for independent review, not proof of reviewer identity or lack of exposure elsewhere. No human reference answers have been invented or prefilled.

To use a new answer, expand **Assess a new answer through this chat**, enter the answer and any help supplied, and download its request. Attach that request in this chat. Import the returned `{input, assessment}` record to review it. The request includes the criteria and assessment instructions. Editing the answer or help invalidates the pending request; importing an assessment for a different input is rejected.

## What was run

[Inputs](inputs.json) contain ten constructed responses across binary search and grammar. The same assistant authored and assessed them; this is a development batch, not real learner data or a held-out benchmark. The [assessor instructions](assessor-prompt.md) and exact packets were read in the current chat, and the resulting semantic judgments were saved in [model-output.json](model-output.json). This is chat-assisted assessment, not an independently invoked grading API.

| Case | AI's proposed next step |
|---|---|
| A01 | Stop immediate diagnosis after a coherent explanation |
| A02 | Ask for the omitted halving-to-logarithm connection |
| A03 | Practice the ordering condition; preserve the separate step-count error |
| A04 | Check a fresh example because the derivation was supplied before the answer |
| A05 | Request an on-task answer; ignore instructions embedded in learner text |
| B01 | Ask which things are missing before choosing subject or verb-form practice |
| B02 | Ask why the correct word was chosen; do not treat an omitted reason as failure |
| B03 | Stop diagnosis on the requested targets; do not penalize unrelated awkward wording |
| B04 | Practice the explicitly reversed verb-form rule; retain correct subject identification |
| B05 | Clarify the empty submission without recording a knowledge failure |

These are the AI's judgments, not validated expected answers. In particular, B01's attribution of the controlling noun and A03's interpretation of the elimination step warrant human scrutiny. Accurate quotation is insufficient to establish sound interpretation.

The user was asked for a human next-step judgment on B01 after its AI assessment was saved and before that assessment was disclosed in the question. They did not supply a separate next-step answer before discussing the AI judgment. On 2026-10-13, after explanations of the reviewer role, assessment choices, and grammar criterion, they said: “done the review. i think you judgement makes sense”. This supports the design direction qualitatively. The message does not specify cases or individual ratings, and no exported reviews were received. Structured human comparison is **pending**, and grading accuracy is **not measured**. The original run metadata retains zero structured comparisons; do not convert this feedback or synthetic probes into review scores.

## Reproduce and inspect

From the repository root, using Node.js 26 as verified in this workspace:

```sh
node .scratch/skill-maintenance/spikes/assessment-trial/trial.mjs packet B01
node .scratch/skill-maintenance/spikes/assessment-trial/trial.mjs build
node .scratch/skill-maintenance/spikes/assessment-trial/probe.mjs
node .scratch/skill-maintenance/spikes/assessment-trial/trial.mjs compare /absolute/path/to/human-reviews.json
```

`packet` prepares the exact input and instructions; it does not invoke a model. `build` checks the saved batch and creates [bound records](assessed.json), the standalone page, and [run metadata](run-report.json). The input-file hash must match the one recorded with the AI output. Changed inputs require reassessment; rebuilding does not silently attach old judgments to new answers.

`compare` checks that human and AI judgments concern identical inputs, then reports differences in criteria, action and target selection. Agreement is not accuracy. Different useful follow-ups can reasonably produce different labels; inspect their reasons. The report does not choose a winner or average these dimensions into a score.

The [source shell](review-shell.html) is a build input; open `review.html` for the self-contained artifact. The pure validation/comparison functions in `trial.mjs` are embedded in the generated page. Nothing is persisted by the browser unless the user downloads it.

## Verification and limits

[Fourteen structural probes](verification.json) passed: real-record validation, invented-quote rejection, missing/duplicate criteria, unsupported remedial practice, identical follow-up branches, stale answers/help/prompts/rubrics, comparison arithmetic, incomplete human reviews, reveal-order flags, and the exact model embedded in the generated page. Synthetic review objects were kept inside the probe and never entered the assessment batch or human-review count.

[Two additional CLI checks](cli-verification.json) passed: modified input is rejected before saved judgments can be rebound, and an empty human-review file reports zero comparisons with unknown accuracy. The first check exposed a silent no-op when Node ran through a macOS path alias. Using Node's main-module detection fixed it, and the same path-alias check then exercised the intended rejection.

Generated JavaScript compiled, HTML static IDs were unique, and the page references no external assets. The user reports completing the review; browser layout and file-download/import interactions have **not** been directly verified with tools. The clarification needed during review is usability feedback to carry forward. An earlier browser tool restriction on local files remains respected; no alternative browser route was used.

This first trial covers one answer at a time. It does not yet run a full conversational diagnosis loop, integrate with the earlier scheduler prototype, assess retention, or establish reliable autonomous grading. Structured human judgments and actual learner attempts are still needed for the comparison proposed in the [diagnosis design](../../diagnosis-design.md).

Local source snapshot: `codex/prototype/answer-assessment`.
