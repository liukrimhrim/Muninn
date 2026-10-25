# Sparse inference about untested knowledge

Research date: **2026-10-14**. Decision input for [learner inference](../issues/11-learner-inference.md), following [the earlier memory-model investigation](memory-model.md). This is a bounded primary-source review and proposed experiment, not a validated learner model. The learning goal is general memorization; the mathematical and operational examples are test cases, not the domain boundary.

**Recommendation:** retain the descriptive evidence ledger and run a tiny finite-state Bayesian calculation beside it. Compare an explicitly constrained state space with an unconstrained alternative, exposing assumptions and contradictions. Do not use the numerical output to skip reviews or update FSRS. The immediate question is whether structural assumptions produce useful, inspectable hypotheses about untested knowledge—not whether this small dataset can calibrate a general tutor.

## What the alternatives actually assume

| Alternative | What it adds | What must be supplied or justified |
|---|---|---|
| Descriptive ledger | Observed success/error, assistance, unresolved interpretation, context and date | Defensible assessment contracts and provenance; no probability calibration claimed |
| Constrained finite-state model | A distribution over feasible combinations of capabilities; observations can change estimates of untested capabilities | Allowed states, initial probabilities, response likelihoods, and conditions under which knowledge is treated as unchanged |
| Unconstrained finite-state model | All combinations remain possible; useful control for what the structural restriction contributes | The same observation model and explicit prior; without dependence or shared evidence, unrelated capabilities receive no update |
| Small conjunctive cognitive-diagnosis model | A task may require several latent attributes together | Task–attribute mapping, conjunction assumption, state probabilities, item error parameters, and evidence for estimating them |
| BKT / PFA | Models repeated performance across practice opportunities | The already-researched tagging, parameter-estimation and evaluation requirements; neither is automatic graph-wide reinforcement |

The first three rows describe proposed repo comparators. The last two are established model families, bounded below.

