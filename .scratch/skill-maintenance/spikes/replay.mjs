// Synthetic experiment: replay the exact pure model embedded in the standalone demo.
// This produces observations, not a learning-efficacy benchmark or a production test suite.
import {readFileSync,writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import vm from 'node:vm';
const html=readFileSync(new URL('./evidence-policy.html',import.meta.url),'utf8');
const source=html.match(/<script id="model">([\s\S]*?)<\/script>/)[1];
const M=vm.runInNewContext(source+'\nEvidenceSpike');
const cases=[
 ['Recognition only',['recognition']],
 ['Successful final state without trace',['outcome']],
 ['Hinted lab',['guided']],
 ['Independent observed scenario',['observed']],
 ['Ambiguous failure',['ambiguous']],
 ['Failure then narrow diagnosis',['ambiguous','miss']],
 ['Duplicate observed scenario',['observed','duplicate']],
 ['Observed scenario then eight-day delay',['observed','advance']]
];
const results=cases.map(([name,actions])=>{
 let s=M.fresh();let n=0;
 for(const action of actions)s=action==='advance'?M.apply(s,{kind:'advance'}):action==='duplicate'?M.apply(s,s.attempts.at(-1)):M.apply(s,M.attempt(action,`a${++n}`,s.day));
 const unsupported=M.slots.filter(k=>M.status(s.naive[k.id],s.day)==='Observed pass'&&M.status(s.direct[k.id],s.day)!=='Observed pass').map(k=>k.id);
 const unsupportedBlame=M.slots.filter(k=>M.status(s.naive[k.id],s.day)==='Needs practice'&&M.status(s.direct[k.id],s.day)!=='Needs practice').map(k=>k.id);
 return {name,actions,uniqueAttempts:s.attempts.length,practiceSeconds:s.seconds,naiveUnsupportedPasses:unsupported,naiveUnsupportedFailures:unsupportedBlame,directStatuses:Object.fromEntries(M.slots.map(k=>[k.id,M.status(s.direct[k.id],s.day)])),oneMinute:M.choose(s,60),tenMinutes:M.choose(s,600)};
});
const report={scope:'Authored synthetic traces; unsupported means not established by the supplied rubric observations. No hidden true ability or learning effect is simulated. The topology-only comparator intentionally ignores evidence boundaries and does not reproduce a named product.',freshnessDays:7,results};
const output=fileURLToPath(new URL('./replay-results.json',import.meta.url));
writeFileSync(output,JSON.stringify(report,null,2)+'\n');
console.table(results.map(r=>({case:r.name,attempts:r.uniqueAttempts,seconds:r.practiceSeconds,unsupportedPasses:r.naiveUnsupportedPasses.length,unsupportedFailures:r.naiveUnsupportedFailures.length,unmetAtOneMinute:r.oneMinute.unmet.length})));
console.log(`Saved ${output}`);
