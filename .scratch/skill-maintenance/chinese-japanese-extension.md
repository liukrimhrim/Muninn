# Chinese to Japanese learning extension

Status: proposed extension, 2026-10-16. The user accepted writing this specification against [Design Baseline 1](design-baseline.md). The requirements below come from the language-learning conversation; the proposed contracts and acceptance cases make them reviewable. This does not amend the finalized general baseline or authorize implementation.

## Purpose and scope

Build a Japanese-learning web experience for a native Chinese speaker pursuing native-level fluency. Optimize for retained, usable language ability and the time required to acquire it. Preserve progress as the curriculum, assessment methods, scheduling algorithms and application architecture evolve. Later source and target languages must fit the same learning lifecycle.

Native-level fluency is the long-term goal, not a badge earned through vocabulary coverage. The app must distinguish reading, listening, production, pronunciation, grammatical control and appropriate use in context. The learner's reported Duolingo score of 25 is background information, not transferable evidence of any of these abilities.

The reference deployment remains the baseline's one learner, browser, application process and local SQLite store. Speech introduces microphone input, reference playback and durable media; these are explicit additions to the baseline's text-oriented scope. Neither a multiuser service nor a plugin platform is needed to express the current requirements.

| Requirement from the conversation | Observable behavior |
|---|---|
| Adapt to Chinese background and learning habits | Explain relevant similarities and differences in Chinese, let demonstrated familiarity shorten instruction, and allow vocabulary intake to advance independently of unrelated grammar lessons |
| Reduce unnecessary repetition | Use eligible actual FSRS reviews for recall; use observed coverage of larger tasks without counting bypassed skills or repeating already demonstrated requirements within the encounter |
| Diagnose a specific gap | Attribute an error to the narrowest supported requirement; preserve uncertainty and unaffected evidence |
| Explain words deeply | Offer sourced meanings, readings, usage, collocations, word formation and etymology where established; label mnemonics separately |
| Teach synonym nuance and pragmatic appropriateness | Judge the intended meaning, construction, relationship, setting and tone; explain why another choice fits better when appropriate |
| Teach polite, gentle Japanese | Practice honorific choices and interpersonal softening under explicit situations; accept suitable alternatives |
| Tolerate an accent while giving precise feedback | Separate task success and intelligibility from optional refinement; locate supported deviations and admit when a recording cannot be judged |
| Connect vocabulary by frequency and meaning | Support frequency information, categories, situational groups and contrast relations without forcing one introduction or review order |
| Measure mastery honestly | Show evidence by ability and context, later independent performance and total learning effort; keep unobserved abilities visible |
| Remain extensible and compatible | Reuse target knowledge across teaching languages when contracts permit; retain exact historical evidence and schedule meaning through changes |

## Reuse of the general learning system

The [representation contract](representation-design.md) already distinguishes knowledge, capabilities, selected targets, assessment criteria and practice bundles. A word is content; recalling its meaning under a particular cue is a capability; selecting that capability for the learner creates a target. A synonym distinction can be a relation and a capability without duplicating the underlying words.

The existing [module ownership](module-design.md) remains the boundary for the extension:

| Owner | Language-specific responsibility |
|---|---|
| Content | Languages and forms, word senses, constructions, usage conditions, contrast relations, reference media, source provenance and versioned exercise rubrics |
| Evidence | Written and recorded responses, transcript and acoustic observations, judgments, uncertainty, exposure and qualification for named claims |
| Practice | Admission, ordinary review ownership, FSRS recall streams, integrated practice, bounded diagnosis and repair, and learner overrides |
| Measurement | Attributable effort, comparable outcomes by ability/context, missingness and reproducible reports |
| Application Workflows, Library and Web Interaction | Coordinate provider requests and atomic commands, preserve media and records, and present recording/playback and correction controls |

These are additions within existing responsibilities. Language content does not own a second scheduler, and a speech provider cannot directly alter progress. Reference-media meaning belongs to Content; submitted learner-media meaning belongs to Evidence; Library supplies their storage mechanics.

The baseline's repair limits, capability-review delays, selection order, exposure rules and tracking definitions remain the initial policies. They are not established optima for Japanese acquisition. Any replacement needs a named requirement or observed result, versioned behavior and a compatibility disposition. FSRS recall scheduling remains distinct from capability-review delays.

## Language content and learner background

Content needs language-aware references, not an identity derived from a translation string. A Japanese expression can have several senses, spellings, readings and uses. A Chinese explanation describes those references without becoming their identity.

