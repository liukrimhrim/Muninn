// Authored contrasts, not additional learner answers or independent grading data.
export function createExamples() {
 const clone=x=>JSON.parse(JSON.stringify(x));
 const capability=(id,label,content,action,mode='explanation')=>({id,label,contract:{version:1,content:[{id:content,version:1}],action,mode,conditions:'Use the supplied situation without an answer hint. Earlier teaching remains in context.'}});
 function dataset(title,components,capabilities,selected,knowledgeGroups,bundles){
  return {title,components,capabilities,goal:{text:title,targets:selected},targets:capabilities.filter(c=>selected.includes(c.id)),knowledgeGroups,practiceBundles:bundles};
 }
 function exercise(data,id,prompt,criteria,coverage){
  return {id,version:1,rubric_version:1,subject:data.title,prompt,criteria:Object.entries(criteria).map(([id,rule])=>({id,rule})),
   coverage:Object.entries(coverage).map(([target,criteria])=>({target,contract:clone(data.targets.find(c=>c.id===target).contract),criteria}))};
 }
 function record(id,task,response,statuses,options={}){
  const observations=task.criteria.map(c=>({criterion:c.id,status:statuses[c.id]||'not_shown',quotes:statuses[c.id]&&statuses[c.id]!=='not_shown'?[response]:[],reason:'Authored criterion judgment for this behavior experiment; not a measured grading result.'}));
  const next=options.next||{kind:'stop',targets:[],text:'No additional diagnostic question proposed.',reason:'The planner uses only the supported observations.'};
  return {input:{case_id:id,attempt:{id,origin:'hypothetical',phase:options.phase||'current'},exercise:clone(task),response,
    context:[{id:'provenance',role:'task',text:'Invented example for inspecting the representation; no new learner response or measured delay.'}],assistance:options.assistance||[]},
   assessment:{case_id:id,observations,next,alternatives:[]},assessor:'Authored in this chat for the representation spike',protocol:{name:'Explicit capability coverage, version 1'}};
 }
 const ops=dataset('Choose useful evidence and produce commands',[
  {id:'ops.evidence',version:1,statement:'Application logs can supply evidence about a reported application failure.'},
  {id:'ops.command',version:1,statement:'The example log command identifies the namespace and Pod after the logs subcommand.'},
  {id:'ops.function',version:1,statement:'Process state and evidence of intended application work are different observations.'}
 ],[
  capability('ops.chooseLogs','Choose relevant log evidence','ops.evidence','Select logs and explain their relevance.','selection'),
  capability('ops.produceLogs','Write the log command','ops.command','Produce the command with the correct subcommand and supplied target.','recall'),
  capability('ops.function','Verify the intended work','ops.function','Name evidence of the requested application behavior.')
 ],['ops.chooseLogs','ops.produceLogs','ops.function'],[
  {id:'ops.explanation',members:['ops.evidence','ops.command','ops.function'],structure:'Choose evidence, obtain it, then judge whether it establishes the intended behavior.'}
 ],[{id:'ops.incident',title:'One new troubleshooting incident',exercise:'ops.exercise@1',targets:['ops.chooseLogs','ops.produceLogs','ops.function']}]);
 const opsTask=exercise(ops,'ops.exercise','A worker in namespace shop stopped processing reports. Choose evidence, write a command for Pod worker-7, and say what would show recovery.',{
  choice:'Select logs to investigate the application failure.',verb:'Use the logs subcommand.',address:'Identify the supplied namespace and Pod in the command.',verification:'Require evidence of report processing; running alone does not establish it.',wording:'An incidental wording detail, retained for interpretation but not selected as a learning target.'
 },{'ops.chooseLogs':['choice'],'ops.produceLogs':['verb','address'],'ops.function':['verification']});
 const opsGood='Inspect application logs: kubectl -n shop logs worker-7. Confirm that reports are processed; running alone is insufficient.';
 const opsPass={choice:'demonstrated',verb:'demonstrated',address:'demonstrated',verification:'demonstrated'};
 const clarify={kind:'clarify',targets:['verb'],text:'Did you intend to inspect application logs, and which subcommand would you use?',reason:'The command wording needs clarification before choosing corrective practice.'};
 const opsRecords={
  error:record('ops-error',opsTask,'Inspect the application logs: kubectl -n shop show worker-7. Verify reports are processed, rather than relying on running.',{...opsPass,verb:'error'}),
  choiceError:record('ops-choice-error',opsTask,'Logs cannot help investigate the application error. I can write kubectl -n shop logs worker-7. Recovery requires reports to be processed.',{...opsPass,choice:'error'}),
  partial:record('ops-partial',opsTask,'Inspect logs with the logs subcommand. Check that reports are processed.',{choice:'demonstrated',verb:'demonstrated',verification:'demonstrated'}),
  ambiguous:record('ops-ambiguous',opsTask,'Inspect app information: kubectl -n shop show worker-7. Verify report processing.',{...opsPass,verb:'error'},{next:clarify}),
  unclear:record('ops-unclear',opsTask,'I cannot clarify what command I intended.',{verb:'cannot_judge'}),
  corrected:record('ops-corrected',opsTask,opsGood,opsPass,{assistance:[{timing:'current',targets:['verb'],text:'Use the logs subcommand.'}]}),
  later:record('ops-later',opsTask,opsGood,opsPass,{phase:'later'}),
  hinted:record('ops-hinted',opsTask,opsGood,opsPass,{phase:'later',assistance:[{timing:'current',targets:['verb'],text:'The subcommand is logs.'}]}),
  bypass:record('ops-bypass',opsTask,'I used the application dashboard to confirm report processing; I did not use a log command.',{verification:'demonstrated'},{phase:'later'})
 };
 const math=dataset('Explain reductions and combine them with total work',[
  {id:'math.halving',version:1,statement:'For n=2^k, k halvings reduce n to 1.'},
  {id:'math.work',version:1,statement:'Constant work per call must be combined with the number of calls across all branches.'},
  {id:'math.composition',version:1,statement:'One continuing half-size branch and two continuing half-size branches have the same depth but different total work.'}
 ],[
  capability('math.explain','Explain the halving–logarithm relationship','math.halving','Connect successive halving to the number of reductions.'),
  capability('math.work','Account for work across calls','math.work','Count work across every continuing branch.'),
  capability('math.integrate','Connect depth, branching and total work','math.composition','Distinguish one branch from two and justify the resulting total work.'),
  capability('math.fluent','Recall the complexity label fluently','math.composition','Retrieve the correct label within a separately agreed time condition.','fluent recall')
 ],['math.explain','math.work','math.integrate'],[
  {id:'search',members:['math.halving','math.work','math.composition'],structure:'A search continues in one candidate region after each reduction.'},
  {id:'recursion',members:['math.halving','math.work','math.composition'],structure:'Recursion combines reduction depth with the number of branches that continue.'}
 ],[
  {id:'math.comparison',title:'One new comparison of branching and work',exercise:'math.exercise@1',targets:['math.explain','math.work','math.integrate']},
  {id:'math.reduction',title:'Alternative short halving explanation',exercise:'math.exercise@1',targets:['math.explain']}
 ]);
 const mathTask=exercise(math,'math.exercise','For n=2^k, stop at size 1 and do constant work per call. Explain the depth, then compare one continuing half-size branch with two continuing branches.',{
  reductions:'Express repeated halving as n/2^k = 1 or an equivalent explanation.',logarithm:'Connect the number of reductions to log2(n).',work:'Include calls in every continuing branch when counting total work.',integration:'Distinguish one path of k+1 calls from the two-branch tree of 2n-1 calls; equal depth does not imply equal total work.'
 },{'math.explain':['reductions','logarithm'],'math.work':['work'],'math.integrate':['integration','work']});
 const mathGood='After k halvings, n/2^k = 1, so k = log2(n). Constant work applies to every call: one branch has k+1 calls; two branches have 2n-1. Equal logarithmic depth does not mean equal total work.';
 const mathPass={reductions:'demonstrated',logarithm:'demonstrated',work:'demonstrated',integration:'demonstrated'};
 const mathRecords={
  error:record('math-error',mathTask,'n/2^k = 1 gives k = log2(n). Work includes every call in every branch, but both cases have logarithmic total work because their depths match.',{...mathPass,integration:'error'}),
  corrected:record('math-corrected',mathTask,mathGood,mathPass),
  later:record('math-later',mathTask,mathGood,mathPass,{phase:'later'}),
  partsOnly:record('math-parts',mathTask,'n/2^k = 1 gives k = log2(n). Total work includes every call in every branch.',{reductions:'demonstrated',logarithm:'demonstrated',work:'demonstrated'},{phase:'later'}),
  hinted:record('math-hinted',mathTask,mathGood,mathPass,{phase:'later',assistance:[{timing:'current',targets:['work'],text:'Remember that the work count includes all calls.'}]})
 };
 const fact=dataset('Remember one supplied association',[
  {id:'fact.example',version:1,statement:'In this invented vocabulary exercise, mavo means blue.'}
 ],[capability('fact.recall','Recall the supplied meaning','fact.example','Recall blue when asked for the taught meaning of mavo.','recall')],['fact.recall'],[],[{id:'fact.check',title:'One short vocabulary check',exercise:'fact.exercise@1',targets:['fact.recall']}]);
 const factTask=exercise(fact,'fact.exercise','In the invented vocabulary we taught, what does mavo mean?',{meaning:'Recall the supplied association blue.'},{'fact.recall':['meaning']});
 const factRecords={error:record('fact-error',factTask,'It means red.',{meaning:'error'}),corrected:record('fact-corrected',factTask,'It means blue.',{meaning:'demonstrated'}),later:record('fact-later',factTask,'It means blue.',{meaning:'demonstrated'},{phase:'later'})};
 return {
  operations:{data:ops,records:opsRecords,walk:['error','corrected','later'],note:'Useful evidence choice and command production receive separate judgments. Try the correction, then the invented later answer.'},
  mathematics:{data:math,records:mathRecords,walk:['error','corrected','later'],note:'The parts can be demonstrated while their combination is wrong. Compare a full explanation with the parts-only answer.'},
  fact:{data:fact,records:factRecords,walk:['error','corrected','later'],note:'A simple fact uses one target and one criterion. It does not require a reasoning chain.'}
 };
}
