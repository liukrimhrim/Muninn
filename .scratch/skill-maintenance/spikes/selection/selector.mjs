// Throwaway selection comparison. Needs come from the existing evidence planner.
export function createSelector(M,B){
 const unique=xs=>[...new Set(xs)];
 const stable=x=>JSON.stringify(x,(_,v)=>v&&typeof v==='object'&&!Array.isArray(v)?Object.fromEntries(Object.keys(v).sort().map(k=>[k,v[k]])):v);
 const same=(a,b)=>stable(a)===stable(b);
 const cost=a=>Object.values(a.seconds).reduce((n,x)=>n+x,0);
 const coverage=a=>a.exercise.coverage.map(c=>c.target);
 const start=(budgetSeconds,phase='later',diagnosticLimit=3)=>({budgetSeconds,phase,diagnosticLimit,completed:[],checked:[],repaired:[]});
 const spent=s=>s.completed.reduce((n,c)=>n+c.seconds,0);
 function needs(data,state,session){
  const plan=M.plan(data,state),questions=plan.now.filter(a=>['clarify','follow_up'].includes(a.kind));
  const review=unique(plan.now.filter(a=>a.kind==='review').flatMap(a=>a.targets));
  const diagnose=unique(questions.flatMap(q=>q.targets));
  const practice=unique(plan.now.filter(a=>a.kind==='help').flatMap(a=>a.targets));
  const checks=state.events.length?unique(plan.later.flatMap(a=>a.targets)):data.goal.targets;
  const check=unique([...session.repaired.filter(t=>checks.includes(t)),...checks]).filter(t=>!review.includes(t)&&!diagnose.includes(t)&&!practice.includes(t)&&!session.checked.includes(t)&&M.status(state,t).last?.issue!=='accepted_misread');
  return {plan,review,diagnose,practice,check,questions,taskConcern:questions.find(q=>!q.targets.length)||null};
 }
 // Exhaustive small-catalog comparison, not a production optimizer or learning objective.
 function bundles(actions,targets,remaining){
  let options=[{actions:[],seconds:0,covered:[]}];
  for(const action of actions){
   const added=options.map(p=>({actions:[...p.actions,action],seconds:p.seconds+cost(action),covered:unique([...p.covered,...coverage(action).filter(t=>targets.includes(t))])}));
   options.push(...added.filter(p=>p.seconds<=remaining));
  }
  options=options.filter(p=>p.actions.length&&p.covered.length);
  const full=options.filter(p=>targets.every(t=>p.covered.includes(t)));
  return (full.length?full:options).sort((a,b)=>{
   if(!full.length)for(const t of targets){const d=Number(b.covered.includes(t))-Number(a.covered.includes(t));if(d)return d;}
   return a.seconds-b.seconds||a.actions.length-b.actions.length||a.actions.map(x=>x.id).join().localeCompare(b.actions.map(x=>x.id).join());
  })[0];
 }
 function choose(data,state,catalog,session){
  const n=needs(data,state,session),remaining=Math.max(0,session.budgetSeconds-spent(session)),declined=[];
  const result={remaining,spent:spent(session),needs:n,declined,unresolved:unique([...n.review,...n.diagnose,...n.practice,...n.check])};
  if(M.contractConflicts(data,state).length)return {...result,kind:'stop',reason:'Review changed capability definitions before reusing this evidence.'};
  if(n.taskConcern)return {...result,kind:'stop',reason:'The whole task has an unresolved concern without a specific target. Clarify the outcome before selecting more practice; do not mark the session complete.'};
  const done=new Set(session.completed.map(c=>c.action)),valid=[];
  for(const a of catalog){
   let reason;
   if(done.has(a.id))reason='This prompt was already attempted in this session; use a fresh variant.';
   else if(!a.exercise.coverage.length||a.exercise.coverage.some(c=>!same(c.contract,data.targets.find(t=>t.id===c.target)?.contract)))reason='The task does not match the required action, mode or conditions.';
   else if(!Object.values(a.seconds).every(x=>Number.isFinite(x)&&x>=0)||cost(a)<=0)reason='The task needs a positive total cost including setup, answering and feedback.';
   else if(cost(a)>remaining)reason='The full task cost exceeds the remaining time.';
   else if(coverage(a).some(t=>n.review.includes(t)))reason='Assessment review is pending for a covered target.';
   else if((a.requires||[]).some(t=>n.practice.includes(t)||n.diagnose.includes(t)||n.review.includes(t)))reason='An observed prerequisite concern blocks this task.';
   if(reason)declined.push({id:a.id,reason});else valid.push(a);
  }
  const diagnosticCount=session.completed.filter(c=>c.kind==='diagnose').length;
  const diagnostic=valid.filter(a=>{
   if(a.kind!=='diagnose')return false;
   let reason;
   const branches=a.branches||[],signatures=unique(branches.map(b=>JSON.stringify([b.next,b.targets])));
   if(!coverage(a).some(t=>n.diagnose.includes(t)))reason='There is no supported unresolved concern for this question.';
   else if(diagnosticCount>=session.diagnosticLimit)reason='The diagnostic prompt limit is reached; keep the concern unresolved.';
   else if(signatures.length<2)reason='Every answer would lead to the same teaching action.';
   else if(branches.some(branch=>{
    if(branch.next==='stop')return false;
    const continuation=valid.filter(b=>b.kind===branch.next&&b.id!==a.id&&branch.targets.every(t=>coverage(b).includes(t)));
    const checkCost=branch.next==='practice'?Math.min(...valid.filter(b=>b.kind==='check'&&branch.targets.every(t=>coverage(b).includes(t))).map(cost)):0;
    return !continuation.some(b=>cost(a)+cost(b)+checkCost<=remaining);
   }))reason='A substantive answer branch would leave no time for its next useful action and any post-practice check.';
   if(reason)declined.push({id:a.id,reason});return !reason;
  }).sort((a,b)=>cost(a)-cost(b)||a.id.localeCompare(b.id));
  if(diagnostic.length)return {...result,kind:'diagnose',action:diagnostic[0],planned:[diagnostic[0].id],reason:'Resolve a supported concern whose answers change the next teaching action; reserve follow-up time, including a check after corrective practice.'};
  for(const kind of ['practice','check']){
   const targetSet=n[kind];
   const candidates=valid.filter(a=>a.kind===kind&&coverage(a).some(t=>targetSet.includes(t))&&!coverage(a).some(t=>n.diagnose.includes(t)||(kind==='check'&&n.practice.includes(t))));
   const selected=bundles(candidates,targetSet,remaining);
   if(selected)return {...result,kind,action:selected.actions[0],planned:selected.actions.map(a=>a.id),plannedSeconds:selected.seconds,expectedCoverage:selected.covered,reason:kind==='practice'?'Address an observed error; retain successful and unresolved targets.':'Choose an affordable set of exercises for the pending targets, then reassess after the next answer. Expected coverage is not observed coverage.'};
  }
  return {...result,kind:'stop',reason:result.unresolved.length?'No suitable next action fits the evidence and remaining budget. Retain unresolved needs.':'The checks for this illustrative session are complete. Future retention remains untested.'};
 }
 function complete(data,state,catalog,session,actionId,record,actualSeconds){
  const action=catalog.find(a=>a.id===actionId);
  if(!action||!same(action.exercise,record.input.exercise))throw Error('The answer must belong to the selected task and its full coverage contract.');
  if(!Number.isFinite(actualSeconds)||actualSeconds<0)throw Error('Record a nonnegative actual duration.');
  const old=session.completed.find(c=>c.answer===record.input.case_id);
  if(old&&(old.action!==actionId||old.seconds!==actualSeconds))throw Error('The completed answer already has different cost or task metadata.');
  if(!old&&choose(data,state,catalog,session).action?.id!==actionId)throw Error('Recompute the next action before accepting an answer to it.');
  const packet=JSON.parse(JSON.stringify(record));
  // A check after correction here is immediate practice, not a delayed retention result.
  packet.input.attempt.phase=old?state.events.find(e=>e.id===packet.input.case_id).phase:session.phase==='later'&&!session.repaired.length&&action.kind!=='practice'?'later':'current';
  const out=B.connect(data,state,packet.input,packet);
  if(out.errors.length)throw Error(out.errors.join('; '));
  if(old)return {state:out.state,session,event:out.event,decision:choose(data,out.state,catalog,session)};
  const shown=out.event.observations.filter(o=>o.result==='demonstrated'&&!o.assisted).map(o=>o.target);
  const errors=out.event.observations.filter(o=>o.result==='error').map(o=>o.target);
  const repaired=unique([...session.repaired,...(action.kind==='practice'?coverage(action):[])]);
  const checked=unique([...session.checked.filter(t=>!errors.includes(t)&&!(action.kind==='practice'&&coverage(action).includes(t))),...(action.kind==='check'?shown:[])]);
  const next={...session,repaired,checked,completed:[...session.completed,{action:actionId,kind:action.kind,answer:packet.input.case_id,seconds:actualSeconds}]};
  return {state:out.state,session:next,event:out.event,decision:choose(data,out.state,catalog,next)};
 }
 return {start,spent,cost,coverage,needs,choose,complete};
}
