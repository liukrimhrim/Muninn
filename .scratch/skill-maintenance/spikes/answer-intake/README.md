# Connecting answers to practice choices

Prepared 2026-10-14 on `codex/prototype/next-session-plan`. This is a throwaway continuation of the [evidence spike](../../issues/04-evidence-spike.md), not a deployed or independently validated grader.

Open [the standalone demo](index.html). It shows the prompt, original answer, context, help, assessment and resulting practice choice together. The buttons explore recorded answers and labelled invented contrasts. No further learner exercise is required to inspect it.

## Question and bounded result

Can an answer assessment reach the existing planner without losing its evidence, mistaking grading uncertainty for a knowledge gap, or treating helped work as independent performance?

The connected pipeline reproduces the three accepted next-session choices from ten recorded responses. It checks the assessment's binding to the input, retains the assessor and protocol identity, and carries only demonstrated/error observations into the learning ledger. The full assessment still contains omitted and ambiguous criteria. A targeted clarification now takes precedence over corrective practice for its targets without changing the knowledge observations; no question is automatically sent. Earlier hints remain in history. See the [clarification continuation](clarification-notes.md) and [walkthrough](clarification.html).

This settles that the two existing components can be joined with these boundaries. It does **not** establish that Codex correctly interprets arbitrary new answers. Codex made the semantic judgments in this chat; the local program validates and connects them. Exact quotations can still support a wrong interpretation. The seven contrast cases were also authored by this assessor, which had seen the earlier judgments of real responses. They are not independent or held-out grading evidence.

## What changed

The [version-2 assessment protocol](assessor-prompt-v2.md) includes the learner's misread feedback and the distinction between a vague answer and a demonstrated error. The original trial prompt and its outputs remain historical artifacts.

The [bridge](bridge.mjs) reuses `createTrial()` from the earlier assessment trial and `NextSession` from the existing planning HTML. The former checks all rubric criteria; the latter receives only actual observations. A short adapter preserves `not_shown` and `cannot_judge` in the attached record without promoting them to failures. This reconciles the different record shapes; it does not replace either component.

| Situation | Connected behavior |
|---|---|
| Corrected comparison fits prior halving reasoning | Preserve the supported misread; no extra remediation |
| One log-command error alongside correct listing and source selection | Offer help only for the log form |
| Source explanation omitted | Retain previous source evidence and its later check; no immediate compulsory question |
| Source wording cannot be interpreted | Plan its targeted clarification; create no target failure and preserve the later checks |
| Hint supplied only for locating the source | Preserve that help only on its target; correct commands remain separately observed |
| “I misread” accompanies an explicit wrong halving rule | Preserve the substantive error |
| Input, context, help, criteria or protocol changes | Reject reuse of the old judgment |
| Same answer ID arrives with a changed assessment | Reject silent replacement; explicit revision design remains open |

A supported-misread tag requires a correct current observation and exact quotations of prior learner context. This is a structural prerequisite, not a semantic proof of misreading. Stopping without that tag is still allowed when there is no observed gap. The protocol must not manufacture a follow-up merely to collect a correction or fill a rubric cell.

Assistance timing is supplied by the caller: `current` means help for this response, `earlier` preserves past teaching. The focused command response is explicitly helped, while later application preserves earlier teaching. Task context and simulated diagnostic output are not automatically hints. The caller also supplies attempt identity, provenance and session phase; the assessor cannot change those through its output. Completeness and truth of that caller-supplied history remain assumptions.

## Reproduce

From the repository root:

```sh
node .scratch/skill-maintenance/spikes/answer-intake/replay.mjs
```

This reads the frozen [inputs](inputs.json) and [chat judgments](judgments.json), connects the real components, writes [report.json](report.json), and builds the standalone HTML from [shell.html](shell.html). The page embeds those same functions; it has no service, server, database, network request or persistence.

**35/35 replay observations matched** after the clarification change (34 in the original run). These cover the accepted real plan, seven constructed contrasts, input and quote binding, target-scoped help, missing evidence, duplicate/conflicting records, and actual page handlers on a minimal DOM surface. The original **4/4 CLI checks** remain in [their historical results](cli-verification.json); the continuation adds [five current CLI and historical-report checks](clarification-cli-results.json). These use temporary constructed records, not additional learner assessments.

The earlier browser policy denial for local artifacts remains in effect. No alternate route was used. Rendering, layout and accessibility are unverified; the DOM wiring check is not a browser test. No delayed learner attempt, live Kubernetes command, learning gain, optimal review date, calibrated confidence or FSRS update was measured.

## A new answer through the same boundary

For this bounded spike, save one packet with the same shape as an entry in `inputs.json`: a new case ID, attempt metadata, exact prompt, selected criteria mapped to the six example targets, response, visible context and target-scoped help. Source excerpts and summaries must be labelled accurately. This does not yet create arbitrary curricula or infer targets.

```sh
node .scratch/skill-maintenance/spikes/answer-intake/replay.mjs packet /absolute/path/answer.json
```

The output supplies instructions and hashes. Codex or another explicitly identified assessor reads that packet and supplies a new judgment file in the documented shape. There is no automatic model-service call. Then:

```sh
node .scratch/skill-maintenance/spikes/answer-intake/replay.mjs connect /absolute/path/answer.json /absolute/path/judgment.json
```

This prints the evidence record and resulting plan against the ten-response example history. It saves no learner-state changes. It rejects judgments for changed input/protocol bytes and preserves the earlier history. Subsequent answers are not automatically accumulated across CLI invocations; a persistent tutoring workflow is outside this spike.

## Next unresolved question

The weakest remaining link is semantic assessment: would an assessor reach defensible component-level conclusions on unseen real answers, including shorthand, ambiguity and unfamiliar but correct reasoning? An independent review should judge original packets before seeing the AI proposals, then inspect disagreements about both observations and resulting practice. Use the existing human-comparison machinery where applicable. At the end of this intake spike there were zero independent comparisons; that was not an accuracy score.

A subsequent [blinded comparison with historical human annotations](../independent-assessment/review.md) supplies 36 comparable judgments: 23 matches, 10 disagreements and three abstentions, with 12 other facets excluded. Its records are separate from this spike's historical reports. It exposed conflicting clarification and help proposals; the [clarification continuation](clarification-notes.md) now resolves that conflict for the affected targets. The corpus has no human judgments of teaching actions; no fresh human reviewer, semantic accuracy claim or learning benefit is supplied.

The user has already accepted the three next-session choices. Do not ask for that approval again. General representation, indirect inference, exercise selection, revised-assessment handling, validation criteria and learning benefit remain open on the map. These contrasts and the version-2 protocol are proposed behavior, not additional user-approved decisions.

The subsequent [representation continuation](../representation/README.md) adds optional version-bound capability coverage to this same bridge and planner. Its new examples separate rubric criteria from learning targets and practice bundles from semantic groups. Legacy packets and these recorded judgments retain their original contracts; no historical grades are split.
