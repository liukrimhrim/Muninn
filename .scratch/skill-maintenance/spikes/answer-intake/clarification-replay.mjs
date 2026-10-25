// Real frozen conflict plus authored continuations; no new learner or model call.
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import vm from 'node:vm';
import {createTrial} from '../assessment-trial/trial.mjs';
import {createBridge} from './bridge.mjs';
import {packets} from '../independent-assessment/adapter.mjs';
const here=new URL('./',import.meta.url),read=n=>readFileSync(new URL(n,here),'utf8'),json=n=>JSON.parse(read(n));
const sha=s=>createHash('sha256').update(s).digest('hex'),clone=x=>JSON.parse(JSON.stringify(x)),same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const frozen=json('../independent-assessment/freeze.json');
for(const [file,hash] of Object.entries(frozen.files))if(sha(read('../independent-assessment/'+file))!==hash)throw Error('Changed frozen assessment artifact: '+file);
const input=packets(json('../independent-assessment/blind-inputs.json')).find(i=>i.case_id==='SE.27b.333.1');
const assessment=json('../independent-assessment/assessment.json').records.find(a=>a.case_id===input.case_id);
const original={input,assessment},prediction='SE_27b_f2',cause='SE_27b_f4',other='arithmetic';
const source=read('../next-session.html').match(/<script id="next-session-model">([\s\S]*?)<\/script>/)[1];
const M=vm.runInNewContext(source+'\nNextSession'),B=createBridge(createTrial(),M);
const labels={[prediction]:'Change in the reading',[cause]:'Effect of hand contact',SE_27b_f3:'Whose hand is involved',SE_27b_f6:'Warming effect',[other]:'Separate arithmetic answer'};
const data={targets:[...input.exercise.criteria.map(c=>({id:c.id,label:labels[c.id],...([prediction,cause].includes(c.id)?{group:'pending'}:{})})),{id:other,label:labels[other]}],groups:{pending:'Invented later check for the two clarified targets'}};
function reply(id,response,statuses,kind='stop',targets=[],phase='current',assistance=[]){
 const criteria=Object.keys(statuses).map(id=>input.exercise.criteria.find(c=>c.id===id)||{id,rule:'Two plus two equals four.'});
 const input2={case_id:id,attempt:{id,origin:'hypothetical',phase},exercise:{prompt:assessment.next.text,criteria},response,
  context:[{id:'origin',role:'task',text:'Authored continuation of the archived thermometer example; not a collected learner answer.'}],assistance};
 return {input:input2,assessment:{case_id:id,observations:Object.entries(statuses).map(([criterion,status])=>({criterion,status,quotes:status==='not_shown'?[]:[response],reason:'Authored observation for checking action policy, not independent semantic validation.'})),next:{kind,targets,text:kind==='practice'?'Offer help for the stated error.':'Stop this diagnostic turn.',reason:'This constructed branch checks what the existing planner does.'},alternatives:[]}};
}
const records={original,
 correct:reply('invented-correct','The reading rises because my hand transfers heat to the bulb.',{[prediction]:'demonstrated',[cause]:'demonstrated'}),
 wrong:reply('invented-wrong','The reading falls because my hand takes heat away from the bulb.',{[prediction]:'error',[cause]:'error'},'practice',[prediction,cause]),
 unclear:reply('invented-unclear','I cannot explain what I meant.',{[prediction]:'cannot_judge',[cause]:'cannot_judge'}),
 omitted:reply('invented-omitted','I left that part out.',{[prediction]:'not_shown',[cause]:'not_shown'}),
 partial:reply('invented-partial','The reading rises.',{[prediction]:'demonstrated',[cause]:'not_shown'}),
 unrelated:reply('invented-unrelated','Two plus two equals five.',{[other]:'error'},'practice',[other])};
