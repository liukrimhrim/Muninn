# Where FSRS should end and capability inference should begin

Research date: 2026-10-13. Decision input for **Where should FSRS end and capability inference begin?** The supplied conversation is a source of hypotheses and user goals, not proof of its technical or educational claims. This report separates verified implementation behavior, published findings, and proposed design rules.

**Recommendation:** use unmodified FSRS for directly observed retrieval units; use an evidence ledger and explicit diagnostic tasks for broader capabilities. A curriculum graph can select a useful question without pretending that its edges are measured transfer coefficients. Do not add a neural graph model, implicit stability boosts, or a numerical “understanding percentage” to the first system.

## Verified FSRS boundary

The inspected official Python implementation is **py-fsrs 6.3.2**, released August 9, 2026. The release tag and inspected `main` both resolve to **`9446cb06605c597a063aeee49f7d188d42e34dc2`**; PyPI also reports 6.3.2. Pin this commit for reproducibility, rather than a moving `main`. It implements **FSRS-6**, not a novel graph scheduler. [Release](https://github.com/open-spaced-repetition/py-fsrs/releases/tag/v6.3.2), [pinned source](https://github.com/open-spaced-repetition/py-fsrs/tree/9446cb06605c597a063aeee49f7d188d42e34dc2), [package metadata](https://pypi.org/pypi/fsrs/6.3.2/json).

FSRS-6 has 21 parameters. It stores stability and difficulty and derives retrievability from elapsed time. Stability is the interval at which predicted recall falls to 90%; difficulty lies between 1 and 10. Its forgetting curve is `R(t,S) = (1 + factor*t/S)^(-w20)`, with `factor = 0.9^(-1/w20)-1`. The inverse curve yields the next interval for the chosen retention target. These are predictions of recall under the model, not measurements of conceptual understanding. [Official algorithm](https://github.com/open-spaced-repetition/awesome-fsrs/wiki/The-Algorithm#fsrs-6).

The public update is:

```python
updated_card, review_log = scheduler.review_card(
    card, rating, review_datetime=None, review_duration=None
)
```

`Card` serializes `card_id`, `state`, `step`, `stability`, `difficulty`, `due`, and `last_review`. Its state is Learning, Review, or Relearning. New cards start in Learning, step zero, with no stability/difficulty or previous review. `ReviewLog` contains only card identity, rating, UTC timestamp, and optional duration in milliseconds. There are no skill IDs, assessment formats, graph links, confidence weights, assistance flags, or grader records. Those belong in the application. [Card source](https://github.com/open-spaced-repetition/py-fsrs/blob/9446cb06605c597a063aeee49f7d188d42e34dc2/fsrs/card.py#L25-L92), [log source](https://github.com/open-spaced-repetition/py-fsrs/blob/9446cb06605c597a063aeee49f7d188d42e34dc2/fsrs/review_log.py#L24-L50).

The scheduler copies its input card, updates the copy, and returns it with the log. Explicit review timestamps must be timezone-aware UTC. Duration is recorded but does not change this scheduler's memory update. Elapsed time for retrievability uses whole elapsed days, while sub-day repetitions use the short-term update. Default learning steps are one and ten minutes, relearning is ten minutes, desired retention is 0.9, and interval fuzzing is enabled. Disable fuzzing for deterministic probes. [Scheduler source](https://github.com/open-spaced-repetition/py-fsrs/blob/9446cb06605c597a063aeee49f7d188d42e34dc2/fsrs/scheduler.py#L164-L271).

The four ratings mean: Again = forgot; Hard = recalled with serious difficulty; Good = recalled after hesitation; Easy = recalled easily. **Hard is a success, not partial credit for failure.** Anki explicitly warns that treating forgotten answers as Hard produces excessive intervals. A coding task's “70% tests passed” therefore has no automatic FSRS rating. [Rating definitions](https://github.com/open-spaced-repetition/py-fsrs/blob/9446cb06605c597a063aeee49f7d188d42e34dc2/README.md#quickstart), [Anki rating guidance](https://docs.ankiweb.net/manual/deck-options#fsrs).

Successful learning repetitions advance steps; Easy graduates immediately. A Review-state Again enters Relearning when relearning steps exist. Without those steps it remains Review. The library does not determine whether a response was correct or whether recall actually occurred. [State transitions](https://github.com/open-spaced-repetition/py-fsrs/blob/9446cb06605c597a063aeee49f7d188d42e34dc2/fsrs/scheduler.py#L273-L517).

## Small live probe

I cloned the release into `/tmp/wayfinder-py-fsrs`, installed it in `/tmp/wayfinder-fsrs-venv`, and executed the real library. Project dependencies were untouched. With an explicit card ID, UTC start `2026-10-01T00:00:00Z`, defaults, and fuzzing disabled:

| Observation | Actual result |
|---|---|
| New, never-reviewed card | `get_card_retrievability` returns `0` |
| Good at start | Learning step 1; S = 2.3065 days; due in ten minutes |
| Good ten minutes later | Review; S = 2.3065; due in two days |
| Good seven days after that | S = 21.42621174777395; due in 21 days |
| Otherwise identical next review lasting 1 versus 100 seconds | Identical resulting card |
| Review call against existing card | Original object unchanged |
| Pass `indirect_confidence=0.5` | `TypeError`: unexpected keyword argument |

Reproduce after checking out the pinned source with `Scheduler(enable_fuzzing=False)`, `Card(card_id=1, due=t)`, and sequential `review_card` calls at the listed timestamps. These numbers verify software behavior, not human learning. In particular, the library's zero for missing memory state must display as **unobserved**, not “0% mastery.” [Retrievability implementation](https://github.com/open-spaced-repetition/py-fsrs/blob/9446cb06605c597a063aeee49f7d188d42e34dc2/fsrs/scheduler.py#L210-L234).

## Indirect evidence and exercise identity

**Verified:** standard py-fsrs has no API or observation model for fractional indirect review. Manually editing stability or manufacturing Good reviews for prerequisites would create a new algorithm. The library accepting a `Card` with arbitrary stability would not validate that intervention scientifically. The same restriction applies to “review compression”: skipping a due prerequisite is a policy choice, not evidence that its memory improved.

**Proposed boundary:** a retrieval unit is a stable claim under a stable assessment contract: for example, “explain why repeated halving gives logarithmic growth, without cues.” Its content can concern a fact, relationship, comparison, or short derivation. The data model should separately represent:

| Identity | Meaning |
|---|---|
| Capability | What the learner should do, such as justify logarithmic complexity |
| Retrieval unit | A repeatable retrieval contract scheduled by FSRS |
| Item version | Exact prompt, expected answer, and rubric presented |
| Item family | Variants sharing a solution pattern or source template |
| Format | Free recall, multiple choice, explanation, coding, or construction |
| Context | Domain/example, tools, cues, and allowed assistance |

Start with one stable format per retrieval unit. Cosmetic variants can share a unit only when the author explicitly declares the same target, cues, response demand, and grading standard; this is a testable authoring assumption. A definition, a multiple-choice recognition task, and an unfamiliar proof do not become interchangeable because they mention the same concept. A new variant is also not automatically independent evidence of transfer.

For a composite problem, record the actual response and separately scored criteria. Do not mark every prerequisite successful from the final answer. A failure may warrant a diagnostic follow-up, but does not show that every prerequisite failed. A directly observed substep can count as evidence when its rubric genuinely isolates the target; keep its shared episode identity. Evidence-centered assessment design explicitly separates claims about learners, observable evidence, and tasks that elicit that evidence. [Mislevy, Almond, and Lukas](https://www.ets.org/research/policy_research_reports/publications/report/2003/hsgs.html).

Shared stimuli and dependent questions can cause models assuming independent observations to overstate measurement precision. Apply that lesson cautiously to generated variants and multistep exercises: retain family and episode identifiers, do not call three paraphrases three independent demonstrations, and keep all variants from a family on one side of a transfer evaluation split. This is a conservative design inference, not an estimated correlation coefficient. [Wainer and Wang, testlet dependence](https://onlinelibrary.wiley.com/doi/10.1002/j.2333-8504.2001.tb01851.x).

## What a small personal dataset can support

**BKT** is a useful interpretable comparison: canonical Bayesian Knowledge Tracing tracks a binary latent learned/unlearned state with initial knowledge, learning, guess, and slip parameters. It estimates a probability of correct response separately from a probability of the latent learned state. Standard BKT does not by itself implement calendar-time forgetting, heterogeneous task difficulty, or all forms of assistance. [Original knowledge-tracing paper](https://perso.liris.cnrs.fr/pierre-antoine.champin/2014/m2iade-ia2/_static/893CorbettAnderson1995.pdf).

An important correction: do **not** say BKT is inherently non-identifiable. Doroudi and Brunskill show identifiability under nondegenerate conditions and distinguish it from local optima and semantically misleading fitted parameters. Their result concerns identifying a model from a distribution of response sequences; it does not say three responses by one learner are enough to estimate four meaningful parameters. [2017 primary paper](https://www.cs.cmu.edu/~shayand/papers/EDM2017.pdf).

For this project, separately fitting prior knowledge, forgetting, slip, guess, format, item difficulty, and graph transfer from a few observations per skill is unsupported. This is an inference from the proposed data regime, not a universal minimum-sample theorem. A fixed-prior BKT baseline could be explored later, with sensitivity analysis and predictions labeled as conditional on those priors. First gather varied, delayed, unassisted demonstrations; do not present a point estimate as confidence in understanding.

**PFA** predicts performance using a logistic model with per-skill intercepts and counts of prior successes and failures; the original formulation can include multiple skills for one performance. It is computationally small and a useful later predictive baseline. It still requires defensible skill tags and fitted parameters, and vanilla counts do not capture the elapsed-time forgetting FSRS models. Its linear predictor is part of a statistical model, not a proposed weighted-sum question-selection policy. [Pavlik, Cen, and Koedinger](https://files.eric.ed.gov/fulltext/ED506305.pdf).

A negative PFA failure coefficient must not be interpreted as “making errors harms learning.” A recent primary investigation shows how PFA parameters can confound prior knowledge, learner–skill differences, and learning from successes/failures. Predictive performance and parameter meaning must be evaluated separately. [Rachatasumrit, Carvalho, and Koedinger, 2024](https://educationaldatamining.org/edm2024/proceedings/2024.EDM-long-papers.17/index.html).

**GKT** uses graph neural networks to update latent concept representations and predict future performance. Its graph is a relational modeling assumption or learned statistical structure; it is not an observed map of a learner's understanding. The primary study reports predictive evaluation on educational datasets, not proof of improved personal learning from a graph-driven tutor. That makes GKT a later research comparator, not a justified cold-start dependency here. [Nakagawa, Iwasawa, and Matsuo](https://journals.sagepub.com/doi/10.3233/WEB-210458).

The minimal baseline is therefore **diagnostic measurement without a fitted mastery model**: report the latest observed performance, unresolved error, contexts covered, assistance used, and dates. “Demonstrated independently on two different families, one week apart” is reviewable evidence; “92% understands graph topology” is unjustified precision. Counts and thresholds remain policy choices, not calibrated probabilities.

## Implementable state and evidence contract

Keep immutable assessment events and two rebuildable projections: FSRS state for retrieval units, and capability evidence summaries. One event may appear in both views, but they are not independent observations to be fused later.

Minimum event fields:

```text
event_id, learner_id, occurred_at_utc, episode_id
item_id, item_version, family_id, format, context
target_capabilities, retrieval_unit_id?
attempt_index, response, assistance, answer_revealed_at?
criterion_results, rubric_version, grader, grading_status
fsrs_rating?, rating_source?, scheduler_version?
supersedes_event_id?
```

`criterion_results` distinguishes passed, failed, and not observed. A grader's confidence is not learner mastery. Preserve the first response before hints and feedback; an initially failed recall receives Again even if feedback later enables success. Genuine later relearning reviews can still reach FSRS. Scaffolding-only exercises remain instructional events unless their retrieval contract was actually assessed.

Enforce these rules:

1. Apply a finalized event at most once to a retrieval unit; no graph propagation.
2. Keep correction history and replay affected state after an erroneous grade; do not append a fake compensating review.
3. Require a defined mapping from an assessed recall outcome to the four ratings. Ambiguous composites and disputed grades have no FSRS update until resolved.
4. Preserve temporal order, model parameters, library version, and resulting state. Use a transaction/idempotency boundary around event persistence and projection updates.
5. Summarize capability evidence by episode, family, format, assistance, and delay. Never discard those distinctions into one success count.

Keep policy explicit: honor the session time budget; offer due direct retrievals; select one diagnostic task when a named weakness or missing demonstration justifies it; after feedback, verify later on an unseen family. Record the selection reason. Do not introduce a weighted sum of urgency, graph centrality, mastery, and uncertainty without evidence establishing its meaning.

## What would justify changing this baseline

First audit grading against human judgments, review the item-to-capability mappings, and verify event replay and duplicate handling. Then measure prediction calibration on later observations, grouped by format and item family. Use chronological evaluation and hold out whole families to distinguish repeated-item prediction from generalization. Report cohort size and uncertainty; sparse slices remain descriptive.

Only after these checks should a constrained BKT/PFA model compete with the descriptive baseline. Graph propagation would need its own falsifiable test: does an advanced exercise predict *later independent prerequisite performance*, after accounting for prior performance and direct practice? Even that association would not establish that the exercise caused improvement. A learning-benefit claim requires a prospective comparison with comparable practice time and delayed unseen tasks. Better next-answer log loss, a prettier graph, and passing this software probe cannot substitute for that comparison.

## Reproduction appendix

Setup used (already completed in this session; use fresh paths when repeating):

```sh
git clone --depth 1 --branch v6.3.2 https://github.com/open-spaced-repetition/py-fsrs.git /tmp/wayfinder-py-fsrs
git -C /tmp/wayfinder-py-fsrs rev-parse HEAD
python3 -m venv /tmp/wayfinder-fsrs-venv
/tmp/wayfinder-fsrs-venv/bin/pip install /tmp/wayfinder-py-fsrs
```

Pinned commit output is `9446cb06605c597a063aeee49f7d188d42e34dc2`. Installation used fsrs 6.3.2 and typing-extensions 4.16.0. The standalone probe below exercises the same cases as the initial full-state probe:

```sh
/tmp/wayfinder-fsrs-venv/bin/python - <<'PY'
from datetime import datetime, timedelta, timezone
from fsrs import Scheduler, Card, Rating
s = Scheduler(enable_fuzzing=False)
t = datetime(2026, 10, 1, tzinfo=timezone.utc)
c = Card(card_id=1, due=t)
print('unreviewed', s.get_card_retrievability(c, t))
for seconds in [0, 600, 7 * 86400]:
    t += timedelta(seconds=seconds)
    c, _ = s.review_card(c, Rating.Good, t, 1000)
    print(c.state.name, c.step, c.stability, c.due.isoformat())
before = c.to_dict()
a, _ = s.review_card(c, Rating.Good, t + timedelta(days=1), 1000)
b, _ = s.review_card(c, Rating.Good, t + timedelta(days=1), 100000)
print('duration_state_equal', a == b)
print('input_unchanged', before == c.to_dict())
try:
    s.review_card(c, Rating.Good, t, indirect_confidence=0.5)
except TypeError as error:
    print(error)
PY
```

Expected stdout:

```text
unreviewed 0
Learning 1 2.3065 2026-10-01T00:10:00+00:00
Review None 2.3065 2026-10-03T00:10:00+00:00
Review None 21.42621174777395 2026-10-29T00:10:00+00:00
duration_state_equal True
input_unchanged True
Scheduler.review_card() got an unexpected keyword argument 'indirect_confidence'
```
