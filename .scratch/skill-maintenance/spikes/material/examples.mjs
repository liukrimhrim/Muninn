import {createSelectionExamples} from '../selection/examples.mjs';
import {createMaterial} from './material.mjs';

// Semantic proposals are authored here. This is not an extractor or an automated fact checker.
export function createMaterialExamples(){
 const A=createMaterial(),old=createSelectionExamples(),clone=x=>JSON.parse(JSON.stringify(x));
 const ns=id=>'material.'+id;
 const source=(id,title,text)=>({id,version:1,title,text,provenance:'Authored example for this spike; not a new learner submission.'});
 const mathSource=source('branching-note','Depth and total work',[
  'Let n = 2^k. Stop at size 1 and do constant local work per call.',
  'After k halvings, n/2^k = 1, so k = log2(n).',
  'Total work counts every call in every continuing branch.',
  'One continuing half-size branch has k+1 calls. Two continuing half-size branches have 2n-1 calls.',
  'Equal logarithmic depth does not imply equal total work.'
 ].join('\n'));
 const factSource=source('vocabulary-note','An invented association','In this invented vocabulary exercise, mavo means blue.');
 const ref=(s,start,end=start)=>({source:s.id,version:s.version,start,end,quote:s.text.split('\n').slice(start-1,end).join('\n')});
 function make(e,s,scopes,ranges){
  const units=e.data.components.map((u,i)=>({...clone(u),id:ns(u.id),scope:scopes[i],refs:[ref(s,...ranges[i])],dependsOn:[],status:'usable',review:{reviewer:'Example author',reason:'Inspected against this short authored source; not an independent validation.'}}));
  const targets=e.data.capabilities.map(t=>({id:ns(t.id),label:t.label,...clone(t.contract),content:t.contract.content.map(r=>({...r,id:ns(r.id)}))}));
  const exercises=e.catalog.filter(a=>a.id!=='fact.recognition').map(a=>({id:ns(a.id),label:a.label,kind:a.kind,seconds:clone(a.seconds),version:1,rubric_version:1,prompt:a.exercise.prompt,criteria:clone(a.exercise.criteria),coverage:a.exercise.coverage.map(c=>({target:ns(c.target),criteria:clone(c.criteria)})),status:'usable',samples:Object.fromEntries(Object.entries(a.outcomes).map(([k,r])=>[k,{response:r.input.response,observations:clone(r.assessment.observations),assistance:clone(r.input.assistance)}]))}));
  for(const e of exercises)for(const c of e.coverage){const t=targets.find(t=>t.id===c.target);c.authoredFor=Object.fromEntries(['version','content','action','mode','conditions'].map(k=>[k,clone(t[k])]));}
  return {source:s,library:A.capture(A.empty(),s),draft:{revision:1,title:s.title,goal:e.data.goal.text,units,targets,selected:e.data.goal.targets.map(ns),groups:e.data.knowledgeGroups.map(g=>({...clone(g),members:g.members.map(ns)})),exercises},budget:180};
 }
 const math=make(old.partial,mathSource,[
  'Start at n=2^k and halve to 1; k is a nonnegative integer. This describes reductions, not all work.',
  'Count constant local work in every call, including terminal calls, across all continuing branches.',
  'Compare one continuing branch with two equal continuing half-size branches, n=2^k, constant local work per call and size-1 termination.'
 ],[[1,2],[1,3],[1,5]]);
 math.draft.units[2].statement='One continuing half-size branch and two continuing half-size branches can have the same depth but different total work.';
 math.draft.units[2].dependsOn=math.draft.units.slice(0,2).map(u=>({id:u.id,version:u.version}));
 const prompts={
  'math.practice':'Worked explanation: count every call, not only the depth. One path has k+1 calls; two continuing branches form a full binary tree with 2n-1 calls. Explain why matching depth does not imply matching work.',
  'math.combined':'Let n=2^k. Stop at size 1 and do constant local work per call. Explain the number of halvings, then compare the total calls with one versus two continuing half-size branches. Justify the difference.',
  'math.explain':'Let n=2^k. Explain how many halvings reduce n to 1, and why the count is logarithmic.',
  'math.work':'A procedure branches into smaller calls. Each call, including a size-1 call, does constant local work. Explain what must be counted to determine total work.',
  'math.integrate':'Two procedures start at n=2^k, stop at size 1 and do constant local work per call. One continues in one half; the other continues in both halves. A colleague says equal depth means equal total work. Evaluate that claim, accounting for every call.'
 };
 for(const e of math.draft.exercises)e.prompt=prompts[e.id.replace('material.','')];
 math.draft.omitted=[{detail:'A separate timed complexity-label drill',reason:'Fluent recall is available as a capability but is not selected for the explanation goal.'}];
 const fact=make(old.fact,factSource,['The supplied invented vocabulary only; recall from mavo to blue.'],[[1]]);
 fact.draft.exercises.find(e=>e.kind==='check').prompt='In the invented vocabulary you studied, what does mavo mean? Answer without a hint.';
 fact.draft.exercises.find(e=>e.kind==='practice').prompt='The supplied association is mavo → blue. Say the meaning, then attempt a separate recall check.';
 fact.budget=25;
 const doubtful=clone(math);
 doubtful.draft.units[2].statement='Every procedure that halves its input has logarithmic total work.';
 doubtful.draft.units[2].status='needs_review';
 doubtful.draft.units[2].concern='This drops the number-of-branches condition and contradicts the supplied comparison. Exact source quotes do not justify it.';
 return {math,fact,doubtful};
}
