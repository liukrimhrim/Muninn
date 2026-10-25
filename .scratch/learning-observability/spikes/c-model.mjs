// THROWAWAY analytical behavior model. All records below are authored fixtures.
// No persistence, learner fitting, scheduling, telemetry or application integration.
export const CModel = (() => {
  const catalogs = {
    search: {name:'Search and algorithms', items:[
      ['Repeated halving','explain','How many halvings reduce 65,536 names to 1,024?','Six: log2(65,536) − log2(1,024).','Sixty-four halvings, because 65,536 / 1,024 = 64.','Distinguish the size ratio from the number of halvings.'],
      ['Safe exclusion','explain','Why discard names before a midpoint smaller than Mira?','The list is sorted, so all earlier names are also smaller.','Discard them because they are earlier.','Connect sorted order to the comparison and excluded region.'],
      ['Work across branches','explain','How many nodes are at depth d in a full binary tree?','2^d nodes.','There are d nodes because the depth is d.','Distinguish branching count from path depth.'],
      ['Depth versus total work','explain','Does logarithmic depth imply logarithmic total work?','No; sum work across all branches and levels.','Yes; the tree has logarithmic depth.','Explain why path depth and total work differ.'],
      ['Stopping condition','explain','When does unsuccessful binary search stop?','When the candidate interval is empty.','When only one name remains, even if it might match.','Preserve the last candidate and stop on an empty interval.'],
      ['Choosing a search strategy','explain','For one search of an unsorted list, is binary search always cheaper?','No; include the cost of sorting before choosing.','Yes, binary search is always logarithmic.','Account for preparation and applicability conditions.'],
      ['Boundary handling','select','Which interval follows a nonmatching midpoint?','The smaller interval excluding that already-compared midpoint.','Keep the midpoint so we do not lose a candidate.','Require strict progress after a nonmatch.'],
      ['Ordering assumptions','select','Which input permits this binary search procedure?','One sorted under the same comparison used by the search.','Any list; the search will sort it as it goes.','Select the matching order precondition.']
    ]},
    grammar: {name:'Grammar and sentence meaning',items:[
      ['Find the subject','recall','In “The keys to the cabinet are missing”, what is the subject?','The keys.','The cabinet.','Identify the head of the subject phrase.'],
      ['Explain agreement','explain','Why is “are” appropriate in that sentence?','Keys is plural and controls the verb.','Cabinet is close to the verb.','Explain the subject–verb relationship.'],
      ['Recall the plural verb','recall','Complete: The keys ___ missing.','are','is','Recall the plural verb form.'],
      ['Separate modifier from subject','explain','What role does “to the cabinet” have?','It modifies keys; cabinet does not control the verb.','Cabinet becomes the subject.','Distinguish modifier and grammatical head.']
    ]},
    operations: {name:'Kubernetes operations — described actions',items:[
      ['Read scoped logs','describe_procedure','Describe how to read a named pod’s logs in namespace shop.','Use kubectl -n shop logs POD_NAME.','Use logs without identifying the pod or namespace.','Identify the pod and namespace.'],
      ['Check readiness','select','Does Running alone establish service readiness?','No; check readiness and relevant service behavior.','Yes, Running is enough.','Separate process phase from readiness.'],
      ['Inspect configured arguments','describe_procedure','Where would you check whether an invalid option came from deployment arguments?','Inspect the container command/args in the deployment.','Rebuild the image without checking configuration.','Inspect the relevant configuration before choosing repair.'],
      ['Verify useful work','select','What evidence would support that a report worker is functioning?','Check readiness and evidence of successfully processed reports.','Only that the new pod exists.','Select evidence of the intended behavior.']
    ]}
  };
  const cases = {
    progress:'Follow progress over time', missing:'A missing answer', maintenance:'Still able to do it',
    mix:'Questions got easier', cost:'Count all the time', correction:'Fix a grading mistake', help:'Hints and ungraded answers', early:'Too early to tell'
  };
  const snapshots={early:{S:20,T:'2026-10-04T12:00:00Z',name:'Oct 4 · before the next check'},original:{S:100,T:'2026-10-09T12:00:00Z',name:'Oct 9 · original report'},current:{S:150,T:'2026-10-09T12:00:00Z',name:'Oct 9 · updated report'},history:{S:300,T:'2026-10-23T12:00:00Z',name:'Oct 23 · all four check dates'}};
  const checkDates=[{key:'week1',date:'2026-10-08T12:00:00Z',label:'Oct 8',sequence:30},{key:'week2',date:'2026-10-15T12:00:00Z',label:'Oct 15',sequence:180},{key:'week3',date:'2026-10-22T12:00:00Z',label:'Oct 22',sequence:230}];
  const labels={S:'Correct without help',E:'Incorrect without help',H:'Answered with help',U:'Not graded yet',M:'No answer',N:'Not due yet',X:'Not checked'};
  const dataset=state=>['maintenance','correction','help'].includes(state.scenario)?state.scenario:'ordinary';
  const initial=()=>({curriculum:'search',mode:'all',scenario:'progress',snapshot:'history',check:'week3',highlight:'all',missingCase:'unknown',costScope:'full',unknownCost:false,mismatch:false});
  function move(state, action){
    const s={...state};
    if(action.type==='case'){Object.assign(s,{scenario:action.value,snapshot:action.value==='progress'?'history':action.value==='early'?'early':'original',check:action.value==='progress'?'week3':'week1',highlight:'all',missingCase:'unknown',costScope:'full',unknownCost:false,mismatch:false});}
    else if(action.type==='curriculum'){s.curriculum=action.value;s.mode='all';s.highlight='all';}
    else if(action.type==='snapshot'){s.snapshot=action.value;s.check=action.value==='history'?'week3':'week1';}
    else if(action.type==='reset')return initial();
    else s[action.type]=action.value;
    return s;
  }
  function records(state){
    const items=catalogs[state.curriculum].items, n=items.length;
    return items.map((item,i)=>{
      const [name,mode,prompt,correct,wrong,criterion]=item;
      const id=`${state.curriculum}.${i+1}`, key=`${dataset(state)}.${id}`, targetRef=`target:${id}@1`, before=(i<2||(state.scenario==='maintenance'&&i<n-3))?'S':'E';
      let outcome=i===n-1?'M':i>=n-3?'E':'S';
      // Four-target examples intentionally use 2 successes, 1 error and 1 missing.
      if(n===4)outcome=['S','S','E','M'][i];
      if(state.scenario==='maintenance'&&n===4&&i<2)outcome='S';
      if(state.scenario==='help'){if(i===1)outcome='H';if(i===2)outcome='U';}
      const checks=checkDates.map((date,j)=>{
        const result=j===0?outcome:(n===8?(j===1?['S','S','S','E','E','S','E','M']:['S','S','S','S','S','S','E','M']):(j===1?['S','E','E','M']:['S','S','S','M']))[i];
        const episode=result==='M'?null:`attempt:${dataset(state)}.${state.curriculum}.${date.key}.${n===8?Math.floor(i/2)+1:i+1}@1`;
        return {...date,sequence:date.sequence+i,ref:['M','U'].includes(result)?null:`assessment:${key}.${date.key}@1`,episode,submitted:result!=='M',outcome:result,answer:result==='M'?null:result==='E'?wrong:correct,help:result==='H'?'A hint about this skill was shown.':null,assessed:!['M','U'].includes(result)};
      });
      const baseline=[{ref:`assessment:${key}.baseline@1`,sequence:5+i,outcome:before,answer:before==='S'?correct:wrong,reason:criterion}];
      if(state.scenario==='correction'&&i===2){baseline[0].answer=correct;baseline[0].reason='Original assessor incorrectly marked this saved answer as an error.';baseline.push({ref:`assessment:${key}.baseline@2`,sequence:120,outcome:'S',answer:correct,reason:'The saved answer meets the stated criterion. Revise the judgment at its original time; no new attempt.',supersedes:baseline[0].ref});}
      return {id,targetRef,name,mode,prompt,correct,wrong,criterion,
        baseline,baselineAt:'2026-10-01T12:00:00Z',endpoint:`endpoint:${key}.${state.check}`,assignedAt:'2026-10-01T12:00:00Z',due:checks.find(c=>c.key===state.check).date,
        checks,later:checks.find(c=>c.key===state.check),
        exposure:'These examples do not establish what was studied between checks. A later correct answer does not prove uninterrupted retention.'};
    });
  }
  function totals(rows){
    const counts=Object.fromEntries(['S','E','H','U','M','N'].map(k=>[k,rows.filter(r=>r.outcome===k).length]));
    const P=rows.length-counts.N, judged=counts.S+counts.E, completed=P-counts.M;
    const transitions={improved:0,maintained:0,regressed:0,persistent:0,incomplete:0};
    rows.forEach(r=>{const k=r.before==='E'&&r.outcome==='S'?'improved':r.before==='S'&&r.outcome==='S'?'maintained':r.before==='S'&&r.outcome==='E'?'regressed':r.before==='E'&&r.outcome==='E'?'persistent':'incomplete';transitions[k]++;});
    return {counts,P,judged,completed,transitions,episodes:new Set(rows.map(r=>r.episode).filter(Boolean)).size,
      successFraction:judged?counts.S/judged:null,completion:P?completed/P:null,assessability:completed?(counts.S+counts.E+counts.H)/completed:null,
      bounds:P&&!counts.H&&!counts.U?[counts.S/P,(counts.S+counts.M)/P]:null};
  }
  function effort(state){
    const minutes=state.snapshot==='early'?[['Getting ready',6]]:[['Getting ready',6],['Answering',12],['Finding the problem',5],['Studying / practicing',8],['Reading feedback',4],['Reviewing progress / grades',2],['Waiting',3]];
    if(state.snapshot==='history'&&state.check!=='week1')minutes.push(['Oct 9–15: answering',8],['Oct 9–15: practice',10],['Oct 9–15: feedback',4]);
    if(state.snapshot==='history'&&state.check==='week3')minutes.push(['Oct 16–22: answering',8],['Oct 16–22: practice',6],['Oct 16–22: feedback',4]);
    let cursor=0;
    const spans=minutes.map(([category,duration],i)=>{const row={ref:`span:${dataset(state)}.${state.curriculum}.${i+1}@1`,category,startMinute:cursor,endMinute:cursor+duration,duration,quality:'authored foreground estimate'};cursor+=duration;return row;});
    return {spans,total:cursor,scope:'Time for the whole course through the selected check date. Filtering skills does not divide up shared work.',unplaced:null};
  }
  function comparison(state){
    const a=state.unknownCost?27:40,b=32,placed=state.costScope==='full';
    return {a:placed?a:12,b:placed?b:20,aFull:a,bFull:b,aAnswer:12,bAnswer:20,delta:placed?a-b:-8,
      meaning:state.unknownCost?'We cannot yet tell which took less total time. If more than five of A’s extra minutes were separate work, B took less.':placed?'B took eight fewer recorded minutes in this made-up example.':'A took eight fewer answering minutes, but this leaves out 28 other minutes for A and 12 for B.',
      outcomeComparison:state.mismatch?'The results cannot be compared fairly: A was checked seven days later, B only one day later.':'Both examples have 5 correct answers, 2 incorrect and 1 missing after seven days. Equal counts alone do not prove the methods work equally well.',
      adoption:'This example does not tell us which method to use. That needs a fair comparison of later learning results and all the time spent.'};
  }
  function view(state){
    const snap=snapshots[state.snapshot], all=records(state), excluded=[];
    const rows=all.filter(r=>{if(state.mode==='all'||r.mode===state.mode)return true;excluded.push({ref:r.targetRef,reason:`Mode ${r.mode} outside selected ${state.mode}`});return false;}).map(r=>{
      const effective=r.baseline.filter(a=>a.sequence<=snap.S).at(-1);
      const available=r.later.sequence<=snap.S, mature=r.due<=snap.T;
      const outcome=!mature?'N':!available||!r.later.submitted?'M':r.later.outcome;
      const {checks,...visible}=r;
      return {...visible,baseline:r.baseline.filter(a=>a.sequence<=snap.S),later:available?r.later:null,before:effective?.outcome||'X',baselineEffective:effective,outcome,episode:available?r.later.episode:null,laterVisible:available&&r.later.submitted};
    });
    const stats=totals(rows), cost=effort(state), comp=comparison(state);
    const scenarioFraction=stats.bounds&&stats.counts.M>0&&state.missingCase!=='unknown'?(stats.counts.S+(state.missingCase==='success'?stats.counts.M:0))/stats.P:null;
    const manifest={definition:'c-walkthrough-3',focusRule:'observed-review-order-1',fixture:`authored-c-fixture-2:${dataset(state)}:${state.curriculum}`,sourceThroughSequence:snap.S,evaluationAt:snap.T,
      curriculum:state.curriculum,mode:state.mode,scenario:state.scenario,selectedCheck:state.check,selectedCheckDate:checkDates.find(d=>d.key===state.check).date,selectedTargets:rows.map(r=>r.targetRef),excluded,
      baselineRefs:rows.map(r=>r.baselineEffective?.ref).filter(Boolean),endpointRefs:rows.map(r=>r.endpoint),
      assessmentRefs:rows.filter(r=>r.laterVisible&&r.later.assessed).map(r=>r.later.ref),submittedEpisodeRefs:[...new Set(rows.map(r=>r.episode).filter(Boolean))],
      costScope:'whole curriculum through selected check date',timeSpanRefs:cost.spans.map(r=>r.ref),
      units:{targets:rows.length,submittedEpisodes:stats.episodes,independentParticipants:1},
      limitations:['Authored data only','No population or causal inference','Fixture version is not a production snapshot fingerprint','Outside exposure not independently established'],
      inspection:{highlight:state.highlight,doesNotChangeTotals:true},whatIf:{missing:state.missingCase,changesRecordedGrades:false},comparison:{costScope:state.costScope,unplacedA:state.unknownCost,horizonMismatch:state.mismatch,scope:'separate authored method-comparison example'}};
    return {state:{...state},snapshot:snap,rows,stats,cost,comparison:comp,scenarioFraction,manifest};
  }
  function history(state){
    const current=view(state),snap=snapshots[state.snapshot];
    const first=current.rows.map(r=>({...r,outcome:r.before,episode:null}));
    const points=[{key:'baseline',date:'2026-10-01T12:00:00Z',label:'Oct 1',counts:totals(first).counts,evidence:first.map(r=>r.baselineEffective.ref)}];
    for(const date of checkDates){if(date.date>snap.T)continue;const v=view({...state,check:date.key});points.push({...date,counts:v.stats.counts,evidence:v.manifest.assessmentRefs});}
    return {targets:current.rows.length,points};
  }
  function focus(state){
    const current=view(state),selected=checkDates.find(d=>d.key===state.check),cutoff=selected.date<snapshots[state.snapshot].T?selected.date:snapshots[state.snapshot].T;
    const dates=checkDates.filter(d=>d.date<=cutoff).map(d=>({date:d,rows:view({...state,check:d.key}).rows}));
    const units=current.rows.map(r=>{
      const checks=[{date:r.baselineAt,label:'Oct 1',outcome:r.before,ref:r.baselineEffective?.ref,answer:r.baselineEffective?.answer}];
      for(const d of dates){const row=d.rows.find(x=>x.id===r.id);checks.push({date:d.date.date,label:d.date.label,outcome:row.outcome,ref:row.later?.ref,episode:row.episode,answer:row.laterVisible?row.later.answer:null});}
      const latest=checks.at(-1),errors=checks.filter(c=>c.outcome==='E');
      let streak=0;for(let i=checks.length-1;i>=0&&checks[i].outcome===latest.outcome;i--)streak++;
      return {id:r.id,targetRef:r.targetRef,name:r.name,mode:r.mode,checks,latest,errors,streak};
    });
    const needsCheck=units.filter(u=>!['S','E'].includes(u.latest.outcome)).map(u=>{
      const previous=u.checks.slice(0,-1).filter(c=>['S','E'].includes(c.outcome)).at(-1);
      return {...u,reason:`${labels[u.latest.outcome]} on ${u.latest.label}.${previous?` Last graded answer without help: ${previous.outcome==='S'?'correct':'incorrect'} on ${previous.label}.`:''}`,
        next:u.latest.outcome==='U'?'Finish or review the grading before drawing a conclusion.':'Try a fresh check without help before deciding what to practice.'};
    });
    const candidates=units.filter(u=>['S','E'].includes(u.latest.outcome)&&u.errors.length).map(u=>{
      const incorrect=u.latest.outcome==='E',lastError=u.errors.at(-1);
      return {...u,tier:incorrect?0:1,order:incorrect?-u.streak:u.streak,
        status:incorrect?(u.streak>1?'Repeated difficulty':'Mistake on latest check'):u.streak===1?'Just recovered':u.streak===2?'Improving':'Holding up recently',
        reason:incorrect?`Incorrect on ${u.latest.label}; ${u.streak===1?'one incorrect check in the current run':`incorrect at the last ${u.streak} checks`}.`:`Correct at the last ${u.streak} ${u.streak===1?'check':'checks'}; last incorrect on ${lastError.label}.`,
        next:incorrect?'Inspect the mistake, then try a fresh question or focused practice.':u.streak===1?'Try a fresh question to check that the recovery holds.':'Keep normal practice; recent success does not call for extra remedial work.'};
    }).sort((a,b)=>a.tier-b.tier||a.order-b.order||a.name.localeCompare(b.name));
    candidates.forEach((u,i)=>{const previous=candidates[i-1];u.rank=previous&&previous.tier===u.tier&&previous.order===u.order?previous.rank:i+1;u.tied=candidates.filter(v=>v.tier===u.tier&&v.order===u.order).length>1;});
    const flagged=candidates.slice(0,5),last=flagged.at(-1);
    return {rule:'observed-review-order-1',through:cutoff,flagged,needsCheck,
      tiedBeyondLimit:last?candidates.slice(5).filter(u=>u.rank===last.rank).map(u=>({id:u.id,name:u.name})):[],
      eligibleCount:candidates.length,selectedCount:units.length,
      allChecks:units.map(u=>({id:u.id,checks:u.checks})),limitations:['Example data, not personal mastery','Review order, not a calibrated mastery score','An incorrect answer does not by itself diagnose a knowledge gap']};
  }
  function savedReport(state){const v=view(state);return {manifest:v.manifest,recordedSummary:v.stats,records:v.rows,history:history(state),focus:focus(state),effort:v.cost,separateMethodComparison:v.comparison,missingOutcomeScenario:v.scenarioFraction};}
  const mix=()=>[
    {difficulty:'Easy',earlier:{s:8,n:10},later:{s:63,n:90}},
    {difficulty:'Hard',earlier:{s:18,n:90},later:{s:1,n:10}}
  ];
  return {catalogs,cases,snapshots,checkDates,labels,initial,move,records,totals,view,history,focus,savedReport,mix};
})();
