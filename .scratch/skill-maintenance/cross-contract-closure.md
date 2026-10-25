# Cross-contract patch: case-by-case verification

Status: design verification, 2026-10-15. The user requested “patch those gaps.” All seven findings in the [second audit](cross-contract-audit.md) now have concrete proposed rules, record bindings, visible behavior and build-slice ownership. This record checks the design, not an implemented application. The original audit remains available as provenance.

Subsequent audit: [Remaining gaps after the lifecycle and observability patch](integrated-design-audit.md) found four unresolved interactions. In particular, X07 below did not specify what happens when the corrected transition already has a completed descendant, and the milestone rule conflicted with retaining replaced obligations as unsatisfied. The [follow-up closure](integrated-design-closure.md) now patches those cases and the exposure/cost findings. These earlier traces retain their bounded value; neither closure is proof that the entire design has no other gaps.

Canonical patches: [one consistent learning lifecycle](learning-lifecycle-contract.md) and [tracking plans and claim-qualified calculations](../learning-observability/tracking-contract.md). The main build, material, everyday-learning, compatibility, observability data/C contracts, delivery plan and readiness review are reconciled to them. No app code, model integration, prototype page or live learner record is changed.

## Finding closure

| Finding | Concrete resolution | Canonical section |
|---|---|---|
| A01 First independent success | First later capability check at actual answer +24h; target-specific initial errors/omissions; no invented study | [First evidence](learning-lifecycle-contract.md#2-first-evidence-and-the-next-check) |
| A02 Selected versus admitted practice | Enrollment practice entries, explicit admission, shared schedule, pause/open-task rules, separate denominators/milestones | [Admission](learning-lifecycle-contract.md#1-selecting-goals-does-not-create-a-review-backlog) |
| A03 New teaching/variants | Three authoring intents, accepted teaching definition before delivery, actual completion/verification binding, bounded retry/stale/cancel behavior | [Authoring](learning-lifecycle-contract.md#3-authoring-is-a-checked-operation-before-delivery) |
| A04 Competing real attempts | Owned obligation offers, preserved extras, pending/release rules and occurrence-ordered atomic recomputation | [Ownership/order](learning-lifecycle-contract.md#4-one-due-opportunity-two-tabs-and-late-grading) |
| A05 Exposure ordering/recovery | Response interval, ongoing view state, supported ended-by boundary and prospective checkpoint without invented past timestamps | [Exposure](learning-lifecycle-contract.md#5-exposure-has-an-end-and-uncertainty-has-a-prospective-recovery) |
| A06 Legitimate comparison creation | Ordinary history plus preview/freeze/use-ordinary-reviews/close workflow; explicit baseline/windows/assignment/stop and curriculum-change rules | [Tracking lifecycle](../learning-observability/tracking-contract.md#1-ordinary-history-works-before-a-tracking-plan-exists) |
| A07 Raw versus qualified metrics | Two axes, exhaustive disjoint qualified partition, preserved full denominator and raw assessability, claim-specific formulas/withholding | [Qualified counts](../learning-observability/tracking-contract.md#4-two-axes-for-every-endpoint) |

## The fifteen original audit cases

All dates/times below are authored UTC examples. “Verified” means the specified records/rules produce the stated document-level trace, not that a command handler has been executed.

| Case | Trace through the patched contracts | Design result |
|---|---|---|
| CCA01 First answer before grading | Admit target; own initial offer; answer 15 Oct 10:00; accept success 10:20; use answer occurrence | First later capability due 16 Oct 10:00. No study or second immediate quiz |
| CCA02 Mixed larger answer | Bind requirements for A/B/C; accepted result A fully demonstrated, B omitted, C explicit error; resolve each target separately | A later check; B initial/clarification; C supported concern/repair. No blanket pass/fail |
| CCA03 Import 200, begin 3 | Save goal set of 200 unstarted entries; session preview admits three; no learning evidence merely from starting | Goal denominator 200; admitted 3; unstarted 197; zero invented missed reviews or demonstrations |
| CCA04 Two shared curricula | Second curriculum's start preview activates its two already admitted exact targets; existing schedules reused; pause first enrollment | Two schedule identities retained; no duplicate initial tests, reviews or effort; shared active work continues |
| CCA05 Generate needed explanation | Assessment creates scoped concern; teaching intent saves request; semantic/reference gate accepts teaching; actual presentation then completion; fresh variant binds completed study refs | Delivered explanation has provenance; verification refers to actual teaching, not the proposed intervention; display alone is not completion |
| CCA06 Source changes during generation | Request binds source v1/target v1; content revision holds dependent current definitions before output returns; delivery rechecks | Old output saved as stale for current delivery; no v2 stamping. Prior answer and unrelated work preserved; reuse compatible content or show authoring need |
| CCA07 Grading arrives backward | Owner A success at 10:00, extra B error at 10:05; B grade commits first; late A grade replays A→B from occurrence evidence | Historical A transition retained; current B repair survives. Reverse grade arrival yields same effective need, without erasing either answer |
| CCA08 Same obligation in two tabs | Two distinct starts compete atomically; one owner, other resumes or is extra; each actual response gets its own attempt | Both raw answers retained; at most one consumption of the same obligation. Extra success cannot award a second interval or FSRS review |
| CCA09 Feedback between answer and grade | Answer ends 10:00; feedback exposed 10:01; assessment/rating saved 10:02 | Earlier answer unaffected by later feedback. Feedback defers future eligibility at its actual scope |
| CCA10 Answer drawer still open | Reveal yesterday, availability ongoing; response interval overlaps relevant aid | No “24h since opening” certification. Usable aided response H; unknown availability yields uncertain qualified evidence. Close/establish end before a future independent check |
| CCA11 Historic exposure time unknown | Preserve unknown timing; supported checkpoint says prior exposure ended by 15 Oct 12:00; no later exposure; future answer in later session at 16 Oct 12:00 | Prospective 24h condition can qualify. Earlier reports/unknown timestamps stay unchanged; outside-report limitation disclosed. Without a supported end bound the hold remains |
| CCA12 No experiment setup | Learner imports/practises for two weeks, never starts tracking | Ordinary dated history/effort/goals available. No manufactured same-set prospective comparison. A later plan freezes only future windows and identifies its prior baseline rule |
| CCA13 Frozen plan encounters changes | Add a target after freeze; reveal help for an assigned check; skip another; close windows | Added target outside original cohort but visible in goals/history; helped/ineligible and missing endpoints stay in original P; no substitution or hidden extra test |
| CCA14 Correct but too early | P=8 raw 5S+2E+1M; one S fails minimum delay | Raw 5/7 correctness and 7/7 grading coverage; qualified 4QS+2QE+1QX+1QM; coverage 4/8, conditional 4/6. Qualified missing-only range withheld |
| CCA15 Help plus outside window | One matured submitted endpoint has usable judgment, relevant help and known out-of-window occurrence, all by report T | One QH by fixed precedence; both help/window reasons retained. Not also QX; P unchanged; reason counts labelled overlapping |

## Additional boundaries checked while patching

| Case | Required consequence |
|---|---|
| X01 Pause during delivered combined task | Original prompt/rubric/answer binding stays fixed; finish or leave draft; genuine observed evidence remains, but paused scope is not reactivated for follow-up |
| X02 Abandoned or pending owner | Unsubmitted release preserves draft/exposure; submitted owner never expires silently. Explicit pending release makes late result extra; unresolved chronology can still hold advancement |
| X03 Two unknown-time outcomes conflict | Receipt order cannot establish latest/recovery/streak; hold affected advancement. A supported prior-occurrences boundary and a fully scoped new independent check can resolve current need without rewriting old order |
| X04 Exact simultaneous success and error | Receipt sequence makes processing deterministic, but conflicting simultaneous evidence cannot certify recovery; retain concern/uncertainty |
| X05 Restore during pending ownership | Same obligation/offer survives; accepted retry returns receipt; timer's new activation grants no new check ownership. Restore validation writes no learning event |
| X06 Valid first answer has unknown time | Keep success and timing limitation; do not use grading/import time. A supported prospective boundary can create a future check with its own honest reason |
| X07 Correction invalidates earlier interval | Recompute from effective historical judgments; preserve former schedule and dependent obligation lineage. No new attempt, review, exposure or automatic model call |
| X08 Cancel generation after request | Late candidate stays tied to cancelled input; never presented automatically. Reusing accepted content still requires compatible current dependencies |
| X09 Definition is accepted, study not completed | Exposure may exist; no completed study or completed repair cycle is invented. Verification cannot bind a merely planned/completable intervention |
| X10 Baseline missing/helped/pending | Keep designated latest attempt or honest empty baseline; endpoint-only evidence can qualify, but independent paired change remains unavailable. No search for a convenient older baseline |
| X11 Window boundary | F=15 Oct 12:00; first window ends 22 Oct 12:00. Answer exactly at end is outside the first half-open window; a report at that time matures its endpoint. It is not retroactively assigned to the next window |
| X12 Known late versus uncertain-by-T | Definitely after T: endpoint M, no future grade. Unknown occurrence straddling T: preserve raw candidate grade with limitation, qualified uncertainty, no exact by-T completion rate |
| X13 Stop tracking midway | Stop prevents new assignments; fixed future checks stay N until their original close, then M with stopped-plan reason. No denominator shrink or false learning failure; ordinary practice continues |
| X14 New curriculum meaning or family | Keep old cohort target/family contract; do not relabel the endpoint with new meaning. New plan/series for changed scope, history preserved |
| X15 Help and unusable grading | QU takes precedence over QH; preserve both reasons and assistance. Grading coverage falls because the judgment is unusable, not because a valid answer was too early |
| X16 Raw and qualified assessment coverage | Changing only a delay/exposure qualification cannot change raw graded count. QX is not a failure or missing judgment, and never vanishes from P |
| X17 Same episode assigned to two plans | Both prospective refs may be valid; one actual attempt/effort episode remains. No multiplication of participants or minutes |
| X18 Prospective reset versus fixed past plan | A new checkpoint can enable future ordinary checking; it cannot substitute a frozen cohort anchor or cure an old ineligible endpoint |
| X19 A check is not its own prior exposure | The current response/retrieval does not reset its own delay to zero; older attempts and actual hints/views during it still count. Later rating/grade arrival does not move its retrieval time |

## Verification performed and remaining limits

Read the changed contracts together and checked the record roles, independent timing/assignment boundaries and claimed denominators. Checked the partition across all 18 raw-state/eligibility combinations and all 5,832 three-endpoint combinations: exactly one bucket per endpoint, equal raw/qualified matured populations, no qualified success from an ineligible/uncertain S, and raw grading coverage unchanged by qualification. Checked the eight-target example, first-success/exposure 24-hour arithmetic and half-open weekly boundary. These are small authored calculations of the proposal, not tests of a product implementation.

Verified 261 local links and 74 Markdown heading anchors across the 19 scoped documents, separately from content correctness. The fifteen CCA and nineteen boundary-case rows are complete and unique. Snapshot verification compares only the explicitly changed design files against the attached research checkout; unrelated working-tree changes are preserved. Existing prototype logic and report definitions are not rewritten to make this new contract appear implemented.

The seven omissions are patched in the design. Numeric policy defaults remain inspectable assumptions; deployment/provider selection, actual storage/browser/model qualification, semantic accuracy and genuinely delayed learning/cost outcomes remain separate work. No further user exercise or approval of internal field names is needed to complete this patch.
