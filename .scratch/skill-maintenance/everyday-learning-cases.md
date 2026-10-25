# Worked cases for everyday learning decisions

Status: authored design examples and future acceptance cases, 2026-10-15. These illustrate the [detailed policy proposal](everyday-learning-design.md); no learner outcome, runtime pass or efficiency gain is claimed. Times below are invented to make the decisions checkable.

## 1. Ten minutes, three curricula, several unfinished needs

The learner selects Mathematics, Language and Operations, in that order, with 600 seconds. The saved state contains:

| Need | Waiting since | Full estimated upper cost | Eligibility |
|---|---|---:|---|
| Explain why a search interval can be discarded | 12 October due check | 180 seconds | Ready; new valid instance |
| Recall one language association | 13 October due check | 45 seconds | Ready; exact cue is legitimate |
| Verify the outcome of a described procedure | 14 October due check | 240 seconds | Ready; written plan, not executed skill |
| Repair an ambiguous tool-command answer | 15 October concern | 30-second diagnosis plus branches of 90 and 150 seconds | Needs 180 seconds, not 120 |
| Start a new mathematics topic | Unstarted | 120 seconds | Ready initial material |

Begin with the oldest eligible due need, not whichever has most dashboard errors. If the first three responses need no repair and match their estimates, they use 465 seconds and leave 135. The diagnostic branch cannot fit. New material can be offered because no remaining pending action fits, with the unresolved command concern visible. Starting it is not completion of the four older needs.

If the first response instead shows a supported connection error, a focused explanation (90) plus fresh verification (150) uses the next 240 seconds. The total is now 420, leaving 180. The language check (45) fits, leaving 135; the procedure check and diagnosis do not. Replan from that outcome, not from the original six-hundred-second wish list. An immediate successful repair leaves its delayed check pending.

If a learner explicitly selects Operations first, record that override; do not pretend Mathematics was completed. Shared targets appear once even if selected by two curricula. Unknown costs cannot be treated as zero to squeeze extra work into the plan.

## 2. A past success and a recent error

Unit A was correct without help on 12 September, with a review due 19 September and no later response. Unit B had one supported independent error on 14 October. As of 15 October:

- A says “Last correct 12 September; review overdue since 19 September.” It belongs to pending checks, not observed errors.
- B says “Error on 14 October,” with its affected mode and answer evidence. It is eligible for the difficulty shortlist.
- The session selector may offer A first because its due need has waited longer. This does not contradict the shortlist: the displays answer different questions.
- No numeric mastery decay or conclusion that B is less knowledgeable than A is justified. If A's next answer is wrong, that becomes new evidence at its actual date.

## 3. The learner knows the rule but misreads the request

The learner correctly explains binary search, then gives the total reductions for 65,536 names when asked for the increase relative to 1,024. They clarify with `log2(65,536) - log2(1,024)` and the reasoning supports the correction.

Accept a scoped misread interpretation, preserve the original answer and supporting clarification, and remove the unsupported error flag. Do not assign a logarithm lesson or demand an arithmetic check merely to finish a rubric. If another criterion still contains an explicit wrong rule, that separate concern remains. Correction time counts as effort; the correction is not a new independent retrieval or demonstrated learning gain.

## 4. New wording is not a new reasoning test

After teaching why binary search can discard a sorted interval, changing only the person's name gives a surface variant. It may be usable practice, but cannot substantiate broader transfer. A new instance requiring the learner to justify the retained interval under a different comparison result can check the same decision under the same target contract.

Changing to an unsorted list tests applicability or method selection; it does not silently join the old explanation trend. Asking a multiple-choice version does not satisfy the unaided explanation requirement. For a direct association such as “mavo → blue,” repeating the same cue after the required delay is appropriate; forcing a new context could change the meaning being tested.

## 5. Seeing the dashboard answer before a check

The learner opens a due unit at 09:00 on 15 October. The evidence panel initially shows dates/results without its answer. Choosing **Check before seeing the answer** can start an eligible check under the existing contract.

