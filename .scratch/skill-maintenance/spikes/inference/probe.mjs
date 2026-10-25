// Throwaway assumption probe. Synthetic responses, fixed parameters, no learning/forgetting.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import vm from 'node:vm';
import {createTrial} from '../assessment-trial/trial.mjs';
import {createBridge} from '../answer-intake/bridge.mjs';
import {createExamples} from '../representation/examples.mjs';

const here=new URL('./',import.meta.url),read=p=>readFileSync(new URL(p,here),'utf8');
const targets=['A','B','C'];
const chain=[[],['A'],['A','B'],['A','B','C']];
const unrestricted=Array.from({length:8},(_,mask)=>targets.filter((_,i)=>mask&(1<<i)));
const uniform=states=>states.map(()=>1/states.length);
const independent=(marginals)=>unrestricted.map(s=>targets.reduce((p,t)=>p*(s.includes(t)?marginals[t]:1-marginals[t]),1));
const marginal=(states,p)=>Object.fromEntries(targets.map(t=>[t,states.reduce((sum,s,i)=>sum+(s.includes(t)?p[i]:0),0)]));
const near=(a,b)=>assert.ok(Math.abs(a-b)<1e-12,`${a} != ${b}`);
const response=(id,target,outcome,extra={})=>({id,revision:1,episode:id,family:'synthetic-distinct-prompts',target,outcome,assisted:false,...extra});
const cPass=response('c-pass','C','correct'),aFail=response('a-fail','A','incorrect');

// Explicit assessment revisions replace an effective judgment; they are not new responses.
function effective(history){
 const latest=new Map();
 for(const r of history){
  const old=latest.get(r.id);
  if(old){
   assert.equal(r.episode,old.episode);
   assert.equal(r.target,old.target);
   assert.equal(r.family,old.family);
   if(r.revision<old.revision)continue;
   if(r.revision===old.revision){assert.deepEqual(r,old,'Conflicting judgment needs an explicit revision');continue;}
  }
  latest.set(r.id,r);
 }
 const all=[...latest.values()];
 const included=all.filter(r=>!r.assisted&&['correct','incorrect'].includes(r.outcome));
 const episodes=new Set();
 for(const r of included){
  assert.ok(!episodes.has(r.episode),'Multiple judgments from one episode require a joint likelihood');
  episodes.add(r.episode);
 }
 return {included,excluded:all.filter(r=>!included.includes(r))};
}

function infer(states,prior,history,{slip=.1,guess=.1}={}){
 const observations=effective(history);
 let p=[...prior],sequenceLikelihood=1;
 for(const r of observations.included){
  const weights=states.map((s,i)=>{
   const correct=s.includes(r.target)?1-slip:guess;
   return p[i]*(r.outcome==='correct'?correct:1-correct);
  });
  const total=weights.reduce((a,b)=>a+b,0);
  sequenceLikelihood*=total;
  if(total===0)return {status:'incompatible',sequenceLikelihood,posterior:null,marginals:null,...observations};
  p=weights.map(w=>w/total);
 }
 return {status:'ok',sequenceLikelihood,posterior:p,marginals:marginal(states,p),...observations};
}

