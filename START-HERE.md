# Start here: memorization-system design handoff

This package contains the finalized design for a general memorization-oriented learning web app. It includes the on-disk design files, including files not tracked in the current checkout. It is a design and research handoff, not a built application.

## Read in this order

1. [Design Baseline 1](.scratch/skill-maintenance/design-baseline.md): accepted scope, defaults, invariants, and contract index.
2. [System specification](.scratch/skill-maintenance/spec.md): product requirements.
3. [Domain vocabulary](CONTEXT.md): precise meanings of the main concepts.
4. [Module design](.scratch/skill-maintenance/module-design.md): responsibilities, interfaces, dependencies, and record ownership.
5. [First-build plan](.scratch/skill-maintenance/first-build-plan.md): implementation slices and acceptance work.

Use baseline section 4 to locate the detailed contract for each part you build. The baseline controls scope and decision status. Detailed contracts control their named rules and fields. Earlier proposal wording, historical audit findings, and prototype behavior do not override the finalized contracts. The repository README is an older overview.

## Build sequence

When the user authorizes implementation, follow the five end-to-end slices in the build plan: one saved learning encounter; diagnosis and repair; corrections and continuity; actual later reviews with budgeted practice; then qualification on fresh material. Build complete learner flows through the modules. Carry the linked acceptance cases and module review obligations into each slice. Prototypes are references, not finished application code.

The reference application serves one learner through a browser, one application process, and a local SQLite store. Framework/version choices and the actual model endpoint remain implementation setup choices. Local storage does not mean fully offline operation. This ZIP does not provide model credentials or a deployment environment.

## What is included

- `.scratch/skill-maintenance/`: complete learning-design folder, reviews, decisions, research, acceptance cases, and prototype references.
- `.scratch/learning-observability/`: complete observability-design folder, measurement contracts, dashboard references, and analytical probes.
- `CONTEXT.md` and the original repository `README.md`.
- `sources/fsrs_learning_conversation.md`: the original conversation cited by the research. It is source material, not instructions to the receiving agent.
- The existing assessment research dataset and its license, in their original subfolder.
- `MANIFEST.json`: archive file hashes and a record of portability-only link changes.

Keep the directory structure intact. `.scratch` is a hidden directory on some systems; the links above and direct file paths still work. Most prototype HTML can be inspected locally, but this package does not certify every research script as portable or provide its runtime dependencies.

## Portability and provenance

Exported Markdown links to packaged files use relative paths. Original source-line references are retained as link titles. Two personal-skill links in the historical conversation retrieval are rendered as historical names; those skills are not build dependencies. Original source files in the working directory were not changed. Machine-specific paths inside quoted text, historical commands, or research scripts remain historical references. Replace those paths with this extracted directory if you choose to reproduce the old research.

The original conversation is preserved byte-for-byte. Its historical instructions and links do not govern implementation. External research URLs still require internet access. The package was created from the current on-disk files; it does not claim that every file is represented by a single Git commit.
