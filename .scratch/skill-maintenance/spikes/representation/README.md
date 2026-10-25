# Different gaps, one useful exercise

Prepared 2026-10-14 on `codex/prototype/next-session-plan`. This implements the bounded path proposed in the [representation design](../../representation-design.md), using the existing validator, answer bridge, and planner.

Open [the standalone walkthrough](index.html). Select Operations, Mathematics, or One fact, then press the guided sample-answer buttons. The page shows the resulting practice choice, evidence for each target, original criterion judgments, and full retained records. Free-play buttons explore ambiguity, partial evidence, hints, and an alternate solution. **You are inspecting decisions; you do not need to answer the exercises.**

All new responses and assessments are authored examples. The ten previously recorded learner responses keep their old contracts and judgments. This is a throwaway behavior experiment, not an automatic grader or evidence of retained learning.

## What now works

| Example | Executable behavior |
|---|---|
| Selects useful logs but writes the wrong subcommand | Help targets command production; useful evidence selection remains separately observed |
| Writes the command but rejects logs as useful evidence | Help targets evidence selection |
| Shows only part of a required command | Keep the partial criterion evidence; emit neither a complete capability success nor an invented error |
| Knows the mathematical parts but combines them incorrectly | Help targets the connection between branching, depth, and total work |
| Demonstrates the mathematical parts in a later answer without their combination | Preserve the unresolved integration need |
| Receives a hint about a criterion used by two capabilities | Qualify both dependent observations; leave unrelated evidence independent |
| Succeeds through an alternative path | Preserve the demonstrated result and leave bypassed targets unobserved |
| A criterion's meaning needs clarification | Map the question to the affected capability and clarify before corrective practice |
| Several pending targets fit one exercise | Keep one combined check; overlapping bundles do not duplicate a target in the plan |
| Changes a capability definition | Reject reuse of an old bound assessment; direct planning also detects incompatible retained evidence |
| Recalls one supplied fact | Use one capability and criterion without requiring integration or an explanation chain |

The mathematical example also includes a fluent-recall capability in the catalog, outside the selected goal. Successful reconstruction does not silently select or demonstrate it. The vocabulary association is explicitly invented, so it supplies no unsupported claim about a real language.

## Small implementation boundary

`createTrial()` still validates exact input binding, one assessment per rubric criterion, evidence quotations, and proposed next actions. `createBridge()` now accepts optional explicit `exercise.coverage`:

```js
{
  target: "ops.produceLogs",
  contract: /* exact current capability contract snapshot */,
  criteria: ["verb", "address"]
}
```

The contract contains a version, versioned content references, action, assessment mode, and conditions. The exercise and rubric also have versions. The saved assessment binds to the full input, including coverage and contract wording; comparing against the current contract catches changes even when an author forgets to increment its version. The goal explicitly selects capabilities from the example catalog.

For this slice, **every mapped criterion is required**. All must be demonstrated for a complete capability observation. An observed error is sufficient evidence of an error in that capability; otherwise unresolved interpretation or absent evidence prevents a complete observation. Partial and ambiguous rows remain in the original assessment. A targeted clarification controls the immediate action without erasing an observed error. Criteria that describe acceptable alternatives should express that in their rubric; this experiment does not introduce a general logic language for combining criteria.

There is at most one derived observation for each capability in an assessed answer. Evidence references include the answer, attempt, exercise/version, rubric/version, and criterion. Reusing a criterion across capabilities retains the same reference; separate answers within an attempt remain distinguishable. These are evidence links, not independent successes, strength increments, or FSRS reviews.

For explicit coverage, assistance identifies affected **criterion IDs**, then follows the coverage mapping to capabilities. The caller must list all affected criteria; the prototype does not infer hidden hint dependencies. Earlier help remains context, while current help qualifies the resulting demonstration.

The raw assessment is preserved in `assessmentRecord`; a separate `planningAssessment` projects criterion judgments and clarification targets onto capabilities. Explicit events are copied on intake so subsequent edits to a caller's packet cannot change retained evidence. Contract checks include unresolved projections that emitted no knowledge observations. A contract change requiring old evidence to be reconsidered is blocked for review; no migration or historical regrading mechanism is implemented.

`NextSession` accepts explicit `practiceBundles` independently of descriptive `knowledgeGroups`. It visits bundles in their authored order and schedules each pending target once. This is a transparent demonstration policy, not an optimized coverage algorithm. The existing output field `group` identifies the chosen practice bundle. Semantic group membership never creates evidence or a practice update.

Legacy packets without explicit coverage keep the original one-criterion/one-target behavior. The accepted next-session plan still consists of one later operations exercise, with no extra remediation for the supported binary-search misread. The older standalone pages are rebuilt from the same updated functions so their behavior matches the current code.

## Reproduce and verification

From the repository root:

```sh
node .scratch/skill-maintenance/spikes/representation/replay.mjs
node .scratch/skill-maintenance/spikes/answer-intake/replay.mjs
node .scratch/skill-maintenance/spikes/answer-intake/clarification-replay.mjs
node .scratch/skill-maintenance/spikes/replay-next-session.mjs
node .scratch/skill-maintenance/spikes/answer-intake/verify-clarification-cli.mjs
```

The first command builds the self-contained page and writes [report.json](report.json). It runs the real validator → bridge → planner path, and the actual page handlers on a minimal DOM surface. No framework, model service, server, database, or network request is required.

- Initial reproduction against the code at `68dfaf6`: **8/33 checks passed**, preserved in [before.json](before.json). The rejection checks could already pass because the old bridge rejected all new mappings; positive acceptance cases exposed the limitation. Do not interpret those eight passes as support for the new model.
- Current representation replay: **40/40**. During the implementation review, three additional checks first failed: retained packet mutation, unresolved contract drift, and answer identity within an attempt. Those boundaries were then corrected and the checks passed.
- Existing behavior: **35/35** answer-intake checks, **22/22** clarification checks, **22/22** prior-planner checks, and **5/5** CLI/historical-report checks. The frozen independent-assessment artifacts and audited comparison remain unchanged.

These 124 checks are program-behavior observations, not independent judgments of semantic accuracy. The new scenarios are deliberately constructed by the same assistant implementing the policy. The original source-bound learner cases provide regression coverage, not newly collected outcomes.

Browser rendering and accessibility remain unverified. The earlier local-artifact browser denial was not bypassed; the DOM checks do not replace browser inspection. The “later” examples use supplied phase labels, not measured elapsed time or demonstrated retention on unseen variants. No learning benefit, calibrated uncertainty, automatic target discovery, graph propagation, schedule optimization, or content-entry workflow was established.

The next useful validation is to apply these contracts to fresh learner answers and review disagreements about both diagnosis and the resulting practice. The representation question remains open to that evidence; no additional infrastructure is justified by this spike.
