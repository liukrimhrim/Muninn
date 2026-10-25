# Sparse-inference assumption probe

**Throwaway numerical experiment.** Asks what an answer permits a model to infer, how much the answer depends on the model's assumptions, and what happens when the same evidence is counted twice. No new learner answers, calibrated mastery scores, learning effects, review omissions or FSRS updates.

Run with Node.js (verified with v26.0.0), no packages:

```sh
node .scratch/skill-maintenance/spikes/inference/probe.mjs
```

The command checks the calculations and writes [results.json](results.json). The [design](../../inference-design.md) explains the consequences; [research](../../research/sparse-inference.md) supplies the primary sources. This is a script, not another learner exercise or browser-review request.

## Disclosed assumptions

The letters stand for possible capability contracts from the existing mathematics example:

- A: explain repeated halving and logarithms (`math.explain`).
- B: count work across continuing branches (`math.work`).
- C: connect depth, branching and total work (`math.integrate`).

Numerical observations are invented direct checks, not the composite example's grades or the user's answers. The strict chain assumes B requires A and C requires B. That is deliberately contestable: someone might count work without explaining logarithms, or use another strategy. The probe does not validate those prerequisites or map the actual composite response into latent states.

The chain allows `[]`, `[A]`, `[A,B]`, `[A,B,C]`, initially each at probability 0.25. The independent control allows all eight subsets, with factorized marginals A=0.75, B=0.50, C=0.25. These match the chain's marginals. A second independent control uses all eight states uniformly to expose the different-prior confound.

For a direct check of target T, the likelihood of a correct response is `1 − slip` if the state contains T, otherwise `guess`. Posterior mass is prior mass times likelihood, normalized. Main calculations use slip=guess=0.10; sensitivity runs use 0.01 and 0.30 plus empty-heavy and full-heavy chain priors. Two additional runs exchange slip=0.01/guess=0.30 with slip=0.30/guess=0.01. None was estimated from learners. Repeated responses are assumed conditionally independent given an unchanged state. There is no feedback, learning transition, elapsed time or forgetting in this calculation. Distinct episodes do not guarantee independence in real practice.

Each numerical update concerns one binary judgment per episode. Identical response IDs/revisions are deduplicated; an explicit later assessment revision replaces the effective grade. Conflicting same-revision grades and multiple included judgments from one episode are refused. Assisted, ambiguous and omitted judgments remain visible but do not enter this unassisted binary likelihood. This small experiment does not implement full production assessment revision validation.

## Results

Fourteen checks pass, including independently stated hand calculations:

| Condition | Chain A / B / C | Matched independent A / B / C |
|---|---|---|
| Before observations | 75% / 50% / 25% | 75% / 50% / 25% |
| C correct | 91.67% / 83.33% / 75% | 75% / 50% / 75% |
| C correct, then A incorrect | 55% / 50% / 45% | 25% / 50% / 75% |

For the chain, one success gives relative state weights `1:1:1:9`. Adding the contradiction gives `9:1:1:9`. The full response sequence has likelihood 0.05 under the chain and 0.09 under the matched independent control. These are likelihoods of this synthetic sequence, not model probabilities or an empirical model-ranking result.

With zero noise the chain reports incompatibility, while the control permits C without A. At 10% noise, different disclosed chain priors put A after the same contradictory pair anywhere from 14.86% to 87.84%; that interval is sensitivity, not statistical uncertainty.

Changing the asymmetry of the error assumptions also changes which answer the model discounts. With uniform chain prior, slip=0.01/guess=0.30 puts C at 4.38%; slip=0.30/guess=0.01 puts C at 92.96%. The respective unnormalized full-state likelihoods are 0.0099 and 0.21, with state-likelihood sums of 0.2259 in both cases. The labels “slip” and “guess” do not establish the real cause of an answer.

A deliberately counterfeit second copy of C success raises C from 75% to 96.43%. Retaining the original identity leaves one effective observation and the original posterior. A genuine separate response is different from a copy; the calculation assumes its independence rather than proving it.

The script also loads the **real validator, bridge, planner and representation example**. Its math answer produces three capability projections with five criterion-reference occurrences, four unique criterion references, and one distinct answer. Deduplicating the shared `work` reference removes a literal duplicate; it does not make the remaining criteria independent. No bridge observation is fed into the fictional Bayesian calculation.

The report contains full priors, allowed states, posteriors, observation identities, sensitivity outputs, checks and dependency hashes. It does not alter the existing demos or historical independent-assessment records. The probe establishes arithmetic and provenance behavior; the usefulness of any inference for a learner remains to be tested.
