# Can a larger exercise lead to specific, revisable reinforcement across subjects?

Type: prototype
Label: wayfinder:prototype
Status: resolved
Mode: HITL
Assignee: Codex
Parent: ../map.md
Blocked by: 08

## Question

Model small binary-search and English-grammar topics, then build a standalone interactive prototype of larger exercise → diagnosis → focused reinforcement → integrated recheck. Show what each response establishes, what remains uncertain, and why the next exercise is selected. Include a missing fact, missing connection, selection difficulty, multiple gaps, success with a local weakness, and evidence that contradicts the current diagnosis. Stop diagnosis within a visible budget and preserve unknown knowledge.

## Comments

The user approved this concrete next step with “go ahead” after the proposal in the current chat. Representation and inference decisions remain open; this prototype supplies evidence for their discussion. Curated content, self-assessment against rubrics, and authored example responses are acceptable prototype assumptions. The prototype does not establish learning efficacy or automatic grading accuracy.

Use the [comprehensive retrieval](../research/conversation-retrieval.md), especially the original binary-search, knowledge-unit/review-unit, and successful-but-hesitant examples. No weighted selection score, backend, persistence, or production model is required.

The [interactive diagnosis prototype](../spikes/diagnosis-prototype.html) and [model notes and replay findings](../spikes/diagnosis-notes.md) are prepared. Both subjects use the same decision logic. Eighteen authored walkthroughs and additional boundary observations were replayed from the exact embedded model; browser interaction and layout remain unverified. Local source snapshot: `codex/prototype/diagnosis-loop`.

On 2026-10-13, the user confirmed the explained sequence: “yes, the sequence makes sense.” The agreement covers trying a larger exercise, investigating an incomplete answer with smaller questions as needed, practicing the identified gap, and trying a different larger exercise. If reliable evidence already identifies the gap, focused practice can come first. This is agreement on the sequence; diagnosis accuracy, learning benefit, interface usability, and the other walkthrough cases remain unconfirmed. Keep this broader prototype decision open. The next design question is what in an actual answer distinguishes a missing fact, a missing connection, and a slip well enough to select useful practice.

The user then authorized designing that answer-to-diagnosis step with “go ahead.” The [draft assessment and follow-up rules](../diagnosis-design.md) include constructed answer branches across binary search, grammar, and a fictional procedure, plus a manual counterexample review. They preserve answer evidence, distinguish omissions from errors, retain possible slips and multiple gaps, and stop when follow-ups do not justify a specific target. This exposes the existing HTML's boundary: it receives rubric judgments and uses a fixed probe order; it does not implement the new assessment proposal. The draft is prepared for discussion, not accepted on the user's behalf. No real learner data or automatic grading accuracy was measured.

The user subsequently said “go” to building the answer-assessment trial. The [working trial](../spikes/assessment-trial/README.md) now records semantic assessments made by Codex in this chat for ten constructed responses across binary search and grammar. It validates criterion coverage, quoted evidence, and exact input binding, and provides a standalone page for human judgments before revealing AI results. Fourteen structural probes passed. The page also prepares arbitrary new answers for assessment through this chat and imports the returned records. It makes no live model calls. The same assistant wrote and assessed the batch; real learner data, independent human comparison, grading accuracy, and browser interaction remain unverified. A human next-step judgment for case B01 has been requested, not supplied or inferred. Snapshot: `codex/prototype/answer-assessment`.

On 2026-10-13, after explanations of the reviewer role, assessment choices, and the grammar criterion, the user said: “done the review. i think you judgement makes sense”. This is qualitative feedback on the judgments they reviewed. The message does not specify case coverage or individual ratings, and no exported review records were received. The earlier request for an independent next-step answer did not produce a separate answer before discussion of the AI judgment. Do not count this feedback as a blinded comparison or numerical agreement.

## Answer

Resolve this prototype discussion with support for the proposed direction: start with a larger exercise, use answer evidence and smaller questions when needed to identify a useful practice target, practice that target, then check a different larger exercise. The user confirmed the sequence and subsequently reported completing the assessment review and finding the judgment sensible. This supports continuing the design; it does not establish that the diagnosis is correct for real learners or that targeted practice improves retention.

The discussion also exposed wording that needed explanation: the learner-versus-reviewer role, the assessment choices, and identifying a noun's role rather than merely mentioning it. Treat this as observed usability feedback, not proof that the interface is self-explanatory. No interface change is implied by this resolution.

The [validation examples and outcomes decision](05-pilot-outcome.md) remains open for testing the full loop on actual learner responses. Structured human comparison, delayed learning outcomes, and the broader representation, inference, and selection decisions remain open. The original run report retains zero structured human comparisons; no ratings were inferred from the user's general feedback.
