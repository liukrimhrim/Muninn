# General memorization-oriented learning: research and design

This repository currently contains a design investigation, not a learning application.

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
