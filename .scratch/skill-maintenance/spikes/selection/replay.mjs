import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import vm from 'node:vm';
import {createTrial} from '../assessment-trial/trial.mjs';
import {createBridge} from '../answer-intake/bridge.mjs';
import {createSelector} from './selector.mjs';
import {createSelectionExamples} from './examples.mjs';

const here=new URL('./',import.meta.url),read=p=>readFileSync(new URL(p,here),'utf8'),clone=x=>JSON.parse(JSON.stringify(x));
const source=read('../next-session.html').match(/<script id="next-session-model">([\s\S]*?)<\/script>/)[1];
const M=vm.runInNewContext(source+'\nNextSession'),B=createBridge(createTrial(),M),S=createSelector(M,B),examples=createSelectionExamples();
const checks=[],traces={};
const check=(name,fn)=>{try{fn();checks.push({name,met:true});}catch(e){checks.push({name,met:false,error:e.message});}};
const eq=(a,b)=>assert.deepEqual(clone(a),clone(b));
function init(key,budget){
 const e=clone(examples[key]);let state=M.empty();
 for(const r of e.seeds){const out=B.connect(e.data,state,r.input,r);assert.deepEqual(out.errors,[]);state=out.state;}
 return {...e,state,session:S.start(budget??e.budget,e.phase)};
}
const decide=c=>S.choose(c.data,c.state,c.catalog,c.session);
function perform(c,outcome='correct',seconds){
 const d=decide(c);assert.ok(d.action,'Expected an eligible next action');
 const r=d.action.outcomes[outcome];assert.ok(r,'Expected an authored response for '+outcome);
 const out=S.complete(c.data,c.state,c.catalog,c.session,d.action.id,r,seconds??S.cost(d.action));
 return {...c,...out};
}
const pending=c=>[...new Set(M.plan(c.data,c.state).later.flatMap(a=>a.targets))];
check('Real planner baseline chooses Q1 Q2 Q3 costing seven authored minutes',()=>{
 const c=init('coverage'),old=M.plan(c.data,c.state).later;
 eq(old.map(a=>a.group),['Q1','Q2','Q3']);assert.equal(old.reduce((n,a)=>n+S.cost(c.catalog.find(x=>x.id===a.group)),0),420);
});
check('Selection finds Q3 Q4 at six minutes with full overlapping coverage',()=>{
 const d=decide(init('coverage'));eq(d.planned,['Q3','Q4']);assert.equal(d.plannedSeconds,360);eq([...d.expectedCoverage].sort(),['A','B','C','D','E']);
});
check('Selecting a plan neither spends time nor creates evidence',()=>{
 const c=init('coverage'),before=JSON.stringify(c);decide(c);assert.equal(JSON.stringify(c),before);assert.equal(S.spent(c.session),0);assert.equal(c.state.events[0].observations.length,0);
});
check('Observed Q3 then Q4 completes the session with exactly six minutes charged',()=>{
 let c=perform(init('coverage'));assert.equal(decide(c).action.id,'Q4');c=perform(c);assert.equal(decide(c).kind,'stop');eq(decide(c).unresolved,[]);assert.equal(S.spent(c.session),360);assert.equal(c.state.events.length,3);
});
check('A partial combined answer selects only the unshown connection next',()=>{
 const c=perform(init('partial'),'partial');assert.equal(decide(c).action.id,'math.integrate');eq(decide(c).needs.check,['math.integrate']);assert.equal(decide(c).remaining,40);
});
check('A missing criterion never becomes a complete capability or an observed failure',()=>{
 const c=perform(init('partial'),'partial');assert.ok(!c.event.observations.some(o=>o.target==='math.integrate'));eq(decide(c).needs.practice,[]);
});
check('A later integration error changes selection from broad checking to focused practice',()=>{
 const c=perform(init('partial',140),'error');assert.equal(decide(c).action.id,'math.practice');eq(decide(c).needs.practice,['math.integrate']);
});
check('Only the observed connection error receives corrective practice',()=>{
 const c=init('repair'),d=decide(c);assert.equal(d.action.id,'math.practice');eq(S.coverage(d.action),['math.integrate']);
});
check('Focused practice is followed by a fresh integrated check without claiming delay',()=>{
 let c=perform(init('repair'));assert.equal(decide(c).action.id,'math.combined');c=perform(c);assert.equal(c.event.phase,'current');eq(decide(c).unresolved,[]);assert.equal(pending(c).length,3);assert.equal(S.spent(c.session),100);
});
check('Wrong and correct clarifications lead to different teaching actions',()=>{
 const c=init('clarification');assert.equal(decide(c).action.id,'ops.clarify');
 assert.equal(decide(perform(c,'error')).action.id,'ops.practice');assert.equal(decide(perform(c,'correct')).action.id,'ops.combined');
});
check('An inconclusive clarification preserves review without inventing command failure',()=>{
 const c=perform(init('clarification'),'unclear'),d=decide(c);eq(d.needs.review,['ops.produceLogs']);eq(d.needs.practice,[]);assert.ok(!S.coverage(d.action).includes('ops.produceLogs'));
});
check('A cheaper question whose branches all prescribe the same help is rejected',()=>{
 const d=decide(init('clarification'));assert.ok(d.declined.some(a=>a.id==='ops.same-help'&&a.reason.includes('same teaching')));
});
check('Diagnosis is skipped when a substantive follow-up would not fit',()=>{
 const d=decide(init('tight'));assert.notEqual(d.kind,'diagnose');assert.ok(d.declined.some(a=>a.id==='ops.clarify'&&a.reason.includes('next useful action')));eq(d.needs.diagnose,['ops.produceLogs']);
});
check('Diagnostic reservation includes a fresh check after the repair branch',()=>{
 const c=init('clarification',65),a=c.catalog.find(a=>a.id==='ops.clarify');a.branches[0].targets=['ops.produceLogs'];
 const d=decide(c);assert.notEqual(d.kind,'diagnose');assert.ok(d.declined.some(a=>a.id==='ops.clarify'&&a.reason.includes('post-practice check')));
});
check('Unrelated useful work cannot clear an unaffordable diagnostic concern',()=>{
 const c=perform(init('tight')),d=decide(c);assert.equal(d.kind,'stop');assert.ok(d.unresolved.includes('ops.produceLogs'));assert.equal(d.remaining,5);
});
check('The provisional diagnostic prompt limit is enforced without changing evidence',()=>{
 const c=init('clarification');c.session.diagnosticLimit=0;const d=decide(c);assert.notEqual(d.kind,'diagnose');assert.ok(d.declined.some(a=>a.id==='ops.clarify'&&a.reason.includes('limit')));eq(d.needs.diagnose,['ops.produceLogs']);
});
check('Cheap recognition cannot substitute for an unaided recall contract',()=>{
 const d=decide(init('fact'));assert.equal(d.action.id,'fact.recall');assert.ok(d.declined.some(a=>a.id==='fact.recognition'&&a.reason.includes('required action')));
});
check('One fact needs one recall prompt without a multi-part procedure',()=>{
 const c=perform(init('fact'));assert.equal(c.session.completed.length,1);eq(decide(c).unresolved,[]);
});
check('Repeating a completed answer charges no extra time and adds no evidence',()=>{
 const a=init('clarification'),d=decide(a),c=perform(a,'error'),count=c.state.events.length;
 const out=S.complete(c.data,c.state,c.catalog,c.session,d.action.id,d.action.outcomes.error,S.cost(d.action));
 assert.equal(out.state.events.length,count);assert.equal(S.spent(out.session),20);
});
check('Replaying an earlier answer after practice preserves its original phase',()=>{
 const a=init('clarification'),d=decide(a),c=perform(perform(a,'error'));
 const out=S.complete(c.data,c.state,c.catalog,c.session,d.action.id,d.action.outcomes.error,S.cost(d.action));
 assert.equal(out.event.phase,'later');assert.equal(S.spent(out.session),45);
});
check('A conflicting duration on duplicate delivery is refused',()=>{
 const a=init('fact'),d=decide(a),c=perform(a);
 assert.throws(()=>S.complete(c.data,c.state,c.catalog,c.session,d.action.id,d.action.outcomes.correct,11),/different cost/);
});
check('Actual time overruns are retained and prevent another task',()=>{
 const c=perform(init('fact'),'correct',13);assert.equal(S.spent(c.session),13);assert.equal(decide(c).remaining,0);assert.equal(decide(c).kind,'stop');
});
check('Setup and feedback count even when answering alone would fit',()=>{
 const c=init('fact');c.catalog.find(a=>a.id==='fact.recall').seconds={setup:5,answer:6,feedback:5};assert.equal(decide(c).kind,'stop');assert.ok(decide(c).unresolved.includes('fact.recall'));
});
check('A hint keeps targets pending after a successful larger answer',()=>{
 const c=perform(init('partial',180),'hinted');assert.equal(c.session.checked.length,0);assert.equal(decide(c).needs.check.length,3);
});
check('An answer to a different task cannot be charged as the chosen cheap task',()=>{
 const c=init('partial'),cheap=c.catalog.find(a=>a.id==='math.explain');
 assert.throws(()=>S.complete(c.data,c.state,c.catalog,c.session,cheap.id,c.catalog[1].outcomes.correct,35),/selected task/);
});
check('Retained capability-version drift stops selection for explicit review',()=>{
 const c=init('fact');c.data.targets[0].contract.version++;assert.equal(decide(c).kind,'stop');assert.ok(decide(c).reason.includes('changed capability'));
});
check('Reordered contract properties remain compatible with the real bridge',()=>{
 const c=init('fact'),a=c.catalog.find(a=>a.id==='fact.recall');
 a.exercise.coverage[0].contract=Object.fromEntries(Object.entries(a.exercise.coverage[0].contract).reverse());
 assert.equal(decide(c).action.id,'fact.recall');const next=perform(c);eq(decide(next).unresolved,[]);
});
check('A failed whole task retains its unresolved concern even after target checks were complete',()=>{
 const c=perform(init('fact'));c.state=M.append(c.state,M.hypothetical('outcome_only'));
 const d=decide(c);assert.equal(d.kind,'stop');assert.ok(d.needs.taskConcern);assert.ok(d.reason.includes('unresolved concern'));assert.ok(!d.reason.includes('checks for this illustrative session are complete'));
});
check('An unlocalized failed task is not bypassed with ordinary target practice',()=>{
 const c=init('fact');c.state=M.append(c.state,M.hypothetical('outcome_only'));
 const d=decide(c);assert.equal(d.kind,'stop');assert.ok(d.needs.taskConcern);
});
check('An insufficient budget retains all unobserved targets instead of grading them weak',()=>{
 const c=init('coverage',1),d=decide(c);assert.equal(d.kind,'stop');eq(d.needs.practice,[]);assert.equal(d.unresolved.length,5);
});
check('The same prompt is not repeated after missing evidence',()=>{
 const c=perform(init('partial',200),'partial'),d=decide(c);assert.notEqual(d.action.id,'math.combined');assert.ok(d.declined.some(a=>a.id==='math.combined'&&a.reason.includes('already attempted')));
});
for(const [key,e] of Object.entries(examples)){
 let c=init(key);const trace=[];
 for(const outcome of e.walk){const d=decide(c);if(!d.action)break;trace.push({action:d.action.id,kind:d.kind,reason:d.reason,remaining:d.remaining,assumedSeconds:S.cost(d.action),outcome});c=perform(c,outcome);}
 traces[key]={description:e.description,trace,spentSeconds:S.spent(c.session),final:decide(c),retainedLaterTargets:pending(c)};
}
const files=['selector.mjs','examples.mjs','replay.mjs','shell.html','../representation/examples.mjs','../answer-intake/bridge.mjs','../assessment-trial/trial.mjs','../next-session.html'];
const hashes=Object.fromEntries(files.map(p=>[p,createHash('sha256').update(read(p)).digest('hex')]));
const report={scope:'Authored selection/coverage experiment through the existing assessment bridge and planner. Costs are illustrative; no measured learning benefit, retention, calibrated inference or live review omissions.',hashes,baseline:{source:'Original conversation lines 1274–1279; assistant-authored example',firstFit:['Q1','Q2','Q3'],seconds:420,alternative:['Q3','Q4'],alternativeSeconds:360},checks,traces};
if(checks.some(c=>!c.met))process.exitCode=1;
else if(existsSync(new URL('shell.html',here))){
 const json=x=>JSON.stringify(x).replace(/</g,'\\u003c');
 const model=`${source}\nconst B=(${createBridge.toString()}) ((${createTrial.toString()})(),NextSession);\nconst S=(${createSelector.toString()})(NextSession,B);\nconst EXAMPLES=${json(examples)};`;
 const page=read('shell.html').replace('/*MODEL*/',model);
 const script=page.match(/<script>([\s\S]*?)<\/script>/)[1];
 // Execute the actual handlers against a minimal DOM surface; this does not render a browser.
 class Element{constructor(){this.children=[];this.textContent='';this.attributes={};}append(...xs){this.children.push(...xs);}replaceChildren(...xs){this.children=xs;}setAttribute(k,v){this.attributes[k]=v;}}
 const elements=new Map([...page.matchAll(/\bid="([^"]+)"/g)].map(m=>[m[1],new Element()]));
 vm.runInNewContext(script,{document:{getElementById:id=>elements.get(id),createElement:()=>new Element()}});
 const uiChecks=[],ui=(name,fn)=>{fn();uiChecks.push(name);};
 ui('Initial page states the chosen exercise and walkthrough completes the six-minute example',()=>{
  assert.ok(elements.get('next').textContent.includes('Q3'));elements.get('play').onclick();assert.ok(elements.get('next').textContent.includes('Stop'));assert.ok(elements.get('spent').textContent.includes('6m 0s'));
 });
 ui('Partial-answer button changes the real next choice to the missing connection',()=>{
  elements.get('scenarios').children[4].onclick();elements.get('answers').children[1].onclick();assert.ok(elements.get('next').textContent.includes('Connect equal depth'));
 });
 ui('Replay and budget controls preserve evidence while recomputing selection',()=>{
  const used=elements.get('spent').textContent;elements.get('replay').onclick();assert.equal(elements.get('spent').textContent,used);
  elements.get('budgets').children[0].onclick();assert.ok(elements.get('next').textContent.includes('Stop'));assert.ok(elements.get('unresolved').textContent.includes('Connect depth'));
  elements.get('reset').onclick();assert.ok(elements.get('spent').textContent.includes('0s'));
 });
 report.uiChecks=uiChecks;
 writeFileSync(new URL('index.html',here),page);
}
writeFileSync(new URL('report.json',here),JSON.stringify(report,null,2)+'\n');
console.table(checks.filter(c=>!c.met));console.log(`${checks.filter(c=>c.met).length}/${checks.length} selection replay checks passed; ${report.uiChecks?.length||0} handler checks passed. Browser rendering is not verified.`);