The proposed minimum content distinctions are:

| Content | Information needed for teaching and assessment |
|---|---|
| Lexical entry and sense | Stable identity, language, written forms/readings, sense, part of speech, usage examples and source references |
| Construction | Form, grammatical roles, particles, inflection or combination rules, meaning and supported contexts |
| Usage or contrast relation | Exact senses/constructions compared; collocation, register, connotation, situational restrictions and examples that reveal the distinction |
| Phonological feature | The relevant sound, length, timing, accent or intonation contrast under a specified pronunciation variety |
| Knowledge group | A category, situation or explanatory relationship, with membership independent of scheduling |
| Teaching explanation | Explanation language, assumed background, source references and whether an analogy is historical, descriptive or merely mnemonic |

These distinctions can be represented in existing content records. They do not require a new generic graph engine or a table for every linguistic label. Exact physical schemas belong to implementation design once representative content has exercised these contracts.

The learner profile records preferred Chinese variety/script, Japanese goals and contexts, pronunciation model, available study time and feedback preferences. Do not infer Mandarin pronunciation or simplified-character preference from “native Chinese speaker.” A Chinese-background explanation can propose that a form is familiar; only the learner's response establishes performance.

Relevant comparisons include shared written forms, different meanings, reading differences, and constructions that invite misleading translation. Each comparison must cite its scope. Visual resemblance, a shared character or an etymological connection never transfers a Japanese listening or speaking achievement automatically.

## Granularity and assessment

Create a separate persistent target only when it matters to the goal, evidence can distinguish it, and the result changes useful practice. Otherwise retain the distinction as a rubric criterion. Do not instantiate every word multiplied by every modality and social context.

For each target, specify content references, observable action, cue and response languages, relevant setting, permitted aids, accepted evidence, and the next practice that success or failure would justify. Recognition, cued recall and free production have different conditions. Explaining a rule in Chinese is useful evidence of explanation; applying it spontaneously in Japanese requires its own evidence.

| Observation | Supported conclusion | Unsupported inference |
|---|---|---|
| Correct meaning from a written Japanese cue | Performance on that sense-recognition or recall contract | Auditory recognition, reading aloud or spontaneous use |
| Correct written answer after hearing a phrase | Evidence for the assessed listening and response requirements | Pronunciation of the phrase |
| Appropriate word in a supplied sentence | Performance under that construction and context | Unrestricted interchangeability with its synonym |
| Successful integrated response | Only requirements actually demonstrated, with any integration criterion assessed directly | Every planned constituent was retrieved independently |
| Wrong response with several plausible causes | A recorded failure and an unresolved attribution | All vocabulary, particles and pragmatic choices are weak |

Preserve the actual response and assess meaning, grammatical form, intelligibility, naturalness and situational appropriateness separately where relevant. A correct alternative outside a model answer must remain acceptable. If a task genuinely requires a particular construction, explain that constraint before the answer; a successful circumlocution may fulfill the communicative goal while leaving that construction unobserved.

When evidence is ambiguous, ask the smallest useful follow-up within the inherited diagnostic budget. For example, distinguish misunderstanding the intended situation from choosing an unsuitable expression despite understanding it. Do not prescribe a synonym drill before the response supports that diagnosis.

## Synonyms, pragmatics and politeness

Synonyms are scoped contrasts, not interchangeable translation labels. A contrast includes overlapping meaning, differences, common combinations, compatible syntactic frames, register, speaker attitude and situational expectations. A Chinese gloss can introduce the meaning; it cannot stand in for this usage contract.

An exercise about appropriateness supplies enough context: communicative intention, speaker and listener roles, relationship, medium, setting and any relevant burden of the request. A rubric names acceptable ranges and the reasons for them. Where omitted context changes the judgment, the assessor asks for clarification or records uncertainty.

Politeness practice includes choosing forms, making requests, declining, disagreeing and repairing a misunderstanding. More formal language is not automatically the best response. The target can require a gentle request in a defined relationship, while allowing multiple natural ways to achieve it. Regional, social or stylistic variation must not become an unsupported universal prohibition.

A typical encounter could ask the learner to make a request in a specified workplace situation. An answer can preserve the intended meaning and grammar but choose a tone the reviewed rubric marks as unsuitable. Feedback names the expression and contextual reason, preserves the demonstrated grammar, and offers a suitable alternative. A fresh situation then checks the relevant choice. Seeing the alternative is recorded as help, so immediate reuse is not reported as independent delayed mastery.

