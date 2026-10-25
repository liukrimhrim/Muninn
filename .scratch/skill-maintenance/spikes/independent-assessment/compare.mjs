// Post-freeze comparison. Never revises the original assessment or raw annotation.
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import vm from 'node:vm';
import {packets} from './adapter.mjs';
import {createTrial} from '../assessment-trial/trial.mjs';
import {createBridge} from '../answer-intake/bridge.mjs';
const here=new URL('./',import.meta.url),read=n=>readFileSync(new URL(n,here),'utf8'),json=n=>JSON.parse(read(n));
const sha=s=>createHash('sha256').update(s).digest('hex'),frozen=json('freeze.json');
for(const [name,hash] of Object.entries(frozen.files))if(sha(read(name))!==hash)throw Error(`Frozen artifact changed: ${name}`);
if(sha(read('withheld-reference.json'))!==frozen.expected_reference_sha256)throw Error('Reference changed since pre-reveal commitment.');
const blind=json('blind-inputs.json'),reference=json('withheld-reference.json'),assessment=json('assessment.json');
if(reference.blind_inputs_sha256!==sha(read('blind-inputs.json')))throw Error('Reference/input mismatch.');
const mapping={'Expressed':'demonstrated','Inferred':'demonstrated','Contra-Expr':'error','Contra-Infr':'error','Self-Contra':'error','Unaddressed':'not_shown','Assumed':null,'Diff-Arg':null};
const source=read('../next-session.html').match(/<script id="next-session-model">([\s\S]*?)<\/script>/)[1];
// This report was independently audited against the pre-fix components. Do not
// silently replace it with a later planner's answers under the old audit claim.
if(sha(source)!=='670f3293704721f1030f34d89956ec004c4883b2c638f98088047b8d0d7a3268'||sha(createTrial.toString())!=='dd8dbe4c98c2e3890e719d192f70cd56ac0950e077ed5553835082e524baec57'||sha(createBridge.toString())!=='3758156775ac7b4f62da67d6df34a5477fb83535c92b4180f9ff1eda248ac717')throw Error('Historical comparison dependencies changed. Replay from commit bef617c to reproduce the audited report; run answer-intake/clarification-replay.mjs for the revised action policy.');
const M=vm.runInNewContext(source+'\nNextSession'),B=createBridge(createTrial(),M);
const refs=new Map(reference.questions.flatMap(q=>q.responses.map(r=>[r.response_id,r])));
const rows=[],cases=[],counts={match:0,disagree:0,abstain:0,excluded:0},byLabel={};
for(const input of packets(blind)){
 const a=assessment.records.find(a=>a.case_id===input.case_id),r=refs.get(input.case_id);
 const data={targets:input.exercise.criteria.map(c=>({id:c.id,label:c.rule})),groups:{}};
 const connected=B.connect(data,M.empty(),input,{input,assessment:a});
 if(connected.errors.length)throw Error(connected.errors.join('\n'));
 if(!r||r.facet_annotations.length!==a.observations.length||new Set(r.facet_annotations.map(f=>f.facetID)).size!==a.observations.length)throw Error('Reference coverage mismatch.');
 const caseRows=a.observations.map(o=>{
  const facet=r.facet_annotations.find(f=>f.facetID===o.criterion);
  if(!facet||!Object.hasOwn(mapping,facet.label))throw Error('Unknown or missing reference label.');
  const mapped=mapping[facet.label],outcome=mapped===null?'excluded':o.status==='cannot_judge'?'abstain':o.status===mapped?'match':'disagree';
  counts[outcome]++;byLabel[facet.label]??={total:0,match:0,disagree:0,abstain:0,excluded:0};byLabel[facet.label].total++;byLabel[facet.label][outcome]++;
  return {case_id:input.case_id,question_id:input.source.question_id,facet_id:o.criterion,reference_label:facet.label,reference_mapped:mapped,assessor_status:o.status,outcome,reason:o.reason,quotes:o.quotes};
 });
 rows.push(...caseRows);
 // This is explicitly counterfactual: a pending check for each comparable facet,
 // treating the archived text AS IF it were a later answer without a hint.
 const comparable=caseRows.filter(r=>r.reference_mapped!==null);
 const probeData={targets:comparable.map(r=>({id:r.facet_id,group:'pending'})),groups:{pending:'Hypothetical pending check of comparable facets'}};
 const planFor=field=>{
  const observations=comparable.filter(r=>['demonstrated','error'].includes(r[field])).map(r=>({target:r.facet_id,result:r[field],assisted:false,help:'COUNTERFACTUAL: assume a later unhinted check; actual corpus assistance and timing are unknown.'}));
  const event={id:`counterfactual-${field}-${input.case_id}`,attempt:input.case_id,origin:'hypothetical',phase:'later',observations};
  const plan=M.plan(probeData,M.append(M.empty(),event));
  return {help:plan.now.flatMap(a=>a.targets),pending:plan.later.flatMap(a=>a.targets),removed:comparable.map(r=>r.facet_id).filter(t=>!plan.later.some(a=>a.targets.includes(t)))};
 };
 const ai=planFor('assessor_status'),ref=planFor('reference_mapped');
 const difference=(a,b)=>a.filter(x=>!b.includes(x));
 cases.push({case_id:input.case_id,proposed_next:a.next,actual_immediate_help:connected.plan.now.flatMap(a=>a.targets),
  clarification_proposed_while_planner_offers_help:['clarify','follow_up'].includes(a.next.kind)&&connected.plan.now.some(x=>x.kind==='help'),
  counterfactual:{assessor:ai,mapped_reference:ref,extra_removed_against_reference:difference(ai.removed,ref.removed),extra_retained_against_reference:difference(ai.pending,ref.pending),extra_help_against_reference:difference(ai.help,ref.help),missing_help_against_reference:difference(ref.help,ai.help)}});
}
if(rows.length!==48||cases.length!==12)throw Error('Unexpected selected sample size.');
const sum=key=>cases.reduce((n,c)=>n+c.counterfactual[key].length,0);
const report={scope:'Blind assessment compared with pre-existing human facet annotations, using the frozen mapping. Agreement is not verified correctness; no human practice judgments exist.',freeze_commit:'f397ef8',freeze_hash_checks:'all passed',reference_sha256:sha(read('withheld-reference.json')),cases:cases.length,facets:rows.length,comparable:rows.length-counts.excluded,counts,byLabel,mapping,rows,caseConsequences:cases,counterfactualTotals:{extra_removed_against_reference:sum('extra_removed_against_reference'),extra_retained_against_reference:sum('extra_retained_against_reference'),extra_help_against_reference:sum('extra_help_against_reference'),missing_help_against_reference:sum('missing_help_against_reference')},limitations:['12 correlated student responses across four selected science questions; not representative.','Public data may have appeared in model training.','12 Assumed labels are excluded by the pre-reveal convention.','Annotation and assessor interpretations may both be wrong.','Practice consequences are policy simulations, not observed teaching effects.','No source human judgments of next actions, misread diagnosis, assistance, retention or mastery.']};
writeFileSync(new URL('comparison.json',here),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({comparable:report.comparable,counts,byLabel,counterfactualTotals:report.counterfactualTotals,clarifyBeforeHelp:cases.filter(c=>c.clarification_proposed_while_planner_offers_help).map(c=>c.case_id)},null,2));
