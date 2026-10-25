// Runs the actual validator -> bridge -> planner seam. No LLM service call.
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import vm from 'node:vm';
import {createTrial} from '../assessment-trial/trial.mjs';
import {createBridge} from './bridge.mjs';
const here=new URL('./',import.meta.url),read=n=>readFileSync(new URL(n,here),'utf8');
const sha=s=>createHash('sha256').update(s).digest('hex');
const raw=read('inputs.json'),inputs=JSON.parse(raw).inputs,instructions=read('assessor-prompt-v2.md');
const html=read('../next-session.html'),source=html.match(/<script id="next-session-model">([\s\S]*?)<\/script>/)[1];
const data=JSON.parse(html.match(/<script id="records" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const M=vm.runInNewContext(source+'\nNextSession'),T=createTrial(),B=createBridge(T,M);
const packetPath=process.argv[3];
if(process.argv[2]==='packet'){
 const packetRaw=packetPath?readFileSync(packetPath,'utf8'):raw;
 console.log(JSON.stringify({input_sha256:sha(packetRaw),prompt_sha256:sha(instructions),instructions,inputs:packetPath?[JSON.parse(packetRaw)]:inputs},null,2));
}else{
 const judgments=JSON.parse(read('judgments.json'));
 if(judgments.input_sha256!==sha(raw))throw Error('Inputs changed since assessment. Reassess; do not rebind old judgments.');
 if(judgments.prompt_sha256!==sha(instructions))throw Error('Assessment protocol changed. Preserve prior judgments; reassess under the new protocol.');
 if(new Set(inputs.map(i=>i.case_id)).size!==inputs.length)throw Error('Duplicate input IDs.');
 const records=inputs.map(input=>({input,assessment:judgments.records.find(a=>a.case_id===input.case_id),assessor:judgments.assessor,protocol:{name:'assessor-prompt-v2.md',sha256:sha(instructions)}}));
 if(judgments.records.length!==inputs.length||new Set(judgments.records.map(a=>a.case_id)).size!==inputs.length)throw Error('Need exactly one assessment per input.');
 const apply=(state,r)=>B.connect(data,state,r.input,r);
 let state=M.empty();const stages=[];
 for(const record of records.filter(r=>r.input.attempt.origin==='recorded')){
  const before=state,result=apply(state,record);if(result.errors.length)throw Error(`${record.input.case_id}: ${result.errors.join('\n')}`);
  state=result.state;stages.push({record,before,result});
 }
 const actual=state,snapshot=JSON.stringify(actual),actualPlan=M.plan(data,actual);
 if(process.argv[2]==='connect'){
  if(!packetPath||!process.argv[4])throw Error('Usage: connect <answer-packet.json> <judgment.json>');
  const packetRaw=readFileSync(packetPath,'utf8'),input=JSON.parse(packetRaw),output=JSON.parse(readFileSync(process.argv[4],'utf8'));
  if(output.input_sha256!==sha(packetRaw)||output.prompt_sha256!==sha(instructions)||!output.assessor||output.records?.length!==1)throw Error('Need one identified assessment bound to these input and protocol bytes.');
  const record={input,assessment:output.records[0],assessor:output.assessor,protocol:{name:'assessor-prompt-v2.md',sha256:sha(instructions)}};
  const result=apply(actual,record);
  console.log(JSON.stringify({scope:'Single-answer intake against the recorded example history. Printed only; no saved learner-state update.',...result},null,2));
  if(result.errors.length)process.exitCode=1;
  process.exit();
 }
 for(const record of records.filter(r=>r.input.attempt.origin==='hypothetical')){
  const result=apply(actual,record);if(result.errors.length)throw Error(`${record.input.case_id}: ${result.errors.join('\n')}`);
  stages.push({record,before:actual,result});
 }
 const checks=[],check=(name,met)=>checks.push({name,met:Boolean(met)}),same=(a,b)=>JSON.stringify(a)===JSON.stringify(b),clone=x=>JSON.parse(JSON.stringify(x));
 const get=id=>stages.find(s=>s.record.input.case_id===id),result=id=>get(id).result;
 const bindings=inputs.filter(i=>i.source).map(i=>{
  const text=read('../'+i.source);
  return {case_id:i.case_id,source:i.source,source_sha256:sha(text),response_found:text.includes(i.response),prompt_found:text.includes(i.exercise.prompt),context_found:i.context.filter(c=>c.source).every(c=>read('../'+c.source).includes(c.text))};
 });
 check('All ten real answers, prompt excerpts and quoted context bind to the transcripts',bindings.length===10&&bindings.every(b=>b.response_found&&b.prompt_found&&b.context_found));
 check('The real raw-answer pipeline reproduces the approved single later exercise',actualPlan.now.length===0&&same(actualPlan.later.map(a=>a.targets),[['ops.list','ops.logs','ops.source']]));
 check('The supported misread adds no extra remediation or second halving observation',M.evidence(actual,'binary.halving').length===1&&M.status(actual,'binary.comparison').last.issue==='accepted_misread');
 check('Every event retains its exact input and assessment',stages.every(s=>same(s.result.event.assessmentRecord,s.record)));
 check('A source hypothesis is unresolved grading, not a learner error',result('L02-source-question').event.observations.length===0&&result('L02-source-question').unresolved.length===1&&result('L02-source-question').proposal.kind==='follow_up');
 check('Correct later responses remove the three separate drill candidates',result('S-later-correct').plan.now.length===0&&result('S-later-correct').plan.later.length===0);
 check('Mixed success directs help only to the log command',same(result('S-later-log-error').plan.now.map(a=>a.targets),[['ops.logs']])&&same(result('S-later-log-error').plan.later.map(a=>a.targets),[['ops.logs']]));
 check('Missing source evidence leaves its previous observation intact without an immediate quiz',result('S-later-omission').plan.now.length===0&&result('S-later-omission').proposal.kind==='stop'&&M.status(result('S-later-omission').state,'ops.source').last.event.id==='L02-source-hinted');
 check('Ambiguous grading schedules its clarification while preserving later checks and evidence',same(result('S-later-ambiguous').plan.later,actualPlan.later)&&same(result('S-later-ambiguous').plan.now.map(a=>[a.kind,a.targets]),[['clarify',['ops.source']]])&&result('S-later-ambiguous').event.observations.length===0&&result('S-later-ambiguous').unresolved.length===1);
 check('A hint applies only to its named target, keeping one later source check',same(result('S-later-hinted').plan.later.map(a=>a.targets),[['ops.source']])&&result('S-later-hinted').event.observations.filter(o=>o.assisted).length===1);
 check('Self-report of a misread cannot remove an explicit wrong halving rule',same(result('S-misread-wrong').plan.now.map(a=>a.targets),[['binary.halving']]));
 check('An instruction-like off-task answer supplies no target evidence',result('S-instructions').event.observations.length===0&&same(result('S-instructions').plan,actualPlan));
 check('Prior hint history survives a later unhinted demonstration',M.evidence(result('S-later-correct').state,'ops.source').some(o=>o.assisted)&&!M.status(result('S-later-correct').state,'ops.source').last.assisted);
 const sample=get('S-later-hinted');
 for(const [name,change] of Object.entries({response:i=>i.response+=' changed',prompt:i=>i.exercise.prompt+=' changed',criteria:i=>i.exercise.criteria[0].rule+=' changed',context:i=>i.context.push({id:'new',role:'task',text:'New evidence'}),help:i=>i.assistance=[],phase:i=>i.attempt.phase='current'})){
  const input=clone(sample.record.input);change(input);
  check(`Changed ${name} cannot reuse an old assessment`,B.connect(data,actual,input,sample.record).errors.length>0);
 }
 const reject=(id,change)=>{const s=get(id),r=clone(s.record);change(r);return apply(s.before,r).errors.length>0;};
 check('An invented response quotation is rejected',reject('S-later-correct',r=>r.assessment.observations[0].quotes=['I never wrote this']));
 check('Misread classification needs contextual support beyond self-report',reject('L01-misread',r=>r.assessment.observations[0].context_quotes=[]));
 check('Misread support cannot cite tutor text as learner reasoning',reject('L01-misread',r=>r.input.context[0].role='tutor'));
 check('A misread tag on an explicit error is rejected',reject('S-misread-wrong',r=>r.assessment.observations[0].issue='supported_misread'));
 check('One error does not authorize remediation of correct neighbors',reject('S-later-log-error',r=>r.assessment.next.targets.push('ops.list')));
 check('A missing criterion cannot silently disappear from assessment',reject('S-later-correct',r=>r.assessment.observations.pop()));
 check('An unknown planning target is rejected',reject('S-later-correct',r=>{r.input.exercise.criteria[0].id='unknown';r.assessment.observations[0].criterion='unknown';}));
 const completed=result('S-later-correct').state;
 check('Exact duplicate delivery is idempotent',same(apply(completed,get('S-later-correct').record).state,completed));
 const changed=clone(get('S-later-correct').record);changed.assessment.observations[0].reason+=' Revised interpretation.';
 check('Changed assessment under the same answer ID cannot overwrite history',apply(completed,changed).errors.length>0);
 check('Contrast cases never alter the real learner history',JSON.stringify(actual)===snapshot&&actual.events.every(e=>e.origin==='recorded'));
 // Feed the actual code to the standalone page; old validators are reused, not copied by hand.
 const json=x=>JSON.stringify(x).replace(/</g,'\\u003c').replace(/\u2028/g,'\\u2028').replace(/\u2029/g,'\\u2029');
 const script=`${source}\nconst T=(${createTrial.toString()})();\nconst B=(${createBridge.toString()})(T,NextSession);\nconst DATA=${json(data)};\nconst RECORDS=${json(records)};\nconst ASSESSOR=${json(judgments.assessor)};`;
 const page=read('shell.html').replace('/*MODEL*/',script);
 // Minimal DOM wiring only; no browser rendering, layout or accessibility claim.
 class Element{constructor(){this.children=[];this.textContent='';this.value='';this.attributes={};}append(...children){this.children.push(...children);}replaceChildren(...children){this.children=children;}setAttribute(k,v){this.attributes[k]=v;}}
 const elements=new Map([...page.matchAll(/\bid="([^"]+)"/g)].map(m=>[m[1],new Element()]));
 const document={getElementById:id=>elements.get(id),createElement:()=>new Element()};
 vm.runInNewContext(page.match(/<script>([\s\S]*?)<\/script>/)[1],{document});
 check('Page initializes the real-record walkthrough',elements.get('case-title').textContent==='L01-explanation');
 elements.get('apply').onclick();
 check('Actual page handler connects the selected answer and displays its evidence',elements.get('observations').children.length===1&&elements.get('result').textContent.startsWith('Connected'));
 elements.get('tabs').children[3].onclick();elements.get('apply').onclick();
 check('Ambiguity walkthrough exposes grading uncertainty without target errors',elements.get('result').textContent.includes('1 unresolved')&&elements.get('observations').children.length===0);
 check('Ambiguity walkthrough labels the action as clarification rather than corrective help',elements.get('plan').children.some(e=>e.textContent.startsWith('Clarify:'))&&!elements.get('plan').children.some(e=>e.textContent.startsWith('Focused help:')));
 elements.get('alter').onclick();elements.get('apply').onclick();
 check('Edited-answer button cannot reuse the old judgment',elements.get('result').textContent.startsWith('Rejected'));
 elements.get('restore').onclick();elements.get('apply').onclick();
 check('Restore returns to the valid bound answer',elements.get('result').textContent.startsWith('Connected'));
 const report={scope:'Input-bound current-chat assessments connected through the existing validator and planner. Seven contrasts are authored, not independent tests of grading accuracy.',assessor:judgments.assessor,input_sha256:sha(raw),prompt_sha256:sha(instructions),validator_sha256:sha(createTrial.toString()),planner_sha256:sha(source),bridge_sha256:sha(createBridge.toString()),bindings,actualPlan,checks,grading_accuracy:null,human_comparisons:0,variants:stages.filter(s=>s.record.input.attempt.origin==='hypothetical').map(s=>({id:s.record.input.case_id,observed:s.result.event.observations.map(o=>({target:o.target,result:o.result,assisted:o.assisted})),unresolved:s.result.unresolved.map(o=>o.criterion),unobserved:s.result.unobserved.map(o=>o.criterion),proposal:s.result.proposal,plan:s.result.plan})),limitations:['Semantic assessments were authored in this chat; no automatic model service is connected.','The same assistant selected cases and expected behavior; no independent accuracy estimate.','Structural quotation checks cannot establish semantic truth or completeness of supplied history.','Browser rendering and accessibility remain unverified; UI handlers ran on a minimal DOM surface.','No real later-session response, elapsed interval, live command execution, or learning benefit was measured.']};
 writeFileSync(new URL('report.json',here),JSON.stringify(report,null,2)+'\n');
 writeFileSync(new URL('index.html',here),page);
 console.table(checks);console.log(`${checks.filter(c=>c.met).length}/${checks.length} observations matched. ${records.length} bound assessments; grading accuracy unmeasured.`);
 if(checks.some(c=>!c.met))process.exitCode=1;
}
