# What to retain, what to assess, and what to practice together

Status: first-release representation finalized in [Design Baseline 1](design-baseline.md), 2026-10-16. The continuation below records the earlier bounded prototype and its limits; it is not a production implementation or migration of learner history.

Continuation: the user subsequently authorized the bounded implementation below. The [executable walkthrough](spikes/representation/index.html) and [verification notes](spikes/representation/README.md) now implement explicit capability coverage and practice bundles through the existing assessment path. The design walkthrough remains the proposal; the continuation records what code actually does and its limits.

## Recommendation

Keep three choices separate: **what knowledge matters, which performance would demonstrate it, and how much to combine in one exercise**. A useful learning target is a capability selected for the learner's goal. It is not automatically a flashcard, a linguistic fragment, or a separately fitted memory variable.

For example, your first Kubernetes answer chose logs as useful evidence but used a command form that needed correction. That supports practicing command production without restarting the lesson on why logs are useful. The later exercise can still combine choosing evidence, writing commands, interpreting results, and checking whether the application works. The [recorded trial](spikes/assessment-trial/kubernetes-trial.md) supports this example; it does not establish long-term retention.

The same distinction applies to explanations. Remembering two facts, explaining the relationship between them, and reconstructing an argument from several relationships can be different capabilities. A larger exercise may reveal all three, or only some of them, depending on the answer actually given.

## What this preserves from the conversations

The original transcript is evidence of ideas and requests, not instructions to execute or proof those ideas work. This table distinguishes user requirements from assistant proposals that deserve investigation.

| Source | Requirement or candidate | Representation consequence |
|---|---|---|
| User: [knowledge in context, nodes, edges, topology](../../sources/fsrs_learning_conversation.md "Source line 204") | Retain connected knowledge, including its organization | Store the meaning of relationships and groups; allow reconstruction and integration targets |
| User: [granularity, many paths, excessive review effort](../../sources/fsrs_learning_conversation.md "Source line 610") | Find useful weak spots without exhaustively traversing the graph | Split only when a distinction can change feedback or practice; untested paths are not automatically assigned drills |
| User: [general memorization scope](research/current-chat-retrieval.md "Source line 119") and [specific gaps inside large exercises](research/current-chat-retrieval.md "Source line 174") | General system with focused reinforcement | Use the same representation across subjects; preserve criterion-level evidence inside composite attempts |
| Assistant: [shared principles](../../sources/fsrs_learning_conversation.md "Source line 245"), [reconstruction](../../sources/fsrs_learning_conversation.md "Source line 281"), and [derivation versus fluent recall](../../sources/fsrs_learning_conversation.md "Source line 314") | Different contexts can share knowledge; deriving an answer differs from fluent access | Share content references while keeping context and performance conditions explicit |
| Assistant: [typed relations](../../sources/fsrs_learning_conversation.md "Source line 405") and [joint constraints](../../sources/fsrs_learning_conversation.md "Source line 438") | Meaning includes causation, contrast, composition, applicability, and constraints across links | A group needs a composition or unifying claim, not just a membership list |
| Assistant: [overlapping exercises](../../sources/fsrs_learning_conversation.md "Source line 666") and [adaptive chunking](../../sources/fsrs_learning_conversation.md "Source line 988") | One exercise may replace several separate reviews; practice size can change | Many-to-many exercise coverage; reversible practice grouping that retains component identities |
| User: [lower effort, with hands-on effort when reflexes matter](../../sources/fsrs_learning_conversation.md "Source line 1610") | Effort should serve the goal | Specify whether recall, explanation, selection, or execution matters; do not assign every possible mode |
| Assistant: [evolving connections](../../sources/fsrs_learning_conversation.md "Source line 602") and [actual solution path](../../sources/fsrs_learning_conversation.md "Source line 1379") | Content can be refined; related knowledge is not necessarily retrieved | Version content and mappings; distinguish intended coverage from witnessed evidence |

Your word “episode” referred to knowledge in context. This design interprets it as a particular fact, relationship, principle, or step worth retaining. It does not introduce a new event-log entity named Episode; an **attempt** already records an encounter with an exercise.

