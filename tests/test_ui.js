// Small DOM contract test; not a real browser/rendering test.
const vm=require('node:vm'), fs=require('node:fs'), assert=require('node:assert/strict');
class Element {constructor(){this.content='token';this.textContent='';this.disabled=false;this.hidden=false;this.children=[]}replaceChildren(...items){this.children=items;this.textContent=''}append(...items){this.children.push(...items)}click(){}}
const elements=new Map();const get=k=>{if(!elements.has(k))elements.set(k,new Element());return elements.get(k)};
const pending=[];const ok=data=>({ok:true,json:async()=>data});
const context={document:{querySelector:get,querySelectorAll:()=>[],createElement:()=>new Element(),createTextNode:t=>t},fetch:async(path,opts)=>{
 if(path.endsWith('health'))return ok({engine_ready:false});
 if(opts?.method==='DELETE')return ok({deleted:true});
 return new Promise(resolve=>pending.push({path,resolve}));
},URL,Date,setTimeout,clearTimeout,console};
vm.createContext(context);vm.runInContext(fs.readFileSync('app/static/app.js','utf8')+'\nthis.setJob=id=>{job=id}; this.runPoll=poll;',context);
(async()=>{
 context.setJob('old');const summary=get('#summary').onclick();
 await new Promise(r=>setImmediate(r));assert.equal(pending.length,1);
 await get('#delete').onclick();context.setJob('new');get('#summary-result').textContent='NEW JOB';get('#summary').disabled=true;
 pending.shift().resolve(ok({bullets:[{text:'OLD PRIVATE TEXT',segment_ids:[1]}],warning:'old'}));await summary;
 assert.equal(get('#summary-result').textContent,'NEW JOB');assert.equal(get('#summary').disabled,true);
 context.setJob('poll-old');const poll=context.runPoll();await new Promise(r=>setImmediate(r));
 await get('#delete').onclick();context.setJob('poll-new');get('#status').textContent='NEW STATUS';
 pending.shift().resolve(ok({status:'failed',error:'OLD ERROR'}));await poll;
 assert.equal(get('#status').textContent,'NEW STATUS');
 console.log('PASS: stale summary and stale poll cannot overwrite another job (DOM stub, not browser).');
})().catch(e=>{console.error(e);process.exitCode=1});
