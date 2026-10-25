# Kubernetes learner trial — L02

Status: bounded trial complete. Both corrected command forms were recalled and applied in a fresh incident; the argument-source repair used a hint; the learner then proposed checking status and actual report processing. Recovery outputs are simulated. Delayed retention, real execution, and learning benefit remain unmeasured. The learner chose Kubernetes commands and operations and reported uneven mastery. That is a topic preference and self-report, not evidence of a specific missing component. Kubernetes remains one example within the general learning system. This trial belongs to the [validation decision](../../issues/05-pilot-outcome.md).

This is a simulated incident with real learner responses. Do not run commands against a cluster. Written commands and interpretations can demonstrate recall and reasoning; they do not establish executed operational skill. Codex acts as tutor and assessor, not an independent evaluator. Initial command choices have been assessed below; repair benefit and retention remain unmeasured.

## Initial learner prompt

Ask the learner to answer from memory, writing commands and brief reasons; permit a description when syntax is forgotten. Do not show the assessor notes or solution before the attempt.

Scenario: the `checkout` application is unavailable. Assume the correct cluster context. Namespace: `shop`. Deployment: `checkout`. The Pod has one container named `app`. Supplied output:

```text
NAME                         READY   STATUS             RESTARTS   AGE
checkout-7d9f6c8b5d-k2m7q      0/1     CrashLoopBackOff   6          8m
```

Goal: find why it is failing and explain how to check that a fix worked.

First request: “What are the first two or three commands you would run, and what would you look for in each result?” The tutor then returns simulated output so the learner can continue the investigation. One useful command is acceptable; do not make the suggested count a grading requirement.

The supplied listing is a cue: it does not demonstrate that the learner could independently choose or use `kubectl get pods`. Returned output is simulated evidence for this larger exercise, not remedial teaching. Track any later command hints separately.

## Fixed scenario facts for the assessor

Keep these facts stable across alternative command paths. Reveal only what the learner's selected commands or questions would expose; label outputs as simulated excerpts. This is a discussion fixture, not a deployed application.

- `shop/checkout` has one replica, selector `app=checkout`, and the listed Pod is controlled through its ReplicaSet. One ordinary container, `app`; no init or sidecar containers. Image: `example.invalid/checkout:v2`, stipulated successfully pulled in this fictional cluster. The hostname is a placeholder, not a real image to fetch.
- The application exits at startup because version 2 requires the environment variable `APP_MODE`. Its accepted production value is `production`. The Deployment template currently sets only `MODE=production`; it has no `envFrom` sources or alternative configuration files. The earlier version 1 accepted `MODE` and worked. Image and configuration history are available if requested; do not infer a cause merely from a recent rollout.
- Pod detail/status shows Waiting / CrashLoopBackOff; last termination Reason Error, exit code 1. Events show successful scheduling/pull/start and repeated backoff. There are no OOM, probe, image-pull, or scheduling failures. Exit code 1 alone does not identify the missing configuration.
- Relevant application log excerpt is `FATAL startup: required environment variable APP_MODE is not set`. The immediately preceding instance failed for the same reason. A valid ordinary log request or previous-instance request can supply this evidence; do not withhold useful ordinary logs to force knowledge of `--previous`.
- Pod or Deployment configuration inspection exposes `MODE=production` and the missing `APP_MODE`. Equivalent YAML, JSON, describe, or appropriate field-specific inspection is acceptable. Do not reveal the application's expected variable merely from Kubernetes events; that evidence belongs to its logs or supplied application documentation.
- A proposed fix may update the controlling Deployment's template/source configuration to supply `APP_MODE=production`, or use an explained rollback to the known compatible version. Recreating an unchanged Pod would retain the defect. Evaluate exact mutation syntax only when the learner proposes it; all actions remain simulated.
- After a compatible simulated fix, new Pods can become Ready with startup logs showing success. Verification should connect the proposed change to fresh status/logs and an application check; do not equate a successful API update message with a functioning application. No live recovery is claimed.