**Knowledge Space Theory (KST).** A knowledge structure specifies feasible subsets of a defined problem domain. A knowledge space is union-closed; a learning space adds conditions equivalent to well-gradedness. Pairwise prerequisite orders describe an intersection-closed special case, not every learning space. Probabilistic assessment introduces state probabilities and response-error assumptions. Construction can involve expert judgments, then refinement from assessment data; it is not just importing a semantic graph. The authors describe an adaptive assessment algorithm and large-domain projection methods. See Doignon and Falmagne, *Knowledge Spaces and Learning Spaces* (2015 preprint), §§3, 9–11, particularly pp. 9, 27–30 and 36–38. [Author paper](https://arxiv.org/pdf/1511.06757).

**Small Bayesian cognitive diagnosis.** Junker and Sijtsma's DINA model uses a task–attribute matrix and a noisy conjunction: success probability is `1 − slip` when all required attributes are present, otherwise `guess`. It assumes conditional independence of task responses given latent attributes. Monotonic interpretation requires `1 − slip ≥ guess`. The paper explicitly cautions that these error names need not identify literal guessing or carelessness: alternative strategies and other causes can generate the same observations. It examines parameter estimation using response data and prior assumptions; mathematical simplicity does not make the skill mapping empirically correct. The inspected author-hosted manuscript is the December 2000 preprint of the 2001 publication. [Manuscript, §§3–4](https://www.stat.cmu.edu/~brian/apm/np-cog4.pdf), [publication record](https://research.tilburguniversity.edu/en/publications/cognitive-assessment-models-with-few-assumptions-and-connections-/).

**Existing BKT/PFA boundary.** BKT separates a binary knowledge state, noisy performance and a learning transition. Its identifiability under nondegenerate conditions does not promise reliable estimation from three answers by one person; semantic degeneracy remains a distinct issue. [Doroudi and Brunskill, 2017](https://www.cs.cmu.edu/~shayand/papers/EDM2017.pdf). PFA uses fitted skill terms and prior success/failure counts to predict responses; the original formulation can combine multiple skill contributions. It does not supply a causal interpretation of practice effects or calendar-time forgetting by itself. [Pavlik, Cen and Koedinger, 2009, §2](https://files.eric.ed.gov/fulltext/ED506305.pdf). Neither comparison licenses new fitted parameters from the current few examples.

## ALEKS is a lead, not a portable guarantee

The current ALEKS first-party page describes empirically feasible states over roughly 400–500 Algebra 1 problem types and claims assessment in **20–25 questions**. Its language about precise diagnosis is a vendor description, not an independent accuracy estimate inspected here. The 2015 KST chapter instead describes roughly **25–35 trials** for its algorithm. Neither supports repeating “25–30” as a verified universal bound. Neither establishes the question count, accuracy, content-authoring cost or retention benefit for this general system. [ALEKS research page, undated; inspected 2026-10-14](https://www.aleks.com/about_aleks/research_behind), [2015 chapter, p. 30](https://arxiv.org/pdf/1511.06757).

## Consequences for this system

The following are design deductions, not reported experimental findings.

With a static state `K` and response `r`, a minimal update is:

```text
posterior(K) ∝ prior(K) × P(r | K, assessment contract)
```

This changes **our belief**, not necessarily the learner's knowledge. If a state is excluded or assigned zero prior, ordinary Bayesian updating cannot restore it. Nonzero error probabilities keep contradictory answers mathematically possible, but can make a wrong structural assumption explain every contrary answer as noise. A posterior concentrated on the surviving states can therefore be confidently wrong about the learner.

For example, declaring “can perform advanced procedure B only if independently recalling fact A” rules out a learner who performs B through another strategy or tool. A curricular prerequisite, semantic relation, or shared topic is not sufficient evidence for that exclusion. Scope the assessment mode, permitted help and actual solution path before proposing a relation. Treat discrepancies as possible problems in the graph, task contract, grading or learner estimate; do not automatically label the learner careless.

The current representation seam makes dependence concrete. Two projections of the **same scored evidence** are one observation. Multiplying their likelihoods changes `L(K)` to `L(K)^2`, exaggerating the evidence without a second response. Keep an evidence identity stable across rubric/capability projections. Different criteria from one answer are not necessarily duplicates, but their joint independence must also be justified; using one joint response event is a conservative experiment boundary. Independent observations can still be informative even when they agree—the issue is shared origin, not repeated values. Corrections should replace the effective assessment through replay, not become another independent vote.

Similarly, a successful composite response can support an inference about an unobserved part without demonstrating that part's independent recall. It may also involve real practice, but the amount and durability of reinforcement are separate claims. No inferred prerequisite success should become a fabricated FSRS review. A model learning transition would itself require assumptions; none is necessary for this static sensitivity experiment.

## Minimal experiment and stopping conditions

Use three narrowly defined capabilities from an existing example. Publish their contracts and which relationships are merely hypotheses. Construct two numerical comparators: a deliberately strict chain with four allowed states, and all eight combinations without that restriction. Use fixed, disclosed parameters; no fitting to these examples. A strict chain is a stress case, not a claim that it represents the real domain.

Run these conditions:

1. No observations: show what the prior alone implies. Uniform distributions over four versus eight states generally produce different marginal priors; report that confound. Add a control with matched marginal priors where feasible, or explicitly say the comparison changes both structure and prior.
2. One direct success: show which untested estimates change and the assumed dependency responsible. Unrelated evidence should not move an independent capability in the unconstrained control.
3. Advanced success plus prerequisite failure: preserve both observations; show remaining alternatives and the response likelihood under each model. With zero-noise likelihoods, report incompatibility rather than normalize zero mass. With noise, expose how much the conclusion depends on it.
4. Replay one response twice through separate projections: verify one effective update. Distinct genuine attempts remain separate; a revised grade must replace, not accumulate with, the original effective grade.
5. Vary priors and plausible low/high response-noise settings. These are sensitivity settings, not calibrated estimates. If the recommended diagnostic question changes, expose the instability rather than presenting a single authoritative probability.
6. Keep ambiguous grading, omitted criteria and assisted answers outside an unassisted binary-response likelihood unless that contract explicitly models them. Preserve the source observations alongside every derived estimate.

This probe can verify arithmetic, provenance, dependence handling and sensitivity. It cannot show that the graph is correct or that inference saves study time. Do not call its synthetic outcomes calibration results.

For subsequent real observations, save predictions **before** independent checks, retain dates and item-family boundaries, and distinguish within-session diagnosis from delayed retention. Compare numerical models using held-out probability forecasts and report sample size and uncertainty. Compare the descriptive policy using decisions and outcomes—questions asked, unresolved gaps, and missed errors—rather than inventing probabilities for it. Do not pool duplicate projections as independent evaluation cases.

Added complexity needs a named failure. Repeated independent contradictions of a prerequisite relation justify revising that relation or preserving alternative states before adding a richer model. Correct task grading with poor delayed predictions may justify a forgetting comparison. Distinct answer patterns collapsed by the same likelihood may justify separate response categories or a better task mapping. Stable predictive gains across later, separated observations could justify a constrained probabilistic model. None alone proves that skipping a review preserves retention; that requires a prospective, comparable-time evaluation with delayed checks.

The minimal deliverable now is therefore an inspectable **assumption test**, plus a clear record of what future evidence would change the design. It preserves the ambition to infer useful information without exhaustively testing every component, while preventing inference from silently becoming reinforcement credit.
