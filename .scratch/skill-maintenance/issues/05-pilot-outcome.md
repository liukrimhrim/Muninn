# Which examples and outcomes should validate the general system?

Type: grilling
Label: wayfinder:grilling
Status: open
Mode: HITL
Assignee: unassigned
Parent: ../map.md
Blocked by: none

## Question

Choose contrasting examples that test the shared model across subjects and knowledge types, together with delayed-recall outcomes, learner scope, and time budget. These examples validate the general system; they do not restrict its product scope.

## Comments

During initial preparation, the coordinator asked about a first pilot and used Kubernetes as a provisional example. The user subsequently confirmed a general system focused on memorization-oriented learning. Product scope is therefore settled in [the scope decision](08-product-scope.md). This ticket now concerns representative validation examples, retention outcomes and time budgets.

On 2026-10-13, the user said “go” after the proposal to test the full sequence with actual learner responses. Begin a [live chat trial](../spikes/assessment-trial/learner-trial.md), using a fresh binary-search task as a provisional first example. The user answers as learner; Codex assesses the response and chooses any follow-up from its evidence. No response or result has yet been collected. Prior teaching in this conversation is recorded as exposure. This starts an exploratory attempt; contrasting subjects, delayed outcomes, broader learner scope, and evaluation thresholds remain undecided. Do not resolve this ticket from authorization to begin.

The first actual learner response is now recorded in the trial. Codex judges the search procedure, safe elimination, and halving-to-logarithm explanation supported. The answer omits the requested increase between list sizes, so the next action is a single comparison follow-up. No explicit knowledge error or need for reinforcement has been established. This is one assessor's judgment of one real answer; independent assessment, remedial benefit, and retention remain unmeasured.

The learner then supplied `log2(65,536) - log2(1,024)` and explicitly reported a trivial misread, asking that it be distinguished from a real knowledge gap. The first live attempt is complete with no reinforcement needed. The [diagnosis design](../diagnosis-design.md) now separates answer completeness from practice need and prefers a brief correction over an unnecessary diagnostic turn when the surrounding reasoning is sound. Release the claim; the broader validation decision remains open. This case supplies usability and assessment feedback, not evidence that a gap was repaired or learning retained.

The user chose “k8s commands and ops. I know some, but the mastery is never solid” for the next learner exercise. Start a [simulated Kubernetes investigation](../spikes/assessment-trial/kubernetes-trial.md) with real learner responses. This is an explicit choice of validation content, not a change to the general product scope. The learner's self-report does not identify a particular gap. Distinguish remembering a command, knowing what evidence to collect, and interpreting that evidence; no cluster execution is authorized or needed for this chat exercise. Broader validation choices remain open.

On 2026-10-14, the learner chose logs and Deployment details, with a log-command syntax error and a readiness-probe hypothesis. The trial preserves useful evidence selection, corrects the command and briefly explains probe effects without treating the ambiguous hypothesis as a confirmed misconception. Return the requested simulated logs and configuration; the learner's proposed fix and verification remain pending. No operational execution or retained learning has been established.

The learner then proposed editing the Deployment and adding `APP_MODE=production`, which addresses the simulated evidence. Supply the exact environment-list YAML without treating their shorthand as a demonstrated misconception, then continue to verification. The conceptual remedy is supported; exact YAML recall and recovery verification are not yet independently demonstrated.

The learner selected a Pod listing and expected Running after the update. Correct `show po` to `get po`; their short answer does not assert that Running alone proves health. Close the guided walkthrough with a simulated snapshot and tutor-supplied additional checks. Begin brief practice of the two corrected command forms, listing Pods and reading logs. Useful evidence selection and remedy reasoning remain credited; immediate practice, a fresh larger exercise, and delayed retention are separate outcomes. No real cluster recovery or complete independent verification is claimed.

Both focused commands were then supplied correctly: `kubectl -n billing get pods` and `kubectl -n billing logs invoice-abc123`. Record immediate recall after help, then move to a fresh report-worker incident where the learner chooses evidence sources. Command selection in that incident and retained recall are still unobserved; this result does not establish lasting mastery or a causal benefit from the intervention.

The learner begins that incident with `kubectl -n analytics get po` and explains checking Pod status. This supplies correct selection and syntax in a fresh context after recent teaching. Return the fixed simulated listing; the next investigation step remains the learner's choice. No delayed-retention result is available.

After seeing CrashLoopBackOff, the learner correctly requests the named Pod's logs to investigate the error. Both corrected command forms have now been selected and written appropriately in the fresh incident without new syntax hints. Return the frozen application error; interpretation and remedy remain pending. Record immediate application, without inferring durable mastery or intervention efficacy.

The learner correctly identifies an unsupported option but proposes removing it in code and rebuilding before its source has been established. Ask one focused question about locating the argument; explain that container configuration can also supply it and record that as help. Preserve the correct log interpretation and avoid judging against undisclosed scenario facts. A stable gap in configuration knowledge is not established by this single hypothesis.

After that hint, the learner chooses the valid namespaced Deployment edit command, searches for the flag and proposes removing it if present. Reveal the active container args, accept removal in the simulation, and continue to recovery verification. This is a useful application of the configuration distinction with help; it neither establishes independent prior recall nor warrants further gap diagnosis. No actual build or deployment occurred.

The learner finishes by correctly proposing `get po`, explicitly distinguishing Running from intended function, and choosing logs to check report processing. Return simulated Ready/Running status and report-completion messages, then stop the exercise. The trial now includes focused practice and a fresh larger task: both command forms applied correctly; source-location repair used a hint; verification reasoning applied an earlier taught distinction. Preserve those different evidence conditions. Release the active claim without resolving this broader decision. Independent assessment, durable retention, learner effort, representative sample choices and acceptance thresholds remain unmeasured or undecided.

The user subsequently accepted the [next-session proposal](04-evidence-spike.md#agreed-next-session-proposal--2026-10-14). Its choices are settled for this example; the future exercise has not occurred and its timing remains unspecified. Do not treat that acceptance as evidence of delayed retention or resolution of broader evaluation scope.

### Independent annotation comparison — 2026-10-14

The user authorized the next independent assessment review without another learner exercise. A [blinded comparison](../spikes/independent-assessment/review.md) now checks 48 selected facet judgments on 12 historical student responses across four science questions against pre-existing human annotations. The assessment and mapping were committed before selected labels were revealed. Of 36 comparable judgments, 23 matched, 10 disagreed and three were assessor abstentions; 12 `Assumed` annotations were excluded by the prior mapping. All frozen hashes and source-label copies were verified. This is agreement with annotations, not established grading accuracy; no new human reviewer participated.

The review traces disagreements into the real planner and separately labelled later-check simulations. It reproduces one unresolved conflict between a proposed clarification and immediate help, identifies one answer where movement evidence was also credited as wearing away, and questions whether grammatical facets should become review targets. Disputed source annotations remain disputed; no corrected gold labels or human teaching preferences were invented. Release this bounded claim without resolving the broader HITL decision. The next small implementation experiment should reconcile immediate actions while preserving observations; representative evaluation, acceptance thresholds, learner effort and retained learning remain open.
