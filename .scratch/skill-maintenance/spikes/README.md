# Can the learner state avoid false credit while choosing affordable practice?

Status: artifact ready for user reaction; the prototype decision remains open.

Scope correction: the product is a general memorization-oriented learning system. This existing Kubernetes example explores procedural evidence only. Its mandatory execution rules are specific to that example and must not become defaults for every subject.

Open [the standalone HTML demo](evidence-policy.html). It has free-play actions, six guided walkthroughs, the full relevant evidence state, and a reason for the proposed next exercise. Everything is in memory. No network requests, actual learner assessment, FSRS implementation, LLM, or Kubernetes execution is involved.

The question is whether the *evidence boundaries and visible policy behavior* make sense. It is not whether the policy improves learning.

## What the spike compares

The intentionally unsafe comparator assigns the outcome of an exercise to all prerequisite capabilities and all their assessment modes. This is a deliberately constructed counterexample, **not** a reproduction of plcourse, Obsidian Learning Engine, Math Academy, or FSRS.

The proposed state records only the rubric observations supplied in the attempt, preserving whether help was used. It keeps task-level uncertainty when an ambiguous failure has not been explained. Replaying the same attempt cannot create a second observation.

Prerequisite links guide questions; they do not manufacture direct evidence. An instrumented multi-capability task can still compress reviews: the single observed scenario supplies four rubric observations without assuming that all six mode-specific capabilities were demonstrated. Those four observations share one attempt and are correlated.

## Reproduce

Requires Node.js; verified here with v26.0.0. No packages.

```sh
node .scratch/skill-maintenance/spikes/replay.mjs
```

The runner loads the exact pure model from the HTML, replays eight authored traces, prints the table, and writes [replay-results.json](replay-results.json). It is an experiment driver, not a production test suite.

| Authored trace | Unsupported pass claims from comparator | Unsupported failure attributions from comparator | What the proposal retains |
|---|---:|---:|---|
| Recognition only | 1 | 0 | Recognition observation; four operational requirements still open |
| Successful final state without trace | 6 | 0 | Outcome without capability attribution |
| Hinted lab | 6 | 0 | Assisted practice; no independent execution claim |
| Independent observed scenario | 2 | 0 | Four directly observed capabilities in one attempt |
| Ambiguous failed lab | 0 | 6 | An unresolved diagnostic question |
| Failed lab then failed recall probe | 0 | 5 | One direct recall weakness; remaining cause still unresolved |
| Duplicate observed scenario | 2 | 0 | Still one attempt and 180 illustrative seconds |
| Observed scenario then eight days | 0 | 0 | Four operational requirements need a fresh check |

“Unsupported” means the injected evidence does not establish the claim; it does **not** mean the learner actually lacks that skill. The proposal avoids these claims by construction. This is a contract demonstration, not independent evidence that the proposal predicts ability more accurately.

With a one-minute budget and missing execution evidence, the policy offers only optional preparation and explicitly leaves the longer task due. With the observed scenario complete and still recent, it stops rather than demanding separate recall evidence irrelevant to this illustrative operational objective.

## What the spike changed in the proposed design

1. Separate final outcome, assisted practice, and independent rubric evidence. A final-state checker alone is insufficient for attributing operational competence.
2. Keep assessment modes distinct initially; a correct recognition item cannot automatically retire explanation or execution work.
3. Give related observations a shared attempt identity. Duplicate delivery, graph diamonds, and multiple rubric rows must not look like independent successful reviews.
4. Model unresolved diagnosis explicitly. A narrow probe can reveal one weakness without explaining the entire task failure.
5. Make infeasible budgets visible. Do not replace the target behavior with a cheaper proxy and claim the requirement met.

These are proposed design constraints pending user reaction, not closed product decisions.

## Limits and verification

The 7-day freshness threshold, task durations, curriculum edges, required capability set, and supplied observations are illustrative constants. There is no learned forgetting or transfer model and no simulated learning process. A later hinted or failed attempt conservatively replaces the displayed latest observation; the full history remains visible. This is a simplification for discussion, not a final posterior estimator.

The executable model replay completed for all eight cases. Browser interaction and visual layout were not verified: the browser tool rejected the local `file:` URL under its URL policy. No alternate browser path was attempted. The file remains available for the user to open directly.

Separate from the illustrative model, [source-probe-results.txt](source-probe-results.txt) preserves independently rerun output from the actual pinned py-fsrs and Obsidian scheduler modules. Reproduction code and limitations are in [the memory-model report](../research/memory-model.md#reproduction-appendix) and [the implementation report](../research/existing-implementations.md#reproduce-the-four-obsidian-fixtures).

Questions for the eventual prototype review: should a hinted success revoke the display of an earlier independent result; what evidence is enough to defer a separate review; and how should the product help when required practice never fits the learner's usual session?
