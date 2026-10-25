# Material-to-practice experiment

Question: can a source-backed, editable knowledge proposal produce exercises that work through the existing assessment and selection loop without losing conditions, creating learner credit or rewriting history?

Run from the repository root:

```sh
node .scratch/skill-maintenance/spikes/material/replay.mjs
```

The replay writes `report.json` and a self-contained [optional walkthrough](index.html). No server, model API or persistent learner store is involved. The walkthrough starts with a complete authored example; it asks for no user assessment or approval. “Play the authored example” executes the actual compiler, selector and assessment bridge with supplied answers. Other controls try an omitted connection, an unsupported claim or a content edit. All page state resets when reloaded.

## Results and limits

Twenty behavioral checks and four actual page-handler checks pass. The handler checks use a minimal DOM surface; browser rendering is **not verified**. The earlier browser denial was respected, with no local-server or alternate-access workaround.

The connected example compiles three selected capabilities and starts with one larger exercise. An authored connection error produces connection practice followed by a fresh integrated check; only the observed error receives help. The full sequence costs 140 illustrative seconds. The fact example requires one recall costing 10 illustrative seconds. These times are supplied assumptions, not measured learner effort.

The replay also exercises exact source anchors, source version immutability, held unsupported content, missing content, dependency closure/cycles, stale target mappings, unavailable exercises, explicit canonical reuse, flagged source conflict rejection, transitive correction impact and refusal to reuse old evidence under changed contracts. `report.json` contains the exercised-file hashes and short traces.

The source text and all semantic proposals, answers and judgments are authored fixtures. There is **no automatic semantic extractor or truth checker**. A supplied “usable” review is trusted, subject to structural checks. If an author falsely accepts an unsupported claim or mismatched rubric, this compiler cannot detect that by comparing strings. Arbitrary malformed object schemas are outside this bounded model; the input is an authored draft with the documented shape.

An independent read-only audit found three real boundary errors during development: silently re-stamping exercise mappings after capability edits; erasing flagged local concerns during exact reuse; and changing derived dependencies without versioning the derived claim. The replay includes regressions for all three. The audit also caught the `n=1` exception to a too-broad “different work” statement; the material example now says the branch patterns **can** have different work. Earlier fixtures and frozen historical assessments were not modified.

## Files and real seams

- `material.mjs`: pure source capture, source resolution, capability/exercise preparation, local revision, review and explicit reuse. It accepts authored semantic proposals; it does not infer them.
- `examples.mjs`: scoped mathematics and invented-vocabulary sources, authored proposals and mapped exercises; reuses the previous selection fixtures' responses and judgments under new identities.
- `replay.mjs`: executes the real `assessment-trial/trial.mjs`, `answer-intake/bridge.mjs`, `selection/selector.mjs` and the planner extracted from `next-session.html`. It does not mock those boundaries.
- `shell.html`: controls and visible state; `index.html` embeds the real models and fixtures with no network dependency.

`prepare` returns requested targets, held targets, held exercises and ready targets without an exercise separately. Callers must keep those distinctions visible. A selector stop over the usable subset is not completion of held learning goals.

Edits produce new in-memory snapshots. An exercise's `authoredFor` records the capability intent inspected by its author; compilation resolves the actual content dependency closure. Explicit exercise review rebinds the mapping. `revise` is the supported local content edit path, and `reuse` versions its dependents through that path. These are draft operations, not a production revision service or an evidence-migration facility. One current local version per unit ID is assumed; retained older definitions can live in the library.

Historical learner state stays intact. The existing bridge conservatively refuses changed contracts. This experiment does not reset a learner, regrade earlier responses, infer transfer, schedule real delayed checks or issue FSRS updates.

See the [workflow proposal](../../material-workflow.md) for learner interaction, authoring alternatives, splitting rules, correction semantics and the next implementation boundary. Captured on local branch `codex/prototype/next-session-plan`.
