# Is the observability design ready for a staged implementation plan?

Type: grilling
Label: wayfinder:grilling
Status: open
Mode: HITL
Assignee: unassigned
Parent: ../map.md
Blocked by: 06, 07, 09, 11

## Question

Review the consolidated metric, statistical, collection and dashboard designs against both user goals and all original requirements. Separate the minimum usable slice from later analyses and research-dependent features, attach validation and rollback/withholding criteria to each, and identify every unresolved choice. Decide design readiness without treating prototype arithmetic, an attractive screen or a plan document as empirical validation or implementation authorization.

## Comments

2026-10-15 patch completed: all seven second-audit omissions have concrete integrated specifications and [closure traces](../../skill-maintenance/cross-contract-closure.md). The [readiness review](../readiness-review.md) now marks those omissions patched. Remaining deployment/provider choices, policy assumptions and real semantic/browser/storage/learning qualification are stated separately; the old unspecified integration backlog must not be repeated as current.

2026-10-15 continuation: readiness also depends on the [everyday-learning policy investigation](../../skill-maintenance/issues/14-everyday-learning-policy.md), now drafted with source reviews, corrected edge cases and 43 authored acceptance criteria. The five areas were substantive missing behavior, not merely later experiments. Detailed draft availability, user acceptance of its proposed defaults, implemented correctness and measured learning benefit remain separate states.

The user selected analytical dashboard C on 2026-10-15 and retained A/B's scenarios. The dashboard-direction ticket is resolved within that scope. Carry forward the original prototype's remaining comprehension, burden, browser and accessibility checks here and in the implementation qualification plan; do not reopen the preference question or treat that preference as a test result.

The user subsequently found C hard to understand because of its terminology, found the paired-change display inadequate for time trends, and found the walkthrough steps unclear as workflow. This is an observed clarity problem in the earlier version. The [revised C contract](../c-dashboard-contract.md) and [same walkthrough](../spikes/c-walkthrough.html) address those points with plain labels, dated repeated checks and sequential guidance. Confirm the revision through actual use; source/arithmetic verification alone cannot close that gap.

2026-10-15: after the readability revision and weakest-unit section, the user says “looks good. continue.” Record positive presentation feedback without claiming a formal comprehension study. The [data-contract draft](../data-contract.md) now reconciles complete transactions, time quality, timer restore, exposure, endpoint assignment, unit attribution and saved-report replay, with sixteen future acceptance examples. Its metric dependency, deletion recommendation and real collection/browser qualification remain open. Production implementation remains unauthorized.

2026-10-15 consolidation: the [readiness review](../readiness-review.md) maps settled requirements, first descriptive-release proposals, remaining product preferences, runtime qualification and future experiment decisions. The [deletion recommendation](../deletion-design.md) specifies managed-copy scope, interruption and report effects, with a conditional format gate for selective erasure. No user preference is invented and this readiness ticket remains open.

Dependency refinement: the experiment-contract ticket no longer blocks ordinary descriptive measurement readiness. It still gates any policy comparison/adoption or causal efficiency claim. No experiment decision is closed, and no initial product claim is strengthened by removing that dependency.

2026-10-15: user accepts the recommendation for archive plus whole-library deletion in the first release; individual answer/source erasure is deferred. [The deletion scope decision](11-deletion-contract.md#answer) is resolved, satisfying that dependency. Claims/ranking policy, data reconciliation and overall readiness remain open; this acceptance authorizes no implementation or actual deletion.