This scenario describes the assessment behavior. Production examples and claims about native usage require suitable sources and independent review before they become an authoritative answer key.

## Vocabulary intake and practice order

Keep three decisions separate: how content is organized, which new targets to admit, and which admitted targets need practice now. A color group, synonym set or restaurant scenario can support explanation without forcing every member into adjacent reviews.

Frequency is useful content metadata only with its corpus, genre and sense limitations. The learner can select a useful situation or topic, use frequency to inform choices within it, and override the suggested intake. The baseline's scheduling and waiting-time rules continue to govern existing obligations; a new frequency list cannot silently postpone them.

A noun-heavy opening and grouped synonym/antonym learning are learner preferences and hypotheses to evaluate, not a mandatory parts-of-speech ladder. The proposed starting policy allows familiar concrete vocabulary to move quickly while introducing the verbs and constructions needed for useful tasks. Particles belong in grammatical explanations and meaningful constructions; isolating their teaching section must not remove them from language use.

Vocabulary intake can advance while a grammar target needs repair. Known material can receive an appropriate initial check instead of compulsory teaching. Rapid intake still exposes the expected review burden and preserves the learner's time budget. Increasing today's intake is not itself evidence of faster durable acquisition.

If grouped learning produces observed confusion, adjust the bundle or contrast exercise without resetting the component targets. Immediate performance and later independent performance remain separate. No weighted score combines frequency, uncertainty, interest and mastery into an unexplained priority.

## Speech evidence and feedback

Treat speech recognition, sound analysis, speech generation and language judgment as different capabilities. The application may use one provider for several, but it must record which observation supports each judgment. A transcript alone cannot establish pronunciation quality. A recognition mismatch alone cannot establish a learner error.

| Dimension | Evidence and feedback contract |
|---|---|
| Communicative success and intelligibility | Assess whether the intended message is understood under the task's conditions; do not substitute character-level transcript agreement for this claim |
| Sound realization and timing | Identify a supported segment or time span and describe the relevant difference; retain uncertainty when alignment or recording quality is inadequate |
| Accent and intonation | Use a declared variety and reviewed reference range; distinguish an optional refinement from a task-relevant contrast |
| Grammar and pragmatic choice | Assess the utterance against intention and situation, preserving uncertainty in the recognized words |
| Fluency | Use actual speech timing under a defined task; distinguish planning time, audio duration and provider latency |

An intelligible accent can meet the task while receiving optional, specific refinement feedback. If a deviation obscures the intended contrast, explain that consequence rather than assigning an accent penalty. Never grade proximity to a single speaker's waveform as general speaking competence.

Feedback should let the learner replay the relevant part of their recording and a qualified reference, see what differed, and retry with one actionable focus. Showing a transcript, slowing audio, displaying furigana, replaying a model answer and shadowing all have explicit assistance/exposure consequences for affected requirements. Unaffected observations remain usable. Repeated playback or imitation does not mint an FSRS review.

Save the submitted recording reference, exercise/offer, timing and pending assessment operation before requesting external assessment. Submission succeeds only when the referenced recording is durably available. A recording or upload failure remains a recoverable draft or explicit failure; it is never a saved successful submission with missing audio. No model call runs inside the write transaction.

Provider timeout, unsupported analysis, noisy input or unresolved transcription leaves the relevant judgment unassessed, with an explanation and a retry or correction path. The learner can correct a transcript without the system pretending the correction was another spoken answer. Dependent judgments are reconsidered through the existing atomic correction workflow. A text-only alternative, if chosen, collects text evidence and does not settle a speaking obligation.

## Content and media quality

Every accepted explanation, rubric and reference pronunciation retains provenance and revision identity. Authoring can use generated suggestions, but a generator's own agreement with its output is insufficient qualification. Content review must cover the senses, constructions and contextual alternatives on which learner judgments depend.

Historical etymology, productive word formation and memory aids need distinct labels. An invented mnemonic must never be presented as a word's origin. If an origin is uncertain, preserve that uncertainty. Corrections to explanations or pronunciation references identify affected exercises and evidence, hold disputed interpretations and preserve unrelated progress under the baseline's correction rules.

Audio assets need stable identities plus integrity information, media type, duration, language/variety and provenance. Reference assets also identify human or synthetic origin and permitted use; learner recordings identify the associated attempt and capture conditions. A remote URL alone is not a durable historical reference. The exact licensed asset or a clearly recorded availability restriction must accompany its use.

