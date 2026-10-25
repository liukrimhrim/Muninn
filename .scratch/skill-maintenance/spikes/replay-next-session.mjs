// Bounded design experiment using the exact model and records in the HTML.
// Authored expectations check policy behavior, not grading or learning efficacy.
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import vm from 'node:vm';
const here=new URL('./',import.meta.url),html=readFileSync(new URL('next-session.html',here),'utf8');
const source=html.match(/<script id="next-session-model">([\s\S]*?)<\/script>/)[1];
const data=JSON.parse(html.match(/<script id="records" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const M=vm.runInNewContext(source+'\nNextSession'),checks=[];
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const check=(name,condition)=>checks.push({name,met:Boolean(condition)});
const keys=xs=>[...xs].sort();
const actual=M.recorded(data),before=JSON.stringify(actual),plan=M.plan(data,actual);
const sourceBindings=data.events.map(event=>{
 const contents=readFileSync(new URL(event.source,here),'utf8');
 return {id:event.id,source:event.source,source_sha256:createHash('sha256').update(contents).digest('hex'),quote_found:contents.includes(event.quote)};
});
check('Every real excerpt exists in its linked transcript',sourceBindings.every(r=>r.quote_found));
check('Real record requests no immediate remediation',plan.now.length===0);
check('The three approved later targets share exactly one exercise',plan.later.length===1&&same(keys(plan.later[0].targets),['ops.list','ops.logs','ops.source']));
check('Accepted misread does not add binary-search remediation',!plan.later.some(g=>g.targets.some(t=>t.startsWith('binary.')))&&plan.perTarget['binary.comparison'].includes('accepted misread'));
const cases=['success','command_error','source_unclear','source_hint','partial','outcome_only'].map(kind=>{
 const state=M.append(actual,M.hypothetical(kind));
 return {kind,state,plan:M.plan(data,state)};
});
const get=kind=>cases.find(c=>c.kind===kind);
check('A later unhinted demonstration stops separate drills',get('success').plan.now.length===0&&get('success').plan.later.length===0);
check('A log error focuses help only on that target',same(get('command_error').plan.now.map(a=>[a.kind,a.targets]),[['help',['ops.logs']]]));
check('Successful targets are not kept in the repair exercise',same(get('command_error').plan.later.map(a=>a.targets),[['ops.logs']]));
check('Unclear source evidence asks for clarification, not a failure label',same(get('source_unclear').plan.now.map(a=>[a.kind,a.targets]),[['clarify',['ops.source']]]));
check('A hinted success remains eligible for an unhinted check',same(get('source_hint').plan.later.map(a=>a.targets),[['ops.source']])&&M.status(get('source_hint').state,'ops.source').last.assisted);
check('Unobserved source evidence is not inferred from correct commands',same(get('partial').plan.later.map(a=>a.targets),[['ops.source']])&&M.status(get('partial').state,'ops.source').last.event.id==='L02-source-hinted');
check('Whole-task failure does not assign target errors',same(get('outcome_only').plan.now.map(a=>[a.kind,a.targets]),[['clarify',[]]])&&data.targets.every(t=>M.status(get('outcome_only').state,t.id).last?.result!=='error'));
check('Duplicate delivery adds no record or practice choice',same(M.append(actual,actual.events.at(-1)),actual));
check('A later observation preserves earlier assistance',M.evidence(get('success').state,'ops.source').some(o=>o.assisted)&&M.evidence(get('success').state,'ops.source').length===3);
check('The corrected comparison does not add another halving explanation',M.evidence(actual,'binary.halving').length===1&&M.evidence(actual,'binary.comparison').length===1);
const contradiction=M.append(actual,{id:'hypothetical-binary-error',attempt:'imagined-math-check',origin:'hypothetical',phase:'later',observations:[{target:'binary.halving',result:'error',issue:'accepted_misread',assisted:true,help:'Invented explicit error; an old misread must not excuse it.'}]});
check('Explicit contradictory knowledge evidence is not excused as a misread',same(M.plan(data,contradiction).now.map(a=>a.targets),[['binary.halving']])&&M.status(contradiction,'binary.halving').label==='Observed error');
check('One rule path handles a relationship error outside Kubernetes',M.plan(data,contradiction).now[0].kind==='help');
check('Planning and hypothetical transitions leave the real history unchanged',JSON.stringify(actual)===before&&actual.events.every(e=>e.origin==='recorded'));
check('Empty history makes no learner claim',M.plan(data,M.empty()).now.length===0&&M.plan(data,M.empty()).later.length===0);
// Syntax and portable DOM wiring smoke: execute the actual page script with a tiny
// element surface, then invoke its real button handlers. This does NOT render a browser.
class Element {
 constructor(tag){this.tagName=tag;this.children=[];this.disabled=false;this.attributes={};this.textContent='';}
 append(...children){this.children.push(...children);}
 replaceChildren(...children){this.children=[...children];}
 setAttribute(key,value){this.attributes[key]=value;}
}
const elements=new Map([...html.matchAll(/\bid="([^"]+)"/g)].map(m=>[m[1],new Element('element')]));
elements.get('records').textContent=JSON.stringify(data);
const document={getElementById:id=>elements.get(id),createElement:tag=>new Element(tag)};
const ui=html.match(/<script>\s*([\s\S]*?)<\/script>/)[1],context=vm.createContext({document});
vm.runInContext(source+'\n'+ui,context);
check('Page initializes a row for every target',elements.get('rows').children.length===data.targets.length);
elements.get('actions').children[0].onclick();
check('Real later-success button visibly labels hypothetical mode',elements.get('mode').textContent.startsWith('Includes hypothetical')&&elements.get('plan').children.length===1);
elements.get('reset').onclick();
check('Real reset button restores the recorded mode',elements.get('mode').textContent.startsWith('Recorded chat history only'));
elements.get('tabs').children[0].onclick();
elements.get('steps').children[0].onclick();
check('Guided walkthrough button appends its recorded response',elements.get('counts').textContent.startsWith('1 recorded response'));
const report={scope:'Deterministic replay of supplied chat assessments plus explicitly invented future outcomes. Not automatic grading, independent assessment, retention measurement, or a browser rendering check.',model_sha256:createHash('sha256').update(source).digest('hex'),sourceBindings,actualPlan:plan,realResponseExcerpts:data.events.length,checks,variants:cases.map(({kind,plan})=>({kind,plan})),limitations:['Only selected excerpts and observations from the recorded conversations are represented.','The reviewed policy is a hand-authored example; it does not discover a knowledge graph or optimize exercise coverage.','The later outcomes are hypothetical; no time interval or learning gain was measured.','UI script and button handlers ran against a minimal DOM surface; actual browser layout and interaction are unverified.']};
writeFileSync(new URL('next-session-replay-results.json',here),JSON.stringify(report,null,2)+'\n');
console.table(checks);
console.log(`${checks.filter(c=>c.met).length}/${checks.length} replay observations matched. One actual-plan combined exercise covers: ${plan.later[0].targets.join(', ')}.`);
if(checks.some(c=>!c.met))process.exitCode=1;
