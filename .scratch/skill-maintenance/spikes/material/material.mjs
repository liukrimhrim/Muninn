// Throwaway source-to-practice boundary. Semantic proposals/reviews are supplied, not inferred here.
export function createMaterial(){
 const clone=x=>JSON.parse(JSON.stringify(x));
 const stable=x=>JSON.stringify(x,(_,v)=>v&&typeof v==='object'&&!Array.isArray(v)?Object.fromEntries(Object.keys(v).sort().map(k=>[k,v[k]])):v);
 const key=r=>`${r.id}@${r.version}`;
 const version=v=>Number.isInteger(v)&&v>0;
 const intent=t=>({version:t.version,content:clone(t.content),action:t.action,mode:t.mode,conditions:t.conditions});
 const empty=()=>({sources:[],units:[]});
 function capture(library,source){
  if(!source.id||!Number.isInteger(source.version)||source.version<1||typeof source.text!=='string'||!source.text.trim())throw Error('A source needs an ID, positive version and literal text.');
  const old=library.sources.find(s=>key(s)===key(source));
  if(old&&stable(old)!==stable(source))throw Error('This source version already exists with different content. Capture a new version.');
  return old?clone(library):{...clone(library),sources:[...clone(library.sources),clone(source)]};
 }
 function referenceErrors(library,refs){
  if(!Array.isArray(refs)||!refs.length)return ['Source references are missing.'];
  return refs.flatMap(ref=>{
   const source=library.sources.find(s=>s.id===ref.source&&s.version===ref.version);
   if(!source)return ['The referenced source version is unavailable.'];
   const lines=source.text.split('\n');
   if(!Number.isInteger(ref.start)||!Number.isInteger(ref.end)||ref.start<1||ref.end<ref.start||ref.end>lines.length)return ['The source location is outside the saved text.'];
   return lines.slice(ref.start-1,ref.end).join('\n')===ref.quote?[]:['The quoted passage does not match that source version and location.'];
  });
 }
 function prepare(library,draft){
  const definitions=[...library.units,...draft.units],unitMap=new Map(),definitionErrors=new Map();
  for(const unit of definitions){const k=key(unit),old=unitMap.get(k);if(old&&stable(old)!==stable(unit))definitionErrors.set(k,'One content identity has conflicting definitions.');else unitMap.set(k,unit);}
  function closure(refs){
   const found=new Map(),issues=[];
   function visit(ref){
    const k=key(ref);if(found.has(k))return;
    const unit=unitMap.get(k);found.set(k,unit);
    if(!unit){issues.push(`Missing content ${k}.`);return;}
    if(definitionErrors.has(k))issues.push(definitionErrors.get(k));
    if(!unit.id?.trim()||!version(unit.version))issues.push(`${k}: content needs a stable ID and positive version.`);
    if(!unit.statement?.trim()||!unit.scope?.trim())issues.push(`${k}: content needs its meaning and scope.`);
    if(unit.status!=='usable')issues.push(`${k}: ${unit.concern||'content is still a proposal'}.`);
    issues.push(...referenceErrors(library,unit.refs).map(e=>`${k}: ${e}`));
    for(const link of draft.sourceLinks||[])if(key(link.unit)===k)issues.push(...referenceErrors(library,link.refs).map(e=>`${k}: ${e}`));
    for(const dependency of unit.dependsOn||[])visit(dependency);
   }
   refs.forEach(visit);return {units:[...found.values()].filter(Boolean),issues};
  }
  const held=[],targets=[];
  for(const id of new Set(draft.selected)){
   const candidate=draft.targets.find(t=>t.id===id);
   if(!candidate){held.push({target:id,reasons:['Selected capability is missing.']});continue;}
   const resolved=closure(candidate.content);
   if(draft.targets.filter(t=>t.id===id).length!==1||!version(candidate.version))resolved.issues.push('Capability identity or version is invalid.');
   if(!candidate.content.length||!candidate.action?.trim()||!candidate.mode?.trim()||!candidate.conditions?.trim())resolved.issues.push('The capability needs content, action, mode and conditions.');
   if(resolved.issues.length){held.push({target:id,reasons:[...new Set(resolved.issues)]});continue;}
   targets.push({id,label:candidate.label,contract:{version:candidate.version,content:resolved.units.map(u=>({id:u.id,version:u.version})).sort((a,b)=>key(a).localeCompare(key(b))),action:candidate.action,mode:candidate.mode,conditions:candidate.conditions}});
  }
  const catalog=[],heldExercises=[];
  for(const e of draft.exercises){
   if(!e.coverage.some(c=>draft.selected.includes(c.target)))continue;
   const criteria=e.criteria.map(c=>c.id),reasons=[];
   if(!e.id?.trim()||draft.exercises.filter(x=>x.id===e.id).length!==1||![e.version,e.rubric_version].every(version))reasons.push('Exercise and rubric identities need positive versions.');
   if(!['check','practice'].includes(e.kind))reasons.push('This material spike supports checks and practice tasks.');
   if(!['setup','answer','feedback'].every(k=>Number.isFinite(e.seconds?.[k])&&e.seconds[k]>=0)||Object.values(e.seconds||{}).reduce((n,x)=>n+x,0)<=0)reasons.push('Include usable setup, answering and feedback time estimates.');
   if(e.status!=='usable')reasons.push(e.concern||'Exercise needs review after a content change.');
   if(!e.prompt?.trim()||!criteria.length||new Set(criteria).size!==criteria.length||e.criteria.some(c=>!c.rule?.trim()))reasons.push('Exercise needs a prompt and distinct usable criteria.');
   if(new Set(e.coverage.map(c=>c.target)).size!==e.coverage.length)reasons.push('Map each capability once per exercise.');
   if(e.coverage.some(c=>!targets.some(t=>t.id===c.target)||!c.criteria.length||new Set(c.criteria).size!==c.criteria.length||c.criteria.some(id=>!criteria.includes(id))))reasons.push('Coverage must resolve to ready selected capabilities and their criteria.');
   if(e.coverage.some(c=>{const t=draft.targets.find(t=>t.id===c.target);return !t||stable(c.authoredFor)!==stable(intent(t));}))reasons.push('The target changed since this exercise mapping was reviewed.');
   if(reasons.length){heldExercises.push({exercise:e.id,reasons});continue;}
   const exercise={id:e.id,version:e.version,rubric_version:e.rubric_version,subject:draft.title,prompt:e.prompt,criteria:clone(e.criteria),coverage:e.coverage.map(c=>({target:c.target,criteria:clone(c.criteria),contract:clone(targets.find(t=>t.id===c.target).contract)}))};
   catalog.push({id:e.id,label:e.label,kind:e.kind,seconds:clone(e.seconds),exercise,samples:clone(e.samples)});
  }
  const noExercise=targets.filter(t=>!catalog.some(a=>a.exercise.coverage.some(c=>c.target===t.id))).map(t=>t.id);
  const data={title:draft.title,components:[...unitMap.values()].map(clone),capabilities:targets,targets,goal:{text:draft.goal,targets:targets.map(t=>t.id)},knowledgeGroups:clone(draft.groups),practiceBundles:catalog.filter(a=>a.kind==='check').map(a=>({id:a.id,title:a.label,targets:a.exercise.coverage.map(c=>c.target)}))};
  return {revision:draft.revision,requested:clone(draft.selected),held,heldExercises,noExercise,data,catalog,note:'Source-location validity and supplied review status do not establish truth or teaching quality.'};
 }
 function revise(draft,id,patch){
  const next=clone(draft),unit=next.units.find(u=>u.id===id);
  if(!unit)throw Error('Edit a local proposal; shared library revisions need their own explicit mapping.');
  const affected=new Set([id]);
  for(let changed=true;changed;){changed=false;for(const u of next.units)if(!affected.has(u.id)&&(u.dependsOn||[]).some(r=>affected.has(r.id))){affected.add(u.id);changed=true;}}
  const oldVersions=new Map(next.units.map(u=>[u.id,u.version]));
  const move=ref=>affected.has(ref.id)&&ref.version===oldVersions.get(ref.id)?{id:ref.id,version:ref.version+1}:ref;
  for(const u of next.units){
   if(u.id===id)for(const field of ['statement','scope','refs'])if(Object.hasOwn(patch,field))u[field]=clone(patch[field]);
   if(affected.has(u.id)){u.version++;u.status='needs_review';u.concern='Meaning or a supporting claim changed; inspect this version.';u.replaces={id:u.id,version:u.version-1};}
   u.dependsOn=(u.dependsOn||[]).map(move);
  }
  const targetIds=[];
  for(const t of next.targets){if(t.content.some(r=>affected.has(r.id))){targetIds.push(t.id);t.version++;}t.content=t.content.map(move);}
  const exerciseIds=[];
  for(const e of next.exercises)if(e.coverage.some(c=>targetIds.includes(c.target))){e.version++;e.rubric_version++;e.status='needs_review';e.concern='Review the prompt, answer criteria and coverage after the content change.';exerciseIds.push(e.id);}
  next.revision++;next.lastChange={units:[...affected],targets:targetIds,exercises:exerciseIds};return next;
 }
 function reviewed(draft,kind,id,reviewer,reason){
  if(!['unit','exercise'].includes(kind))throw Error('Review a unit or an exercise.');
  if(!reviewer?.trim()||!reason?.trim())throw Error('Record who inspected this version and why it is usable.');
  const next=clone(draft),item=(kind==='unit'?next.units:next.exercises).find(x=>x.id===id);
  if(!item)throw Error('The reviewed item is missing.');
  if(kind==='exercise')for(const c of item.coverage){const t=next.targets.find(t=>t.id===c.target);if(!t)throw Error('The reviewed capability is missing.');c.authoredFor=intent(t);}
  item.status='usable';delete item.concern;item.review={reviewer,reason};next.revision++;return next;
 }
 function reuse(library,draft,localId,existingRef,reason){
  const existing=library.units.find(u=>key(u)===key(existingRef)),local=draft.units.find(u=>u.id===localId);
  if(!existing||!local||!reason?.trim())throw Error('An explicit local-to-existing mapping and reason are required.');
  if(existing.status!=='usable'||local.status!=='usable')throw Error('Resolve the flagged content or source concern before reusing this claim.');
  if(existing.statement!==local.statement||existing.scope!==local.scope||stable(existing.dependsOn||[])!==stable(local.dependsOn||[]))throw Error('Different meaning, scope or dependencies are not an exact duplicate. Keep it separate for review.');
  // A new dependency identity is a revision even when its wording is identical.
  const next=revise(draft,localId,{}),replace=r=>r.id===local.id&&r.version===local.version+1?clone(existingRef):r;
  next.units=next.units.filter(u=>u.id!==localId).map(u=>({...u,dependsOn:(u.dependsOn||[]).map(replace)}));
  next.targets=next.targets.map(t=>({...t,content:t.content.map(replace)}));
  next.groups=next.groups.map(g=>({...g,members:g.members.map(id=>id===localId?existing.id:id)}));
  next.sourceLinks=[...(next.sourceLinks||[]),{unit:clone(existingRef),refs:clone(local.refs),reason}];
  next.lastChange.units=next.lastChange.units.filter(id=>id!==localId);next.lastChange.reused={from:{id:local.id,version:local.version},to:clone(existingRef)};return next;
 }
 function bind(action,outcome,id){
  const sample=action.samples[outcome];if(!sample)throw Error('This example has no such authored answer.');
  const input={case_id:id,attempt:{id,origin:'hypothetical',phase:'current'},exercise:clone(action.exercise),response:sample.response,context:[{id:'provenance',role:'task',text:'Authored material-to-practice fixture; no learner or automatic grader supplied this response.'}],assistance:clone(sample.assistance||[])};
  return {input,assessment:{case_id:id,observations:clone(sample.observations),next:{kind:'stop',targets:[],text:'Use the recorded evidence to choose useful practice.',reason:'No additional diagnostic claim is supplied.'},alternatives:[]},assessor:'Authored example',protocol:{name:'Material-to-practice boundary'}};
 }
 return {empty,capture,referenceErrors,prepare,revise,reviewed,reuse,bind};
}
