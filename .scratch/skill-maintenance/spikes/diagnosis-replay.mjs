// Experiment driver: replay the exact model and walkthroughs in the HTML.
// This verifies authored policy behavior, not diagnosis accuracy or learning gains.
import {readFileSync,writeFileSync} from 'node:fs';
import vm from 'node:vm';
const html=readFileSync(new URL('./diagnosis-prototype.html',import.meta.url),'utf8');
const source=html.match(/<script id="diagnosis-model">([\s\S]*?)<\/script>/)[1];
const M=vm.runInNewContext(source+'\nDiagnosisPrototype');
const results=[];
for(const subject of Object.keys(M.topics)){
 for(const walk of M.walks){
  let s=M.fresh(subject);const trace=[];
  for(const step of walk.steps){
   const before=M.choose(s);
   if(!before.criteria&&!step.type){trace.push({unexpectedStop:before.reason});break;}
   s=M.apply(s,M.exampleEvent(s,step));
   const after=M.choose(s);
   trace.push({action:step.label,kind:before.kind,target:before.target,next:after.kind,nextTarget:after.target,unresolved:M.unresolved(s),reason:after.reason});
  }
  results.push({subject,case:walk.name,attempts:s.history.length,probes:s.probes,seconds:s.spent,final:M.choose(s).kind,settled:s.settled,trace});
 }
}
// Additional free-play observations, outside the guided paths.
let s=M.fresh('binary',60);
const shortBudget={before:M.choose(s),after:M.choose(M.apply(s,{type:'settings',budget:720,limit:3}))};
s=M.fresh();s=M.apply(s,{results:{},outcome:'fail'});
const noAttribution={storedEvidence:Object.keys(s.latest),next:M.choose(s)};
const unchanged=JSON.stringify(s);const next=M.apply(s,{results:{0:'pass'},outcome:'pass'});
const purity={inputUnchanged:JSON.stringify(s)===unchanged,afterTarget:M.choose(next).target};
let contradiction=M.fresh();contradiction=M.apply(contradiction,{results:{0:'pass',1:'pass',2:'pass',3:'pass',4:'pass',5:'pass'},outcome:'fail'});
let assisted=M.fresh();assisted=M.apply(assisted,{results:{0:'pass',1:'pass',2:'pass',3:'pass',4:'pass',5:'pass'},outcome:'pass',assisted:true});
let unobservedIntegration=M.fresh();unobservedIntegration=M.apply(unobservedIntegration,{results:{0:'pass',1:'pass',2:'pass',3:'pass',4:'pass'},outcome:'pass'});
const checks={shortBudget,noAttribution,purity,contradictoryGrade:M.choose(contradiction),assisted:{settled:assisted.settled,next:M.choose(assisted)},unobservedIntegration:M.choose(unobservedIntegration)};
const report={scope:'Synthetic authored walkthroughs using the exact HTML model. No automated natural-language assessment, real learner, retention effect, or browser interaction is simulated.',results,checks};
writeFileSync(new URL('./diagnosis-replay-results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.table(results.map(r=>({topic:r.subject,case:r.case,attempts:r.attempts,probes:r.probes,seconds:r.seconds,next:r.final,settled:r.settled,unexpectedStop:r.trace.some(t=>t.unexpectedStop)})));
console.log('Additional observations:',JSON.stringify({shortBudget:shortBudget.before.kind,budgetRestored:shortBudget.after.kind,noAttributedEvidence:noAttribution.storedEvidence.length,firstProbe:noAttribution.next.target,purity,contradictoryGrade:checks.contradictoryGrade.kind,assistedSettled:assisted.settled,assistedNext:checks.assisted.next.kind,unobservedIntegration:checks.unobservedIntegration.kind},null,2));
