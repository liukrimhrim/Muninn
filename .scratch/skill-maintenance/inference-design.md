# Infer enough to choose useful practice

Status: qualitative first-release inference finalized in [Design Baseline 1](design-baseline.md), 2026-10-16. Fitted models, inferred review omission and their empirical claims remain deferred research. The source investigation and numerical probe below do not validate those candidate mechanisms.

## Recommendation

Use a larger answer to identify what was demonstrated, estimate what remains uncertain, and choose the smallest useful next action. Do not require an independent quiz for every related component. Keep the original answer and its assessment separate from the estimate so a mistaken assumption can be corrected without rewriting the learner's history.

The next implementation should add inspectable inference claims to the existing loop, initially as suggestions for diagnosis and recorded predictions. Compare a tiny probabilistic model beside the descriptive baseline before letting numerical estimates suppress future reviews. This is a staged route toward fewer questions, not a conclusion that the system must rely only on direct evidence forever.

The named needs are already concrete: the user wants a failed large exercise traced to the relevant component or connection; their binary-search correction demonstrated a misread rather than the asserted knowledge gap; and the existing mathematics example reuses one criterion across two capabilities. These motivate revisable explanations and stable evidence identity. They do not motivate a new service, graph database or neural model.

## What an estimate means

The claim is scoped: “Based on this answer and these assumptions, we expect this learner to perform this specified action under these conditions.” A probability of a latent state is not automatically a probability of the next correct response, and neither is a universal mastery percentage. A future-retention forecast also needs an explicit horizon and a time model; the current numerical probe has neither learning transitions nor forgetting.

| Keep distinct | Example | Consequence |
|---|---|---|
| Direct observation | The explanation explicitly connects repeated halving with logarithms | Retain evidence for that capability under the actual assistance and conditions |
| Untested estimate | A larger solution suggests the learner can explain a prerequisite independently | Can guide a question or a candidate deferral; does not manufacture a successful attempt |
| Practice exposure | The learner used the relationship while answering | Record what was elicited and any help; exposure alone does not quantify durable improvement |
| Learning effect | Related practice improved later independent recall | Requires a separate comparison with delayed outcomes |

Two uncertainties need different responses. Unclear grading asks “What did this answer mean?” Uncertain knowledge asks “What can the learner do on another task?” More testing cannot repair an ambiguous rubric by itself. An omitted explanation is unobserved; a wrong answer does not by itself identify forgetting, never learning, a misread or temporary retrieval failure.

## Evidence-to-estimate contract

Extend the existing learner-estimate record, not the observation grade. Each claim carries:

- The target's versioned capability contract, including action, mode and allowed help.
- The observation cutoff and prediction horizon. Use “current assessment only” until a delay model is justified.
- Supporting and contradicting raw answer/criterion references, plus attempt and exercise-family identity.
- The relationship or model assumption used, its version, and plausible alternatives.
- A qualitative hypothesis, or a numerical forecast explicitly marked experimental until calibrated. Do not turn an assessor's verbal confidence into an invented probability.
- The proposed action and its reason: clarify an answer, test a distinction, practice a demonstrated weakness, or record a possible future deferral.

Claims are rebuildable from the effective assessments. A grade correction supersedes an assessment of the same response; it is not another response. Repeated retrieval after feedback is a new event whose help and context remain visible. A target-contract change requires an explicit compatibility decision before old evidence informs the new target.

One response can supply useful evidence about several capabilities. Preserve that coverage, but do not multiply several projections of the same criterion as independent trials. Even distinct criteria from one answer can be dependent. Until a joint response model is specified, the numerical experiment accepts one binary judgment per episode and refuses to multiply additional judgments from that episode. This restriction is for the experiment; the existing descriptive ledger still retains every criterion. Distinct episodes may also be dependent, especially after feedback or within one exercise family.

## Which relationships may support inference

Semantic links help locate relevant material. They are not sufficient to justify a statistical update. A curriculum prerequisite is a hypothesis about a particular action and context. Recognizing a term, recalling it unaided, deriving it and using a tool that supplies it can support different conclusions.

The source review distinguishes Knowledge Space Theory's feasible combinations from a generic prerequisite graph. Our four-state chain is a deliberately strict special case used to test assumptions, not a claim that every subject or learner follows one order. A production model would need defensible task mappings, response-error assumptions and evidence about alternative strategies. [Primary-source investigation](research/sparse-inference.md).

Compare these alternatives before adopting a larger model:

| Candidate | Useful now | Evidence needed before relying on it |
|---|---|---|
| Descriptive observations plus explicit hypotheses | Explain a next action and preserve ambiguity without invented probabilities | Reliable assessment and defensible question branches |
| Independent finite-state control | Show what a response says without a dependency between targets | Explicit priors and response likelihoods; a comparison tool, not a claim of real independence |
| Constrained finite-state model | Show how a proposed relationship changes untested estimates | Support for the allowed states, contradictory cases, sensitivity and prospective prediction checks |
| BKT/PFA or richer temporal model | Candidate once repeated performance needs modeling | Enough appropriately separated observations and an observed failure of the simpler approach |

Hard exclusions are consequential: an excluded state cannot be recovered by ordinary Bayesian updating. Adding response noise makes contradictory answers possible, but can conceal an incorrect relationship by repeatedly explaining contrary evidence as error. Contradiction must therefore be able to challenge the model as well as the learner estimate.

## What the numerical probe established

The [reproducible probe](spikes/inference/README.md) uses fictional responses about three capabilities, fixed priors and fixed error rates. It also inspects the actual representation bridge for shared evidence references. Fourteen executable checks passed; none measures learner accuracy or retention.