Transcripts, alignment, acoustic observations and generated feedback are derived records. Retain their input references, producer/version, parameters relevant to interpretation and acceptance status. Updating a provider must not overwrite these records or silently reinterpret old speech.

The proposed default is to retain the original submitted audio needed for replay and correction, with derived records linked to it. Audio retention and any external processing require an explicit data-handling choice before speech is enabled. The interface must identify what will leave the machine; the general baseline does not authorize sending recordings to a provider.

Export/restore must include retained media and verify its integrity and references. An unavailable or nonportable asset must be reported explicitly; such an export cannot claim complete speech replay. Whole-library erasure extends to app-managed original and derived media under the [deletion contract](../learning-observability/deletion-design.md); independently retained exports remain subject to that contract's ownership limits. No selective-erasure promise is introduced here.

## Extensibility and progress compatibility

Target-language content, source-language explanations and learner-specific evidence have separate identities. Another source language can provide explanations and contrastive teaching for the same Japanese content. Changing a cue language, however, can change the retrieval task and its comparability. Reuse content freely where meaning agrees; reuse evidence or schedules only through reviewed compatibility mappings.

Adding another target language supplies its content, constructions, phonological distinctions, accepted variants and assessment cases. The framework must not assume all languages have kanji, particles or Japanese honorific categories. Language-specific rules live in the relevant content and assessment contracts; scheduling consumes qualified observations without embedding a Japanese grammar hierarchy. A provider replacement uses the existing workflow boundary, not a new plugin architecture without an observed need.

The [compatibility contract](compatibility-design.md) governs all migrations. The language extension adds these cases:

| Change | Required continuity |
|---|---|
| Reorganize words by frequency, category or situation | Preserve target identities, evidence and schedules; revise organization or bundles only |
| Improve a Chinese explanation without changing the assessed capability | Preserve the target contract; record any new exposure when the explanation is viewed |
| Change the cue from Chinese translation to a Japanese situation | Assess contract equivalence explicitly; preserve old achievement under its original conditions if non-equivalent |
| Add listening or speaking to a known written word | Create selected, initially unobserved targets as needed; no inherited listening/speaking passes or fabricated recall ratings |
| Split a broad synonym target into contextual distinctions | Map only attributable criterion evidence; keep the original episode identity and leave unsupported distinctions unobserved |
| Correct a pronunciation reference or accepted wording | Retain originals, identify affected judgments and recompute their consequences atomically; never mark all related words failed |
| Replace a speech assessor | Use the new assessor prospectively; historical reassessment is explicit, preserves the old result and uses the original learning time |
| Replace the web framework, storage layout or scheduler | Preserve raw evidence, revisions, due dates and pending work; intentional policy transitions are separately versioned |
| Change source-language explanations or add another language pair | Preserve target knowledge identity where appropriate; do not relabel historical cue conditions or copy grades between different capabilities |
| Restore on a machine without the original speech provider | Display retained media and accepted judgments without regrading; explicitly hold only operations that require an unavailable capability |

Preserving progress means preserving its evidence and meaning, not freezing every future score. Correcting a wrong judgment may legitimately change current progress; the old judgment and the reason remain inspectable. A technical upgrade cannot invent learning, reset unrelated targets or turn unknown history into zero mastery.

## Measurement

Use the baseline's [tracking contract](../learning-observability/tracking-contract.md) and [data contract](../learning-observability/data-contract.md). Report performance on stated targets and conditions with denominators, evidence age, assistance, missingness and the applicable rule identity. Retain the distinction between raw correctness and qualification for an independent or delayed claim.

Useful views include written recall, auditory recognition, contextual production, pronunciation requirements, pragmatic choice and integrated communication. These are views over actual selected targets, not a mandatory universal mastery vector. A beginner can have strong written recognition and unobserved listening; the interface must make that intelligible.

Track time spent learning, retrieving, listening, diagnosing, receiving feedback and reviewing, with overlapping time accounted for once and idle/unknown time visible. A short session, more cards completed or a longer streak is not a learning-efficiency outcome. Show retained performance and total effort side by side. Do not average weak listening and strong reading into a reassuring global score.

Future comparisons of noun-heavy intake, thematic grouping or different scheduling choices need agreed outcomes, delayed checks, time costs and stopping rules. Routine tracking does not establish causality. Neither the proposed architecture nor a synthetic acceptance test establishes native-level attainment or a learning-speed advantage over Duolingo.

## Acceptance cases

