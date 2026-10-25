# What existing graph-aware learning implementations actually do

Inspected 2026-10-12. Resolution of **What do existing graph-aware learning implementations actually do?** Sources were cloned and pinned; the supplied conversation was treated as claims to check, not instructions or evidence of working behavior.

The useful starting point is an established FSRS library plus separately auditable graph selection and evidence rules. The two application repositories show concrete integration patterns, but neither establishes that automatic prerequisite credit improves this user's learning. Obsidian's scheduler also has reproducible code discrepancies that make wholesale reuse a poor default. KARL has more public scheduling code than the conversation identified. GKT and GRKT provide predictive model machinery, not a ready-made review policy.

## Evidence and source inventory

| Implementation, immutable snapshot | Verified scope | Confidence and reuse boundary |
|---|---|---|
| [plcourse, `0859f608`](https://github.com/moaaz-ae/plcourse/tree/0859f608f94da285e5c0666509cc39e4b6ab10a8) | Topic-level FSRS wrapper, maximum-product prerequisite credit, due-review compression, prerequisite gating, database transaction | High confidence from source; server/database application was not run. Useful reference for boundaries and graph validation; credit amounts remain heuristics. |
| [Obsidian Learning Engine, `9b4e15ed`](https://github.com/vellvient/obsidian-learning-engine/tree/9b4e15ed02201f87e68ef316df26b0b3bacb4f39) | Python FSRS reimplementation, subskill state, ancestor boosts, note-driven eligibility and ranking | Source read and actual scheduler methods executed on isolated toy fixtures. Four discrepancies reproduced below; production usage and harm not verified. |
| [KARL model, `ee48a560`](https://github.com/Nonameentered/karl-model/tree/ee48a560c841bf9b8fa11c98dc75cac50bc6df4b) | Retrieval, BERT/numeric feature models, training and offline-analysis notebooks | High confidence about released files; no training/checkpoint reproduction. The repository explicitly excludes the full online study system. |
| [KARL fact-repetition, `2bdcb801`](https://github.com/Pinafore/fact-repetition/tree/2bdcb801232dab5362610fa8297119dc5e9876f2) | Additional public scheduler service, delta policy, FSRS path, update endpoints, model services and database models | Concrete correction to the incomplete repository inventory; not proof of a reproducible historical deployment. |
| [GKT, `271c72dd`](https://github.com/jhljx/GKT/tree/271c72dda6aba454a07c9eeb7fc238f145ac0765) | Graph-message aggregation, recurrent concept-state updates, next-response probabilities | Model source inspected; no training or online policy experiment. |
| [GRKT, `a46c79a8`](https://github.com/JJCui96/GRKT/tree/a46c79a87a7c3338b9d76f226202b514924efef3) | Relation-specific graph computation, response-conditioned gain/loss, time-dependent learning/forgetting | Model source inspected; training not reproduced. No license file found in this pinned tree. |

## plcourse: precise behavior

`SchedulerService.processReview` calls `ts-fsrs`, persists the reviewed topic, logs the interaction, and applies prerequisite boosts inside one database transaction. Its wrapper enables fuzzing and short-term learning. This is a library integration, rather than an independent FSRS implementation. [Review transaction][pl-review]; [FSRS wrapper][pl-fsrs].

`computeFireBoosts` does nothing for Again or Hard. Good multiplies credit by 0.5; Easy by 1. It traverses positive-weight prerequisite edges, multiplies weights along each path, keeps the greatest path product per ancestor, and drops products below 0.001. A diamond contributes once per ancestor through its strongest route, rather than summing every path. The importer constrains edge weights to [0,1] and rejects graph cycles. [Credit traversal][pl-credit]; [weight validation][pl-schema]; [cycle check][pl-cycle].

`applyFireBoosts` only updates existing ancestors in `State.Review`: `S' = S × (1 + boost)`, then `due = last_review + S' days`. It does **not** perform an FSRS review transition for the ancestor and does not refresh its last-review timestamp. Thus an ancestor sufficiently overdue can remain overdue after credit. The due-date formula also fixes the interpretation to the 90%-retention stability interval; it does not call the library's interval function or reproduce its fuzzing. Treat this as a heuristic extension of state, not calibrated evidence of recall. [Database update][pl-update].

`getDailyTasks` first excludes New states and blocks due topics with an immediate prerequisite in Relearning. It compresses an eligible due prerequisite only when another **eligible** due topic has a direct positive-weight edge to it. New-topic eligibility accepts prerequisites in either Learning or Review. This distinction matters: a Learning state is not a measured mastery threshold. Compression checks whether a dependent is due; it does not inspect which prerequisites a selected problem actually elicits or wait for a successful answer. [Selection][pl-select].

The last point is a design risk, not an observed learner failure: a due dependent can be selected without demonstrating every prerequisite. Topic-level success, explicit prerequisite retrieval, and syllabus dependency are different observations. No inspected source establishes that this credit rule has calibrated transfer effects for the intended domain.

## Obsidian: supported features and reproduced discrepancies

The ancestor algorithm is materially different from plcourse. It uses a default weight of 0.3, distance decay 0.5, and a maximum of four hops. A single dictionary indexed by ancestor ID supplies weights across the walk; weights are not retrieved from each traversed edge. `prerequisites`/`dependents` inspect endpoints without filtering relationship type. Each matching ancestor's review entries receive multiplicative stability increases, without the plcourse restriction to Review state. Future due dates extend by part of the remaining interval; overdue dates receive a grace extension from now. [Traversal][ob-anc]; [boost application][ob-boost].

The watcher grades a newly ticked checkbox as Good and invokes chain credit with an empty weight dictionary. The UI action therefore acts as the observation; there is no automatic test of an independently recalled prerequisite at this boundary. The separate daily ranker combines flow-zone eligibility, mastery labels, weak-spot notes, and the number of downstream nodes for which a skill is the sole missing prerequisite. These are inspectable workflow heuristics, not measured learning gains. [Watcher][ob-watcher]; [unlock count][ob-unlock].

These four outcomes were produced by importing the **actual pinned `srs_fsrs.py`** and supplying isolated in-memory/temporary-file fixtures. They establish code behavior, not prevalence, operational severity, or confirmed harm to the author's users.

| Probe | Observed result | What it establishes |
|---|---|---|
| Stability 10 days; elapsed 10; target retention .9; fuzz disabled | `R = 0.8450220974`; next interval = 5 days | The claimed faithful port disagrees with FSRS's normalization. |
| Due prerequisite A in Relearning; due dependent B | `due_today()` returns `[]` | B is locked, but B still compresses A: the remediation review disappears too. |
| Diamond: child 4 depends on 2 and 3; both depend on 1; weights `{1:.8, 2:.3, 3:.9}` | Ancestor 1 emitted at weights .12 and .36; S=10 becomes 15.232 | The earlier weaker result remains in the output when a stronger path arrives; both boosts apply. A strongest-path-only update would give 13.6. |
| Invoke `apply_fire_from_srs` twice with the same recent child event, weight .3 | S=10 → 13 → 16.9 | Reprocessing the same timestamp can apply credit repeatedly without new practice evidence. |

The first result follows from `_FACTOR = 0.9 ** (1 / _DECAY)` at line 106. Official `py-fsrs` subtracts one, so that `R(S,S)=.9`. Its interval equation then gives ten days at S=10 and retention .9. This was checked against pinned official source and direct arithmetic; importing the official package with the system Python stopped on missing `typing_extensions`, so no full official-library execution is claimed. [Port formula][ob-formula]; [official formula, `9446cb06`][fsrs-factor]; [official interval][fsrs-interval].

The second result follows from compression consulting the complete due-ID map, including locked dependents. The same map stores only one key per exercise and only due keys; additional multi-subskill and not-yet-due Relearning cases deserve tests, but were not counted as reproduced findings. [Due selection][ob-due].

The third follows from appending each improved path rather than replacing the prior result. The fourth follows from scanning recent timestamps without a consumed-event identity. Those observations motivate graph-credit deduplication and replay tests; they do not establish that every invocation path duplicates credit. [Ancestor results][ob-anc]; [recent-event scan][ob-replay].

## KARL: model availability is narrower than the whole release

The conversation correctly describes `Nonameentered/karl-model` as a model/retrieval/training release. In its notebooks, `KARLWRetrieval` combines BERT representations and numeric features for the target and retrieved cards, concatenating them for prediction. This is content-aware prediction using related experience, not a rule that a prerequisite must have been retrieved because a dependent was correct. [Notebook model][karl-notebook].

However, the paper points to **Pinafore/fact-repetition**, whose pinned source contains `schedule_delta`, `/api/karl/schedule_v3`, model-service calls, and response updates. The broad statement that no online scheduling implementation is public would therefore be false. A complete reproducible study application and historical deployment are a separate question; they were not reconstructed. [Paper][karl-paper]; [scheduler][karl-policy]; [endpoint][karl-api].

The released delta function predicts current recall, hypothetical next-day recall after correct/incorrect outcomes, and a no-study baseline, then sorts the absolute difference of the expected studied probability and baseline. A source discrepancy merits a targeted spike before reuse: the baseline call receives `date`, although its comment describes tomorrow. The correct/incorrect calls receive `tomorrow`. This is a confirmed code/comment mismatch; its historical study impact is unknown. [Exact calls][karl-policy].

The reported online study has 32 study paths from 27 users and a trivia setting. It motivates testing a content-aware model; it does not validate replacing calibrated item retention with heuristic graph transfer, nor establish results for broad skill maintenance. [Study abstract][karl-paper].

## GKT and GRKT: prediction components, not scheduling answers

GKT represents each concept with a hidden vector. `_agg_neighbors` combines incoming/outgoing graph-weighted messages; `_update` uses an erase/add gate and GRU; `_predict` produces sigmoid response probabilities. `forward(features, questions)` iterates response events and extracts the next-question prediction. The inspected forward path has no elapsed-time input or next-review-date output. Its learned graph/hidden vectors should not be relabelled as causal prerequisite-transfer probabilities. [GKT implementation][gkt-code].

GRKT's `forward` adds distinct related/prerequisite/subsequent relation paths, predicts correctness from mastery minus difficulty, applies response-dependent gain/loss, and models intervening time using learned exponential kernels. Its training base uses binary cross-entropy and evaluates AUC/accuracy. This is more explicit learning-process machinery, but neither the inspected forward contract nor its loss optimizes retained learning per study minute. Moving from response prediction to a scheduling policy requires an additional decision and evaluation. [GRKT retrieval and update][grkt-code]; [training objective][grkt-loss].

The paper's source link is verified, but the pinned GRKT tree contains no license file. Keep it as a research reference pending clarification of reuse permission. Other inspected repositories contain MIT license files: [plcourse][pl-license], [Obsidian][ob-license], [KARL model][karl-license], [fact-repetition][fact-license], and [GKT][gkt-license]. Preserve their notices if copying covered code; datasets, weights, and learning content require their own checks.

## Consequences for the design map

1. **Reuse the scheduler library; test the adapter.** Pin the version, verify `R(S,S)=.9`, ratings, timestamps, learning/relearning, interval limits, and serialization. A README's fidelity claim did not protect the Obsidian port from a basic equation discrepancy.
2. **Preserve explicit evidence separately from inferred credit.** Give each practice event a stable identity; retain exercised skills, assistance, score and source. Make inferred evidence derivable, versioned, and deduplicated instead of repeatedly mutating S with no provenance.
3. **Make graph semantics explicit.** Prerequisite, similarity, and actual retrieval coverage must not share an unconditional credit rule. Validate cycles/weights; aggregate each event–ancestor pair once; do not use the existence of multiple paths as independent evidence.
4. **Keep a direct-review escape route.** Apply eligibility before compression, test locked dependents, and preserve direct probes of uncertain/overdue prerequisites. If substitution is permitted, tie it to demonstrated exercise coverage and an observed outcome.
5. **Use predictive research as challengers to a baseline.** Start with direct-event FSRS. Compare graph-based selection without credit before credit variants, and defer a neural model until there is adequate representative event data. Require held-out direct probes and time-cost outcomes; synthetic consistency tests can reject broken rules but cannot establish educational efficacy.

Outstanding facts: target population/domain, valid exercise-to-skill coverage, acceptable omission risk, and empirical transfer strength. No source here supplies them for this user. Full application integration tests, GPU training, original study replication, and operator validation of real-world severity remain unperformed. Source access itself was successful for every named repository.

## Reproduce the four Obsidian fixtures

The inspected scratch checkout remains at `/tmp/wayfinder-impl.QQAftP/obsidian-learning-engine`. Confirm it with `git -C /tmp/wayfinder-impl.QQAftP/obsidian-learning-engine rev-parse HEAD`; expected: `9b4e15ed02201f87e68ef316df26b0b3bacb4f39`. For another machine, clone the linked repository, check out that commit, and adjust the import path below. This uses Python standard library only, imports unmodified code, and writes state only into an automatically removed temporary directory. No real vault is touched.

```python
import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, "/tmp/wayfinder-impl.QQAftP/obsidian-learning-engine/vault")
from srs_fsrs import FSRS, State, VaultFSRS

now = datetime(2026, 10, 12, 12, tzinfo=timezone.utc)
f = FSRS(enable_fuzzing=False)
print("FSRS", {
    "R(S,S)": f.retrievability(10, 10),
    "interval_S10_p90": f._next_interval(10),
    "reference_factor": 0.9 ** (1 / f._DECAY) - 1,
    "port_factor": f._FACTOR,
})

def card(state=State.Review):
    return {
        "state": state, "stability": 10.0, "difficulty": 5.0,
        "due": (now - timedelta(days=1)).isoformat(),
        "last_review": (now - timedelta(days=11)).isoformat(),
    }

with tempfile.TemporaryDirectory() as td:
    p = Path(td)
    (p / "srs.json").write_text(json.dumps({"reviews": {
        "1:A": {"fsrs": card(State.Relearning)},
        "2:B": {"fsrs": card()},
    }}))
    (p / "edges.json").write_text(json.dumps([
        {"from": 1, "to": 2, "type": "HARD_PREREQ"},
    ]))
    v = VaultFSRS(p / "srs.json", p / "edges.json")
    print("relearning_compression", v.due_today(now))

    v.state = {"reviews": {
        "1:A": {"fsrs": card()},
        "4:D": {"fsrs": card(), "ticked_at": now.isoformat()},
    }}
    v.edges = [
        {"from": 1, "to": 2}, {"from": 1, "to": 3},
        {"from": 2, "to": 4}, {"from": 3, "to": 4},
    ]
    ew = {1: 0.8, 2: 0.3, 3: 0.9}
    print("diamond", v.ancestors_with_weights(4, ew))
    v.apply_fire_chain(4, ew, now)
    print("diamond_stability", v.state["reviews"]["1:A"]["fsrs"]["stability"])

    v.edges = [{"from": 1, "to": 4}]
    v.state["reviews"]["1:A"]["fsrs"] = card()
    ex = {4: {"pct": 0.5, "fire_weights": {1: 0.3}}}
    v.apply_fire_from_srs(ex, now)
    first = v.state["reviews"]["1:A"]["fsrs"]["stability"]
    v.apply_fire_from_srs(ex, now)
    print("repeat_identical_event", first,
          v.state["reviews"]["1:A"]["fsrs"]["stability"])
```

Complete stdout from this script:

```text
FSRS {'R(S,S)': 0.8450220973648142, 'interval_S10_p90': 5, 'reference_factor': 0.9803464944134797, 'port_factor': 1.9803464944134797}
relearning_compression []
diamond [(2, 0.3, 1), (3, 0.9, 1), (1, 0.12, 2), (1, 0.36000000000000004, 2)]
diamond_stability 15.232000000000003
repeat_identical_event 13.0 16.900000000000002
```

`due_today` returns review-key strings; `ancestors_with_weights` returns `(ancestor_id, chain_weight, distance)` tuples. The diamond fixture demonstrates sensitivity to arrival order: a stronger path discovered first may suppress the weaker one. This is why keeping only final per-node maxima before applying credit matters.

[pl-review]: https://github.com/moaaz-ae/plcourse/blob/0859f608f94da285e5c0666509cc39e4b6ab10a8/src/lib/server/services/scheduler.service.ts#L69-L127
[pl-fsrs]: https://github.com/moaaz-ae/plcourse/blob/0859f608f94da285e5c0666509cc39e4b6ab10a8/src/lib/server/fsrs/index.ts#L1-L17
[pl-credit]: https://github.com/moaaz-ae/plcourse/blob/0859f608f94da285e5c0666509cc39e4b6ab10a8/src/lib/server/services/scheduler.service.ts#L130-L166
[pl-select]: https://github.com/moaaz-ae/plcourse/blob/0859f608f94da285e5c0666509cc39e4b6ab10a8/src/lib/server/services/scheduler.service.ts#L10-L66
[pl-update]: https://github.com/moaaz-ae/plcourse/blob/0859f608f94da285e5c0666509cc39e4b6ab10a8/src/lib/server/queries/topic-state.queries.ts#L93-L118
[pl-schema]: https://github.com/moaaz-ae/plcourse/blob/0859f608f94da285e5c0666509cc39e4b6ab10a8/src/lib/scripts/sync-curriculum.ts#L27-L36
[pl-cycle]: https://github.com/moaaz-ae/plcourse/blob/0859f608f94da285e5c0666509cc39e4b6ab10a8/src/lib/scripts/sync-curriculum.ts#L395-L430
[ob-anc]: https://github.com/vellvient/obsidian-learning-engine/blob/9b4e15ed02201f87e68ef316df26b0b3bacb4f39/vault/srs_fsrs.py#L319-L374
[ob-boost]: https://github.com/vellvient/obsidian-learning-engine/blob/9b4e15ed02201f87e68ef316df26b0b3bacb4f39/vault/srs_fsrs.py#L546-L597
[ob-formula]: https://github.com/vellvient/obsidian-learning-engine/blob/9b4e15ed02201f87e68ef316df26b0b3bacb4f39/vault/srs_fsrs.py#L94-L135
[ob-due]: https://github.com/vellvient/obsidian-learning-engine/blob/9b4e15ed02201f87e68ef316df26b0b3bacb4f39/vault/srs_fsrs.py#L668-L709
[ob-replay]: https://github.com/vellvient/obsidian-learning-engine/blob/9b4e15ed02201f87e68ef316df26b0b3bacb4f39/vault/srs_fsrs.py#L711-L738
[ob-watcher]: https://github.com/vellvient/obsidian-learning-engine/blob/9b4e15ed02201f87e68ef316df26b0b3bacb4f39/automation/srs_watcher.py#L117-L137
[ob-unlock]: https://github.com/vellvient/obsidian-learning-engine/blob/9b4e15ed02201f87e68ef316df26b0b3bacb4f39/vault/study_today.py#L62-L74
[fsrs-factor]: https://github.com/open-spaced-repetition/py-fsrs/blob/9446cb06605c597a063aeee49f7d188d42e34dc2/fsrs/scheduler.py#L186-L234
[fsrs-interval]: https://github.com/open-spaced-repetition/py-fsrs/blob/9446cb06605c597a063aeee49f7d188d42e34dc2/fsrs/scheduler.py#L677-L692
[karl-notebook]: https://github.com/Nonameentered/karl-model/blob/ee48a560c841bf9b8fa11c98dc75cac50bc6df4b/karl_training.ipynb#L403-L436
[karl-paper]: https://aclanthology.org/2024.emnlp-main.784.pdf
[karl-policy]: https://github.com/Pinafore/fact-repetition/blob/2bdcb801232dab5362610fa8297119dc5e9876f2/karl/scheduler.py#L83-L157
[karl-api]: https://github.com/Pinafore/fact-repetition/blob/2bdcb801232dab5362610fa8297119dc5e9876f2/karl/web.py#L477-L519
[gkt-code]: https://github.com/jhljx/GKT/blob/271c72dda6aba454a07c9eeb7fc238f145ac0765/models.py#L111-L317
[grkt-code]: https://github.com/JJCui96/GRKT/blob/a46c79a87a7c3338b9d76f226202b514924efef3/model/GRKT.py#L302-L488
[grkt-loss]: https://github.com/JJCui96/GRKT/blob/a46c79a87a7c3338b9d76f226202b514924efef3/BaseModel.py#L45-L72
[pl-license]: https://github.com/moaaz-ae/plcourse/blob/0859f608f94da285e5c0666509cc39e4b6ab10a8/LICENSE
[ob-license]: https://github.com/vellvient/obsidian-learning-engine/blob/9b4e15ed02201f87e68ef316df26b0b3bacb4f39/LICENSE
[karl-license]: https://github.com/Nonameentered/karl-model/blob/ee48a560c841bf9b8fa11c98dc75cac50bc6df4b/LICENSE
[fact-license]: https://github.com/Pinafore/fact-repetition/blob/2bdcb801232dab5362610fa8297119dc5e9876f2/LICENSE
[gkt-license]: https://github.com/jhljx/GKT/blob/271c72dda6aba454a07c9eeb7fc238f145ac0765/LICENSE