With initial probabilities A=75%, B=50%, C=25% in both models and 10% response error in either state:

| Synthetic observation | Strict chain: estimate of A | Independent control: estimate of A |
|---|---:|---:|
| Nothing observed | 75.0% | 75.0% |
| C answered correctly | 91.7% | 75.0% |
| Then A answered incorrectly | 55.0% | 25.0% |

The first increase comes from the assumed dependency. After the contradiction, the chain also lowers C from 75% to 45%; the independent control leaves C at 75%. These are consequences of assumptions, not claims about a real learner. Using equal starting marginals avoids the misleading comparison between uniform distributions over four states and eight states, which already imply different beliefs before an answer arrives.

Three further results constrain the design:

- **Copies create false confidence.** Counting one C success twice raises the chain's C estimate from 75% to 96.4%. Exact replay leaves it at 75%. The real bridge supplies five criterion references, covering four distinct criteria from one answer; the shared `work` criterion appears twice.
- **Contradictions can invalidate a model.** With zero response noise, C success followed by A failure has zero likelihood under the strict chain. The probe reports incompatibility instead of inventing a posterior. The independent control can represent that combination.
- **Sparse estimates can depend heavily on the starting assumptions.** At the same 10% noise, the contradiction leaves A near 14.9%, 55.0% or 87.8% under the three disclosed chain priors. These are sensitivity settings, not a calibrated range or confidence interval.

Error assumptions also affect the apparent diagnosis. For the same contradiction and uniform chain prior, setting slip=1%, guess=30% leaves C at 4.4%; exchanging those rates leaves C at 93.0%. A model can explain the successful answer as noise or the failed answer as noise depending on parameters we have not established. It cannot identify an exact knowledge gap merely by returning a precise number.

The experiment uses no timestamps, estimates no reinforcement and changes no learner-facing plan or FSRS record. It does not implement ALEKS or show that KST is superior. Source and dependency hashes are retained with the results.

## How this changes the next action

The accepted sequence remains **larger exercise → specific diagnosis → focused practice → fresh integrated check**. Diagnosis can also occur after an apparently successful answer if a relevant weakness or uncertainty remains.

| Evidence situation | Proposed next action | What would change the action |
|---|---|---|
| User corrects a misread and gives the intended reasoning | Retain the correction; do not schedule remediation for an unsupported gap | A later independent answer actually reveals a gap |
| Parts demonstrated, connection wrong | Focus on the connection, then check it in a new integrated problem | A narrow check shows a part also fails, requiring a revised diagnosis |
| Wrong final answer fits several causes | Ask one question whose possible answers lead to different help | If every answer would lead to the same help, skip that diagnostic question |
| Larger success suggests an unshown prerequisite | Retain the estimate; prefer a useful integrated check that can also expose it | A mode mismatch or contradiction makes a focused check necessary |
| Direct answer contradicts a prerequisite inference | Preserve the answer; inspect grading, task conditions and the relationship; withdraw affected deferral suggestions | Corrected grading or new independent evidence supports a revised claim |
| Multiple gaps remain when time runs out | State what remains unresolved and offer focused help or stop | A later session has enough time to distinguish remaining causes |

For the user's binary-search example, correcting the requested endpoint from one candidate to 1,024 is evidence about that answer. It should not become “all logarithm knowledge is now proven,” nor should the original misread become automatic logarithm remediation. In the mathematics contrast, knowing the parts while mixing up depth and total work supports practicing their combination. These are different diagnoses and should lead to different work.

A diagnostic question earns its time only if the answer can change useful teaching. Information gain alone is insufficient. The system should not make the learner exhaustively certify the graph. The next selection experiment must make question cost, overlapping coverage, remaining uncertainty and the stopping condition visible.

## Build and validation plan

1. **Compare concrete next actions.** Use the current math, operations and simple-fact examples. Supply explicit qualitative inference claims and authored time costs to the existing selector. Compare a short distinguishing question, focused practice and a combined exercise under the same budget. Recompute after each answer; retain unresolved targets when nothing suitable fits. This is the next bounded implementation slice, with no required learner homework.
2. **Record forecasts before checks.** For any future real trial, freeze the target, context, model version, probability and horizon before seeing the held-out answer. Keep whole attempts and related exercise families together in evaluation; separate grading disagreements from failed knowledge forecasts. Report sample size and uncertainty, not a general calibration claim from a handful of answers. The numerical probe's parameters are not defaults for that trial.
3. **Evaluate prediction before omissions.** Compare the constrained model against the independent control on later, separated observations. Compare the descriptive policy using actions, unresolved gaps and learner time rather than assigning it invented probabilities. Repeated contradictions should first revise task mappings or relationships. Add temporal modeling only when an observed timing failure calls for it.
4. **Evaluate actual review savings separately.** A later prospective experiment may bound deferrals, reserve direct audit checks and restore affected reviews when an inference fails. Predeclare retention outcomes, delays, acceptable tradeoffs and total learner time before seeing results. Same-session prediction success cannot establish that skipped practice preserves later recall. User choices about study time and acceptable tradeoffs belong here, once the trial is concrete.

The inference investigation is complete at this bounded level. The general model choice, calibration, delayed retention and omission policy remain open. The next design work is exercise selection under a budget; another approval of the already accepted learning sequence is unnecessary.

Continuation: the [selection comparison](selection-design.md) now implements that bounded next step using the existing evidence planner and authored diagnostic branches. It preserves the numerical probe's separation from real learner estimates and review omissions.