const models=[
 {name:'strict-chain-uniform',states:chain,prior:uniform(chain)},
 {name:'independent-matched-marginals',states:unrestricted,prior:independent({A:.75,B:.5,C:.25})},
 {name:'independent-uniform',states:unrestricted,prior:uniform(unrestricted)}
];
const conditions=[['prior',[]],['C correct',[cPass]],['C correct then A incorrect',[cPass,aFail]]];
const scenarios=models.flatMap(m=>conditions.map(([condition,history])=>({model:m.name,condition,states:m.states,prior:m.prior,parameters:{slip:.1,guess:.1},...infer(m.states,m.prior,history)})));
const checks=[];
function check(name,fn){fn();checks.push(name);}
const result=(model,condition)=>scenarios.find(s=>s.model===model&&s.condition===condition);
const strict=result('strict-chain-uniform','C correct');
const matched=result('independent-matched-marginals','C correct');
check('Independent control matches all three initial marginals',()=>{
 const a=result(models[0].name,'prior'),b=result(models[1].name,'prior');
 for(const t of targets)near(a.marginals[t],b.marginals[t]);
});
check('Chain update agrees with hand-calculated state weights 1:1:1:9',()=>{
 [1/12,1/12,1/12,9/12].forEach((p,i)=>near(strict.posterior[i],p));
 near(strict.marginals.A,11/12);near(strict.sequenceLikelihood,.3);
});
check('Independent C success leaves untested A and B at their priors',()=>{
 near(matched.marginals.A,.75);near(matched.marginals.B,.5);near(matched.marginals.C,.75);
});
check('Contradiction agrees with hand-calculated state weights 9:1:1:9',()=>{
 const r=result(models[0].name,conditions[2][0]);
 [9/20,1/20,1/20,9/20].forEach((p,i)=>near(r.posterior[i],p));
 near(r.marginals.A,.55);near(r.marginals.C,.45);near(r.sequenceLikelihood,.05);
});
check('Independent model preserves C success while revising A after its failure',()=>{
 const r=result(models[1].name,conditions[2][0]);
 near(r.marginals.A,.25);near(r.marginals.C,.75);near(r.sequenceLikelihood,.09);
});
const zeroNoise=models.slice(0,2).map(m=>({model:m.name,...infer(m.states,m.prior,[cPass,aFail],{slip:0,guess:0})}));
check('Zero-noise contradiction reports incompatible chain instead of normalizing zero',()=>{
 assert.equal(zeroNoise[0].status,'incompatible');assert.equal(zeroNoise[0].posterior,null);
 near(zeroNoise[1].marginals.A,0);near(zeroNoise[1].marginals.C,1);
});
const once=infer(chain,uniform(chain),[cPass]);
const duplicate=infer(chain,uniform(chain),[cPass,cPass]);
// Deliberately false provenance illustrates the effect of counting a copy as a fresh answer.
const counterfeit=infer(chain,uniform(chain),[cPass,response('counterfeit','C','correct')]);
check('Exact replay is one effective observation; counterfeit independence inflates certainty',()=>{
 assert.deepEqual(once,duplicate);near(counterfeit.marginals.C,27/28);assert.equal(duplicate.included.length,1);
});
check('A revised grade replaces the original effective likelihood and keeps source history external',()=>{
 const revised={...cPass,revision:2,outcome:'incorrect'};
 assert.deepEqual(infer(chain,uniform(chain),[cPass,revised]),infer(chain,uniform(chain),[revised]));
 assert.equal(cPass.outcome,'correct');
});
check('Conflicting same-revision assessments are refused',()=>{
 assert.throws(()=>effective([cPass,{...cPass,outcome:'incorrect'}]),/explicit revision/);
});
check('Distinct criteria in one episode are not silently multiplied',()=>{
 assert.throws(()=>effective([cPass,response('b-part','B','correct',{episode:cPass.episode})]),/joint likelihood/);
});
const withheld=['not_shown','cannot_judge'].map((outcome,i)=>response(`withheld-${i}`,'A',outcome));
withheld.push(response('hinted','B','correct',{assisted:true}));
check('Omitted, ambiguous and assisted judgments remain visible without unassisted numeric updates',()=>{
 const r=infer(chain,uniform(chain),withheld);assert.deepEqual(r.posterior,uniform(chain));assert.equal(r.excluded.length,3);
 const revised={...cPass,revision:2,outcome:'cannot_judge'};
 assert.deepEqual(infer(chain,uniform(chain),[cPass,revised]).posterior,uniform(chain));
});
check('Every compatible scenario has normalized nonnegative mass and retains supplied observations',()=>{
 for(const r of scenarios){near(r.posterior.reduce((a,b)=>a+b,0),1);assert.ok(r.posterior.every(p=>p>=0));}
});
const sensitivity=[
 ['uniform',uniform(chain)],['empty-heavy',[.7,.1,.1,.1]],['full-heavy',[.1,.1,.1,.7]]
].flatMap(([priorName,prior])=>[.01,.1,.3].map(noise=>({priorName,prior,slip:noise,guess:noise,...infer(chain,prior,[cPass,aFail],{slip:noise,guess:noise})})));
const asymmetricNoise=[{slip:.01,guess:.3},{slip:.3,guess:.01}].map(parameters=>({prior:uniform(chain),...parameters,...infer(chain,uniform(chain),[cPass,aFail],parameters)}));
check('Asymmetric error assumptions change which contradictory answer is attributed to noise',()=>{
 near(asymmetricNoise[0].marginals.C,99/2259);near(asymmetricNoise[1].marginals.C,2100/2259);
});

// Inspect the actual representation seam; do not turn its capabilities into these fictional states.
const source=read('../next-session.html').match(/<script id="next-session-model">([\s\S]*?)<\/script>/)[1];
const M=vm.runInNewContext(source+'\nNextSession'),B=createBridge(createTrial(),M);
const example=createExamples().mathematics,r=example.records.later;
const connected=B.connect(example.data,M.empty(),r.input,r);
assert.deepEqual(connected.errors,[]);
const refs=connected.event.observations.flatMap(o=>o.evidenceRefs);
const unique=[...new Map(refs.map(ref=>[JSON.stringify(ref),ref])).values()];
const coverage={answer:r.input.case_id,projectedCapabilities:connected.event.observations.length,referenceOccurrences:refs.length,uniqueCriterionReferences:unique.length,distinctAnswers:new Set(unique.map(r=>r.answer)).size,references:unique};
check('Real math bridge yields five references to four criteria from one answer',()=>{
 assert.equal(coverage.projectedCapabilities,3);assert.equal(coverage.referenceOccurrences,5);
 assert.equal(coverage.uniqueCriterionReferences,4);assert.equal(coverage.distinctAnswers,1);
 assert.equal(refs.filter(r=>r.criterion==='work').length,2);
});
const paths=['probe.mjs','../representation/examples.mjs','../answer-intake/bridge.mjs','../assessment-trial/trial.mjs','../next-session.html'];
const hashes=Object.fromEntries(paths.map(p=>[p,createHash('sha256').update(read(p)).digest('hex')]));
const report={scope:'Synthetic fixed-state sensitivity probe; actual bridge inspected only for shared evidence identity. No learner model calibration, practice effect, timing, review omissions or FSRS updates.',hashes,checks,scenarios,zeroNoise,duplicates:{once,duplicate,counterfeit},sensitivity,asymmetricNoise,coverage};
writeFileSync(new URL('results.json',here),JSON.stringify(report,null,2)+'\n');
console.table(scenarios.map(r=>({model:r.model,condition:r.condition,...r.marginals,sequenceLikelihood:r.sequenceLikelihood})));
console.log(`${checks.length} checks passed. Wrote spikes/inference/results.json.`);