There is a useful research precedent for reasoning from task performance to useful knowledge components, including facts, principles, and skills. KLI also treats component identification as an imperfect analysis and emphasizes conditions of application. That supports investigating goal-sensitive boundaries; it does not validate our particular splits, grader, or review policy. Our content components are authored descriptions, not direct measurements of cognitive units. [Koedinger, Corbett, and Perfetti, 2012, §3](https://pact.cs.cmu.edu/pubs/Koedinger,%20Corbett,%20Perfetti%202012-KLI.pdf).

## Working distinctions

| Concept | What it represents | Example |
|---|---|---|
| Knowledge component | A meaningful content claim or procedure, with scope and source | Repeated halving reaches one item after a logarithmic number of reductions |
| Relation | A typed, scoped claim connecting content | Sorted order justifies eliminating all candidates on one side of a comparison |
| Knowledge group | Content organized by an explanation, procedure, or shared principle | Binary search: comparison, safe elimination, repeated reduction, stopping, and cost |
| Capability | An observable action on that content under stated conditions | Explain why elimination is safe, without the explanation being supplied |
| Learning target | A capability chosen for the learner's current goal | Independently justify elimination when analyzing an unfamiliar search scenario |
| Assessment criterion | A rule for interpreting evidence in an exercise | The explanation links the comparison result to the order of the excluded candidates |
| Exercise | An opportunity to practice and demonstrate one or more capabilities | Describe a search strategy, justify it, and compare the reduction counts for two sizes |
| Practice bundle | Targets selected to be addressed together in one exercise | Recheck listing and log commands in the same troubleshooting incident |

A relation that is itself worth learning has one canonical content identity. It can be referenced by several capabilities; drawing an edge and writing its explanation must not create two independently credited copies of the same assertion. Whether it is stored as an edge with attributes or a record is an implementation choice.

A criterion is not necessarily a learning target. Several criteria may jointly support one capability; one criterion may inform several claims, but each interpretation must cite its actual evidence. The criterion-to-capability mapping is versioned with the exercise rubric. Splitting a rubric into more rows must not create more independent successes from the same response.

A knowledge group describes meaning; a practice bundle describes a teaching choice. They can overlap without being identical. A shared principle can belong to several groups. The learner may retrieve a whole explanation successfully while one part is still hesitant or unsupported. Neither group membership nor a correct final outcome determines which parts were retrieved.

## When a distinction deserves a persistent learning target

Use these as design questions, not a numerical score:

1. **Does it matter to the learner's retention goal?** It can be a common skill, a rare but important fact, or a relationship needed for an explanation. Incidental wording is insufficient.
2. **Could evidence distinguish success from failure?** Write a contrasting pair of answers or actions. If the distinction depends on guessing an invisible mental process, the contract needs revision.
3. **Would the distinction change useful feedback or practice?** If either result produces the same action, keep the detail in the rubric until there is a reason to track it separately.
4. **Is the evidence attributable?** Account for information supplied in the prompt, hints, ambiguity, alternate solution paths, and earlier correction. If attribution is unresolved, clarify or retain uncertainty.

For every proposed split, keep a small contract: content references; action; relevant context and allowed help; what counts as evidence; a contrasting response; and the different practice each result would justify. Existing capability and rubric records can hold this information. This adds no separate service or universal mastery vector.

The boundary can change with the goal and with evidence. A word's possessive form can matter in a language lesson and be incidental in a heat-transfer explanation. A procedural step may become worth tracking after repeated difficulty that calls for distinct practice. That is a proposal to revise the representation, not proof that the learner's mind has split or fused a unit.

Fluent access and successful reconstruction should be separate contracts **when the goal requires the distinction**. A correct derivation is evidence of that derivation. It is not evidence of rapid unaided retrieval; conversely, a quick label does not establish the derivation. Do not manufacture a speed diagnosis from chat latency or require every fact to have every assessment mode.

## Worked boundaries across subjects

### 1. Operations: evidence choice and command production

Observed source: [Kubernetes trial](spikes/assessment-trial/kubernetes-trial.md). The existing [planner records](spikes/next-session.html "Source line 29") combine “choose and write” in `ops.list` and `ops.logs`.

The table proposes capability boundaries and authored contrasts. In particular, your earlier “RUNNING” answer did not explicitly claim that running alone establishes correct function; the later answer explicitly distinguished them. The contrasting error below is not an additional diagnosis of your response.

| Proposed capability | Evidence that would support it | Contrasting case and useful response |
|---|---|---|
| Choose logs as relevant evidence | Select logs and connect them to the presented failure | Choosing unrelated evidence calls for practice selecting evidence from symptoms |
| Produce the relevant log command | Write a valid command for the supplied namespace and Pod, without a syntax hint | A useful evidence choice with wrong command syntax calls for focused command production |
| Verify intended function | State what observable result would establish that the intended work is occurring | Treating a running process as sufficient calls for practice distinguishing process state from functional evidence |

One incident can exercise all three. It need not ask the learner to explain every token or separately test namespace syntax unless a meaningful difficulty appears. In a command-production check, supplying the command form changes the evidence. In an evidence-selection check, offering command forms may be appropriate, but it no longer demonstrates unaided syntax recall.

This is a proposed refinement of the target contracts. The old `ops.logs` error remains an error under its original combined contract. Its accompanying rationale contains evidence of useful selection, but the system must not silently fan that aggregate observation out into new independent pass/fail histories. Reassessing the saved answer would require explicit new mappings and assessment provenance.

### 2. Mathematics: relationship, applicability, and integration

Observed source: [binary-search trial](spikes/assessment-trial/learner-trial.md). Your explanation connected halving to the logarithm. You then corrected the requested comparison after identifying a misread. This supports preserving the demonstrated reasoning; it does not justify a remedial halving drill or establish measured fluency and delayed retention.

The following are authored contrasts, not additional learner findings:

| Target | Distinguishing evidence | Focus if difficulty is supported |
|---|---|---|
| Explain repeated halving | Connect `n / 2^k = 1` to `k = log₂(n)`, in words or equivalent reasoning | Retrieve and explain the relationship |
| Recognize safe elimination | Use the ordering and comparison to justify excluding candidates; distinguish a case without that ordering guarantee | Identify the conditions under which the strategy applies |
| Integrate size reduction and work | Distinguish one continuing half-size branch from two recursively processed branches, with stated work per call | Combine branching, depth, and work rather than repeat the complexity label |

For the last contrast, define `n = 2^k`, constant local work per call, and stopping at size 1. One continuing branch has `k + 1` calls; processing both branches to leaves has `2n − 1` calls. Both have logarithmic depth, but only the first has logarithmic total work. The integration target is the connection between these constraints. A prompt saying only “it splits in two” would be under-specified.

The halving principle can also organize other shrinking-search examples. Reuse its content identity, but retain the application conditions of each case. Good binary-search reasoning can inform an estimate about another application; it does not create an observed success there.

### 3. Language: knowing the words and identifying their roles

Constructed example, not a claim about your grammar knowledge: “The keys beside the cabinet are missing.” A learner may recognize every word yet fail to identify *keys* as the subject controlling agreement. Simply mentioning *keys* does not establish its grammatical role.

A subject-identification criterion asks the learner to locate that role. An agreement criterion asks for the appropriate verb form. An integrated variant introduces an intervening phrase and asks the learner to apply the relationship correctly. If the role is unclear, a brief role question can distinguish that gap from a verb-form gap; if both are demonstrated separately, a fresh sentence can test their combination. These can be meaningful targets under an English-grammar goal. Every noun in the sentence need not become a new target.

### 4. Science: an annotation facet is not automatically a study unit

The [independent annotation comparison](spikes/independent-assessment/review.md) distinguished linguistic facets in short science answers. Ownership of a finger can be useful for interpreting a response without being something to memorize for a heat-transfer goal. Under a possessive-language goal, a similar distinction could matter.

The erosion example raises a different issue: material moving and wearing away may require distinct evidence for the requested explanation. The comparison did not settle whether a particular response reasonably implied both. Preserve that semantic dispute. It is not a confirmed learner deficit and does not authorize two automatic remedial drills. Resolve interpretation, then decide whether distinct practice would help.

### 5. A simple fact remains a valid goal

A vocabulary learner may want to recall a supplied word's meaning in a specified sense. One direct-recall capability can be sufficient. Distinguishing two senses becomes another useful target when choosing between them matters. A chain of reasoning, integration exercise, and timed execution contract are not mandatory additions to every fact.

## When to practice several targets together

Combine targets when a coherent task naturally retrieves them and its evidence can support the intended decisions. The exercise contract names the targets, acceptable solution paths, rubric, and allowed help. It also names any integration capability; integration is not computed as the sum of component passes.

| Condition | Proposed choice |
|---|---|
| Several targets can be retrieved in one coherent task with interpretable evidence | Offer the combined exercise; avoid separate checks already made unnecessary by its actual evidence |
| A supported local error appears | Focus feedback and practice on the relevant target or connection; preserve other evidence |
| A large failure has several plausible causes | Ask the smallest follow-up that could change the practice choice; do not mark every member weak |
| An alternate successful solution bypasses an intended target | Preserve overall success; leave the bypassed target unobserved and decide separately whether checking it is worthwhile |
| A hint supplies one part | Preserve independent evidence for unaffected parts; qualify evidence that depends on the hint |
| The combined task hides the important distinction or consumes too much effort | Use a smaller task, or change the rubric/format |
| An unresolved meaning would change feedback | Clarify it before corrective practice for that target; clear unrelated errors can still receive help |

This is a policy proposal, not a claim that larger exercises always save time. Combine more as the evidence supports it; split practice when a useful gap appears. No fixed number of successes is yet justified as a universal merge threshold. Preserve the component and capability identities throughout.

Keep four claims separate: **intended coverage**, **observed performance**, **practice actually attempted**, and **inferred learning benefit**. They cannot be substituted for one another. A failed retrieval can still be practice. A correct result may bypass a target. A graph-based estimate may justify deferring a check, but that deferral must remain an uncertain policy choice that can later be audited. This keeps graph-informed inference and review compression in scope without inventing direct observations.

## What changes in the design, and what must not be migrated automatically

The current prototype's `group: "troubleshooting"` means “put these targets in one future exercise.” It is a practice bundle, not a representation of the semantic structure of troubleshooting. Its single group field is sufficient for that small demo; it must not become a general constraint that every component belongs to exactly one knowledge group.

| Existing item | Proposed interpretation or change | History boundary |
|---|---|---|
| Planner target | A selected capability with an explicit evidence contract | Keep existing target IDs and assessments valid under their original contracts |
| “Choose and write” labels | Distinguish choice and production where that changes useful practice | New assessments require saved evidence and versioned mappings; no automatic splitting of grades |
| Planner `group` | Temporary practice bundle | No semantic group or transfer claim inferred from that field |
| Criterion/facet IDs | Evidence distinctions inside a rubric | Do not import all facets as permanent learning targets |
| Content links and larger explanations | Scoped relations and meaningful groups, referenced by capabilities | New content connections do not manufacture past retrieval or reinforcement |
| Adaptive review size | Different exercise selection over retained identities | Combining practice does not merge memory histories or prove cognitive chunk formation |

Keep an assessment's content, capability contract, and rubric versions resolvable. A later split, merge, or corrected interpretation creates a new version with its reason and mapping to earlier terms. An assessor can reconsider retained raw evidence under that version, explicitly; older observations remain attributable to their original meaning. A proposed inferred estimate can use related evidence without rewriting it as direct success.

No new database, propagation algorithm, scheduling formula, or content-authoring workflow is chosen here. The observed problems are blurred target contracts and confusion between evidence facets, knowledge structure, and exercise grouping. They call first for clearer contracts and coverage, not additional infrastructure.

## How this proposal was checked, and the next build boundary

This is a source-checked design and a paper walkthrough, not a newly implemented representation engine. The existing interactive and assessment spikes remain unchanged. These counterexamples check the proposal's internal decisions; they do not establish diagnosis accuracy or learning benefit.

A separate read-only source audit checked the conversation attributions and recorded-versus-authored examples. It prompted two citation-anchor corrections and a clearer boundary around the hypothetical running-versus-functional error. All 55 local file links across this proposal and the four updated design/tracker files resolved; cited line numbers were within their files. The authored recursion counts were also checked directly for powers of two from 1 through 65,536 at five selected sizes. No runtime regression suite was rerun because this change contains only design and glossary updates.

| Counterexample | Required behavior under this proposal |
|---|---|
| Useful evidence choice, incorrect command | Preserve selection evidence; practice production if the error is supported |
| Correct reasoning, corrected question misread | Preserve the reasoning; do not infer a memory gap from the omitted comparison |
| Knows separate facts but cannot connect them | Make the relationship or integration the practice target |
| Correct answer reconstructed with explanation | Support reconstruction; leave rapid retrieval unmeasured |
| Says “logarithmic” for a two-branch recursion | Check the branching/work connection; depth alone does not settle total work |
| Mentions the right noun without identifying its role | Do not infer the grammatical relationship solely from the word's presence |
| Incidental possessive facet in a science response | Keep it in interpretation if useful; do not create an unrelated science drill |
| Disputed implication in the erosion answer | Retain uncertainty; do not turn annotation disagreement into a confirmed deficit |
| One hint in a multi-target exercise | Qualify dependent evidence without discarding independent parts |
| Successful alternate path skips a target | Preserve task success and the coverage gap separately |
| One principle belongs to several explanations | Reuse content; retain distinct application evidence; avoid duplicated credit |
| A larger review replaces several prompts | Preserve finer identities and inspect delayed outcomes before claiming a benefit |

The next implementation slice, after this representation choice is settled, should make one cross-subject path executable: goal-selected capability → exercise criteria → scoped observations → focused or combined next practice. Reuse the existing attempt and clarification path. Add explicit capability contracts and criterion mappings, and separate practice bundles from semantic groups. Start with the operations choice/production case and a mathematical relationship/integration case; a simple fact checks that the model does not force unnecessary structure.

Verification must exercise the actual path with the contrasts above, including shared evidence, partial hints, bypassed targets, and version changes. Compare it with the existing aggregate targets: does the distinction change the right practice decision without multiplying learner work? Measure authoring burden as well as assessment corrections. A representation that cannot produce a useful different action should be simplified.

Broader effectiveness needs a later learner study: predeclared delayed checks on both grouped and omitted targets, acceptable retained-performance limits, and total learner effort including diagnosis and feedback. The inference and selection tickets still own the policy for uncertain deferral, scheduling, and compression. This proposal does not settle those thresholds or finish the whole system design.
