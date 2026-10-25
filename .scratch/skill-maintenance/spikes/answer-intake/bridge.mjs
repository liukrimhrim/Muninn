// Throwaway boundary experiment; dependencies are the real existing components.
export function createBridge(T, M) {
 const stable=x=>JSON.stringify(x,(_,v)=>v&&typeof v==='object'&&!Array.isArray(v)?Object.fromEntries(Object.keys(v).sort().map(k=>[k,v[k]])):v);
 const present=s=>typeof s==='string'&&s.trim().length>0;
 function connect(data, state, input, record) {
  const errors=T.validateBound(input,record);
  const criteria=input.exercise.criteria.map(c=>c.id), known=data.targets.map(t=>t.id);
  const explicit=Object.hasOwn(input.exercise,'coverage'),coverage=input.exercise.coverage;
  if(!explicit&&(criteria.some(id=>!known.includes(id))||new Set(criteria).size!==criteria.length))errors.push('Criteria must map once each to known planning targets.');
  if(!explicit&&data.targets.some(t=>t.contract&&criteria.includes(t.id)))errors.push('Versioned capabilities require explicit exercise coverage.');
  if(explicit){
   if(!Array.isArray(coverage))errors.push('Coverage must be an array.');
   else{
    if(new Set(coverage.map(c=>c?.target)).size!==coverage.length)errors.push('Map each capability once per exercise.');
    for(const c of coverage){
     if(!c){errors.push('Each coverage entry needs a capability and required criteria.');continue;}
     const target=data.targets.find(t=>t.id===c.target),contract=c.contract;
     if(!target||!contract||stable(contract)!==stable(target.contract))errors.push('Coverage must match the current capability contract exactly.');
     if(!contract||!Number.isInteger(contract.version)||contract.version<1||!['action','mode','conditions'].every(k=>present(contract[k]))||!Array.isArray(contract.content)||!contract.content.length||contract.content.some(r=>!present(r?.id)||!Number.isInteger(r.version)||r.version<1))errors.push('A capability contract needs a version, content references, action, mode and conditions.');
     if(!Array.isArray(c.criteria)||!c.criteria.length||new Set(c.criteria).size!==c.criteria.length||c.criteria.some(id=>!criteria.includes(id)))errors.push('Coverage must name distinct existing required criteria.');
    }
   }
   if(!present(input.exercise.id)||![input.exercise.version,input.exercise.rubric_version].every(v=>Number.isInteger(v)&&v>0))errors.push('Explicit coverage needs exercise and rubric versions.');
   if(data.goal&&!sameTargets(data.goal.targets,known))errors.push('Planning targets must match the selected goal.');
  }
  if(!present(input.attempt?.id)||!['recorded','hypothetical'].includes(input.attempt?.origin)||!['current','later'].includes(input.attempt?.phase))errors.push('The caller must supply attempt identity, origin and phase.');
  if(!Array.isArray(input.context)||new Set(input.context?.map(c=>c.id)).size!==input.context?.length)errors.push('Context must have distinct reference IDs.');
  if(!Array.isArray(input.assistance)||input.assistance.some(h=>!['current','earlier'].includes(h.timing)||!present(h.text)||!Array.isArray(h.targets)||!h.targets.length||h.targets.some(t=>!(explicit?criteria:known).includes(t))))errors.push('Record help timing, text and known targets explicitly; explicit coverage uses rubric criterion IDs.');
  if(errors.length)return {errors,state};
  const a=record.assessment;
  for(const o of a.observations){
   if(o.issue!==undefined){
    if(o.issue!=='supported_misread'||o.status!=='demonstrated'||!present(o.issue_reason)||!Array.isArray(o.context_quotes)||!o.context_quotes.length)errors.push('A supported misread needs a demonstrated correction, reason and prior learner evidence.');
    for(const ref of o.context_quotes||[]){const c=input.context.find(c=>c.id===ref.id);if(c?.role!=='learner'||!present(ref.quote)||!c.text.includes(ref.quote))errors.push('Misread support must quote supplied learner context.');}
   }
  }
  if(a.next.kind==='practice'&&a.next.targets.some(t=>!a.observations.some(o=>o.criterion===t&&o.status==='error')))errors.push('Every remedial target needs its own observed error.');
  if(explicit&&a.next.targets.some(id=>!coverage.some(c=>c.criteria.includes(id))))errors.push('A next-action criterion must map to a selected capability.');
  if(M.contractConflicts(data,state).length)errors.push('Retained evidence uses a different capability contract. Preserve that history and review the mapping explicitly.');
  if(errors.length)return {errors,state};
  let event={id:input.case_id,attempt:input.attempt.id,origin:input.attempt.origin,phase:input.attempt.phase,quote:input.response,
   why:explicit?'Explicit criterion-to-capability mapping; structural validation is not semantic validation.':'Current-chat assessment under the version-2 protocol; structural validation is not semantic validation.',
   assessmentRecord:record,
   observations:a.observations.filter(o=>['demonstrated','error'].includes(o.status)).map(o=>{
    const help=input.assistance.filter(h=>h.targets.includes(o.criterion));
    return {target:o.criterion,result:o.status,quotes:o.quotes,reason:o.reason,assisted:help.some(h=>h.timing==='current'),
     help:help.length?help.map(h=>`${h.timing}: ${h.text}`).join(' '):'No task-specific help recorded; outside help is not established.',
     ...(o.issue==='supported_misread'?{issue:'accepted_misread'}:{})};
   })};
  if(explicit){
   // All named criteria are required. Missing evidence cannot complete a capability;
   // an observed error remains evidence even when another required part is absent.
   const derived=coverage.map(c=>{
    const rows=c.criteria.map(id=>a.observations.find(o=>o.criterion===id));
    const status=['error','cannot_judge','not_shown','demonstrated'].find(s=>rows.some(o=>o.status===s));
    const help=input.assistance.filter(h=>h.targets.some(id=>c.criteria.includes(id)));
    return {criterion:c.target,status,contract:c.contract,criteria:c.criteria,
     evidenceRefs:c.criteria.map(criterion=>({answer:input.case_id,attempt:input.attempt.id,exercise:input.exercise.id,exerciseVersion:input.exercise.version,rubricVersion:input.exercise.rubric_version,criterion})),
     quotes:[...new Set(rows.flatMap(o=>o.quotes))],reason:rows.map(o=>`${o.criterion}: ${o.reason}`).join(' '),
     assisted:help.some(h=>h.timing==='current'),help:help.length?help.map(h=>`${h.timing}: ${h.text}`).join(' '):'No task-specific help recorded; outside help is not established.',
     ...(status==='demonstrated'&&rows.some(o=>o.issue==='supported_misread')?{issue:'accepted_misread'}:{})};
   });
   event.observations=derived.filter(o=>['demonstrated','error'].includes(o.status)).map(({criterion,status,...rest})=>({target:criterion,result:status,...rest}));
   // The original bound assessment stays intact. Only this projection uses capability IDs.
   event.planningAssessment={observations:derived,next:{...a.next,targets:[...new Set(a.next.targets.flatMap(id=>coverage.filter(c=>c.criteria.includes(id)).map(c=>c.target)))]}};
   event=JSON.parse(JSON.stringify(event));
  }
  const existing=state.events.find(e=>e.id===event.id);
  if(existing&&stable(existing)!==stable(event))return {errors:['This answer ID already has different content or an assessment. Keep the original; review the change explicitly.'],state};
  // Missing or ambiguous evidence stays in the attached record, not in learner-failure state.
  const next=M.append(state,event);
  return {errors:[],state:next,event,plan:M.plan(data,next),unresolved:a.observations.filter(o=>o.status==='cannot_judge'),
   unobserved:a.observations.filter(o=>o.status==='not_shown'),proposal:a.next};
 }
 function sameTargets(a,b){return Array.isArray(a)&&new Set(a).size===a.length&&stable([...a].sort())===stable([...b].sort());}
 return {connect};
}