These cases qualify the implemented extension when implementation is authorized. They supplement the baseline's persistence and lifecycle cases; they are not completed test results.

| Case | Required observation |
|---|---|
| J01 Chinese background | A familiar written sense can pass its initial check and shorten teaching; its listening and pronunciation remain unobserved. Chinese variety and script preference are not inferred |
| J02 Narrow diagnosis | An integrated error with two plausible causes remains unlocalized until useful evidence distinguishes them; demonstrated constituents retain their results |
| J03 Synonym context | A grammatical, understandable response can receive contextual feedback without a grammar failure; a reviewed appropriate alternative passes |
| J04 Politeness | Changing relationship or setting can change the acceptable range; maximum formality is not rewarded by default, and missing decisive context produces uncertainty |
| J05 Accent tolerance | Reviewed intelligible accented samples can meet the task while receiving localized refinement; samples that obscure the required contrast receive a distinct explanation |
| J06 Recognition disagreement | A transcript error or unreliable alignment does not become a pronunciation failure; transcript correction preserves the original audio and triggers only dependent reassessment |
| J07 Assistance | Furigana, subtitles, translation, reference playback and shadowing affect the requirements they reveal; immediate helped reuse is not called delayed independent retention |
| J08 Review ownership | Replay, retries, shadowing and extra practice cannot create duplicate owned FSRS reviews; a mixed-target task settles only its eligible owned slots |
| J09 Curriculum order | Moving a word between groups changes neither its evidence nor due date; vocabulary can advance while an unrelated grammar concern remains open |
| J10 Content correction | Correcting a bad reading, explanation or rubric preserves the old response and reason, holds/recomputes affected interpretations, and leaves unrelated progress usable |
| J11 Capture and provider failure | Denied microphone access, failed persistence, timeout and late results preserve drafts or saved submissions correctly; none becomes a false learner failure or duplicate assessment |
| J12 Durable upgrade | Export/restore and a physical migration preserve media integrity, exact prompts/rubrics, assistance, corrections, schedules and unfinished work; historical reads make no provider calls |
| J13 Target evolution | Splitting a target or adding a modality retains the original episode without multiplying independent successes; missing evidence and non-equivalent recall histories remain explicit |
| J14 Another language pair | A bounded fixture changes the source language and separately the target language; only declared content, assessment and collection differences change, while the same lifecycle and progress invariants hold |
| J15 Measurement | A report exposes strong written performance alongside missing or weak listening, includes feedback/repair effort and missing planned outcomes, and reproduces under its pinned historical definitions |
| J16 Media handling | Provider transmission follows the chosen scope; exports disclose missing/restricted assets, and confirmed whole-library deletion covers app-managed recordings and derivatives |

Speech qualification needs independently reviewed samples spanning acceptable variation, task-relevant errors, recognition disagreement and unusable recordings. Contextual-language qualification needs more than one model-generated answer key. Agree the intended contexts and error tolerances before evaluating a provider; do not invent a universal numerical pass threshold here.

## Choices to settle before implementation

The following choices affect executable contracts and remain open:

- The learner's preferred Chinese variety/script, priority Japanese situations and pronunciation variety.
- The initial licensed content sources, frequency corpus, reference recordings and independent language-review process.
- Which speech dimensions the first selected tools can support reliably, with acceptance tolerances for each; an unsupported dimension must remain visibly unassessed.
- Whether recordings may leave the machine, provider processing/retention terms, and the local retention policy for original and derived audio.
- The supported browser/microphone environment and concrete framework/provider versions within the baseline's reference deployment.

Implementation should extend the baseline's end-to-end slices: first a saved language encounter with contextual criteria, then focused repair, speech evidence, corrections and continuity, and real later review. Build media preservation with the first recorded answer. Validate the second-language fixture before claiming framework extensibility; conduct a separately agreed delayed study before claiming superior acquisition efficiency.

<!-- Read stamps: /Users/jinxinliu/.agents/skills/GOVERNANCE.md v12; /Users/jinxinliu/.agents/skills/knowledge-tools/SKILL.md v4; /Users/jinxinliu/.agents/skills/write-a-brief/SKILL.md v8; /Users/jinxinliu/.agents/skills/ticket/SKILL.md v3; /Users/jinxinliu/.agents/skills/brainstorm/SKILL.md unversioned; /Users/jinxinliu/.codex/plugins/cache/openai-curated-remote/pages/0.1.23/skills/write-page/SKILL.md unversioned; write-page/writing_quality.md unversioned. -->
