import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import vm from 'node:vm';
import {createMaterial} from './material.mjs';
import {createMaterialExamples} from './examples.mjs';
import {createTrial} from '../assessment-trial/trial.mjs';
import {createBridge} from '../answer-intake/bridge.mjs';
import {createSelector} from '../selection/selector.mjs';

const here=new URL('./',import.meta.url),read=p=>readFileSync(new URL(p,here),'utf8'),clone=x=>JSON.parse(JSON.stringify(x));
const source=read('../next-session.html').match(/<script id="next-session-model">([\s\S]*?)<\/script>/)[1];
const M=vm.runInNewContext(source+'\nNextSession'),B=createBridge(createTrial(),M),S=createSelector(M,B),A=createMaterial(),examples=createMaterialExamples();
const checks=[],traces={};
const check=(name,fn)=>{try{fn();checks.push({name,met:true});}catch(e){checks.push({name,met:false,error:e.message});}};
const eq=(a,b)=>assert.deepEqual(clone(a),clone(b));
const pack=e=>A.prepare(e.library,e.draft);
function run(e,outcomes){
 const p=pack(e);let state=M.empty(),session=S.start(e.budget,'current');const trace=[];
 for(const outcome of outcomes){
  const d=S.choose(p.data,state,p.catalog,session);assert.ok(d.action);
  const r=A.bind(d.action,outcome,'material-attempt-'+trace.length),out=S.complete(p.data,state,p.catalog,session,d.action.id,r,S.cost(d.action));
  trace.push({action:d.action.id,kind:d.kind,prompt:d.action.exercise.prompt,outcome,observations:out.event.observations.map(o=>({target:o.target,result:o.result,assisted:o.assisted})),next:out.decision.action?.id||'stop'});
  state=out.state;session=out.session;
 }
 return {pack:p,state,session,trace,next:S.choose(p.data,state,p.catalog,session)};
}
check('Source capture preserves literal text and identical captures are idempotent',()=>{
 const e=examples.math;eq(A.capture(e.library,e.source),e.library);assert.equal(e.library.sources[0].text,e.source.text);
});
check('A source cannot be silently replaced under the same version',()=>{
 const e=examples.math;assert.throws(()=>A.capture(e.library,{...e.source,text:'Changed'}),/new version/);
 const newer=A.capture(e.library,{...e.source,version:2,text:'New source version'});assert.equal(newer.sources.length,2);assert.equal(newer.sources[0].text,e.source.text);
});
check('Incorrect quotes and unavailable source versions hold affected targets',()=>{
 const e=clone(examples.math);e.draft.units[0].refs[0].quote='Made up';let p=pack(e);eq(p.held.map(h=>h.target),['material.math.explain','material.math.integrate']);
 e.draft.units[0].refs[0].version=99;p=pack(e);assert.ok(p.held[0].reasons.some(r=>r.includes('unavailable')));
});
check('Exact source quotes do not resolve a known unsupported claim',()=>{
 const e=examples.doubtful;eq(A.referenceErrors(e.library,e.draft.units[2].refs),[]);const p=pack(e);
 eq(p.held.map(h=>h.target),['material.math.integrate']);assert.ok(!p.catalog.some(a=>a.id==='material.math.combined'));
});
check('The goal selects explanation targets without inventing a timed recall requirement',()=>{
 const p=pack(examples.math);assert.equal(p.data.targets.length,3);assert.ok(!p.data.targets.some(t=>t.id==='material.math.fluent'));
 eq(p.held,[]);eq(p.noExercise,[]);
});
check('The connected target includes actual versioned supporting claims without creating learner credit',()=>{
 const p=pack(examples.math),t=p.data.targets.find(t=>t.id==='material.math.integrate');
 assert.equal(t.contract.content.length,3);assert.equal(M.empty().events.length,0);assert.equal(p.data.knowledgeGroups[1].members.length,3);
});
check('Missing and conflicting content definitions cannot become a usable contract',()=>{
 const e=clone(examples.math);e.draft.units[2].dependsOn.push({id:'missing',version:1});assert.equal(pack(e).held.length,1);
 const c=clone(examples.math);c.library.units=[{...clone(c.draft.units[0]),statement:'Conflicting identity'}];assert.equal(pack(c).held.length,2);
});
check('An explicit dependency cycle terminates without multiplying references',()=>{
 const e=clone(examples.math);e.draft.units[0].dependsOn=[{id:e.draft.units[2].id,version:1}];
 const p=pack(e);eq(p.held,[]);assert.equal(p.data.targets[0].contract.content.length,3);
});
check('Coverage with an unknown criterion is held instead of reaching the assessment bridge',()=>{
 const e=clone(examples.math);e.draft.exercises.find(a=>a.kind==='check').coverage[0].criteria=['unknown'];
 const p=pack(e);assert.equal(p.heldExercises.length,1);assert.ok(!p.catalog.some(a=>a.id==='material.math.combined'));
});
check('Changing the target cannot stamp an old recall prompt as a newly reviewed recognition task',()=>{
 const e=clone(examples.fact);e.draft.targets[0].mode='recognition';const p=pack(e);
 assert.equal(p.catalog.length,0);assert.equal(p.heldExercises.length,2);assert.ok(p.heldExercises[0].reasons.some(r=>r.includes('mapping was reviewed')));
});
check('Invalid versions or missing total-cost fields cannot produce runnable exercises',()=>{
 const e=clone(examples.fact);e.draft.exercises[1].rubric_version=0;assert.equal(pack(e).heldExercises.length,1);
 e.draft.exercises[0].seconds={answer:1};assert.equal(pack(e).heldExercises.length,2);
 e.draft.targets[0].version=0;assert.equal(pack(e).held.length,1);
});
check('A ready content target with no exercise remains visibly unserved',()=>{
 const e=clone(examples.fact);e.draft.exercises=[];const p=pack(e);eq(p.noExercise,['material.fact.recall']);
 const d=S.choose(p.data,M.empty(),p.catalog,S.start(30));eq(d.unresolved,['material.fact.recall']);assert.equal(d.kind,'stop');
});
check('The new material contract runs a larger task then repairs only its observed connection error',()=>{
 const r=run(examples.math,['error','correct','correct']);
 eq(r.trace.map(t=>t.action),['material.math.combined','material.math.practice','material.math.integrate']);
 eq(r.trace[0].observations.filter(o=>o.result==='error').map(o=>o.target),['material.math.integrate']);
 assert.equal(r.trace[1].observations[0].assisted,true);eq(r.next.unresolved,[]);assert.equal(S.spent(r.session),140);
 assert.ok(r.state.events.every(e=>e.phase==='current'));traces.math=r.trace;
});
check('An omitted connection asks for evidence without treating omission as a knowledge failure',()=>{
 const r=run(examples.math,['partial']);assert.equal(r.next.kind,'check');assert.equal(r.next.action.id,'material.math.integrate');
 eq(r.next.needs.practice,[]);assert.ok(!r.state.events[0].observations.some(o=>o.target==='material.math.integrate'));
});
check('The same pipeline accepts a simple fact with one target and one recall',()=>{
 const r=run(examples.fact,['correct']);assert.equal(r.pack.data.targets.length,1);eq(r.next.unresolved,[]);assert.equal(S.spent(r.session),10);traces.fact=r.trace;
});
check('Draft reuse retains both sources, refuses a scope conflict and creates no observation',()=>{
 const e=clone(examples.math),u=e.draft.units[0],s={...clone(e.source),id:'earlier-note',title:'Earlier source'};
 e.library=A.capture(e.library,s);e.library.units=[{...clone(u),id:'shared.halving',refs:u.refs.map(r=>({...r,source:s.id}))}];
  const d=A.reuse(e.library,e.draft,u.id,{id:'shared.halving',version:1},'Exact scoped claim inspected by the example author.');
  let inspected=d;for(const id of d.lastChange.units)inspected=A.reviewed(inspected,'unit',id,'Example author','Inspected the replacement dependency.');
  for(const id of d.lastChange.exercises)inspected=A.reviewed(inspected,'exercise',id,'Example author','The replacement preserves this exercise purpose.');
  const p=A.prepare(e.library,inspected);eq(p.held,[]);eq(p.heldExercises,[]);assert.equal(d.units.length,2);assert.equal(d.sourceLinks[0].refs[0].source,e.source.id);
 assert.equal(p.data.targets[0].contract.content[0].id,'shared.halving');assert.equal(M.empty().events.length,0);
 e.library.units[0].scope='All algorithms';assert.throws(()=>A.reuse(e.library,e.draft,u.id,{id:'shared.halving',version:1},'Same wording'),/scope/);
});
check('Reuse versions derived claims instead of mutating the old content identity',()=>{
 const e=clone(examples.math),u=e.draft.units[0];e.library.units=[...clone(e.draft.units),{...clone(u),id:'shared.halving'}];
 const before=JSON.stringify(e.library),d=A.reuse(e.library,e.draft,u.id,{id:'shared.halving',version:1},'Explicit exact mapping');
 assert.equal(d.units.find(u=>u.id==='material.math.composition').version,2);
 assert.equal(d.targets.find(t=>t.id==='material.math.integrate').version,2);
 const p=A.prepare(e.library,d);assert.ok(!p.held.flatMap(h=>h.reasons).some(r=>r.includes('conflicting definitions')));
 assert.ok(p.heldExercises.some(h=>h.exercise==='material.math.combined'));assert.equal(JSON.stringify(e.library),before);
});
check('Reusing an existing claim cannot erase a flagged source contradiction',()=>{
 const e=clone(examples.fact),u=e.draft.units[0];e.library.units=[{...clone(u),id:'shared.association'}];
 u.status='needs_review';u.concern='The new source contradicts the existing meaning.';
 assert.throws(()=>A.reuse(e.library,e.draft,u.id,{id:'shared.association',version:1},'Matching words'),/flagged/);assert.equal(pack(e).held.length,1);
});
const changed=A.revise(examples.math.draft,'material.math.halving',{scope:'n = 2^k, integer k >= 0. Count halving operations separately from calls; zero halvings still contains one size-1 call.'});
check('Editing a supporting claim holds its transitive dependents and exercises while preserving independent content',()=>{
 const p=A.prepare(examples.math.library,changed);eq(changed.lastChange.units,['material.math.halving','material.math.composition']);
 eq(p.held.map(h=>h.target),['material.math.explain','material.math.integrate']);eq(p.catalog.map(a=>a.id),['material.math.work']);
 assert.equal(changed.targets.find(t=>t.id==='material.math.integrate').version,2);assert.equal(changed.units[2].dependsOn[0].version,2);
});
let reviewed=changed;
for(const id of changed.lastChange.units)reviewed=A.reviewed(reviewed,'unit',id,'Example author','The zero-reduction case and dependency still support this claim.');
for(const id of changed.lastChange.exercises)reviewed=A.reviewed(reviewed,'exercise',id,'Example author','Prompt and required call counts still fit the clarified scope.');
check('Explicit author review makes revised exercises available without rewriting old evidence',()=>{
 const before=JSON.stringify(examples.math),old=run(examples.math,['correct']),history=JSON.stringify(old.state),p=A.prepare(examples.math.library,reviewed);
 eq(p.held,[]);eq(p.heldExercises,[]);assert.equal(p.catalog.find(a=>a.id==='material.math.combined').exercise.rubric_version,2);
 const d=S.choose(p.data,old.state,p.catalog,S.start(180));assert.equal(d.kind,'stop');assert.match(d.reason,/changed capability/);
 const action=p.catalog.find(a=>a.id==='material.math.combined'),r=A.bind(action,'correct','new-version-answer');
 assert.ok(B.connect(p.data,old.state,r.input,r).errors.some(e=>e.includes('different capability contract')));
 assert.equal(JSON.stringify(old.state),history);assert.equal(JSON.stringify(examples.math),before);
});
const files=['material.mjs','examples.mjs','replay.mjs','shell.html','../selection/selector.mjs','../selection/examples.mjs','../representation/examples.mjs','../answer-intake/bridge.mjs','../assessment-trial/trial.mjs','../next-session.html'];
const hashes=Object.fromEntries(files.filter(p=>existsSync(new URL(p,here))).map(p=>[p,createHash('sha256').update(read(p)).digest('hex')]));
const report={scope:'Authored source and semantic proposals compiled into the real assessment bridge and selector. No arbitrary extraction, semantic validation, learner outcome or history migration is established.',hashes,checks,traces};
if(checks.some(c=>!c.met))process.exitCode=1;
else if(existsSync(new URL('shell.html',here))){
 const json=x=>JSON.stringify(x).replace(/</g,'\\u003c');
 const model=`${source}\nconst B=(${createBridge.toString()})((${createTrial.toString()})(),NextSession);\nconst S=(${createSelector.toString()})(NextSession,B);\nconst A=(${createMaterial.toString()})();\nconst EXAMPLES=${json(examples)};`;
 const page=read('shell.html').replace('/*MODEL*/',model),script=page.match(/<script>([\s\S]*?)<\/script>/)[1];
 class Element{constructor(){this.children=[];this.textContent='';this.attributes={};}append(...xs){this.children.push(...xs);}replaceChildren(...xs){this.children=xs;}setAttribute(k,v){this.attributes[k]=v;}}
 const elements=new Map([...page.matchAll(/\bid="([^"]+)"/g)].map(m=>[m[1],new Element()]));
 vm.runInNewContext(script,{document:{getElementById:id=>elements.get(id),createElement:()=>new Element()}});
 assert.ok(elements.get('exercise').textContent.includes('Let n=2^k'));
 elements.get('walk').onclick();assert.ok(elements.get('trace').textContent.includes('material.math.practice'));
 elements.get('scenarios').children[2].onclick();assert.ok(elements.get('held').textContent.includes('contradicts'));
 elements.get('scenarios').children[1].onclick();elements.get('walk').onclick();assert.ok(elements.get('trace').textContent.includes('material.fact.recall'));
 report.uiChecks=['Initial compiled task appears','Math walkthrough uses real corrective selection','Unsupported proposal remains visibly held','Single fact uses the same real path'];
 writeFileSync(new URL('index.html',here),page);
}
writeFileSync(new URL('report.json',here),JSON.stringify(report,null,2)+'\n');
console.table(checks.filter(c=>!c.met));console.log(`${checks.filter(c=>c.met).length}/${checks.length} material replay checks passed; ${report.uiChecks?.length||0} handler checks. Browser rendering not verified.`);
