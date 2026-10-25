# Statistical methods for a personal learning history

Research date: 2026-10-14. Decision input for [Which statistical methods can support a sparse personal learning history?](../issues/02-statistical-methods.md). This is a proposed analysis contract, not evidence of a learning effect. No learner model was fitted, trial run, or product implemented.

## Recommendation and existing evidence

Use three separate layers: **describe recorded performance**, **evaluate predictions**, and **compare learning policies prospectively**. Each needs a different target quantity and different assumptions. Sparse data can support an accurate description immediately; it cannot automatically support a precise probability of mastery or a causal efficiency claim.

The existing [observability proposal](../../skill-maintenance/observability-design.md) already preserves assistance, endpoint denominators, missingness and full cost. The [inference design](../../skill-maintenance/inference-design.md) and [numerical probe](../../skill-maintenance/spikes/inference/README.md) explicitly use assumed parameters and fictional observations. Their sensitivity results are not empirical uncertainty intervals. The [evaluation contract](../../skill-maintenance/issues/06-evaluation-contract.md) remains open: meaningful savings, acceptable retained-performance loss and stopping rules are undecided. This investigation does not decide those preferences for the learner.

The largest design risk is pretending that one learner creates many independent participants by answering many questions. Neither distinct criterion rows nor distinct episodes establish independence. A second risk is treating alternation between methods as a clean crossover: learning from the first method persists into the second. The CENT reporting guidance explicitly addresses carryover, period effects and correlated observations in single-person trials. Our application is methodological; it supplies no clinical or learning efficacy claim. [CENT explanation, items 12c and related definitions](https://www.bmj.com/content/350/bmj.h1793).

## 1. State the estimand before choosing a method

An estimand is the exact quantity the analysis seeks. Save its definition before interpreting a chart.

| Purpose | Quantity and unit | What can be concluded |
|---|---|---|
| Recorded progress | Counts of demonstrated/error/assisted/unresolved/missing endpoints for a fixed target contract, horizon and cutoff | What these checks showed; no causal claim |
| Comparable change | For N complete comparable pairs, improvements b, regressions c, maintained successes and persistent errors; net observed change `(b-c)/N` | Change on these pairs, with incomplete pairs separately visible |
| Future response forecast | Probability of an eligible independent answer at a declared horizon under specified conditions | Predictive performance on the evaluated selection policy and task population |
| Policy comparison | Difference in delayed independent outcomes under candidate versus baseline assignment; full learner-time difference alongside it | A causal contrast only if allocation, interference, outcome and missingness assumptions hold |

A complete inventory of eight fixed targets is a finite record, not a random sample of all knowledge. Its five successes are exactly five recorded successes. There is no reason to attach a sampling interval to that count. Generalizing to future tasks requires an explicit sampling or response model. Grading uncertainty, missing outcomes and future-response variability are separate uncertainties.

For a proposed paired-family trial, let `Y_kj(a)` denote the prespecified delayed outcome summary of family j in pair k under policy a. A possible finite-study estimand is the average of the `2K` family-specific effects `Y_kj(1)-Y_kj(0)`. Cost has its own estimand. Use fixed equal-size endpoint sets if choosing this simple family-average analysis; unequal family sizes require explicitly choosing family-average versus target-average inference. Do not silently swap denominators or combine learning and time into a weighted utility score.

## 2. Descriptive analysis and conditional statistical intervals

Keep the existing endpoint partition `P=S+E+H+U+M`. Report `S/(S+E)` as conditional success among judged unaided checks, alongside all counts. Paired transitions are preferable to two unrelated overall pass rates. Histories with changing content, assistance, grading or difficulty are separate descriptive strata until comparability is established.

When an explicitly justified model treats n observations as independent Bernoulli trials with one common response probability, a Wilson interval is a reasonable candidate:

```text
p_hat = s/n
center = (p_hat + z²/(2n)) / (1 + z²/n)
half_width = z * sqrt(p_hat(1-p_hat)/n + z²/(4n²)) / (1 + z²/n)
interval = center ± half_width
```

NIST documents the Wilson formula and exact binomial alternatives; it also explains why the ordinary symmetric Wald interval can behave poorly. “Exact” binomial coverage still depends on the binomial model. Neither method repairs dependent observations or selection bias. A 95% confidence interval describes the repeated-sampling procedure; it is not a 95% posterior probability about this learner. [NIST proportion intervals](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm).

Recommendation: offer such intervals only in a report that declares and justifies the process model. Do not attach them automatically to every dashboard fraction. Do not turn related criterion rows into n, replace n with an invented “effective sample size,” or assume ordinary row bootstrap resampling solves clustering. With a few independent families, both cluster bootstrap and asymptotic cluster standard errors need feasibility examination; resampling cannot create missing independent information.

A beta posterior could be an explicit experimental model, but its prior and independence assumptions must be visible and stress-tested. It should not become the default uncertainty decoration. Defer fitted latent ability, item-difficulty, learning and forgetting models until repeated, comparable observations can distinguish their parameters. With one learner, changing ability and fresh item difficulty can explain the same outcomes; an elaborate fitted curve does not resolve that ambiguity. Candidate models must beat a simpler forecast prospectively, with fresh task variants and stable assessment contracts.

## 3. Selection, difficulty and missingness

Adaptive practice chooses observations using earlier outcomes. A pass-rate decline can mean harder tasks were selected, while a rise can mean easier tasks were selected. Therefore store the eligible task set, selection reason, policy version and any actual randomization probability. Ordinary forecasts may still be scored on those selected tasks, but the report must name that distribution; it does not establish performance on omitted material.

Causal reweighting is not an initial rescue method. Identifying effects by standardization or inverse-probability weighting requires conditions including exchangeability, positivity and consistency. A deterministic selector that never assigns the alternative in some context lacks positivity there; estimated weights cannot manufacture that alternative's outcomes. [Hernán and Robins, *Causal Inference: What If*, chapters 2–3 and 12](https://miguelhernan.org/s/hernanrobins_WhatIf_2jan25.pdf). For this app, reserve an explicitly agreed assessment sample when broader coverage matters; its time is evaluation cost. Keep genuinely different modes and difficulties separate instead of “correcting” them with invented difficulty scores.

For fully assessed unaided endpoints plus missing endpoints only, the finite-cohort fraction compatible with the missing outcomes lies between `S/P` and `(S+M)/P`. These are scenario bounds, not confidence limits. With assisted or unresolved endpoints, retain their categories and explicitly define any hypothetical outcome before extending a bound; assistance does not directly reveal what an unaided answer would have been.

Do not carry the last successful grade forward as the missing delayed answer. Do not silently impute missing-as-random because the software can fit an imputation model. Record reasons where available and ask whether missingness could reflect difficulty, burden or avoidance. White and colleagues recommend explicit assumptions and sensitivity analyses including all assigned units; their discussion supports best/worst-case analyses for small amounts of missing binary data. [White et al., 2011](https://www.bmj.com/content/342/bmj.d40).

For policy choice, show a tipping point: how many unknown outcomes or minutes of unallocated cost would reverse the decision? Statistical precision cannot fix an unresolved measurement or missingness assumption.

## 4. Prospective comparison, carryover and stopping

The first candidate design is **matched knowledge-family allocation**, not repeated A/B switching on the same target. Pair comparable families before outcomes, randomly allocate one member to each policy, keep related prerequisites and exercises together, and predeclare fresh delayed endpoints. Balance timing/order where feasible. Restrict claims to this learner and enrolled families. Keep allocation despite noncompletion, showing unavailable outcomes rather than dropping unsuccessful families.

This is only suitable when cross-family transfer can plausibly be limited. A strategy taught in one family may help its comparison family, and shared learner fatigue can couple sessions. If those effects cannot be bounded or designed around, the simple policy comparison stays unidentified. No pretend washout interval should be introduced merely to make the analysis convenient.

Matched cluster randomization can support design-based inference, but estimand and interference assumptions matter. Imai, King and Nall distinguish cluster versus individual target quantities and discuss interference within and between clusters. Their results do not automatically validate our knowledge-family grouping. [Imai et al., sections 3–4](https://imai.sites.fas.harvard.edu/research/files/cluster.pdf).

For K actually randomized pairs, let `d_k` be candidate-minus-baseline family outcomes and `T=mean(d_k)`. Under the **sharp null** that assignment changes no family's outcome, enumerate all allowed within-pair assignment flips:

```text
T(signs) = mean(sign_k * d_k), sign_k ∈ {-1,+1}
p_two_sided = count(abs(T(signs)) >= abs(T_observed)) / 2^K
```

This is exact enumeration for that design, not a generic permutation of arbitrary observational rows. Its p-value tests the sharp null; it neither estimates a useful effect precisely nor proves noninferiority. Failure to reject zero does not establish equivalence. Retention-loss and savings margins need separate prespecified interval/decision procedures whose operating properties are checked before adoption; constant-effect inversion cannot silently stand in for heterogeneous family effects.

Prefer a fixed endpoint count and horizon for the first comparison. The dashboard may update descriptive counts continuously, while the decision waits for the declared analysis. Do not repeatedly apply ordinary fixed-sample intervals/tests and stop when favorable. Confidence sequences can provide time-uniform coverage under their stated probabilistic conditions, but a valid construction must match the actual dependence and allocation process. They do not cure missingness or unmeasured transfer. [Howard et al., 2021, final paper](https://arxiv.org/abs/1810.08240). Add sequential methods only if a real decision requires early stopping and simulation verifies their behavior for the proposed design.

## 5. Forecast scoring and calibration

Freeze each forecast before the answer: probability, target/contract, horizon, relevant exposure, model version and training cutoff. Score the same eligible endpoints for candidate and benchmark; never train on their outcomes first.

For binary outcome y and forecast p, use `Brier=(p-y)²`, averaged over the declared evaluation units. Lower is better. Log loss is `-[y log(p)+(1-y)log(1-p)]`; exact certainty followed by contradiction has infinite loss. Do not silently clip probabilities after seeing outcomes. These are proper scoring-rule choices, not mastery metrics. [Gneiting and Raftery, section 3](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf).

Keep all target facets for coverage, but aggregate score contributions within a declared episode/family design before computing uncertainty. Display paired score differences on identical outcomes, not scores from different task mixes. Use forward evaluation: previous evidence predicts later checks; group related exercise variants and preserve temporal order to prevent leakage.

Calibration asks whether forecast probabilities match observed frequencies. Start with a table of frozen forecasts and outcomes, mean forecast versus observed frequency, and predeclared horizon/family slices. An attractive binned curve with two answers per bin is not established calibration. Sparse results should say “insufficient evidence to assess calibration.” Distinguish calibration from useful discrimination: constantly predicting the overall success fraction can match that average while failing to distinguish individual opportunities. Lower forecast loss also does not prove better learning or safe review omissions.

## 6. Data sufficiency and staged delivery

There is no universal “30 observations” gate. Specify the required precision or policy decision, then examine whether the feasible number of **independent allocation units** can support it. A four-pair experiment contains sixteen possible assignments however many criterion rows it emits.

Before recruiting effort, run a reproducible feasibility study using declared synthetic scenarios: baseline retention, meaningful effect/loss margins, family sizes and correlations, period trends, transfer, grading error, selective missingness and time variability. Compare the proposed analysis against simple descriptive reporting. Report interval coverage/width, false adoption, probability of an inconclusive decision, and evaluation burden. Include null, helpful and harmful policies; a favorable scenario alone cannot qualify the method.

Use the ADEMP structure: aims, data-generating mechanisms, estimands, methods and performance measures. Preserve seeds and report Monte Carlo error; for an estimated simulation event rate q across R replicates, its Monte Carlo standard error is approximately `sqrt(q(1-q)/R)`. Simulated feasibility is conditional on scenarios, not validation of their realism. [Morris, White and Crowther, 2019](https://discovery.ucl.ac.uk/10066118/1/2019%20-%20Morris%20-%20simulation%20studies%20tutorial%20-%20stat%20med.pdf).

| Stage | Deliverable | Permission to conclude |
|---|---|---|
| A: exact descriptive accounting | Cohort counts, paired transitions, full costs, evidence links, sensitivity bounds | What was observed and what remains unknown |
| B: prospective prediction audit | Frozen forecasts, proper scores, same-endpoint benchmark, calibration diagnostics | Prediction quality within the evaluated scope |
| C: comparison feasibility | Estimand, randomization unit, margins, stopping rule, simulated operating characteristics | Whether a bounded policy comparison is worth its measurement burden |
| D: prospective policy comparison | Declared allocation, delayed outcomes, costs, missingness sensitivity, decision analysis | Evidence for adopting a scoped change if its requirements are met |

Every statistical report must retain analysis version, estimand, cutoff, unit counts, dependence/allocation assumptions, eligible/excluded records, missingness treatment, interval meaning and decision rule. Unsupported assumptions produce an explicit unavailable or descriptive-only result. Stage B cannot substitute for D, and product use need not wait for a statistically conclusive optimization claim.

## 7. Four numerical counterexamples for a throwaway spike

All numbers below are authored, not learner measurements. Wilson values and assignment enumeration were checked with standalone Python calculations without adding repository code.

1. **Duplicated evidence narrows an interval falsely.** Ten independent hypothetical episodes contain eight successes. With `z=1.96`, Wilson gives `[0.49015685,0.94331905]`. Copy every grade into ten criterion rows: 80/100 produces `[0.71116904,0.86663408]`. The point estimate remains 80%; the apparent information increase is fictional. Required result: preserve ten episode identities and refuse the second interval as independent-trial inference. Even the ten-episode interval is conditional on its stated model.

2. **Task mix reverses the apparent trend.** Earlier: easy 8/10, hard 18/90, pooled 26/100. Later: easy 63/90, hard 1/10, pooled 64/100. The headline rises 38 percentage points while each difficulty stratum falls ten points. Required result: changing-population warning, both strata and denominators visible, no learning-gain conclusion from pooled rates. No invented composite weighting is required.

3. **Missingness leaves the conclusion open.** Five successes, two errors and one missing endpoint give 5/7 judged success and 7/8 completion; finite-cohort scenarios span 5/8–6/8. Compare a different hypothetical cohort with three successes and five missing: 100% among its three judged answers, but bounds 3/8–8/8. Required result: neither cohort is declared superior by its conditional rate; scenarios never become stored grades or confidence intervals.

4. **Four unanimous pairs do not yield strong randomization evidence.** Differences `[0.1,0.2,0.3,0.4]` give mean 0.25. Enumerating sixteen sign allocations yields two absolute statistics at least as large, so the exact two-sided p-value is 0.125. Required result: state the actual-randomization/sharp-null assumptions and forbid “equivalent,” “proven better” or review reduction. More criterion rows within those four pairs do not improve the assignment resolution.

Optional stopping extension: for independent fair Bernoulli outcomes, use the two-sided exact binomial p-value at every n from 1 through 20 and stop at `p<=0.05`. Exact path enumeration yields false rejection `111796/1048576 = 10.661697%`; one fixed n=20 analysis yields `4.138947%`. This is mathematical behavior of the declared toy model, not measured error in the app. It avoids the incorrect shortcut of treating successive cumulative looks as independent tests.

## Source verification and limits

Eight primary or authoritative sources were checked. NIST, the Imai and Gneiting author PDFs, Morris's institutional PDF and Howard's author manuscript were readable directly. BMJ's CENT and missing-data full-page opens returned access errors, but relevant method passages were verified through indexed text from those exact publisher articles. Hernán's official book PDF exceeded the browser fetch limit; its chapter 3 positivity and consistency passages were verified through indexed text of that exact author-hosted PDF. No secondary summary supplied the methodological claims. Recommendations applying these methods to knowledge families are our design inferences, not results established by those publications.
