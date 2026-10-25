// Real validator -> bridge -> planner. Authored expectations check behavior, not learning.
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import vm from 'node:vm';
import {createTrial} from '../assessment-trial/trial.mjs';
import {createBridge} from '../answer-intake/bridge.mjs';
import {createExamples} from './examples.mjs';
const here=new URL('./',import.meta.url),read=n=>readFileSync(new URL(n,here),'utf8');
const clone=x=>JSON.parse(JSON.stringify(x)),same=(a,b)=>JSON.stringify(a)===JSON.stringify(b),sha=s=>createHash('sha256').update(s).digest('hex');
const source=read('../next-session.html').match(/<script id="next-session-model">([\s\S]*?)<\/script>/)[1];
const M=vm.runInNewContext(source+'\nNextSession'),T=createTrial(),B=createBridge(T,M),examples=createExamples();
const checks=[],check=(name,run)=>{try{checks.push({name,met:Boolean(run())});}catch(e){checks.push({name,met:false,error:e.message});}};
const apply=(key,id,state=M.empty())=>{const {data,records}=examples[key],r=records[id],out=B.connect(data,state,r.input,r);if(out.errors.length)throw Error(out.errors.join('; '));return out;};
const help=r=>r.plan.now.filter(a=>a.kind==='help').flatMap(a=>a.targets),later=r=>r.plan.later.flatMap(a=>a.targets);
const reject=(change)=>{const {data,records}=clone(examples.operations),r=records.later;change(data,r);return B.connect(data,M.empty(),r.input,r).errors.length>0;};
check('Useful evidence choice plus wrong command asks for production help only',()=>same(help(apply('operations','error')),['ops.produceLogs']));
check('Wrong evidence choice plus correct command asks for selection help only',()=>same(help(apply('operations','choiceError')),['ops.chooseLogs']));
check('Several criteria produce one capability observation with all evidence references',()=>{const r=apply('operations','later'),o=r.event.observations.find(o=>o.target==='ops.produceLogs');return r.event.observations.length===3&&same(o.evidenceRefs.map(r=>r.criterion),['verb','address']);});
check('Partial command evidence does not become either a failure or a complete demonstration',()=>{const r=apply('operations','partial');return !r.event.observations.some(o=>o.target==='ops.produceLogs')&&help(r).length===0&&later(r).includes('ops.produceLogs');});
check('An incidental criterion is retained without becoming a practice target',()=>{const {data,records}=clone(examples.operations),r=records.later;r.assessment.observations.find(o=>o.criterion==='wording').status='error';r.assessment.observations.find(o=>o.criterion==='wording').quotes=[r.input.response];const out=B.connect(data,M.empty(),r.input,r);return !out.errors.length&&help(out).length===0&&out.event.assessmentRecord.assessment.observations.some(o=>o.criterion==='wording'&&o.status==='error');});
check('Known mathematical parts with wrong combination target integration only',()=>same(help(apply('mathematics','error')),['math.integrate']));
check('Later parts alone cannot clear a previously observed integration error',()=>{const first=apply('mathematics','error'),r=apply('mathematics','partsOnly',first.state);return same(help(r),['math.integrate'])&&same(later(r),['math.integrate']);});
check('One criterion reused by two capabilities retains the same evidence reference',()=>{const r=apply('mathematics','later'),refs=r.event.observations.filter(o=>['math.work','math.integrate'].includes(o.target)).map(o=>o.evidenceRefs.find(e=>e.criterion==='work'));return refs.length===2&&same(refs[0],refs[1]);});
check('A hint to a shared criterion qualifies both dependent capabilities only',()=>{const r=apply('mathematics','hinted');return same(r.event.observations.filter(o=>o.assisted).map(o=>o.target),['math.work','math.integrate'])&&same(later(r),['math.work','math.integrate']);});
check('A command-form hint leaves evidence choice and functional evidence independent',()=>{const r=apply('operations','hinted');return same(r.event.observations.filter(o=>o.assisted).map(o=>o.target),['ops.produceLogs'])&&same(later(r),['ops.produceLogs']);});
check('A reconstruction goal does not silently add fluent-recall observations or drills',()=>{const r=apply('mathematics','later');return !r.event.observations.some(o=>o.target==='math.fluent')&&!Object.hasOwn(r.plan.perTarget,'math.fluent')&&r.plan.now.length===0&&r.plan.later.length===0;});
check('Overlapping practice bundles schedule each pending target once',()=>{const r=apply('mathematics','corrected');return r.plan.later.length===1&&same(later(r),['math.explain','math.work','math.integrate']);});
check('Semantic knowledge-group overlap changes no practice evidence or policy',()=>{const r=apply('mathematics','corrected'),data=clone(examples.mathematics.data);data.knowledgeGroups.push({...data.knowledgeGroups[0],id:'another-explanation'});return same(M.plan(data,r.state),r.plan);});
check('Clarification maps a criterion to its capability and precedes corrective help',()=>{const r=apply('operations','ambiguous');return same(r.plan.now.map(a=>[a.kind,a.targets]),[['clarify',['ops.produceLogs']]])&&r.event.observations.some(o=>o.target==='ops.produceLogs'&&o.result==='error');});
check('An unclear reply keeps mapped assessment unresolved without reviving help',()=>{const r=apply('operations','unclear',apply('operations','ambiguous').state);return same(r.plan.now.map(a=>[a.kind,a.targets]),[['review',['ops.produceLogs']]]);});
check('A clear later response resolves mapped clarification and pending checks',()=>{const r=apply('operations','later',apply('operations','ambiguous').state);return r.plan.now.length===0&&r.plan.later.length===0;});
check('A successful alternate path leaves bypassed targets unobserved without creating errors',()=>{const r=apply('operations','bypass');return same(r.event.observations.map(o=>o.target),['ops.function'])&&r.plan.now.length===0&&same(later(r),['ops.chooseLogs','ops.produceLogs']);});
check('Current correction ends immediate help while preserving a later check',()=>{const r=apply('operations','corrected',apply('operations','error').state);return !r.plan.now.length&&r.plan.later.length===1&&later(r).length===3;});
check('Simple fact recall works without an integration or relationship requirement',()=>{const first=apply('fact','error'),r=apply('fact','later',first.state);return same(help(first),['fact.recall'])&&!r.plan.now.length&&!r.plan.later.length;});
check('An exact duplicate answer does not multiply evidence',()=>{const r=apply('mathematics','later');return same(apply('mathematics','later',r.state).state,r.state);});
check('A changed interpretation cannot silently replace the same answer ID',()=>{const r=apply('operations','later'),record=clone(examples.operations.records.later);record.assessment.observations[0].reason+=' Changed.';return B.connect(examples.operations.data,r.state,record.input,record).errors.length>0;});
check('Saved assessments stay bound to their original criteria and coverage',()=>{const r=examples.operations.records.later,input=clone(r.input);input.exercise.coverage[0].criteria=['verb'];return B.connect(examples.operations.data,M.empty(),input,r).errors.length>0;});
check('A current contract version change rejects an old assessment',()=>reject(data=>data.targets[0].contract.version++));
check('Contract wording drift is detected even without a version bump',()=>reject(data=>data.targets[0].contract.action='Different required behavior.'));
check('Coverage of an unknown capability is rejected',()=>reject((data,r)=>r.input.exercise.coverage[0].target='unknown'));
check('Missing, repeated, or empty criterion mappings are rejected',()=>[
 (d,r)=>r.input.exercise.coverage[0].criteria=['unknown'],
 (d,r)=>r.input.exercise.coverage[0].criteria=['choice','choice'],
 (d,r)=>r.input.exercise.coverage[0].criteria=[]
 ].every(change=>reject(change)));
