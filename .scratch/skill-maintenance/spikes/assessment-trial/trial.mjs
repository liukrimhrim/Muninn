// Throwaway assessment trial. The model call happens in the Codex chat, not here.
import {readFileSync, writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';

export function createTrial() {
  const statuses = ['demonstrated', 'error', 'not_shown', 'cannot_judge'];
  const kinds = ['follow_up', 'practice', 'fresh_check', 'clarify', 'stop'];
  const stable = x => JSON.stringify(x, (_, v) => v && typeof v === 'object' && !Array.isArray(v) ? Object.fromEntries(Object.keys(v).sort().map(k => [k, v[k]])) : v);
  const nonempty = s => typeof s === 'string' && s.trim().length > 0;
  function packet(data, id) {
    const c = data.cases.find(c => c.id === id);
    if (!c) throw Error(`Unknown case: ${id}`);
    const exercise = data.exercises.find(e => e.id === c.exercise_id);
    if (!exercise) throw Error(`Unknown exercise: ${c.exercise_id}`);
    return {case_id:c.id, exercise, response:c.response, assistance:c.assistance};
  }
  function validate(input, assessment) {
    const errors = [];
    if (!assessment || assessment.case_id !== input.case_id) return ['Assessment belongs to a different case.'];
    const criteria = input.exercise.criteria.map(c => c.id);
    const observations = assessment.observations;
    if (!Array.isArray(observations)) return ['Observations must be an array.'];
    if (observations.length !== criteria.length || new Set(observations.map(o => o.criterion)).size !== criteria.length) errors.push('Record each criterion exactly once.');
    for (const o of observations) {
      if (!criteria.includes(o.criterion)) errors.push(`Unknown criterion: ${o.criterion}`);
      if (!statuses.includes(o.status)) errors.push(`Unknown status: ${o.status}`);
      if (!nonempty(o.reason)) errors.push(`${o.criterion}: supply a reason.`);
      if (!Array.isArray(o.quotes)) { errors.push(`${o.criterion}: quotes must be an array.`); continue; }
      if (['demonstrated','error'].includes(o.status) && !o.quotes.length) errors.push(`${o.criterion}: evidence quote required.`);
      if (o.status === 'not_shown' && o.quotes.length) errors.push(`${o.criterion}: absent evidence cannot have a supporting quote.`);
      for (const q of o.quotes) if (!nonempty(q) || !input.response.includes(q)) errors.push(`${o.criterion}: quotation is not in the original answer.`);
    }
    const n = assessment.next;
    if (!n || !kinds.includes(n.kind)) return [...errors, 'Choose one valid next action.'];
    if (!nonempty(n.text) || !nonempty(n.reason)) errors.push('Next action needs learner-facing text and a reason.');
    if (!Array.isArray(n.targets) || n.targets.some(t => !criteria.includes(t)) || new Set(n.targets).size !== n.targets.length) errors.push('Next-action targets must be distinct criteria from this exercise.');
    if (['follow_up','practice','fresh_check'].includes(n.kind) && !n.targets?.length) errors.push('This action requires a target.');
    if (n.kind === 'practice' && !observations.some(o => o.status === 'error' && n.targets?.includes(o.criterion))) errors.push('Targeted remedial practice requires an observed error in a selected target.');
    if (n.kind === 'follow_up') {
      const branches = ['correct','wrong','unclear'].map(k => n.branches?.[k]);
      if (!branches.every(nonempty) || new Set(branches).size !== 3) errors.push('Follow-up needs distinct correct, wrong and unclear branches.');
    }
    if (!Array.isArray(assessment.alternatives) || !assessment.alternatives.every(nonempty)) errors.push('Alternatives must be an array of explanations.');
    return errors;
  }
  function validateBound(input, record) {
    if (!record || stable(record.input) !== stable(input)) return ['The saved assessment does not match the current prompt, answer, criteria or assistance.'];
    return validate(input, record.assessment);
  }
  function validateReview(input, review) {
    if (!review || stable(input) !== stable(review.input)) return ['Human review does not match this input.'];
    const ids = input.exercise.criteria.map(c => c.id);
    const errors = [];
    if (!nonempty(review.reviewer) || !nonempty(review.reason)) errors.push('Reviewer name and reason are required.');
    if (!review.statuses || Object.keys(review.statuses).length !== ids.length || !ids.every(id => statuses.includes(review.statuses[id]))) errors.push('Judge each criterion before revealing the AI assessment.');
    if (!kinds.includes(review.next_kind)) errors.push('Choose the next action.');
    if (!Array.isArray(review.targets) || review.targets.some(t => !ids.includes(t)) || new Set(review.targets).size !== review.targets.length) errors.push('Review targets must be distinct criteria from the exercise.');
    if (['follow_up','practice','fresh_check'].includes(review.next_kind) && !review.targets?.length) errors.push('Select at least one target.');
    if (typeof review.before_reveal !== 'boolean') errors.push('Record whether the AI assessment was already revealed.');
    return errors;
  }
  function compare(record, review) {
    const errors = [...validateBound(record.input, record), ...validateReview(record.input, review)];
    if (errors.length) throw Error(errors.join('\n'));
    const differences = record.assessment.observations.filter(o => review.statuses[o.criterion] !== o.status).map(o => ({criterion:o.criterion, ai:o.status, human:review.statuses[o.criterion]}));
    return {case_id:record.input.case_id, before_reveal:review.before_reveal,
      matching_criteria:record.assessment.observations.length-differences.length, total_criteria:record.assessment.observations.length,
      differences, action_matches:record.assessment.next.kind === review.next_kind,
      targets_match:stable([...record.assessment.next.targets].sort()) === stable([...review.targets].sort()),
      interpretation:'Agreement or disagreement only. Neither assessor is automatically treated as correct.'};
  }
  return {statuses, kinds, packet, validate, validateBound, validateReview, compare};
}

const T = createTrial();
const here = new URL('./', import.meta.url);
const read = name => JSON.parse(readFileSync(new URL(name, here), 'utf8'));
const save = (name, value) => writeFileSync(new URL(name, here), JSON.stringify(value,null,2)+'\n');
const scriptJSON = value => JSON.stringify(value).replace(/</g,'\\u003c').replace(/\u2028/g,'\\u2028').replace(/\u2029/g,'\\u2029');

function render(data, assessed) {
  const shell = readFileSync(new URL('review-shell.html', here),'utf8');
  const instructions = readFileSync(new URL('assessor-prompt.md',here),'utf8');
  return shell.replace('/*TRIAL_MODEL*/', `const T = (${createTrial.toString()})();\nconst DATA = ${scriptJSON(data)};\nconst ASSESSED = ${scriptJSON(assessed)};\nconst INSTRUCTIONS = ${scriptJSON(instructions)};`);
}

function main() {
  const [command='packet', caseId] = process.argv.slice(2);
  const data = read('inputs.json');
  const inputHash = createHash('sha256').update(readFileSync(new URL('inputs.json',here))).digest('hex');
  if (new Set(data.cases.map(c=>c.id)).size !== data.cases.length) throw Error('Duplicate input case IDs.');
  if (command === 'packet') {
    const inputs = caseId ? [T.packet(data,caseId)] : data.cases.map(c=>T.packet(data,c.id));
    console.log(JSON.stringify({input_sha256:inputHash,instructions:readFileSync(new URL('assessor-prompt.md',here),'utf8'), inputs},null,2));
    return;
  }
  if (command === 'build') {
    const output = read('model-output.json');
    if (output.input_sha256 !== inputHash) throw Error('Inputs changed since assessment. Request new assessments; do not rebind the saved judgments.');
    const ids = output.records.map(r=>r.case_id);
    if (new Set(ids).size !== ids.length) throw Error('Duplicate model assessment IDs.');
    const records = output.records.map(assessment => {
      const input = T.packet(data,assessment.case_id), errors = T.validate(input,assessment);
      if (errors.length) throw Error(`${assessment.case_id}: ${errors.join('\n')}`);
      return {input,assessment};
    });
    if (records.length !== data.cases.length) throw Error(`Missing assessments: ${data.cases.filter(c=>!ids.includes(c.id)).map(c=>c.id).join(', ')}`);
    const assessed = {assessor:output.assessor, input_provenance:data.provenance, records};
    save('assessed.json',assessed);
    writeFileSync(new URL('review.html',here),render(data,assessed));
    save('run-report.json',{assessed_cases:records.length, subjects:[...new Set(records.map(r=>r.input.exercise.subject))], criteria:records.reduce((n,r)=>n+r.assessment.observations.length,0), quotes:records.reduce((n,r)=>n+r.assessment.observations.reduce((m,o)=>m+o.quotes.length,0),0), structural_errors:0, human_comparisons:0, human_status:'Pending; build does not read or manufacture human judgments.', grading_accuracy:null, limitations:['Constructed answers authored by the same assistant.','Assessment performed in the current chat, not an automated API call.','Quote validity is not semantic validity.','Browser layout and interaction not yet verified.']});
    console.log(`Built ${records.length} validated assessment records and review.html. Human comparison pending.`);
    return;
  }
  if (command === 'compare') {
    if (!caseId) throw Error('Pass a human review JSON file path.');
    const reviews = JSON.parse(readFileSync(resolve(caseId),'utf8')).reviews;
    if (!Array.isArray(reviews) || new Set(reviews.map(r=>r.input.case_id)).size !== reviews.length) throw Error('Human reviews must have distinct case IDs.');
    const assessed = read('assessed.json');
    const comparisons = reviews.map(review => {
      const record = assessed.records.find(r=>r.input.case_id === review.input.case_id);
      if (!record) throw Error(`No assessment for ${review.input.case_id}`);
      const current = T.packet(data,record.input.case_id), errors = T.validateBound(current,record);
      if (errors.length) throw Error(errors.join('\n'));
      return T.compare(record,review);
    });
    console.log(JSON.stringify({comparisons,reviewed:comparisons.length,pending:assessed.records.length-comparisons.length,accuracy:null,note:'Human identity and independence are self-reported; comparisons are not accuracy scores.'},null,2));
    return;
  }
  throw Error('Commands: packet [case-id], build, compare <human-review.json>');
}
if (import.meta.main) main();
