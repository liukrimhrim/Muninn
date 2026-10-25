# Can the learner state avoid false credit while choosing affordable practice?

Type: prototype
Label: wayfinder:prototype
Status: open
Mode: HITL
Assignee: unassigned
Parent: ../map.md
Blocked by: none

## Question

Use a throwaway, runnable state-model spike to contrast blind prerequisite credit with direct evidence, separate recognition from execution, handle ambiguous failures and stale evidence, and show an honest outcome when a required practice format exceeds the time budget. Which behaviors match the intended product?

The bounded clarification continuation below was authorized by the user's “go ahead” after the independent comparison. It preserves original evidence and the earlier misread and Kubernetes choices without resolving the broader model decision or requiring another learner exercise.

## Comments

The coordinator prepared [the standalone state-model spike](../spikes/evidence-policy.html), [eight synthetic replay results](../spikes/replay-results.json), and [the findings and limitations](../spikes/README.md). The actual-library source probe output is also preserved. Local snapshot branch: `codex/prototype/evidence-policy`.

Artifact construction and model replay are complete. Browser visual verification was blocked by the tool's local-URL policy. The user has not reacted to the prototype; this HITL decision remains open and unclaimed for the next session. Do not interpret artifact completion as user agreement or proof of learning efficacy.

Conversation-coverage correction: this spike checks evidence boundaries only. Its blind-credit comparator does not establish that conservative direct observation is the best learner model. It does not exercise adaptive chunking, overlap-aware selection, diagnosis-versus-practice decisions or calibrated indirect inference. Those remain separate open design questions; a useful subsequent spike should compare plausible alternatives around a general memorization example.

## Agreed next-session proposal — 2026-10-14

After the [binary-search trial](../spikes/assessment-trial/learner-trial.md) and [Kubernetes trial](../spikes/assessment-trial/kubernetes-trial.md), the user reviewed this concrete proposal in chat:

| Item | What happened | Proposed action |
|---|---|---|
| 1. Binary search | The learner understood the method and misread part of the question. | Do not add remedial practice because of that misread. |
| 2. Kubernetes commands | The corrected commands were used successfully in a new incident. | At a later session, check them within one short troubleshooting exercise. Skip separate command drills if they are used correctly. |
| 3. Choosing where to fix something | The configuration-based fix followed a hint about where arguments can originate. | In that same future exercise, let the learner locate the problem without that hint. Offer focused help only if the answer shows a need. |

The review explicitly said that items 2 and 3 share one exercise, and invited corrections to either the interpretation or the practice choice. The user's response was: **“all agree”**. These three choices are accepted for the next-session example. Do not reopen this approval or turn it into three separate exercises. No new learner answer is required now.

This accepts the proposed learning behavior for the observed cases. It does not approve every case in the original HTML spike, establish an optimal interval or measured learning benefit, or finalize the general representation, inference and selection models. The later exercise has not run, no date is set, and no reminder has been scheduled. This broader ticket remains open; preserve the accepted subset when reviewing the remaining questions.

## Executable next-session example — 2026-10-14

The [standalone next-session prototype](../spikes/next-session.html) now turns selected recorded response assessments into the accepted plan. It retains ten exact excerpts, the help supplied, and six explicit targets; the three approved future checks share one exercise. [Notes and reproduction instructions](../spikes/next-session-notes.md) and [replay results](../spikes/next-session-replay-results.json) record the verification and limits. Snapshot branch: `codex/prototype/next-session-plan`.

The actual-record replay produces the agreed choices; six hypothetical future variants exercise success, a local error, uncertainty, hinted success, missing observations and a failed outcome without attribution. All 22 replay observations matched, including quote binding and a minimal DOM wiring check. This is not automatic answer assessment, visual browser verification or evidence of learning efficacy. No further learner exercise or reapproval of the same three choices is required for this artifact. The original broader prototype questions and the general model choices remain open; release this bounded implementation claim.

## Answer-assessment connection — 2026-10-14

The [answer intake demo](../spikes/answer-intake/index.html) joins the existing assessment validator and planner through an input-bound evidence record. [Reproduction and limits](../spikes/answer-intake/README.md) explain the current-chat assessment step, retained prompt/answer/context/help, and separate handling of grading uncertainty. Ten recorded responses reproduce the agreed plan; seven constructed contrasts exercise local errors, omissions, unclear wording, hints, misread self-report and off-task instructions. The current assistant authored the judgments and contrasts, so this is not an independent grading evaluation.

All 34 connected replay observations and four CLI checks matched. A fresh single-answer packet can be assessed in chat and connected through the CLI; no automatic model service or persistent learner-state update is implemented. Browser layout, semantic accuracy and learning efficacy remain unverified. The [new protocol](../spikes/answer-intake/assessor-prompt-v2.md) preserves the prior protocol and results as historical artifacts. Snapshot branch: `codex/prototype/next-session-plan`.

The bounded connection work is complete. Release its claim; the broader HITL ticket remains open. The existing accepted three-item plan is unchanged. Independent assessment of unseen answers remains necessary before claiming the inference works reliably; the new contrast policies have not been separately accepted by the user.

## Clarification before corrective practice — 2026-10-14

The user authorized fixing the conflict found in the independent comparison. The existing planner now derives pending clarification from stored assessment records, pauses help only for those targets, and preserves the original error. Correct and wrong replies can resolve the question; unclear replies can stop questioning with assessment unresolved. Unrelated errors remain eligible for help, partial answers do not repeat the full question, and clarification alone cannot clear a later check. [Walkthrough](../spikes/answer-intake/clarification.html) and [implementation notes](../spikes/answer-intake/clarification-notes.md).

Six of 16 initial checks failed before the change. All 22 final focused checks, 35 intake checks, 22 existing planning checks and five CLI/report checks pass. The accepted misread and combined later exercise remain unchanged. Frozen assessments and the independently audited comparison remain unchanged; the comparison runner protects its historical output from changed dependencies. Browser rendering, semantic correctness and learning benefit remain unverified. Snapshot branch: `codex/prototype/next-session-plan`. Release this bounded claim; the broader HITL decision remains open.