Instead, suppose they reveal the worked solution at 09:02, then answer a new instance at 09:05 without in-task hints. Preserve both events. The response may be correct and independent of in-task help, but it is immediate practice after exposure, not the untouched delayed endpoint. Do not advance the simple capability schedule by seven days. Keep the original due obligation and propose the next offer no earlier than 09:02 on 16 October under the provisional 24-hour rule.

A research endpoint requiring seven days without relevant exposure remains unqualified even if the ordinary next-day review succeeds. Its original assignment is not swapped for the later successful response. If the exposure time is unknown, do not invent a 09:02 anchor or certify elapsed delay. Display the qualification limitation and retain ordinary practice options.

## 6. Repair did not work twice

An integrated explanation reveals the same supported connection error. The system gives a concise rule and the learner completes a fresh verification; the same error remains. That is one unsuccessful cycle. A second approach uses a worked contrast, followed by another eligible verification. The same supported error remains: two unsuccessful cycles.

Stop automatic repair and offer review of the explanation/assessment, a justified prerequisite check, or pause. Do not run another rephrased lesson, split the curriculum automatically, or call the learner incapable. Closing and returning tomorrow preserves the concern and its cycles. If the second answer was merely unjudgeable, it is not a second failed cycle; route to review or bounded clarification instead of looping until an error appears.

## 7. A saved report leads to current practice

A saved 8 October report flags a unit. An accepted correction on 10 October removes that error; a new report reflects the correction. Opening the old report still shows its original result and definition. Clicking **Work on this now** resolves current evidence and says the earlier concern has been corrected, then offers current applicable work.

After practice, return to the same old report without mutating it. Provide a link to the current result. If the initiating flag disappeared from a live view, restore focus to its announced updated status or the list heading. A renamed curriculum preserves the target; an archived curriculum is not silently resumed.

## 8. Acceptance cases to carry into implementation