If the learner requests another valid evidence source, derive a consistent excerpt from these facts. Explicitly identify any additional assumption instead of silently changing the cause. Do not invent a limitation to make an otherwise useful command fail.

## Assess only what the unfolding attempt reveals

| Component | Evidence to look for |
|---|---|
| Command recall and targeting | Commands or an explicit description that addresses the intended resource and namespace; distinguish remembered intent from missing syntax. Accept equivalent forms and clear placeholders. |
| Selecting evidence | A useful route to status/events, application logs, and configuration as needed; no mandatory order or exhaustive checklist. |
| Interpreting evidence | Distinguish the restart symptom from its cause; use supplied log and configuration evidence without overreading generic backoff or exit status. |
| Choosing and checking a remedy | Tie the change to the observed cause and describe checks of the resulting workload/application, not just command completion. Assess this only when the learner reaches that stage. |

Preserve exact responses and assistance. Apply the [updated diagnosis design](../../diagnosis-design.md), including the misread correction from L01. An omitted optional flag, short resource name, obvious typing error, or fewer commands than suggested is not automatically a knowledge gap. If current logs already provide the needed evidence, leave previous-instance-log recall untested and continue. No perfect command inventory is required.

Follow-up is justified only by a learning concern in the response. If the learner knows what to inspect but cannot recall syntax, target that command-to-purpose link. If they recall commands but misinterpret their output, target interpretation. If a mistaken relationship is explicit, focus on that relationship. Do not diagnose a gap from an incomplete investigation before returning the requested output.

Once a useful gap is supported, use focused practice and a different incident that exercises the same component. Use at most three diagnostic/clarification prompts; continuing to supply requested incident output is part of the larger task, not a diagnostic quiz. If evidence supports the relevant knowledge, finish without inventing remedial work. Stop if the exercise becomes an unbounded investigation and retain unresolved components. Delayed retention is separate; no reminder has been scheduled.

## Source checks

Command semantics were checked against official documentation on 2026-10-13. The incident itself is invented. [Debug Running Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/) describes inspecting Pod details, namespaced events, YAML, and container logs. The [`kubectl logs` reference](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_logs/) defines `--previous` as selecting the previous container instance when one exists. These sources support command interpretation, not a claim that this fixture ran on Kubernetes.

## Attempt log

- Initial learner prompt: presented in chat.
- Learner commands: received verbatim below; outside assistance not reported.
- Initial assessment: useful evidence selection; valid Deployment command and configuration location; log-command syntax corrected. Readiness-versus-restart interpretation is ambiguous, not a confirmed misconception.
- Current assessment: both practiced command forms were chosen and written correctly in the fresh incident. Unsupported-option interpretation was sound; locating the argument source used a tutor hint. The learner then explicitly distinguished Running from application function and chose logs to check report processing, after earlier teaching of that distinction.
- Next action: return simulated recovery evidence and end this exercise; retain component-specific outcomes for the general design. Broader validation choices remain open.
- Focused practice: both commands correct immediately after help. Fresh incident: meaningful command use and verification plan, with the argument-source hint preserved. Retained learning: not assessed.

### Initial response — 2026-10-14

```text
i will check the logs of the pod to see what's going there: kubectl -n shop logs pod checkout-d9f6c8b5d-k2m7q, or i can describe the deployment to see if there is any error msg: kubectl -n shop describe deployment checkout. It's likely that the readiness probe failed. The info of the probe can be found in the deployment spec as well
```

The phrases “check the logs of the pod” and “describe the deployment” select useful evidence sources. `kubectl -n shop describe deployment checkout` is valid. The learner correctly places probe configuration in the Deployment's Pod template, although observing a particular container's termination or Pod events may require Pod inspection.

The written log command uses a separate `pod` token where the command expects a Pod name or resource/name, and drops the leading `7` in the supplied Pod suffix. Correct to `kubectl -n shop logs checkout-7d9f6c8b5d-k2m7q`. Record the syntax correction as help; the evidence-selection intent was already sound. Treat the name difference as transcription, and do not infer a stable command-recall deficit from one malformed command.

