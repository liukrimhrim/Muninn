// Replay the actual validation/comparison functions with controlled mutations.
// Synthetic comparison inputs below are NOT human judgments or grading evidence.
import {readFileSync, writeFileSync} from 'node:fs';
import vm from 'node:vm';
import {createTrial} from './trial.mjs';

const T=createTrial(),root=new URL('./',import.meta.url),read=n=>JSON.parse(readFileSync(new URL(n,root),'utf8'));
const data=read('inputs.json'),records=read('assessed.json').records,find=id=>records.find(r=>r.input.case_id===id),copy=x=>structuredClone(x),results=[];
function observe(name,run,expected){const actual=run();results.push({name,expected,actual,met:JSON.stringify(actual)===JSON.stringify(expected)});}
observe('Saved batch matches exact inputs and evidence contract',()=>records.every(r=>T.validateBound(T.packet(data,r.input.case_id),r).length===0),true);
observe('Reject invented quotation',()=>{const r=copy(find('B03'));r.assessment.observations[0].quotes=['a statement the learner never made'];return T.validateBound(r.input,r).some(e=>e.includes('quotation'));},true);
observe('Reject repeated criterion hiding an omitted criterion',()=>{const r=copy(find('B03'));r.assessment.observations[1]=r.assessment.observations[0];return T.validateBound(r.input,r).some(e=>e.includes('exactly once'));},true);
observe('Reject remedial practice from only missing evidence',()=>{const r=copy(find('B02'));r.assessment.next.kind='practice';return T.validateBound(r.input,r).some(e=>e.includes('observed error'));},true);
observe('Reject follow-up with identical branches',()=>{const r=copy(find('B02'));r.assessment.next.branches={correct:'Repeat.',wrong:'Repeat.',unclear:'Repeat.'};return T.validateBound(r.input,r).some(e=>e.includes('distinct'));},true);
for(const field of ['response','assistance','prompt','criterion'])observe(`Reject stale assessment after ${field} changes`,()=>{const r=find('A04'),input=copy(r.input);if(field==='response')input.response+=' Additional answer.';if(field==='assistance')input.assistance=[];if(field==='prompt')input.exercise.prompt+=' New requirement.';if(field==='criterion')input.exercise.criteria[0].rule='A changed rubric.';return T.validateBound(input,r).length>0;},true);
const r=find('B03');
const synthetic={input:copy(r.input),reviewer:'SYNTHETIC COMPARISON PROBE — NOT A HUMAN',statuses:Object.fromEntries(r.assessment.observations.map(o=>[o.criterion,o.status])),next_kind:r.assessment.next.kind,targets:[...r.assessment.next.targets],reason:'Generated solely to exercise comparison arithmetic.',before_reveal:true};
observe('Synthetic matching review comparison',()=>{const c=T.compare(r,synthetic);return [c.matching_criteria,c.total_criteria,c.action_matches,c.targets_match];},[4,4,true,true]);
observe('Synthetic disagreement remains disagreement, not accuracy',()=>{const changed=copy(synthetic);changed.statuses.subject='not_shown';changed.next_kind='follow_up';changed.targets=['subject'];const c=T.compare(r,changed);return [c.matching_criteria,c.differences.length,c.action_matches,c.targets_match,'accuracy' in c];},[3,1,false,false,false]);
observe('Incomplete human review rejected',()=>{const changed=copy(synthetic);delete changed.statuses.subject;return T.validateReview(r.input,changed).length>0;},true);
observe('Unblinded flag is retained',()=>T.compare(r,{...synthetic,before_reveal:false}).before_reveal,false);
const html=readFileSync(new URL('review.html',root),'utf8'),script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(script);
observe('Generated HTML contains the exact pure model and frozen data',()=>{const source=script.split("const $=id=>")[0],rendered=vm.runInNewContext(source+'\n({T,ASSESSED})');return rendered.ASSESSED.records.length===records.length && rendered.T.validateBound(r.input,r).length===0;},true);
const report={scope:'Structural validation, input binding, comparison arithmetic and generated script syntax only. No real browser, human reviewer, semantic accuracy or learning outcome is tested.',results,all_met:results.every(r=>r.met)};
writeFileSync(new URL('verification.json',root),JSON.stringify(report,null,2)+'\n');
console.table(results.map(r=>({check:r.name,met:r.met})));if(!report.all_met)process.exitCode=1;
