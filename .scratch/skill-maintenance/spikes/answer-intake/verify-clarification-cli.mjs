// Exercise the real CLI using temporary, explicitly constructed assessment files.
import {readFileSync,writeFileSync,mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const here=new URL('./',import.meta.url),read=n=>JSON.parse(readFileSync(new URL(n,here),'utf8'));
const input=read('inputs.json').inputs.find(i=>i.case_id==='S-later-log-error');
const assessment=read('judgments.json').records.find(a=>a.case_id===input.case_id);
const scratch=mkdtempSync(join(tmpdir(),'mem-graph-clarification-')),checks=[];
const check=(name,met)=>checks.push({name,met:Boolean(met)});
const cli=(...args)=>spawnSync(process.execPath,[fileURLToPath(new URL('replay.mjs',here)),...args],{encoding:'utf8'});
try{
 const packetPath=join(scratch,'input.json'),judgmentPath=join(scratch,'judgment.json');
 writeFileSync(packetPath,JSON.stringify(input));
 const packetRun=cli('packet',packetPath);if(packetRun.status!==0)throw Error(packetRun.stderr);
 const packet=JSON.parse(packetRun.stdout),save=a=>writeFileSync(judgmentPath,JSON.stringify({input_sha256:packet.input_sha256,prompt_sha256:packet.prompt_sha256,assessor:'Authored CLI regression fixture; no new learner or model judgment.',records:[a]}));
 save(assessment);
 const clearRun=cli('connect',packetPath,judgmentPath);if(clearRun.status!==0)throw Error(clearRun.stderr);
 const clear=JSON.parse(clearRun.stdout);
 check('CLI still offers help only for the explicit log-command error',clear.plan.now.length===1&&clear.plan.now[0].kind==='help'&&clear.plan.now[0].targets.join()==='ops.logs');
 const clarify=JSON.parse(JSON.stringify(assessment));clarify.next={kind:'follow_up',targets:['ops.logs'],text:'Is that the command you intend, or a transcription mistake?',reason:'Authored counterfactual: the answer can change the practice decision.',branches:{correct:'Keep the corrected form and stop immediate practice.',wrong:'Offer focused log-command help.',unclear:'Pause with unresolved assessment.'}};
 save(clarify);
 const questionRun=cli('connect',packetPath,judgmentPath);if(questionRun.status!==0)throw Error(questionRun.stderr);
 const question=JSON.parse(questionRun.stdout);
 check('CLI selects the targeted follow-up without corrective help',question.plan.now.length===1&&question.plan.now[0].kind==='follow_up'&&question.plan.now[0].targets.join()==='ops.logs');
 check('CLI retains the original error and the pending log check',question.event.observations.some(o=>o.target==='ops.logs'&&o.result==='error')&&question.plan.later[0].targets.join()==='ops.logs');
 input.response+=' Changed after assessment.';writeFileSync(packetPath,JSON.stringify(input));
 check('Changed answer bytes still reject reuse of the assessment',cli('connect',packetPath,judgmentPath).status!==0);
 const historical=new URL('../independent-assessment/comparison.json',here),before=readFileSync(historical,'utf8');
 const historicalRun=spawnSync(process.execPath,[fileURLToPath(new URL('../independent-assessment/compare.mjs',here))],{encoding:'utf8'});
 check('Historical comparison refuses changed dependencies without overwriting audited results',historicalRun.status!==0&&historicalRun.stderr.includes('Historical comparison dependencies changed')&&readFileSync(historical,'utf8')===before);
}finally{rmSync(scratch,{recursive:true,force:true});}
writeFileSync(new URL('clarification-cli-results.json',here),JSON.stringify({scope:'Real CLI with authored fixtures, plus protection of the historical comparison. No saved learner-state changes.',checks},null,2)+'\n');
console.table(checks);if(checks.some(c=>!c.met))process.exitCode=1;