“It's likely that the readiness probe failed” does not explicitly state that readiness causes restarts. It could refer to unavailability or the 0/1 column. Give the short operational distinction without inventing a learner claim: a readiness failure alone does not restart a container; failed liveness or startup probes can trigger a restart. Do not record a confirmed misconception or require a probe quiz before returning the requested data. The specific cause still needs evidence.

The [`kubectl logs` synopsis](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_logs/) and [probe behavior](https://kubernetes.io/docs/concepts/workloads/pods/probes/) were checked on 2026-10-14. No command was run against a cluster.

### Simulated evidence to return

Explain the syntax correction before presenting the corrected command's output; do not imply that the learner's exact spelling ran successfully. Use the fixed scenario facts above.

Application log excerpt:

```text
FATAL startup: required environment variable APP_MODE is not set
```

Deployment describe excerpt:

```text
Pod Template:
  Containers:
   app:
    Environment:
      MODE: production
Conditions:
  Type        Status  Reason
  Available   False   MinimumReplicasUnavailable
```

These are simulated excerpts, not observed cluster output. The requested evidence supplies the application error and configured variable; interpreting their relationship remains the learner's next step. No requirement to name `--previous` is introduced when the ordinary logs provide the evidence.

Next larger-task prompt: “Given these results, what would you change, and how would you check that it worked?” This continues the investigation rather than testing a diagnosed weakness. Learner response: pending. Diagnostic questions so far: 0. Teaching supplied: corrected log syntax, restored Pod-name spelling, and the short probe distinction. No cause-specific fix or verification commands have been supplied.

### Remedy response — 2026-10-14

```text
kubectl -n shop edit deployment checkout, and add under Containers: env: APP_MODE: production
```

The edit command, target resource, and proposed `APP_MODE=production` address the supplied evidence. The inline YAML-like description may be shorthand; do not record a confirmed schema misconception from it. Provide the actual list structure in the existing `app` container under `spec.template.spec.containers`, preserving `MODE` and other settings:

```yaml
env:
  - name: MODE
    value: "production"
  - name: APP_MODE
    value: "production"
```

This is a fragment for the existing container, not a complete manifest. The shape was checked against [Define Environment Variables for a Container](https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/) on 2026-10-14. The Deployment's Pod-template location and rollout behavior were also checked in the [Deployment documentation](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/). The learner supplied the remedy's meaning; the tutor supplied its exact YAML. Do not credit the latter as independent recall or infer knowledge of rollout behavior before the learner explains it.

For the simulation, accept the edit with the supplied YAML; the initial facts above describe the pre-edit state. No real edit or rollout occurred. Next prompt: “What commands would you use to verify the fix, and what results would convince you it worked?” Verification is part of the original operational goal and remains unobserved, not failed. Do not label an omitted verification answer as a knowledge gap. No verification command or recovery output has been supplied yet.

### Partial verification response — 2026-10-14

```text
the pod will auto restart after the change is saved, and if it works, kubectl -n shop show po will show
```

The learner anticipates an automatic update and selects checking Pods as a verification step. Correct the verb to `kubectl -n shop get po`; `po` and the namespace are valid. This is one observed command-recall error on the listing verb, not evidence that the learner cannot choose a useful verification step.

Clarify that this change to the Deployment's Pod template creates replacement Pods with the updated configuration. The phrase “auto restart” may be colloquial; do not assign a confirmed same-Pod-versus-replacement misconception. The [kubectl reference](https://kubernetes.io/docs/reference/kubectl/) documents `get po`, and the [Pod templates documentation](https://kubernetes.io/docs/concepts/workloads/pods/#pod-templates) describes replacement after template changes; both checked on 2026-10-14.

The response ends at “will show”. Do not supply a learner expectation, fail a verification criterion, or return a healthy output before the learner finishes. Next prompt: “Your message ends at ‘will show’—what were you expecting to see?” This is one clarification of an incomplete response, not a diagnosis of a knowledge gap. Clarification/diagnostic prompts so far: 1 of 3. Additional help: the `get` verb and replacement-Pod behavior. Expected results, recovery judgment, and retained learning remain unobserved.

### Completed verification response — 2026-10-14

```text
the status should be RUNNING
```

Running is a correct expected signal. The learner did not claim that it alone proves application health; do not infer that misconception from a brief answer. The [Pod lifecycle documentation](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/), checked on 2026-10-14, distinguishes Running from readiness. Close the guided walkthrough by supplying the additional checks: READY 1/1 for this one-container case, restart count staying stable over time, fresh logs without the startup error, and a working application response. These are teaching, not learner evidence. No further completeness quiz is needed.

Return this explicitly simulated post-edit snapshot, fixing the new Pod identity for any continuation:

```text
NAME                         READY   STATUS    RESTARTS   AGE
checkout-6c8b7d9f45-m8q2r      1/1     Running   0          1m
```

This snapshot does not establish restart stability over time or application health. Neither a new application response nor an actual cluster observation has been collected. Guided exercise completion is not independently verified operational success.

### Focused command practice — prepared 2026-10-14

The observed corrections concern the `get` listing verb and the Pod argument to `logs`. Useful evidence selection and the environment-variable remedy were already supported. Offer brief retrieval practice of these forms without diagnosing a persistent deficit or reteaching the entire topic.

Prompt: “Without looking back, write two commands: list the Pods in namespace `billing`; then read logs from Pod `invoice-abc123` in that namespace (one container).” The arbitrary Pod name is supplied so name recall is not being tested. Accept equivalent valid commands and clear placeholders. Recent help includes both forms, so success is immediate practice evidence, not delayed retention or broader transfer. Learner response: pending. A fresh larger exercise remains separate.

### Focused practice response — 2026-10-14

```text
1. kubectl -n billing get pods 2. kubectl -n billing logs invoice-abc123
```

Both numbered commands are correct for their respective prompts, including namespace and resource targeting. Treat the numbering as two answers, not one shell invocation. The [get reference](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_get/) and [logs reference](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_logs/) were checked on 2026-10-14. This is successful immediate recall after the supplied corrections. Do not claim durable mastery or that a lasting gap has been repaired. Stop isolated command repetition and move to application in a fresh incident.

### Fresh incident — prepared 2026-10-14

Learner-facing prompt: “A report worker has stopped processing queued reports. Its Deployment is `report-worker` in namespace `analytics`; each Pod has one container. Assume the correct cluster context. You have not inspected it yet. What command would you run first, and what would you look for? I will return simulated output.” No listing, Pod name, command, or root cause is pre-supplied.

Fixed fictional facts for consistent responses:

- One replica, selector `app=report-worker`, container `worker`, Pod `report-worker-5b7c9d6f84-q2m8n`. At the first snapshot it is READY 0/1, STATUS CrashLoopBackOff, RESTARTS 5, AGE 7m. The image `example.invalid/report-worker:v3` is a placeholder stipulated pulled successfully; do not fetch it.
- The worker exits with code 2 before processing jobs. Logs say `ERROR: unknown option --fast-mode`. Both current and previous-instance logs can reveal it. No OOM, scheduling, image-pull, or probe failure is present. Pod events show successful start followed by backoff; events do not reveal the application's argument error.
- The Deployment template supplies `args: ["--fast-mode"]`. The fictional version 3 removed that optional flag and runs correctly with no args. Version 2 accepted it and was previously working. App help/release information is available on request; do not invent that fact from generic Kubernetes status.
- Editing the controlling template to remove the unsupported flag, or a reasoned rollback to the known compatible version, addresses the cause. A successful simulated fix permits a new Ready Pod and resumed report processing. Verification should relate fresh workload evidence to actual report completion; an API update alone does not establish success.

Accept any useful first evidence source, including Deployment logs or details. Do not force a Pod listing merely to exercise `get`; an unchosen form remains unobserved in this incident. Return only evidence exposed by the chosen route, preserving all fixed facts. If another source is requested, derive a consistent excerpt and mark any added assumption. No commands run on a cluster.

This is a near application check after recent teaching, not delayed retention or a causal measurement of repair benefit. The cause differs from the first incident while the practiced evidence-gathering commands remain useful. Preserve hints separately, avoid new drills for mere omissions, and finish after the learner has enough evidence to propose and check a remedy. Learner response: pending.

### Fresh incident, first response — 2026-10-14

```text
kubectl -n analytics get po, it will list out the pods and their status, i'll check if report-worker pod is in healthy state
```

Correct command, namespace, and purpose. The learner chooses a useful first check without being explicitly told to list Pods in this incident. Recent teaching still applies; this is immediate application, not delayed retention. The phrase “healthy state” does not assert a specific incorrect criterion. Return the requested evidence without a new diagnosis or command hint:

```text
NAME                              READY   STATUS             RESTARTS   AGE
report-worker-5b7c9d6f84-q2m8n      0/1     CrashLoopBackOff   5          7m
```

Label this output simulated. Next prompt: “What would you run next, and what would you look for?” Log-command selection, interpretation of the output, remedy, and verification remain pending. This is continuation of the larger exercise, not an additional diagnostic probe. No cluster command was executed.

### Fresh incident, log request — 2026-10-14

```text
the status shows that there is some error caused the container to crash. kubectl -n analytics logs report-worker-5b7c9d6f84-q2m8n, to check the error msg in the logs
```

Correct log command, namespace, Pod name, and evidence-gathering purpose. The learner identifies failure and seeks its cause; do not overread “crash” as a particular termination mechanism or a claimed root cause. Both practiced forms have now been used appropriately in the fresh incident without new syntax hints. This supports immediate application after recent teaching, not delayed retention or causal proof of learning benefit.

Return only the requested simulated application log:

```text
ERROR: unknown option --fast-mode
```

Ordinary logs provide this evidence under the frozen fixture; do not require `--previous` or disclose the Deployment args and version history before the learner asks for relevant evidence. Next prompt: “What does this suggest, and what would you do next?” Log interpretation, remedy, and recovery verification remain pending. No new remediation or diagnostic probe is needed, and no cluster command was executed.

### Fresh incident, proposed repair — 2026-10-14

```text
i think prob some command the app in the container runs has a invalid option --fast-mode. remove that option in the code, build a new image and deploy it to the k8s cluster
```

The learner correctly interprets an unsupported option and proposes eliminating it. A code change and image rebuild could be appropriate if the source were inside the image, but no evidence yet identifies that location. Do not label the hypothesis wrong merely because the assessor knows the hidden Deployment args. The specific concern is selecting a repair location before locating the argument, not failure to interpret logs or a confirmed lack of Kubernetes configuration knowledge.

Give a brief distinction: the option may come from code/startup inside the image or from the Deployment's container configuration. Kubernetes supports supplying container arguments through configuration, as checked in [Define a Command and Arguments for a Container](https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/) on 2026-10-14. This is tutor-supplied help, not evidence independently recalled by the learner. Do not disclose the fixture's actual args or invent a source-code inspection result.

Next prompt: “Before rebuilding, how would you check where `--fast-mode` is being supplied?” One targeted follow-up is warranted by the proposed repair's unsupported location assumption. Clarification/diagnostic count: 1 for this fresh incident, 2 across L02 including the earlier truncated-answer clarification; within the maximum of 3. Accept a useful inspection route or a clear description if exact syntax is unknown. If the learner cannot identify a route, teach the specific configuration check rather than expanding into an open-ended quiz. Repair and verification remain pending. No build, deployment, or cluster command is authorized by this simulated answer or has occurred.

### Fresh incident, locating and editing the argument — 2026-10-14

```text
kubectl -n analytics edit deployment report-worker, and in the editor, search `--fast-mode` to see if it appears. if it does, edit it out and save
```

The command, resource, namespace and conditional inspection/edit route are valid. No separate read-only command is required for this chat exercise. Show where the match occurs before accepting the change: this is the active container `args`, not an unrelated annotation or text occurrence. Do not infer indiscriminate deletion from the learner's shorthand.

Simulated editor excerpt from `spec.template.spec.containers`:

```yaml
- name: worker
  image: example.invalid/report-worker:v3
  args:
    - --fast-mode
```

Accept removing that argument and the now-unneeded args field, preserving other settings. Fixture clarification: the version 3 image's default startup does not supply `--fast-mode`; removing the override does not reintroduce it. This is consistent with the previously fixed fact that version 3 runs correctly without the optional flag. No image rebuild is needed for this fixture. Only configuration acceptance is returned at this point:

```text
deployment.apps/report-worker edited
```

Both the editor excerpt and save result are simulated; no real editor, mutation, build or rollout was run. The tutor had just mentioned Deployment configuration as a possible argument source. Credit the learner's valid command and conditional remedy after that hint; do not count the source-location relationship as independent recall or diagnose a persistent gap.

Next prompt: “How would you verify that the worker has recovered and is processing reports again?” This continues the original operational goal rather than adding a diagnostic quiz. Clarification/diagnostic count remains 2 across L02. A successful save is not evidence of recovery. Do not supply a healthy Pod or report-completion result before the learner chooses verification checks.

### Fresh incident, recovery verification — 2026-10-14

```text
same command as before, kubectl -n analytics get po to check the status of the pod. but pod in running state doesn't mean it's functional as intended. should check logs to confirm that it's process reports
```

The status command is correct. The learner explicitly distinguishes process state from intended function and selects application logs to check report processing. The tutor taught this distinction during the first incident; record its application here, not unaided prior knowledge. The log-check description is sufficient: exact log syntax was already demonstrated in this incident, and a new Pod name is not yet available to the learner. Do not add a syntax repetition or require an exhaustive rollout/readiness checklist.

Return these simulated results, fixing the new Pod identity and success-log examples for consistency:

```text
NAME                              READY   STATUS    RESTARTS   AGE
report-worker-6d8f7c9b65-p4r2s      1/1     Running   0          2m
```

```text
INFO report=R-1042 completed
INFO report=R-1043 completed
```

Added fixture detail: these messages represent successful report completion after the fix, not merely worker startup. They are invented evidence consistent with the existing scenario, not observed execution or a new learner answer. They support resumed processing in the simulation; one status snapshot does not establish long-term restart stability, and no independent output-artifact check has been performed. Do not turn that remaining coverage into another mandatory quiz.

### Outcome and stop decision — 2026-10-14

The larger exercise → focused command practice → fresh larger exercise sequence is complete as a chat simulation with one learner. Stop the current drill and preserve the following distinctions:

| Target | Observation | Limit / next useful evidence |
|---|---|---|
| List Pods and read logs | Both initially corrected forms were reproduced correctly and then selected correctly in the fresh incident. | Immediate practice and application after help; later recall remains untested. |
| Interpret error evidence | Missing environment variable and unsupported-option interpretations supported the investigation. | Two local observations, not general operational mastery. |
| Locate the source before choosing a repair | Initial code/image proposal preceded source evidence; valid Deployment inspection and edit followed a source-location hint. | Mark success with help; a future case without that hint could distinguish recall from dependence on it. No persistent deficit established. |
| Verify intended function | Learner explicitly says Running is insufficient and selects logs to confirm report processing. | Correct application after earlier teaching; returned success logs are simulation data, not learner performance or live recovery. |

Diagnostic/clarification prompts: 2 total across L02 (one truncated-answer clarification and one source-location follow-up). Requests that continued the incident investigation and the focused practice itself are recorded separately; this count is not the full interaction length. Elapsed learner effort was not measured. Neither independent assessment nor a controlled comparison establishes intervention benefit. No reminder or delayed test has been scheduled.

The design implication is to preserve the target, response evidence, and assistance separately and stop when the current question is answered. The trial supplies an example of those rules in use, not validation of the whole system. Broader sample selection, retention outcomes, and evaluation thresholds stay open in ticket 05 and its dependents.
