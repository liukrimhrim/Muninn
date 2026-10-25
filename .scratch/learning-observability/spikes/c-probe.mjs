// Reproduce authored calculations. This is not a browser, storage or learner test.
import {writeFileSync} from 'node:fs';
import {CModel as m} from './c-model.mjs';
const base=m.initial();
const firstWeek={...base,snapshot:'original',check:'week1'};
function summarize(state){
  const v=m.view(state);
  return {counts:v.stats.counts,transitions:v.stats.transitions,
    conditional:v.stats.successFraction,completion:v.stats.completion,
    assessability:v.stats.assessability,missingBounds:v.stats.bounds,
    episodeCount:v.stats.episodes,minutes:v.cost.total,
    selected:v.manifest.selectedTargets.length,excluded:v.manifest.excluded.length,
    scenarioFraction:v.scenarioFraction};
}
const report={
  kind:'authored-model-calculation-probe; not browser or learner verification',
  cases:Object.fromEntries(Object.keys(m.cases).map(k=>[k,summarize(m.move(base,{type:'case',value:k}))])),
  firstWeek:summarize(firstWeek),
  filtered:summarize({...firstWeek,mode:'explain'}),
  whatIf:summarize({...firstWeek,missingCase:'success'}),
  highlightLeavesStatisticsUnchanged:JSON.stringify(m.view(base).stats)===JSON.stringify(m.view({...base,highlight:'S'}).stats),
  costScopes:['full','answer'].map(costScope=>m.view({...base,costScope}).comparison),
  unplacedCost:m.view({...base,unknownCost:true}).comparison,
  mismatchedHorizon:m.view({...base,mismatch:true}).comparison,
  otherCurricula:['grammar','operations'].map(curriculum=>({curriculum,...summarize({...base,curriculum})}))
};
const original=structuredClone(m.savedReport({...firstWeek,scenario:'correction',snapshot:'original'}));
const originalBytes=JSON.stringify(original);
const corrected=m.savedReport({...firstWeek,scenario:'correction',snapshot:'current'});
report.correction={before:original.recordedSummary.transitions,after:corrected.recordedSummary.transitions,
  oldUnchanged:originalBytes===JSON.stringify(original),
  originalHasFutureRevisions:original.records.some(r=>r.baseline.some(a=>a.sequence>100))};
const early=m.savedReport({...firstWeek,snapshot:'early'});
report.earlyContainsFutureEvidence=early.records.some(r=>r.later||r.baseline.some(a=>a.sequence>20));
report.trend={full:m.history(base),filtered:m.history({...base,mode:'explain'}),early:m.history({...firstWeek,snapshot:'early'}),original:m.history(firstWeek),
  dateSelections:m.checkDates.map(d=>({date:d.label,...summarize(m.move(base,{type:'check',value:d.key}))})),
  savedOriginalDates:original.history.points.map(p=>p.label),savedOriginalCorrectCounts:original.history.points.map(p=>p.counts.S),
  correctedCorrectCounts:corrected.history.points.map(p=>p.counts.S)};
function focusSummary(state){const f=m.focus(state);return {through:f.through,flagged:f.flagged.map(u=>({id:u.id,name:u.name,rank:u.rank,tied:u.tied,status:u.status,reason:u.reason,dates:u.checks.map(c=>c.label)})),needsCheck:f.needsCheck.map(u=>({id:u.id,reason:u.reason})),tiedBeyondLimit:f.tiedBeyondLimit};}
report.weakUnits={latest:focusSummary(base),selectedFirstWeek:focusSummary({...base,check:'week1'}),
  corrected:focusSummary({...firstWeek,scenario:'correction',snapshot:'current'}),
  helped:focusSummary(m.move(base,{type:'case',value:'help'})),
  early:focusSummary(m.move(base,{type:'case',value:'early'})),
  filtered:focusSummary({...base,mode:'select'}),
  unaffectedByWhatIf:JSON.stringify(m.focus(base))===JSON.stringify(m.focus({...base,missingCase:'success'})),
  unaffectedByHighlight:JSON.stringify(m.focus(base))===JSON.stringify(m.focus({...base,highlight:'S'}))};
writeFileSync(new URL('./c-calculation-results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log('Calculated eight authored cases, population/highlight behavior, corrections, cost scopes and two additional curricula. Saved c-calculation-results.json.');