records.unrelated.input.exercise.prompt='What is two plus two?';
const connect=(state,r)=>{const out=B.connect(data,state,r.input,r);if(out.errors.length)throw Error(out.errors.join('\n'));return out;};
const initial=connect(M.empty(),original),before=JSON.stringify(initial.state),checks=[],check=(name,met)=>checks.push({name,met:Boolean(met)});
const help=r=>r.plan.now.filter(a=>a.kind==='help').flatMap(a=>a.targets);
const questions=r=>r.plan.now.filter(a=>['clarify','follow_up'].includes(a.kind));
check('Frozen thermometer conflict chooses one follow-up with no corrective help',same(questions(initial).map(a=>a.targets),[[prediction,cause]])&&help(initial).length===0);
check('The original wrong prediction and complete assessment remain unchanged',M.status(initial.state,prediction).last.result==='error'&&same(initial.event.assessmentRecord,original));
check('Clarification keeps the constructed later check pending',same(initial.plan.later.map(a=>a.targets),[[prediction,cause]]));
check('Planning the saved state directly makes the same action choice',same(M.plan(data,initial.state),initial.plan));
const outcomes=Object.fromEntries(Object.entries(records).filter(([k])=>k!=='original').map(([k,r])=>[k,connect(initial.state,r)]));
check('A clear correct reply ends clarification and help but preserves the earlier error',outcomes.correct.plan.now.length===0&&M.evidence(outcomes.correct.state,prediction).some(o=>o.result==='error'));
check('A current correct reply does not establish delayed retention',same(outcomes.correct.plan.later.map(a=>a.targets),[[prediction,cause]]));
check('A clear wrong reply releases focused help for the two observed errors',same(help(outcomes.wrong),[prediction,cause])&&questions(outcomes.wrong).length===0);
check('An unclear reply can stop questioning with unresolved assessment, without reviving help',outcomes.unclear.plan.now.length===1&&outcomes.unclear.plan.now[0].kind==='review'&&same(outcomes.unclear.plan.now[0].targets,[prediction,cause])&&help(outcomes.unclear).length===0);
check('Omitted evidence does not dismiss the outstanding question or release help',same(questions(outcomes.omitted).map(a=>a.targets),[[prediction,cause]])&&help(outcomes.omitted).length===0);
check('An unrelated error still receives help while the original clarification stays pending',same(help(outcomes.unrelated),[other])&&same(questions(outcomes.unrelated).map(a=>a.targets),[[prediction,cause]]));
check('A partial answer leaves only the unresolved target for assessment review',outcomes.partial.plan.now.length===1&&outcomes.partial.plan.now[0].kind==='review'&&same(outcomes.partial.plan.now[0].targets,[cause])&&help(outcomes.partial).length===0);
const mixed=clone(original);mixed.input.case_id=mixed.assessment.case_id=mixed.input.attempt.id='invented-mixed';mixed.input.attempt.origin='hypothetical';mixed.input.response+=' Two plus two equals five.';mixed.input.exercise.criteria.push({id:other,rule:'Two plus two equals four.'});mixed.assessment.observations.push({criterion:other,status:'error',quotes:['Two plus two equals five.'],reason:'Separate authored error to check target scope.'});
const mixedResult=connect(M.empty(),mixed);
check('The same answer can clarify one concern and offer help for an unrelated error',same(help(mixedResult),[other])&&same(questions(mixedResult).map(a=>a.targets),[[prediction,cause]]));
const late=clone(records.correct);late.input.attempt.phase='later';
const lateResult=connect(initial.state,late);
check('An explicitly hypothetical later unhinted answer can clear the two checks',lateResult.plan.now.length===0&&lateResult.plan.later.length===0);
late.input.assistance=[{timing:'current',targets:[cause],text:'Invented hint supplying the hand-to-bulb heat direction.'}];
const helped=connect(initial.state,late);
check('A hinted clarification retains only the helped target for a later check',helped.plan.now.length===0&&same(helped.plan.later.map(a=>a.targets),[[cause]])&&M.status(helped.state,cause).last.assisted);
const stillQuestion=clone(late);stillQuestion.input.assistance=[];stillQuestion.assessment.next=clone(assessment.next);
check('A later demonstration with an outstanding interpretation question cannot clear its checks',same(connect(initial.state,stillQuestion).plan.later.map(a=>a.targets),[[prediction,cause]]));
const clarify=clone(original);clarify.assessment.next.kind='clarify';delete clarify.assessment.next.branches;
check('A targeted clarification has the same precedence as a diagnostic follow-up',connect(M.empty(),clarify).plan.now[0].kind==='clarify'&&help(connect(M.empty(),clarify)).length===0);
check('Repeated delivery of the old answer cannot reopen a resolved clarification',same(connect(lateResult.state,original).plan,lateResult.plan));
check('The original state is unchanged by all continuations',JSON.stringify(initial.state)===before);
// Embed the same real functions in the standalone walkthrough, not another policy.
const renamed=(r,id)=>{const c=clone(r);c.input.case_id=c.input.attempt.id=c.assessment.case_id=id;return c;};
records.later=renamed(records.correct,'invented-later');records.later.input.attempt.phase='later';
records.hinted=renamed(records.later,'invented-hinted');records.hinted.input.assistance=clone(late.input.assistance);
const scriptJSON=x=>JSON.stringify(x).replace(/</g,'\\u003c');
const page=read('clarification-shell.html').replace('/*MODEL*/',`${source}\nconst B=(${createBridge.toString()}) ((${createTrial.toString()})(),NextSession);\nconst DATA=${scriptJSON(data)},RECORDS=${scriptJSON(records)};`);
class Element{constructor(){this.children=[];this.textContent='';}append(...xs){this.children.push(...xs);}replaceChildren(...xs){this.children=xs;}}
const elements=new Map([...page.matchAll(/\bid="([^"]+)"/g)].map(m=>[m[1],new Element()]));
vm.runInNewContext(page.match(/<script>([\s\S]*?)<\/script>/)[1],{document:{getElementById:id=>elements.get(id),createElement:()=>new Element()}});
const visible=()=>elements.get('decision').children.map(e=>e.textContent).join('\n');
check('Walkthrough initially displays clarification without corrective help',visible().includes('Clarify first:')&&!visible().includes('Focused help:'));
elements.get('tabs').children[1].onclick();elements.get('steps').children[0].onclick();
check('Guided wrong-answer button displays focused help',visible().includes('Focused help:')&&!visible().includes('Clarify first:'));
elements.get('tabs').children[2].onclick();elements.get('steps').children[0].onclick();
check('Guided unclear-answer button displays unresolved assessment without another question',visible().includes('Assessment unresolved:')&&!visible().includes('Clarify first:')&&!visible().includes('Focused help:'));
elements.get('reset').onclick();elements.get('actions').children[0].onclick();
check('Free-play correct answer retains the original error in visible history',!visible().includes('Focused help:')&&elements.get('evidence').children.some(e=>e.textContent.includes('earlier error remains')));
writeFileSync(new URL('clarification.html',here),page);
const report={scope:'One frozen real response and explicitly authored continuations. Pending checks are constructed, not a curriculum or retention result.',planner_sha256:sha(source),frozen_hashes:'verified',checks,initial:{proposal:initial.proposal,plan:initial.plan},outcomes:Object.fromEntries(Object.entries(outcomes).map(([k,v])=>[k,{plan:v.plan,observations:v.event.observations}])),semantic_accuracy:null};
writeFileSync(new URL('clarification-results.json',here),JSON.stringify(report,null,2)+'\n');
console.table(checks);console.log(`${checks.filter(c=>c.met).length}/${checks.length} clarification checks passed.`);
if(checks.some(c=>!c.met))process.exitCode=1;
