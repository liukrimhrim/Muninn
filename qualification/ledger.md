# Slice 5 coverage ledger

Every case ID the [first-build plan](../.scratch/skill-maintenance/first-build-plan.md#build-order-and-exit-checks) assigns to slice 5, with one disposition each. Written 2026-10-25 against the tree of this commit; test paths are relative to the repository root.

| Disposition | Meaning |
|---|---|
| **existing** | An earlier slice's test already asserts the required consequence at an agreed seam: the real store, commands or HTTP, or (marked "pure rule") the owning module's pure rule function on hand-made inputs. |
| **new** | A deterministic test added in slice 5, through the real store and commands (`tests/test_qualification.py` unless named). |
| **live** | Needs the real model on the [acceptance pack](pack-v1.json): run `uv run python -m tests.qualify` with `ANTHROPIC_API_KEY` set (not yet run; see "Human steps"). |
| **human** | Needs a person, real elapsed time or a decision that is not the build's to make; the reason is given. |
| **known gap** | The situation can arise in this build, and the build does not do what the design asks (deferred work). Each is in the pilot limits statement. |
| **not reachable** | No command in this build can produce the situation (the reason names the missing capability). Recorded so it is not mistaken for coverage; each is a known limit in the pilot limits statement. |

Several cases have two halves (a deterministic invariant and a semantic or human half); both are listed. `Q::` abbreviates `tests/test_qualification.py::`.

## Lifecycle audit cases CCA01–CCA15

| Case | Disposition | Where / why |
|---|---|---|
| CCA01 first answer before grading | existing | `tests/test_workflows.py::test_first_independent_success_schedules_a_check_a_day_after_the_answer` (answer 10:00, graded 10:20, due next day 10:00) |
| CCA02 mixed larger answer | new | `Q::test_one_larger_answer_settles_each_goal_on_its_own_evidence` (A later check, B unresolved/no date, C repair concern); also `tests/test_workflows.py::test_mixed_outcomes_resolve_each_target_separately` |
| CCA03 import 200, begin 3 | new | `Q::test_selecting_two_hundred_goals_and_starting_three_invents_no_backlog` |
| CCA04 two shared curricula | not reachable | No flow creates a shared exact target: reuse links claims, never goals, and linking admitted targets into a second enrollment was deferred in slice 4 |
| CCA05 generate needed explanation | existing | `tests/test_repair.py::test_teaching_is_checked_and_saved_before_delivery_and_completion_is_explicit`; `tests/test_slice2_exit_check.py::test_a_connection_error_is_diagnosed_taught_and_checked_fresh` |
| CCA06 source changes during generation | new | `Q::test_teaching_authored_for_material_that_changed_meanwhile_is_never_delivered` (the late teaching is `stale`, nothing delivered, the answer kept) |
| CCA07 grading arrives backward | existing | `tests/test_corrections.py::test_results_graded_out_of_order_apply_in_the_order_the_answers_happened` |
| CCA08 same obligation in two tabs | existing | `tests/test_later_checks.py::test_a_second_tab_resumes_the_draft_or_starts_extra_work_without_a_second_owner` |
| CCA09 feedback between answer and grade | new | `Q::test_feedback_seen_before_the_grade_never_reclassifies_the_answer` |
| CCA10 answer drawer still open | existing + new | `tests/test_later_checks.py::test_a_view_never_closed_certifies_no_delay_until_the_learner_confirms_it`, `tests/test_evidence.py::test_a_view_with_no_known_end_certifies_no_delay_however_long_ago`; the known-open-during-the-answer half (H) is `Q::test_an_answer_view_open_elsewhere_while_answering_counts_as_help_everywhere` |
| CCA11 historic exposure time unknown | existing | `tests/test_later_checks.py::test_a_view_never_closed_certifies_no_delay_until_the_learner_confirms_it` (learner-confirmed prospective checkpoint) |
| CCA12 no experiment setup | existing | Every slice 1–4 exit check shows dated history without a plan; `tests/test_tracking.py::test_tracking_freezes_its_population_and_assigns_ordinary_checks_before_answers` freezes only future windows with its baseline rule |
| CCA13 frozen plan encounters changes | existing + new | Missing and help: `tests/test_tracking.py` (`…later_windows_become_missing`, `…hint_never_confirmed…`); a changed goal after the freeze keeps the old endpoint: `Q::test_a_frozen_plan_keeps_its_goals_anchors_and_windows_whatever_changes_later`. Adding a brand-new goal to an existing curriculum is not reachable (no command adds one) |
| CCA14 correct but too early | existing (pure rule) | `tests/test_measurement.py::test_the_worked_example_keeps_raw_and_qualified_counts_apart` (5/7 raw, 4QS 2QE 1QX 1QM, range withheld); the store-level partition with real answers is in `tests/test_tracking.py::test_tracking_freezes_its_population_and_assigns_ordinary_checks_before_answers` |
| CCA15 help plus outside window | existing (pure rule) + new | `tests/test_measurement.py::test_each_endpoint_lands_in_exactly_one_bucket_by_precedence` (H with an ineligible reason is QH, reasons kept); with a real answer and store: `Q::test_an_answer_view_open_elsewhere_while_answering_counts_as_help_everywhere` (QH with the aid reason kept) |

### Cross-contract boundary cases X01–X19

| Case | Disposition | Where / why |
|---|---|---|
| X01 pause during delivered combined task | not reachable | Pausing a curriculum or goal has no command (deferred in slice 4); concern pause is covered by P34 |
| X02 abandoned or pending owner | existing | `tests/test_corrections.py::test_a_draft_on_a_corrected_away_opportunity_counts_only_as_practice`, `…test_a_later_answer_still_being_assessed_holds_the_corrected_schedule`, `…test_a_pending_answer_on_a_revoked_draft_does_not_hold_the_schedule`. The explicit "release pending check" command is deferred (not reachable) |
| X03 two unknown-time outcomes conflict | known gap (import only) | The app always records an answer's time, but an archive may carry a submitted answer with no time and restore accepts it; how such answers order and qualify is not qualified |
| X04 exact simultaneous success and error | new | `Q::test_a_success_and_an_error_at_the_same_instant_cannot_certify_recovery` |
| X05 restore during pending ownership | existing | `tests/test_slice4_exit_check.py::test_every_capability_transition_holds_across_a_restart` (offers, next offers and tracking survive restore); restore's new timer activation: `tests/test_exit_check.py::test_after_a_restart_the_page_is_told_to_claim_the_timer_again` |
| X06 valid first answer has unknown time | known gap (import only) | As X03 |
| X07 correction invalidates earlier interval | existing | `tests/test_corrections.py::test_a_corrected_grade_updates_the_effective_state_once_at_the_answer_time`, `…test_a_success_corrected_to_an_error_reopens_the_first_check_and_asks_for_repair` |
| X08 cancel generation after request | existing + new | No cancel command; the closest real paths: a restart's interrupted operation ignores late output (`tests/test_workflows.py::test_a_restart_interrupts_unfinished_operations_and_ignores_their_late_output`) and a late teaching after a content change stays with its input (`Q::test_teaching_authored_for_material_that_changed_meanwhile_is_never_delivered`) |
| X09 definition accepted, study not completed | existing | `tests/test_repair.py::test_teaching_is_checked_and_saved_before_delivery_and_completion_is_explicit` |
| X10 baseline missing/helped/pending | existing | `tests/test_tracking.py::test_tracking_freezes_its_population_and_assigns_ordinary_checks_before_answers` (baseline = last submitted answer; missing stays missing in `measurement._member`) |
| X11 window boundary | new | `Q::test_a_frozen_plan_keeps_its_goals_anchors_and_windows_whatever_changes_later` (an offer exactly at a window's end belongs to the next window; the first window is mature) |
| X12 known late versus uncertain-by-T | not reachable | Reports are live (T = now) and every answer time is known; saved reports with an earlier T are deferred |
| X13 stop tracking midway | existing | `tests/test_tracking.py::test_stopping_tracking_ends_assignment_and_later_windows_become_missing` |
| X14 new curriculum meaning or family | new | `Q::test_a_frozen_plan_keeps_its_goals_anchors_and_windows_whatever_changes_later` |
| X15 help and unusable grading | existing (pure rule) | `tests/test_measurement.py::test_each_endpoint_lands_in_exactly_one_bucket_by_precedence` (U wins) |
| X16 raw and qualified coverage | existing (pure rule) | `tests/test_measurement.py::test_the_worked_example_keeps_raw_and_qualified_counts_apart`; store level: `tests/test_tracking.py::test_a_hint_never_confirmed_keeps_the_raw_grade_but_cannot_qualify_the_claim` |
| X17 same episode assigned to two plans | not reachable | One running plan per curriculum, and no target is shared between curricula |
| X18 prospective reset versus fixed past plan | new | `Q::test_a_frozen_plan_keeps_its_goals_anchors_and_windows_whatever_changes_later` (a checkpoint after the freeze leaves the frozen anchors) |
| X19 a check is not its own prior exposure | existing + new | `tests/test_evidence.py::test_a_delayed_check_starts_24_hours_after_the_latest_relevant_end`; `Q::test_feedback_seen_before_the_grade_never_reclassifies_the_answer` |

## Integrated-design cases I01–I10 and boundaries R01–R11

| Case | Disposition | Where / why |
|---|---|---|
| I01 completed descendant | new | `Q::test_a_real_later_check_keeps_its_week_when_an_earlier_success_is_corrected` (re-anchored seven days from B) |
| I02 open descendant | existing | `tests/test_corrections.py::test_a_draft_on_a_corrected_away_opportunity_counts_only_as_practice`, `…test_a_later_answer_still_being_assessed_holds_the_corrected_schedule` |
| I03 repaired workload | existing | `tests/test_later_checks.py::test_a_repaired_check_is_kept_as_history_and_caught_up_is_reachable_again` |
| I04 whole selected scope | new | `Q::test_caught_up_speaks_about_now_and_never_hides_an_unstarted_goal` |
| I05 reverse-direction reveal | known gap | A reveal of one goal's answer that also answers another goal (shared claim) is reachable; exposure relevance is by exact goal only, because `exposure-scope-1` (checked cross-goal relevance) is not built |
| I06 related versus unrelated | known gap | As I05 |
| I07 target created later | known gap | As I05 |
| I08 historical known cost | existing (pure rule) | `tests/test_measurement.py::test_cost_is_clipped_to_its_evaluation_interval_never_rounded_to_whole_spans`; the store-level cost cutoff is exercised by `tests/test_tracking.py` (cost window) and `Q::test_cost_follows_the_enrollment_identity_across_its_revisions` |
| I09 crossing span | existing (pure rule) | Same test (22 m / 55 m) |
| I10 earlier evaluation, uncertain placement | existing (pure rule) | Same test (evaluation-capped 22 m) plus `tests/test_measurement.py::test_stale_unplaced_and_unknown_time_stay_out_of_the_total` (unplaced time beside, never added) |
| R01 correction reveals newer exposure | new | `Q::test_a_later_check_with_the_answer_in_view_cannot_reanchor_after_a_correction` |
| R02 correction removes the only anchor | existing | `tests/test_corrections.py::test_a_later_real_check_reanchors_when_an_earlier_success_is_corrected` (B + 24 h) |
| R03 mixed larger exercise, one slot affected | known gap | A correction that affects one goal of a mixed draft releases the whole draft (it is kept); per-slot release was deferred in slice 3 |
| R04 replay, repeated correction, restore | existing | `tests/test_corrections.py::test_a_repeated_correction_adds_no_concern_or_schedule_revision`; `tests/test_slice3_exit_check.py::test_corrections_keep_history_and_leave_unrelated_work_usable` (restore) |
| R05 extra or released answer | existing | `tests/test_corrections.py::test_a_second_owner_of_a_consumed_check_does_not_move_it`, `…test_a_draft_on_a_corrected_away_opportunity_counts_only_as_practice` |
| R06 due boundary and first-later evidence | new | `Q::test_caught_up_speaks_about_now_and_never_hides_an_unstarted_goal` (due exactly now is not caught up) |
| R07 later error after a qualifying descendant | new | `Q::test_reanchoring_cannot_clear_a_later_error` |
| R08 relevance uncertainty | known gap | As I05; the replay half (no fresh model judgment on a read) is covered by `Q::test_reading_any_page_writes_nothing_and_calls_no_model` |
| R09 day boundary, empty window, unknown duration | existing + not reachable | Empty interval and unplaced durations: `tests/test_measurement.py` (clip and unplaced tests). Local-midnight day buckets are deferred |
| R10 actual recall stream | existing | `tests/test_later_checks.py::test_a_corrected_grade_takes_its_rating_out_of_the_review_stream`. An unavailable engine is not reachable (fsrs is a pinned dependency of the running process) |
| R11 earlier award and later history | new + not reachable | The live indicator goes stale with time: `Q::test_caught_up_speaks_about_now_and_never_hides_an_unstarted_goal`. Saved awards are deferred |

## Journey cases W01–W08 and boundaries B01–B07

| Case | Disposition | Where / why |
|---|---|---|
| W01 known hint, unknown time | new | `Q::test_a_known_hint_without_a_clock_is_kept_and_an_invented_time_refused` (through the real import path) |
| W02 bounded hint time | existing | `tests/test_workflows.py::test_an_acknowledged_hint_makes_its_targets_helped_and_bounds_its_time` |
| W03 scoped larger answer | existing | Same test (t1 independent, t2 helped); `tests/test_evidence.py::test_help_on_one_criterion_only_affects_the_targets_it_covers` |
| W04 help in another screen | new (defect fixed) | `Q::test_an_answer_view_open_elsewhere_while_answering_counts_as_help_everywhere` |
| W05 same goals, new enrollment revision | new | `Q::test_cost_follows_the_enrollment_identity_across_its_revisions` (10 m on E@1 + 20 m on E@2 = 30 m in the frozen plan's cost) |
| W06 goals change | new | Outcome population frozen: `Q::test_a_frozen_plan_keeps_its_goals_anchors_and_windows_whatever_changes_later`; cost by enrollment identity: `Q::test_cost_follows_the_enrollment_identity_across_its_revisions` |
| W07 shared work | not reachable | A span names one enrollment; explicit attribution to two enrollments cannot be recorded. A two-curriculum session is reported as uncertain membership (`tests/test_sessions.py::test_time_in_a_session_over_two_curricula_is_never_split_by_guessing`) |
| W08 corrected attribution and replay | not reachable | No attribution-correction command and no saved reports |
| B01 invalid or unknown hint time | new (defect fixed) | `Q::test_a_known_hint_without_a_clock_is_kept_and_an_invented_time_refused` |
| B02 uncertain versus known display | existing | `tests/test_workflows.py::test_an_unacknowledged_hint_cannot_certify_independence`, `…test_a_hint_cannot_be_revealed_after_the_answer_is_submitted` |
| B03 several hints in one attempt | new | `Q::test_two_hints_in_one_answer_stay_two_scoped_entries` |
| B04 inherited versus ambiguous scope | existing | `tests/test_sessions.py::test_time_in_a_session_over_two_curricula_is_never_split_by_guessing` |
| B05 new enrollment and narrow roots | not reachable | One enrollment per curriculum; no narrower cost views |
| B06 scope does not override time or quality | existing | `tests/test_measurement.py::test_stale_unplaced_and_unknown_time_stay_out_of_the_total` |
| B07 frozen definitions and old reports | existing + not reachable | A cohort has no edit command after freezing (`measurement.stop_tracking` is the only revision); saved reports are deferred |

## Everyday-learning cases P01–P43

| Case | Disposition | Where / why |
|---|---|---|
| P01 time passes after a success | new | `Q::test_a_month_away_leaves_one_overdue_check_per_goal_not_thirty_misses` |
| P02 E → missing → E | existing + not reachable | Concern reuse keeps one concern: `tests/test_repair.py::test_a_reused_concern_takes_in_new_errors_from_the_same_answer`. Error-run counts belong to the weak-unit shortlist, which is not built |
| P03 three failed criteria, one unit | existing | One concern per answer: same test. Unit flags not built (as P02) |
| P04 scoped misread correction | existing | `tests/test_corrections.py::test_a_misread_correction_removes_the_error_without_inventing_a_success` |
| P05 verification after repair | existing | `tests/test_repair.py::test_a_fresh_integrated_check_resolves_the_concern_without_moving_the_later_check` |
| P06 eligible later due success | new (defect fixed) | `Q::test_an_eligible_later_success_closes_a_repair_that_was_shown_only_with_help` (capability goal, and the closing answer's correction reopens it), `Q::test_a_recall_review_closes_a_repair_waiting_for_its_later_check` (recall goal, closed by the rating), `Q::test_correcting_an_earlier_answer_never_reopens_a_repair_a_later_check_closed` |
| P07 weak explanation, unknown execution | existing + live | Execute goals get no exercise (`tests/test_content.py::test_a_drafted_outline_that_breaks_a_rule_is_refused` and `outline_view.without_exercise`); no average score exists anywhere. Live: pack M4 shows whether the model keeps describe-procedure and execute apart |
| P08 report under ranking v1 | not reachable | No saved reports and no weak-unit ranking |
| P09 same cue after a delay | existing | `tests/test_slice4_exit_check.py::test_recall_reviews_and_budgets_keep_unmet_needs_and_survive_restore` (the Tarvi prompt is served again for its review) |
| P10 renamed copy after teaching | existing + live | Deterministic variant checks: `tests/test_content.py::test_a_variant_that_is_not_a_fresh_comparable_task_is_refused`; whether a real variant is a fresh instance is semantic (live, during a real repair) |
| P11 candidate changes mode/conditions | existing | `tests/test_content.py::test_a_variant_that_is_not_a_fresh_comparable_task_is_refused` (same coverage required) |
| P12 exercise gives away the rule | existing + live | Retry once then a visible authoring need: `tests/test_workflows.py::test_a_refused_draft_gets_one_targeted_retry`, `…test_two_refusals_leave_a_visible_authoring_need_and_no_third_call`; a semantic giveaway needs the live run |
| P13 unanticipated valid solution | live | Pack H2-a, H3-a, H3-d |
| P14 hidden evaluation variant enters teaching | new + not reachable | The pack's held-out variants never reach a drafting request: `Q::test_held_out_text_in_any_drafting_request_is_caught`. The app has no evaluation variants, so in-app contamination recording is not reachable |
| P15 reveal answer, then answer | new + existing | `Q::test_an_answer_after_seeing_the_claims_keeps_its_success_but_not_a_week`; with a feedback view: `tests/test_later_checks.py::test_seeing_the_answer_defers_the_next_offer_but_never_moves_the_due_time` |
| P16 exposure time unknown/bounded | existing | `tests/test_later_checks.py::test_a_view_never_closed_certifies_no_delay_until_the_learner_confirms_it` |
| P17 branch reservation 90/150/30 | existing | `tests/test_sessions.py::test_a_question_reserves_room_for_its_worst_branch` |
| P18 plan stops fitting after repair | existing | `tests/test_sessions.py::test_an_overrun_stops_offering_keeps_the_answer_and_more_time_continues` |
| P19 curricula share one exact target | not reachable | As CCA04 |
| P20 return after thirty missed reminders | new | `Q::test_a_month_away_leaves_one_overdue_check_per_goal_not_thirty_misses` |
| P21 oldest task cannot fit or is held | existing | `tests/test_sessions.py::test_a_budget_too_small_for_any_check_keeps_every_need_and_says_why`; held content: `tests/test_corrections.py::test_flagged_material_holds_what_rests_on_it_and_unrelated_material_stays_usable` |
| P22 new material with overdue work | existing | `tests/test_sessions.py::test_a_session_proposal_names_what_fits_and_that_new_material_waits`; the `new_material` override is exercised in `tests/test_slice4_exit_check.py` |
| P23 unknown cost or unreliable time | existing | Teaching is offered as unknown length (`practice.UNKNOWN_LENGTH`) in `tests/test_sessions.py`; unknown time is never a saving (`tests/test_measurement.py::test_no_spans_means_unknown_not_zero`) |
| P24 prompt shown, refreshed | new | `Q::test_a_refreshed_or_second_tab_question_uses_one_diagnostic_slot` |
| P25 diagnostic caps | existing | `tests/test_repair.py::test_three_questions_per_concern_across_sessions_then_help_under_uncertainty`, `…test_one_question_with_three_requests_uses_the_whole_session_allowance` |
| P26 one question, three requests | existing | `tests/test_repair.py::test_one_question_with_three_requests_uses_the_whole_session_allowance` |
| P27 two unsuccessful cycles | existing + new | `tests/test_repair.py::test_two_unsuccessful_repair_cycles_stop_automatic_repair`; across a restore: `Q::test_a_paused_repair_comes_back_from_restore_exactly_and_stays_paused` |
| P28 missing/unjudgeable verification | existing | `tests/test_repair.py::test_a_helped_or_missing_check_never_loops_back_into_teaching` |
| P29 correction invalidates a failure cycle | existing | `tests/test_corrections.py::test_a_corrected_fresh_check_rederives_its_repair_cycle` |
| P30 model timeout after submission | existing | `tests/test_workflows.py::test_an_assessment_timeout_preserves_the_answer_and_changes_nothing_else`; `tests/test_exit_check.py::test_a_model_failure_preserves_the_answer_until_a_retry` |
| P31 action from a stale saved report | not reachable | No saved reports |
| P32 return after a flag/scope change | human | Return navigation keeps the hash route; no dashboard filters exist to preserve. Browser observation in the issue Comments; a learner check is a human step |
| P33 two tabs, last diagnostic slot | new | `Q::test_a_refreshed_or_second_tab_question_uses_one_diagnostic_slot` |
| P34 export/restore during paused repair | new | `Q::test_a_paused_repair_comes_back_from_restore_exactly_and_stays_paused` |
| P35 reveal, close, reopen five minutes later | existing | `tests/test_later_checks.py::test_seeing_the_answer_defers_the_next_offer_but_never_moves_the_due_time` |
| P36 summary paraphrases the rule | existing + human | "What this rests on" records exposure (slice 4 browser check); whether a page paraphrases an answer is a human review of the screens |
| P37 review confirms a rejected answer | existing | `tests/test_corrections.py::test_a_corrected_grade_updates_the_effective_state_once_at_the_answer_time`, `…test_accepting_does_exactly_what_the_preview_showed` |
| P38 new numbers with the taught method | existing + live | Fresh-instance checks: `tests/test_content.py::test_a_fresh_instance_with_the_same_coverage_passes`; a real variant's quality is live |
| P39 verification succeeds only after hints | existing + new | `tests/test_repair.py::test_a_helped_or_missing_check_never_loops_back_into_teaching`; its later success now closes the concern: `Q::test_an_eligible_later_success_closes_a_repair_that_was_shown_only_with_help` |
| P40 each verification shows a new gap | new | `Q::test_a_fresh_check_that_shows_a_different_gap_opens_an_ordinary_concern` |
| P41 unknown historical time vs new needs | known gap (import only) | As X03 |
| P42 crash around a diagnostic reservation | existing + not reachable | A delivered prompt counts conservatively and resumes (`Q::test_a_refreshed_or_second_tab_question_uses_one_diagnostic_slot`); reserved/confirmed presentation states were deferred in slice 2 |
| P43 explanations/verifications then restore | existing + new | One cycle per completed teaching: `tests/test_repair.py`; restore keeps cycles: `Q::test_a_paused_repair_comes_back_from_restore_exactly_and_stays_paused` |

## Module cases M01–M10

| Case | Disposition | Where / why |
|---|---|---|
| M01 single-owner coverage | existing | `tests/test_architecture.py` (all five tests); `tests/test_library.py::test_a_module_cannot_write_or_read_another_modules_records` |
| M02 acyclic imports | existing | `tests/test_architecture.py::test_the_allowed_import_graph_is_acyclic` |
| M03 atomic correction, crash points | existing | `tests/test_workflows.py::test_a_failure_between_evidence_and_practice_writes_leaves_nothing_half_done`, `…test_a_refusal_after_partial_writes_keeps_none_of_them`, `…test_a_restart_interrupts_unfinished_operations_and_ignores_their_late_output`, `…test_a_retried_submission_creates_one_answer_and_one_assessment_operation` |
| M04 shared qualification | new (defect fixed) | `Q::test_an_answer_view_open_elsewhere_while_answering_counts_as_help_everywhere` (Practice's schedule and Measurement's raw H/QH read one Evidence rule); unknown claims are refused in `evidence.claim_reasons` |
| M05 prospective assignment | existing | `tests/test_later_checks.py::test_a_second_tab_resumes_the_draft_or_starts_extra_work_without_a_second_owner`; `tests/test_tracking.py` assignment at offer creation |
| M06 historical context | new | `Q::test_reading_any_page_writes_nothing_and_calls_no_model`; S/T reproducibility of the live report: `tests/test_slice4_exit_check.py::test_every_capability_transition_holds_across_a_restart` (same pages before and after restore at the same clock) |
| M07 budget without reverse import | existing | `tests/test_architecture.py` (Practice cannot import Measurement); `tests/test_sessions.py` budgets |
| M08 external failure | existing | `tests/test_workflows.py::test_an_assessment_timeout_preserves_the_answer_and_changes_nothing_else`, `…test_an_invented_quote_is_refused_and_retried_once` |
| M09 version continuity | existing + human | Export/restore of every module's records: all exit checks with `FailIfCalled`. A real physical migration waits for the first format change (human decision: declare format 1 released and freeze its fixture) |
| M10 locality experiment | human | A judgment over real change history; slice 5's edits are listed in the issue (each cross-module edit names its contract) |

## Review-response cases V01–V12

| Case | Disposition | Where / why |
|---|---|---|
| V01 mixed roles | existing | `tests/test_later_checks.py::test_a_second_tab_resumes_the_draft_or_starts_extra_work_without_a_second_owner` (`extra`, `owner`) |
| V02 correction then release | existing | `tests/test_corrections.py::test_a_draft_on_a_corrected_away_opportunity_counts_only_as_practice` |
| V03 claim agreement | new | As M04 |
| V04 invalid clock | existing | Server time is authoritative and the raw client time is kept (`tests/test_workflows.py::test_an_acknowledged_hint_makes_its_targets_helped_and_bounds_its_time`); an invented instant is refused on import (`Q::test_a_known_hint_without_a_clock_is_kept_and_an_invented_time_refused`) |
| V05 unavailable engine | not reachable | fsrs is pinned in the running process; a build without it cannot start |
| V06 transaction failure | existing | `tests/test_workflows.py::test_a_failure_between_evidence_and_practice_writes_leaves_nothing_half_done` |
| V07 submission crash | existing | Before commit: `tests/test_library.py::test_a_failing_command_writes_nothing`; after commit: `tests/test_workflows.py::test_a_restart_interrupts_unfinished_operations_and_ignores_their_late_output`; lost response: `tests/test_library.py::test_retrying_a_command_returns_the_saved_receipt_without_writing_again` |
| V08 stale tabs | existing | `tests/test_later_checks.py` two-tab test; `tests/test_exit_check.py::test_a_stale_page_must_refresh_before_writing` |
| V09 budget correction | existing | `tests/test_sessions.py` (overrun, add time, too-small budgets); unknown time is not zero (`tests/test_measurement.py::test_no_spans_means_unknown_not_zero`) |
| V10 import/export seam | existing | One read transaction under the store's single lock (`Store.snapshot`); every restore re-checks receipts against records and the watermark (`tests/test_library.py::test_a_tampered_or_truncated_archive_is_refused`). No threaded race test: by construction |
| V11 forbidden access | existing | `tests/test_architecture.py::test_the_check_catches_seeded_violations` |
| V12 lifecycle versus domain result | existing | `tests/test_workflows.py::test_an_invented_quote_is_refused_and_retried_once` |

## Compatibility cases C01–C20

| Case | Disposition | Where / why |
|---|---|---|
| C01 round trip | existing | `tests/test_library.py::test_restore_into_an_empty_store_reproduces_the_library`; every exit check restores with `FailIfCalled` |
| C02 physical upgrade | human | No released format exists to upgrade from; the design forbids inventing one. Decide when format 1 is released and freeze its fixture |
| C03 multi-release path | human | As C02 |
| C04 crash before migration commit | human | As C02 (no migration exists) |
| C05 crash after migration commit | human | As C02 |
| C06 failed verification | existing | For restore: `tests/test_library.py::test_owner_validation_errors_refuse_the_restore`, `…test_a_tampered_or_truncated_archive_is_refused`; for migrations as C02 |
| C07 recovery after use | new (defect fixed) | `Q::test_a_restore_never_hides_work_the_archive_does_not_contain` |
| C08 future/invalid archive | existing | `tests/test_library.py::test_a_corrupt_archive_is_refused_before_anything_is_created`, `…test_a_tampered_or_truncated_archive_is_refused`, `…test_a_store_from_a_newer_release_is_refused_unchanged` |
| C09 reorder/shared target | new + not reachable | Reorder: `Q::test_reorganising_the_outline_changes_no_evidence_due_date_or_count`; shared target as CCA04 |
| C10 added/removed target | not reachable | Adding or removing requirements and retiring memberships were deferred in slice 3 |
| C11 split/merge | not reachable | Deferred in slice 3 |
| C12 correction after mapping | existing | `tests/test_corrections.py::test_a_late_grade_on_an_old_goal_version_stays_with_that_version`, `…test_a_corrected_grade_updates_the_effective_state_once_at_the_answer_time` |
| C13 policy replacement | existing + not reachable | Model change: a reassessment records the answering model and keeps history (`tests/test_corrections.py`); a scheduler policy transition is deferred until a real library exists (slice 4 decision 2) |
| C14 unavailable engine | not reachable | As V05 |
| C15 retry and stale client | existing | `tests/test_workflows.py::test_a_retried_submission_creates_one_answer_and_one_assessment_operation`; `tests/test_exit_check.py::test_a_stale_page_must_refresh_before_writing` |
| C16 late model output | existing | `tests/test_workflows.py::test_a_restart_interrupts_unfinished_operations_and_ignores_their_late_output` |
| C17 time and absence | existing + browser | Stored instants are UTC strings, compared byte for byte across restore; local display observed in the browser run (issue Comments) |
| C18 snapshot concurrency | existing | As V10 |
| C19 engine/host cutover | new (defect fixed) | `Q::test_a_restore_never_hides_work_the_archive_does_not_contain` (switching back over destination answers is refused); activation durability: `tests/test_library.py::test_the_active_store_choice_is_durable` |
| C20 divergent copies | new (defect fixed) | `Q::test_a_restore_never_hides_work_the_archive_does_not_contain` |

## Observability cases O01–O18

| Case | Disposition | Where / why |
|---|---|---|
| O01 activity versus learning | existing + new | Retries make one attempt (`tests/test_workflows.py::test_a_retried_submission_creates_one_answer_and_one_assessment_operation`); helped stays helped; the summary headline now names met later checks only when they happened (`Q::test_a_session_summary_says_when_later_checks_were_met`) |
| O02 partial/ambiguous evidence | existing | `tests/test_workflows.py::test_not_shown_is_never_a_failure` |
| O03 delayed-check denominator | existing + human | Change pairs and the full matured denominator: `tests/test_tracking.py::test_tracking_freezes_its_population_and_assigns_ordinary_checks_before_answers`. The authored eight-target cohort needs real delayed data (human/elapsed) |
| O04 exposure and first endpoint | existing + new | First assigned endpoint is kept (`tests/test_tracking.py`); a failed due check stays listed: `Q::test_a_due_check_after_a_helped_first_answer_is_listed_when_it_fails` (defect fixed) |
| O05 maintenance | new (defect fixed) | `Q::test_a_session_summary_says_when_later_checks_were_met`, `Q::test_a_session_summary_counts_a_later_check_answered_with_a_mistake`; later-check counts in `tests/test_slice4_exit_check.py` |
| O06 time ledger | existing | `tests/test_measurement.py::test_every_kind_of_work_is_counted_in_its_group` (40 minutes); correction time is now recorded as `assessment_correction` in the browser (Comments) |
| O07 timing failure | existing + browser | Two tabs, restart tails, clock jumps, stale spans: `tests/test_exit_check.py` timer tests, `tests/test_measurement.py`; hidden tab/pagehide observed in the browser |
| O08 corrections | existing | `tests/test_corrections.py::test_a_corrected_grade_updates_the_effective_state_once_at_the_answer_time` |
| O09 curriculum evolution | new | `Q::test_reorganising_the_outline_changes_no_evidence_due_date_or_count` |
| O10 efficiency signal | not reachable | Evidence-linked efficiency flags are not built |
| O11 restore and metric version | existing | `tests/test_slice4_exit_check.py::test_every_capability_transition_holds_across_a_restart` (tracking report identical at the same S and T after restore); the browser run repeated it (only the live "as of" time differs) |
| O12 browser comprehension | human | A learner must find a gain, a maintenance result, an unresolved need and where time went, uncoached. The agent's timed walk-through is recorded in Comments, not as a comprehension result |
| O13 measurement burden | new + browser | Reading pages writes nothing (`Q::test_reading_any_page_writes_nothing_and_calls_no_model`); feedback is optional; progress time is overhead (`progress_inspection`) in the browser ledger |
| O14 no data | existing | `tests/test_measurement.py::test_no_spans_means_unknown_not_zero`; slice 1 summary tests |
| O15 analysis trace, cohort mismatch | existing + not reachable | Frozen cohorts keep exact targets (`Q::test_a_frozen_plan_keeps_its_goals_anchors_and_windows_whatever_changes_later`); chart drilldowns and cohort comparison tools are not built |
| O16 repair-path attrition | not reachable | Repair-path comparisons are not built; the per-goal later-check history now keeps failed and replaced checks (O04) |
| O17 sensitivity and incomplete evidence | existing | `tests/test_measurement.py::test_a_missing_only_range_needs_every_other_endpoint_qualified` (the same rule on 3/5–4/5; the authored 5/8–6/8 example is not replayed) |
| O18 optimization gates | human | No policy comparison exists; Gate A/B decisions belong to the evaluation contract |

## Plan acceptance table (first-build plan, "Acceptance pack and verification")

| Row | Disposition |
|---|---|
| New text contains conditions and connected reasoning | live: pack M2, M3 against their reference notes; the harness checks that authoring created no learner records |
| Source contains instructions to the assistant | existing (`tests/test_content.py::test_source_text_reaches_the_model_only_as_delimited_data`) + live: pack M5 and response H2-d |
| Single fact, intended recall direction | live: M1, H1; deterministic recall path: `tests/test_slice4_exit_check.py::test_recall_reviews_and_budgets_keep_unmet_needs_and_survive_restore` |
| Correct parts, wrong connection | existing (`tests/test_slice2_exit_check.py::test_a_connection_error_is_diagnosed_taught_and_checked_fresh`) + live: H3-b |
| Several possible causes | existing (`tests/test_repair.py::test_competing_causes_get_one_question_and_its_answer_chooses_the_help`) + live: H3-c |
| Omitted explanation, shorthand or unfamiliar correct method | existing (`tests/test_workflows.py::test_not_shown_is_never_a_failure`) + live: H1-c, H2-a, H3-a, H3-d |
| Trivial misread with sound reasoning | existing (`tests/test_repair.py::test_a_supported_misread_gets_a_brief_correction_and_no_repair`) + live: H2-c, a new held-out analogue |
| A correct final result includes local error or help | existing (W03 rows) + live: H4-d |
| An exercise mentions an untested prerequisite | existing: an answer is projected only onto the goals its exercise covers (`tests/test_workflows.py::test_delivery_admits_only_the_covered_targets_with_open_initial_obligations`), projections carry no inference hypotheses, and reviews exist only for rated owned recall answers (`tests/test_later_checks.py::test_help_an_extra_answer_or_a_corrected_grade_never_makes_a_review`) |
| Another source matches or conflicts with existing knowledge | existing (`tests/test_corrections.py` reuse tests) + live: the harness lists any reuse proposal between the pack's unrelated materials as a finding |
| Content or target mode changes | existing (`tests/test_corrections.py::test_a_changed_condition_holds_the_exercise_written_for_the_old_goal`, `…rebound…`) |
| Judgment is corrected or a result arrives twice | existing (`tests/test_corrections.py`, `tests/test_workflows.py::test_a_retried_submission_creates_one_answer_and_one_assessment_operation`) |
| Shared evidence appears in several target projections | existing + new: one answer settles each goal on its own evidence (`Q::test_one_larger_answer_settles_each_goal_on_its_own_evidence`); counts are per goal and per check, never per projection |
| Setup/feedback consume time or diagnostics cannot fit | existing (`tests/test_sessions.py`) |
| No usable exercise or model output exists | existing (`tests/test_workflows.py::test_two_refusals_leave_a_visible_authoring_need_and_no_third_call`, `tests/test_repair.py::test_teaching_refused_twice_is_not_ready_and_never_tried_a_third_time`) |
| A later session and schedule correction | existing (slice 4 exit check) + human: the genuinely elapsed later session |
| Export/restore and a later architecture upgrade | existing (every exit check) + new (C07/C19/C20) + human (first format change) |
| Interrupted migration or unsupported newer format | existing (C08) + human (C04/C05, no migration exists) |
| Curriculum reorganization versus changed meaning | new (C09/O09) + existing (`tests/test_corrections.py`) |
| Model or scheduling policy changes | existing + not reachable (C13) |
| Progress, retention and efficiency metrics | O01–O18 rows above |

## Human steps (owed, not done)

1. **Review the pack's reference notes and judgments** before the live run; amend anything a person disagrees with (they are the build agent's reading).
2. **Live run:** `ANTHROPIC_API_KEY=… uv run python -m tests.qualify`, then open the drafted library it names in the app, edit each outline and record substantive errors, edits and editing minutes in the report's reviewer lines. Inspect every disagreement against its rationale. Never turn the counts into a percentage.
3. **Live learner flow in a real browser** on previously unauthored material with the real model (still open from slices 1–4).
4. **Genuinely elapsed later session** (still open from slice 4): practise, wait at least a day of real time, return and take the due checks.
5. **Learner comprehension of the progress views (O12):** an uncoached learner, timed, on the questions in O12; record confusion as a failed clarity observation.
6. **Declare format 1 released** (or not) and freeze its baseline fixture; C02–C05 and M09's migration half start then.
