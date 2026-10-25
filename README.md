# Muninn

A local web app for memorization-oriented learning: paste material, get a source-linked outline and exercises, answer in your own words, and get criterion-by-criterion feedback that separates independent, helped and unsettled evidence. When an answer shows a gap, the app asks a question only if its answer changes the help, teaches the supported gap, and checks it with a fresh version of the task. Built from the design in this repository; start with [START-HERE.md](START-HERE.md).

**Status:** build slice 4 of 5 ([one saved learning encounter](.scratch/first-build/issues/01-one-saved-learning-encounter.md), [diagnose and repair](.scratch/first-build/issues/02-diagnose-and-repair.md), [corrections](.scratch/first-build/issues/03-correct-knowledge-and-judgments.md), [later checks and time budgets](.scratch/first-build/issues/04-return-later-and-fit-practice-into-time.md)). Later checks follow real due dates: recall items are scheduled by FSRS (py-fsrs 6.3.2) from your own ratings, other goals by a simple 24-hour-then-7-day policy; sessions fit due work into the time you choose. Qualification on fresh material comes in slice 5.

## Run it

Needs [uv](https://docs.astral.sh/uv/) and an Anthropic API key. Drafting, assessment and authoring of teaching and fresh questions send your source text and answers to the Anthropic API (`claude-opus-5-5`); everything else stays in a local SQLite file under `data/`.

```sh
export ANTHROPIC_API_KEY=...
uv run python -m muninn            # http://127.0.0.1:8770
```

```sh
bin/lint                           # ruff (all rules), format, mypy --strict, pyright strict
uv run pytest                      # real SQLite store, scripted model
uv run python -m tests.dev_server  # UI check with a scripted model, no key needed (port 8766)
curl -X POST 'http://127.0.0.1:8766/dev/clock?hours=25'  # move the UI check's clock past a due time
```

Export and restore live on the home page. A restore always goes into a new store file; the previous one stays in `data/`.

---

## Design: general memorization-oriented learning

The design investigation below predates the application and remains the reference for the later build slices.

The product scope is a general system for retaining facts, relationships, connected structures, and procedures across subjects. Kubernetes appears in the existing spike as one procedural example; it does not define the product scope or first release.

- [First usable version: build order and acceptance checks](.scratch/skill-maintenance/first-build-plan.md) — a real path from new material to practice, specific diagnosis, saved history and later review; proposed, not implemented.
- [Proposed system and validation plan](.scratch/skill-maintenance/spec.md)
- [Wayfinder decision map](.scratch/skill-maintenance/map.md)
- [Original conversation: insight coverage and corrections](.scratch/skill-maintenance/research/provenance.md#conversation-coverage-audit)
- [Comprehensive conversation retrieval, examples, and research leads](.scratch/skill-maintenance/research/conversation-retrieval.md)
- [How learner answers lead to targeted practice](.scratch/skill-maintenance/diagnosis-design.md) — proposed assessment rules, concrete answer branches, and cases that should remain uncertain.
- [Answer-assessment trial](.scratch/skill-maintenance/spikes/assessment-trial/review.html) — review ten saved AI assessments, record your own judgment before revealing the AI's, or prepare a new answer for assessment in this chat. [Run details and limits](.scratch/skill-maintenance/spikes/assessment-trial/README.md).
- [Interactive diagnosis prototype: binary search and English grammar](.scratch/skill-maintenance/spikes/diagnosis-prototype.html) — open directly in a browser; try “A missing connection” and “Revise the diagnosis.”
- [Diagnosis model, walkthroughs, and verification notes](.scratch/skill-maintenance/spikes/diagnosis-notes.md)
- [Interactive evidence spike](.scratch/skill-maintenance/spikes/evidence-policy.html) — download/open the HTML file in a browser; no installation or server needed.
- [Spike findings and reproduction](.scratch/skill-maintenance/spikes/README.md)
- [Working domain vocabulary](CONTEXT.md)

The research investigates existing implementations, learning evidence, and the boundary between FSRS and capability assessment. The local decision tickets distinguish resolved research from choices that still need the user's judgment.

Run the earlier evidence-policy replay with:

```sh
node .scratch/skill-maintenance/spikes/replay.mjs
```

No real learner study or Kubernetes lab has been run. The design must earn its complexity against an observed baseline.
