# Observability design probes

**Throwaway artifacts; all numbers and learner histories are authored.** No product code, learner-model fitting, live telemetry or actual study is included.

- [Detailed C walkthrough](c-walkthrough.html): the selected analytical default, with computed population filters, formulas, evidence, what-if controls, correction snapshots and an in-memory saved report. [Metric/interaction/data contract](../c-dashboard-contract.md). Eight guided situations reset to a known search example; free-play also supports grammar and described operations.
- [C's pure model](c-model.mjs), [HTML shell](c-shell.html), [builder](build-c.py), [calculation probe](c-probe.mjs) and [outputs](c-calculation-results.json) keep arithmetic inspectable. Method comparison and task-mix panels use separately labelled authored populations.

- [Dashboard alternatives](dashboard-prototype.html): A — daily briefing, B — capability notebook, C — analysis workspace. Use the bottom arrows to switch structure and the situation selector to inspect seven cases. `?variant=B&scenario=maintenance` selects a layout and case. Target evidence opens in a dialog; this does not save a real exposure.
- [Numerical assumption lab](analysis-prototype.html): eight misleading headlines with explicit evidence and limits. Reveal/reset controls change only in-memory display state.
- [Analysis script](analysis-probe.py) and [machine-readable outputs](analysis-results.json): standard-library calculations, including exact enumeration of randomization assignments and fair-coin stopping paths.
- [Artifact generator](build-prototypes.py): emits both self-contained HTML files and numerical JSON. No server, framework, model call or dependency installation is needed.

Run from the repository root:

```sh
python3 .scratch/learning-observability/spikes/analysis-probe.py
python3 .scratch/learning-observability/spikes/build-prototypes.py
node .scratch/learning-observability/spikes/c-probe.mjs
python3 .scratch/learning-observability/spikes/build-c.py
```

## Results and boundaries

| Case | Computed result | What it establishes |
|---|---|---|
| One missing endpoint | Conditional success 5/7; completion 7/8; possible fixed-set fraction 5/8–6/8 | Missing outcomes can matter; the range is not a confidence interval |
| Changing difficulty mix | Pooled 26%→64%, while easy 80%→70% and hard 20%→10% | Composition can reverse the apparent direction |
| Duplicate criterion rows | Ordinary Wilson intervals roughly 49%–94% for 8/10, versus 71%–87% for copied 80/100 | The narrower copied-row interval is invalid; independence of the original ten is still an assumption |
| Four randomized family pairs | Mean difference .25; two-sided exact sharp-null p=.125 | Unanimous directions do not establish noninferiority or a sufficiently precise effect |
| Full cost | A:12+28=40 minutes; B:20+12=32 minutes | Answer-only cost ranking reverses; retention comparability remains required |
| Unplaced cost | A:27 placed minutes plus up to20 unknown-placement minutes; B:32 | More than5 additional nonoverlapping minutes reverses the ranking; the scenario is not a measured total |
| Paired change | Three improved, two maintained, two persistent gaps, one missing | Later success counts are not all newly learned capabilities |
| Repeated significance checks | 111796/1048576 false-rejecting fair-coin paths versus43400/1048576 with one final look | 10.66% versus4.14% under the specified toy null; repeated fixed-sample looks change error behavior |

The Wilson formula is documented by [NIST](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm); the [statistical research](../research/statistical-methods.md) supplies the analysis assumptions and primary sources. Exact enumeration has no Monte Carlo error. It also provides no evidence that the toy model describes a learner.

## Verification status

The scripts executed, the randomization result was independently recalculated with exact fractions, both emitted JavaScript blocks passed `node --check`, and document/artifact links were checked. These checks are arithmetic/syntax checks, not browser tests.

Browser inspection of the local `file:` artifact was blocked by the browser security policy on 2026-10-14. No alternate serving or browser route was used. Rendering, interactions, keyboard operation, mobile layout and learner comprehension remain unverified. The mockup is not a finished accessible dashboard.

In the original three-layout mockup, dashboard correction, report saving/export, real filters, exposure collection and application navigation are specified requirements, not working controls. Its controls operate only the displayed authored scenarios. On 2026-10-15 the user preferred C as the default while retaining A/B's scenarios; see [the recorded decision](../issues/06-dashboard-spike.md#answer). No comprehension or learning-benefit result follows from that preference.

The C continuation adds working pure-model filters and an in-memory saved-report copy, but no durable save/export, real correction submission or application navigation. Arithmetic probes confirm 3 improved/2 maintained before a correction and 2/3 after it, an unchanged old snapshot, unchanged totals under highlighting, and no future assessment revisions in earlier snapshots. It counts four later exercise episodes for seven submitted target rows. JavaScript syntax and local references were checked; rendered behavior and usability remain unverified under the same browser security limitation above.

## Revision after clarity feedback

The user reported that C's terminology was difficult, its paired-change bars did not show time trends well, and the guided buttons were not clear workflow steps. The same `c-walkthrough.html` now uses plain labels, moves technical records behind details, and opens on a four-date example with **2 → 5 → 4 → 6** correct-without-help results for the same eight skills. Missing/helped/ungraded results have a separate dashed series and a categorical table. Select October8,15 or22 to update cards, evidence and total course effort (40,62,80 minutes). Older report versions retain only the dates then available.

Walkthroughs now show numbered completed/current/upcoming stages, one current action, its result, and Back/Next/Restart controls. Changing a free-play filter or date visibly pauses the guide. Start with **Follow progress over time** or **Fix a grading mistake**. The latter retains an old 2→5 chart while the corrected report shows3→5, with no new learning event. The prior arithmetic example remains available at October8; the opening view now selects October22.

`c-probe.mjs` reproduces dated/filtered counts, cost windows, correction history and old-snapshot exclusions. Browser interaction, rendered layout and the revised presentation's clarity still need actual observation. The user's negative feedback is evidence about the prior version, not proof that this revision has solved it.

The user subsequently said the revision “looks better.” The requested **Weakest knowledge units** section now flags up to five units, with priority ties, recent check history, reasons and evidence dialogs. Current incorrect answers precede less-established recoveries; latest missing/helped/ungraded evidence appears separately. Selecting an earlier date excludes later checks from this shortlist even if the full trend remains visible. It uses no weighted mastery score, does not fill unused slots with healthy units, and labels recently recovered units accordingly. The probe covers date scoping, correction removal, ties, missing/helped evidence, mode filtering and unchanged ranking under what-if/highlight controls.