| ID | Trigger and boundary | Required observation |
|---|---|---|
| P01 | Time passes after an independent success | Date/due state changes without a new failure, mastery percentage or reset |
| P02 | E → missing → E on scheduled comparable checks | Prior concern retained; current consecutive error run is one, not two |
| P03 | Three failed criteria from one exercise map to one unit | One episode and one unit flag; no three-trial streak |
| P04 | Scoped misread correction | Remove only its error basis; no fabricated success, extra review or whole-answer pardon |
| P05 | Independent verification after repair | Remove active error label; show immediate recovery and retain ordinary later check |
| P06 | Eligible later due success | Close recovery concern without scheduling an extra flag-clearing test |
| P07 | One unit weak in explanation, unknown in execution | Display distinct streams once under the unit; no average mastery score |
| P08 | Report generated under ranking version 1 | Reopen with version 1; version 2 produces a different recorded calculation |
| P09 | Same cue for a direct fact after a delay | Eligible recall; novelty requirement does not reject a valid cue→fact target |
| P10 | Renamed copy after integrated teaching | Surface variation disclosed; no broader transfer claim |
| P11 | Candidate changes mode, conditions or background demands | Hold comparison or use a different target/stratum; no silent difficulty adjustment |
| P12 | Schema-valid exercise gives away the required rule | Semantic rejection; retry once with reason, then retain an authoring need |
| P13 | Learner uses an unanticipated valid solution | Judge its actual criteria; no failure from answer-string mismatch or prerequisite inference |
| P14 | Hidden evaluation variant enters teaching | Record contamination; no retrospective replacement by a successful retry |
| P15 | Reveal answer, then answer without in-task help | Keep success plus exposure; no delayed qualification or ordinary seven-day advancement |
| P16 | Exposure time is unknown/bounded | Bound-aware eligibility; no fabricated exact delay or migration-time anchor |
| P17 | Two diagnostic branches need 90 and 150 seconds plus 30 for the question | Reserve 180 seconds; 135 remaining cannot qualify it as affordable |
| P18 | Full plan ceases to fit after actual repair | Replan on actual cost; retain unanswered needs and delayed obligation |
| P19 | Selected curricula share one exact target | One schedule/need/attempt cost; source curriculum memberships retained |
| P20 | Return after thirty missed reminders | One pending practice need per exact target; measurement misses remain separately visible |
| P21 | Oldest task cannot fit or has held content | Keep waiting age/reason, offer another useful action, do not substitute an easier mode |
| P22 | Learner explicitly starts new material with overdue work | Respect choice; preserve backlog and future-check consequences; no inferred quota approval |
| P23 | Unknown cost or unreliable elapsed time | No false fit/saving; one exploratory action is clearly labelled and stoppable |
| P24 | Diagnostic prompt shown, not answered, then refreshed | One consumed prompt; preserved draft; no count reset or duplicate use |
| P25 | Three diagnostics across two concerns/session, or across sessions on one concern | Both caps enforced; route to support/review/pause without a grade |
| P26 | “One question” contains three independent diagnostic requests | Three slots; wording cannot bypass the cap |
| P27 | Two supported unsuccessful repair cycles across sessions | Stop automatic repair; keep evidence and offer review/change/pause |
| P28 | Missing or unjudgeable repair verification | Incomplete evidence, not failure; no automatic endless repair loop |
| P29 | Content/assessment correction invalidates a failure cycle | Recompute concern/schedule atomically; preserve actual effort and old judgments |
| P30 | Model timeout after submission | Saved answer and pending assessment survive reopen; no invented grade |
| P31 | Action launched from stale saved report | Resolve current definitions/evidence before selection; historical report unchanged |
| P32 | Return after flag disappears or scope changes | Preserve return scope/date/filter; restore usable focus and announce change |
| P33 | Two tabs compete for the last diagnostic slot | At most one new presentation authorized under the same session/concern allowance |
| P34 | Export/restore during paused repair | Preserve concern links, presentations, cycles, due/next-offer distinction and report rule; no replayed model call or exposure |
| P35 | Reveal an answer, close without attempting, reopen five minutes later | Exposure deferral still applies; a new session cannot bypass it or advance the due schedule |
| P36 | Evidence summary paraphrases the tested rule while the answer is collapsed | Collapse the revealing explanation too, or record its exposure; no false “check before seeing the answer” offer |
| P37 | Review confirms an originally rejected answer satisfied the rubric | Change the historical judgment E→S at its original time; preview actual effects; no new attempt or gain event |
| P38 | New numbers require six versus four halvings using the taught method | Accept a suitable new instance; method reuse is not confused with copying the final answer |
| P39 | Verification repeatedly succeeds only after hints | Retain independent check and offer later check/pause; no automatic endless teaching loop |
| P40 | Each integrated verification reveals a different supported gap | End the original encounter's precedence; put new concerns into ordinary waiting order |
| P41 | Affordable need has unknown historical time while newer dated needs recur | Preserve a labelled first-recorded-ready anchor/order; no invented failure date or permanent last position |
| P42 | Crash after diagnostic reservation, before or after possible browser display | Release only proven non-delivery; uncertain allowance stays reserved; resume same draft and keep burden uncertainty |
| P43 | Two explanations then one verification, or one explanation then two verification attempts, followed by restore | One bound cycle outcome in both cases; a new cycle requires new completed teaching; prior teaching is not in-task help; replay does not multiply cycles |

Each case must use the real boundary named during implementation: authoring acceptance, assessment projection, saved selector/concern transition, timer, report resolver or browser navigation. Deterministic record checks and independent semantic review serve different purposes. A reference answer baked into a fixture cannot prove that the live model recognizes novel valid answers.

## 9. Design choices still proposed

The three-prompt and two-cycle limits, 24-hour next-offer rule after answer exposure, oldest-waiting session order and revised shortlist are explicit starting proposals. The user has requested that these areas be designed, not individually accepted these values. Their rationale and failure cases are now inspectable. Empirical tuning requires actual burden and delayed outcomes; implementation correctness cannot choose the learner's preferred trade-off.
