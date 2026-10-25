# From recorded answers to the next session

Status: throwaway executable example of the three [agreed practice choices](../issues/04-evidence-spike.md#agreed-next-session-proposal--2026-10-14), prepared 2026-10-14. This is a bounded continuation of the existing evidence-policy spike, not a completed general learning engine.

Open [next-session.html](next-session.html). It starts with the real record and its proposed next practice; nothing needs to be answered or configured. The walkthroughs and free-play buttons explore hypothetical later results. Reloading or restoring the record resets the in-memory state. There is no server, database, network request, background task, review date or FSRS update.

## The question and result

Can the supplied assessment records produce the three choices the learner accepted, without repeating the command drills or treating hinted work as independent evidence?

The current record produces no immediate remedial task and one later troubleshooting exercise covering the two command forms and locating the source of configuration. The supported binary-search misread produces no extra remediation. The program does not decide whether the original answer was a misread; that interpretation was supplied by the chat assessment and accepted by the user.

Hypothetical outcomes change the plan:

| Supplied observation in an imagined later session | Computed action |
|---|---|
| All three planned targets demonstrated without hints | Stop separate drills in that hypothetical session |
| Log-command error; other two targets demonstrated | Focus help on the log command; preserve the successful targets |
| Source choice unclear | Ask one clarification; do not label the target failed |
| Source choice correct with a hint | Retain a later check without that hint |
| Only commands observed | Keep the source check pending; do not infer its result |
| Whole task failed, no target observations | Clarify the outcome without assigning failures to every component |

These variant choices are authored experiments. The user's acceptance covered the original three choices, not every future branch in this demo.

## Input, state and boundaries

- Ten exact response excerpts from the two recorded trials, with source-file references, shared exercise IDs, assessor observations, reasons and help. This is a selected view, not the complete transcript or every assessable target.
- Six target records, including a binary-search relationship, the corrected size comparison, command recall/selection, a repair-location decision and verification reasoning. The corrected comparison does not create another observation of the halving explanation. These are authored examples, not a discovered knowledge graph or a universal component taxonomy.
- Pure append, evidence, status and planning functions in the HTML's `next-session-model` script. Existing observations remain in history; duplicate record IDs add no evidence. All user-facing response text uses DOM text content.
- One explicitly authored exercise group joins the three approved future checks. The model never infers demonstrated knowledge from membership in that group, and does not optimize coverage or estimate transfer.
- The planner offers focused help for observed errors and clarification for unresolved interpretations, while retaining the agreed later checks. It uses no weighted sum. A later unhinted observation satisfies only its named target for that hypothetical session.

The existing [evidence-policy demo](evidence-policy.html) and [diagnosis demo](diagnosis-prototype.html) remain intact. Their pure-model/VM-replay pattern is reused, but their operational prerequisites, seven-day constants and fixed component-probe sequence are not imported into this example. The earlier answer-assessment validator requires each criterion to be present; it is not appropriate for this selective observation ledger and is not reused.

## Reproduce and verify

```sh
node .scratch/skill-maintenance/spikes/replay-next-session.mjs
```

The runner loads the exact model and records in the HTML and writes [next-session-replay-results.json](next-session-replay-results.json). The experiment checks the accepted plan, six hypothetical branches, duplicate delivery, history preservation, conflicting knowledge evidence and unchanged input state. It also checks every excerpt against its source file, recording source hashes. Quote fidelity does not validate the assessment's meaning.

The page script and its real button handlers also run against a minimal DOM surface as a wiring check. This is not a browser rendering or accessibility check. All 22 replay observations matched on 2026-10-14 using Node.js v26.0.0. Actual browser layout and interaction remain unverified: earlier browser access to local artifacts was denied, and no alternate browser route was used to work around that restriction.

## What remains open

The observations are authored assessments, not automatic grading of unseen answers. The later responses are hypothetical; no elapsed interval, learner benefit, retained ability or real cluster operation was measured. Ordinary scheduling for other knowledge is outside this demo. A correct response after help does not establish how the learner would have performed without it.

The general content representation, inference over unobserved knowledge, adaptive exercise coverage, content-entry workflow and evaluation contract remain open. This artifact gives those decisions a runnable accepted example; it does not settle them. Snapshot branch: `codex/prototype/next-session-plan`.

Continuation: [answer intake](answer-intake/README.md) now places the existing full-criterion assessment validator before this selective observation ledger. Its adapter retains unobserved/ambiguous criteria in the attached assessment and forwards only direct observations. This is reuse at a separate boundary; the original prototype and its 22-observation report remain unchanged. New raw packets can be assessed in chat and connected through the CLI, while automatic semantic grading remains unimplemented and unvalidated.