check('Duplicate coverage cannot emit two observations for one capability',()=>reject((d,r)=>r.input.exercise.coverage.push(clone(r.input.exercise.coverage[0]))));
check('Help must identify affected rubric criteria in an explicit-coverage packet',()=>reject((d,r)=>r.input.assistance=[{timing:'current',targets:['ops.produceLogs'],text:'Use logs.'}]));
check('An unmapped incidental criterion cannot become a remedial target',()=>reject((d,r)=>{const o=r.assessment.observations.find(o=>o.criterion==='wording');o.status='error';o.quotes=[r.input.response];r.assessment.next={kind:'practice',targets:['wording'],text:'Practice wording.',reason:'Invented rejected mapping.'};}));
check('A new contract cannot reinterpret retained observations during intake',()=>{const prior=apply('operations','later'),{data,records}=clone(examples.operations),r=records.corrected;data.targets[0].contract.version++;r.input.exercise.coverage[0].contract=clone(data.targets[0].contract);return B.connect(data,prior.state,r.input,r).errors.length>0;});
check('Direct planning detects a retained contract mismatch before choosing practice',()=>{const prior=apply('operations','error'),data=clone(examples.operations.data);data.targets[0].contract.version++;const p=M.plan(data,prior.state);return p.now.length===1&&p.now[0].kind==='review'&&!p.later.length;});
check('A new version can start with new evidence without rewriting old history',()=>{const {data,records}=clone(examples.operations),r=records.later;data.targets[0].contract.version++;r.input.exercise.coverage[0].contract=clone(data.targets[0].contract);return !B.connect(data,M.empty(),r.input,r).errors.length;});
check('Branch comparisons leave their initial evidence unchanged',()=>{const r=apply('operations','error'),before=JSON.stringify(r.state);apply('operations','hinted',r.state);apply('operations','later',r.state);return before===JSON.stringify(r.state);});
check('Retained explicit evidence is a snapshot even when the caller later edits its packet',()=>{const {data,records}=clone(examples.operations),r=records.later,out=B.connect(data,M.empty(),r.input,r),before=JSON.stringify(out.state);r.input.exercise.coverage[0].contract.action='Edited after intake.';r.input.response='Edited after intake.';return !out.errors.length&&before===JSON.stringify(out.state);});
check('Version drift also blocks unresolved judgments that emitted no knowledge observation',()=>{const {data,records}=clone(examples.operations),r=records.unclear;r.assessment.next={kind:'clarify',targets:['verb'],text:'Clarify the command.',reason:'The intended command is unknown.'};const first=B.connect(data,M.empty(),r.input,r);if(first.errors.length)throw Error(first.errors.join('; '));data.targets[1].contract.version++;const next=records.later;next.input.exercise.coverage[1].contract=clone(data.targets[1].contract);return first.event.observations.length===0&&B.connect(data,first.state,next.input,next).errors.length>0&&M.plan(data,first.state).now[0].kind==='review';});
check('Evidence references distinguish separate answers within the same attempt',()=>{const {data,records}=clone(examples.operations),a=records.corrected,b=records.later;b.input.attempt.id=a.input.attempt.id;const first=B.connect(data,M.empty(),a.input,a),next=B.connect(data,first.state,b.input,b);if(first.errors.length||next.errors.length)throw Error([...first.errors,...next.errors].join('; '));return first.event.observations[0].evidenceRefs[0].answer===a.input.case_id&&next.event.observations[0].evidenceRefs[0].answer===b.input.case_id;});
const shell=new URL('shell.html',here);
if(existsSync(shell)&&!process.argv.includes('--before')){
 const json=x=>JSON.stringify(x).replace(/</g,'\\u003c');
 const page=read('shell.html').replace('/*MODEL*/',`${source}\nconst B=(${createBridge.toString()}) ((${createTrial.toString()})(),NextSession);\nconst EXAMPLES=${json(examples)};`);
 // The actual page handlers run against a minimal DOM; this does not render a browser.
 class Element{constructor(){this.children=[];this.textContent='';this.attributes={};}append(...xs){this.children.push(...xs);}replaceChildren(...xs){this.children=xs;}setAttribute(k,v){this.attributes[k]=v;}}
 const elements=new Map([...page.matchAll(/\bid="([^"]+)"/g)].map(m=>[m[1],new Element()]));
 check('Page handlers show focused command help then a combined later check',()=>{vm.runInNewContext(page.match(/<script>([\s\S]*?)<\/script>/)[1],{document:{getElementById:id=>elements.get(id),createElement:()=>new Element()}});elements.get('steps').children[0].onclick();const initial=elements.get('decision').children.map(e=>e.textContent).join('\n');elements.get('steps').children[1].onclick();return initial.includes('Focused practice: Write the log command')&&elements.get('decision').children.some(e=>e.textContent.includes('One new troubleshooting incident'));});
 check('Mathematical walkthrough exposes integration while retaining separate evidence',()=>{elements.get('subjects').children[1].onclick();elements.get('steps').children[0].onclick();return elements.get('decision').children.some(e=>e.textContent.includes('Focused practice: Connect depth, branching and total work'));});
 check('Free play shows a partial answer without manufacturing a complete command observation',()=>{elements.get('subjects').children[0].onclick();elements.get('actions').children[2].onclick();return elements.get('evidence').children.some(e=>e.textContent.includes('Write the log command: Not observed'));});
 check('Version-drift walkthrough refuses reuse and reset restores an empty history',()=>{elements.get('version').onclick();const rejected=elements.get('message').textContent.startsWith('Rejected:');elements.get('reset').onclick();return rejected&&elements.get('message').textContent.includes('No answers loaded');});
 writeFileSync(new URL('index.html',here),page);
}
const report={scope:'Authored examples through the existing validator, bridge and planner. No new learner or model-service call.',hashes:{examples:sha(read('examples.mjs')),planner:sha(source),bridge:sha(createBridge.toString()),validator:sha(createTrial.toString())},checks,grading_accuracy:null,learning_benefit:null};
writeFileSync(new URL(process.argv.includes('--before')?'before.json':'report.json',here),JSON.stringify(report,null,2)+'\n');
console.table(checks);console.log(`${checks.filter(c=>c.met).length}/${checks.length} representation checks passed.`);
if(checks.some(c=>!c.met))process.exitCode=1;
