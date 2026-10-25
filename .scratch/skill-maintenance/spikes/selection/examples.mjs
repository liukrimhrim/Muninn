import {createExamples} from '../representation/examples.mjs';

// All additional prompts, timings, responses and assessments are authored fixtures.
export function createSelectionExamples(){
 const clone=x=>JSON.parse(JSON.stringify(x)),old=createExamples();
 function task(data,base,id,prompt,targets){
  const coverage=base.coverage.filter(c=>targets.includes(c.target)),criteria=[...new Set(coverage.flatMap(c=>c.criteria))];
  return {...clone(base),id,prompt,coverage:clone(coverage),criteria:clone(base.criteria.filter(c=>criteria.includes(c.id)))};
 }
 function record(exercise,label,response,statuses={},options={}){
  const id=exercise.id+'-'+label;
  return {input:{case_id:id,attempt:{id,origin:'hypothetical',phase:'later'},exercise:clone(exercise),response,
   context:[{id:'source',role:'task',text:'Authored selection experiment; durations and judgments are not learner measurements.'}],
   assistance:options.assisted?[{timing:'current',targets:exercise.criteria.map(c=>c.id),text:'The answer was supplied as part of the worked explanation.'}]:[]},
   assessment:{case_id:id,observations:exercise.criteria.map(c=>({criterion:c.id,status:statuses[c.id]||'demonstrated',quotes:['not_shown','cannot_judge'].includes(statuses[c.id])?[]:[response],reason:'Authored assessment for a selection comparison.'})),next:options.next||{kind:'stop',targets:[],text:'Use the supplied evidence to select the next action.',reason:'No extra diagnostic proposal.'},alternatives:[]},
   assessor:'Authored selection fixture',protocol:{name:'Explicit coverage selection experiment'}};
 }
 function action(data,base,id,kind,label,targets,seconds,response,extras={}){
  const exercise=task(data,base,id,label,targets);
  return {id,kind,label,exercise,seconds:{setup:0,answer:seconds-5,feedback:5},outcomes:{correct:record(exercise,'correct',response,{}, {assisted:kind==='practice'})},...extras};
 }
 const ops=old.operations,opBase=ops.records.later.input.exercise;
 const command='kubectl -n shop logs worker-7';
 const opsAll='Inspect application logs with kubectl -n shop logs worker-7. Confirm reports are processed; running alone is insufficient.';
 const opCatalog=[
  action(ops.data,opBase,'ops.clarify','diagnose','Clarify which command you intended',['ops.produceLogs'],20,command,{branches:[{if:'The command is correct',next:'check',targets:['ops.chooseLogs','ops.function']},{if:'The command is wrong',next:'practice',targets:['ops.produceLogs']},{if:'The intention remains unclear',next:'stop',targets:['ops.produceLogs']}],hypothesis:'The wording may hide a command-production gap or a harmless wording mistake; the existing assessment requested clarification.'}),
  action(ops.data,opBase,'ops.practice','practice','Practice the log command',['ops.produceLogs'],25,command),
  action(ops.data,opBase,'ops.combined','check','A new incident: choose evidence, produce the command and verify recovery',ops.data.goal.targets,60,opsAll),
  action(ops.data,opBase,'ops.command','check','Write the command without a hint',['ops.produceLogs'],35,command),
  action(ops.data,opBase,'ops.choice','check','Explain which evidence to inspect',['ops.chooseLogs'],35,'Application logs can expose the reported application error.'),
  action(ops.data,opBase,'ops.verify','check','Say what would establish recovery',['ops.function'],30,'Check that reports are processed; running alone is insufficient.')
 ];
 const diag=opCatalog[0];
 diag.outcomes.error=record(diag.exercise,'error','kubectl -n shop show worker-7',{verb:'error'});
 diag.outcomes.unclear=record(diag.exercise,'unclear','I cannot say which command I intended.',{verb:'cannot_judge',address:'cannot_judge'});
 const useless=clone(diag);useless.id='ops.same-help';useless.exercise.id=useless.id;useless.label='An unnecessary question';useless.seconds={setup:0,answer:5,feedback:0};useless.branches=[{if:'yes',next:'practice',targets:['ops.produceLogs']},{if:'no',next:'practice',targets:['ops.produceLogs']}];
 opCatalog.push(useless);
 const math=old.mathematics,mathBase=math.records.later.input.exercise,mathAll=math.records.later.input.response;
 const mathCatalog=[
  action(math.data,mathBase,'math.practice','practice','Practice connecting branching with total work',['math.integrate'],30,'Every call contributes work. A single path has k+1 calls; the full binary tree has 2n-1. Equal depth does not imply equal work.'),
  action(math.data,mathBase,'math.combined','check','Compare one and two continuing half-size branches',math.data.goal.targets,70,mathAll),
  action(math.data,mathBase,'math.explain','check','Explain repeated halving and logarithms',['math.explain'],35,'After k halvings n/2^k = 1, so k = log2(n).'),
  action(math.data,mathBase,'math.work','check','Count the work across calls',['math.work'],35,'Count the work of every call in every continuing branch.'),
  action(math.data,mathBase,'math.integrate','check','Connect equal depth with different total work',['math.integrate'],40,'Every call counts: one path has k+1 calls and two branches give 2n-1 calls. Equal depth does not imply equal work.')
 ];
 const combined=mathCatalog[1];
 combined.outcomes.partial=record(combined.exercise,'partial',math.records.partsOnly.input.response,{integration:'not_shown'});
 combined.outcomes.error=record(combined.exercise,'error',math.records.error.input.response,{integration:'error'});
 combined.outcomes.hinted=record(combined.exercise,'hinted',mathAll,{}, {assisted:true});
 const fact=old.fact,factBase=fact.records.later.input.exercise;
 const factCatalog=[action(fact.data,factBase,'fact.practice','practice','Practice the supplied association',['fact.recall'],15,'Mavo means blue.'),action(fact.data,factBase,'fact.recall','check','Recall the meaning of mavo without a hint',['fact.recall'],10,'Blue.')];
 const recognition=clone(factCatalog[1]);recognition.id='fact.recognition';recognition.label='Choose blue from visible answers';recognition.exercise.id=recognition.id;recognition.exercise.coverage[0].contract.mode='recognition';recognition.seconds={setup:0,answer:1,feedback:1};factCatalog.unshift(recognition);
 const ids=['A','B','C','D','E'];
 const targets=ids.map(id=>({id,label:'Target '+id,contract:{version:1,content:[{id,version:1}],action:'Recall the supplied content for '+id,mode:'recall',conditions:'Unaided recall in an invented coverage example.'}}));
 const groups=[['Q1',['A','B'],120],['Q2',['B','C','D'],180],['Q3',['D','E'],120],['Q4',['A','B','C','D'],240]];
 const coverageData={title:'Five targets, overlapping questions',goal:{text:'Cover the five pending targets',targets:ids},targets,practiceBundles:groups.map(([id,ts])=>({id,title:id,targets:ts}))};
 const base={id:'coverage-seed',version:1,rubric_version:1,prompt:'Authored starting state',criteria:ids.map(id=>({id,rule:'Recall the specified content for '+id})),coverage:targets.map(t=>({target:t.id,contract:t.contract,criteria:[t.id]}))};
 const coverageCatalog=groups.map(([id,ts,seconds])=>action(coverageData,base,id,'check',id+': recall '+ts.join(', '),ts,seconds,'Invented successful recalls for '+ts.join(', ')));
 const unobserved=record(base,'unobserved','No response evidence for these targets.',Object.fromEntries(ids.map(id=>[id,'not_shown'])));
 const make=(label,data,catalog,seeds,budget,walk,description,phase='later')=>({label,data,catalog,seeds,budget,walk,description,phase});
 return {
  coverage:make('Cover five targets',coverageData,coverageCatalog,[unobserved],360,['correct','correct'],'Watch two overlapping exercises cover the pending targets within six illustrative minutes.'),
  clarification:make('Clarify, then help',ops.data,opCatalog,[ops.records.ambiguous],120,['error','correct','correct'],'A wrong clarification leads to command practice and then a fresh combined check. A correct clarification takes a different route.'),
  tight:make('Too little time to diagnose',ops.data,opCatalog,[ops.records.ambiguous],40,['correct'],'A useful question can still be unaffordable once its follow-up is included. Keep the command concern unresolved and use time only for eligible work.'),
  repair:make('Repair the connection',math.data,mathCatalog,[math.records.error],100,['correct','correct'],'Practice only the missing connection, then check it in a larger answer. Immediate success does not clear the later retention check.','current'),
  partial:make('A larger answer leaves a gap',math.data,mathCatalog,[math.records.corrected],110,['partial','correct'],'A combined answer shows the parts but omits the connection. Recompute and ask only for the missing evidence.'),
  fact:make('A simple fact',fact.data,factCatalog,[fact.records.corrected],10,['correct'],'Use one unaided recall. A cheaper recognition prompt cannot satisfy this recall goal.')
 };
}
