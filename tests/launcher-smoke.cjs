#!/usr/bin/env node
'use strict';
const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const html=fs.readFileSync(process.argv[2]||'build/amd64/config/includes.chroot/usr/share/safeexamos/launcher/index.html','utf8');
const match=html.match(/<script>([\s\S]*?)<\/script>/i);
assert.ok(match,'launcher inline controller missing');
assert.match(html,/id="keyboard-typing-feedback"/);
assert.match(html,/id="typing-test"/);

const base={
  collectorStatus:'ok',generatedAt:'2026-11-13T00:00:00Z',
  cpu:'Virtual CPU',memoryMiB:2048,gpu:'Virtio VGA',
  architecture:'x86_64',kernel:'6.x',
  network:{state:'online',managerState:'connected',interfaces:'lo,eth0',wifiInterfaces:'none'},
  keyboard:{layout:'us'},inputDevices:2,
  displays:{count:1,outputs:'Virtual-1'},bootMode:'BIOS',ephemeral:'yes'
};
function state(overrides){return structuredClone({...base,...overrides});}
function boot(data,nextData){
  const els=new Map(),timers=[],alerts=[];
  function get(id){
    if(!els.has(id)){
      els.set(id,{value:'',textContent:'',className:'',handlers:{},
        addEventListener(type,fn){this.handlers[type]=fn;},
        focus(){this.focused=true;}});
    }
    return els.get(id);
  }
  const ctx={
    window:{SAFEEXAMOS_PREFLIGHT:data,location:{assign(target){alerts.push('NAV:'+target);}}},
    alert(s){alerts.push(s);},
    document:{
      getElementById:get,
      createElement(type){assert.equal(type,'script');return {src:'',onload:null,onerror:null};},
      head:{appendChild(script){
        assert.match(script.src,/^preflight\.js\?check=/);
        if(nextData)ctx.window.SAFEEXAMOS_PREFLIGHT=nextData;
        script.onload?.();
      }}
    },
    setTimeout(fn){timers.push(fn);}
  };
  vm.runInNewContext(match[1],ctx,{timeout:1000,filename:'launcher.js'});
  return {get,timers,alerts};
}

const ok=boot(state({}));
assert.equal(ok.get('compat-status').textContent,'Supported');
assert.equal(ok.get('overall-status').textContent,'System ready');
assert.ok(ok.get('typing-test').focused);
ok.get('typing-test').value='a';
ok.get('typing-test').handlers.input();
assert.equal(ok.get('keyboard-typing-feedback').textContent,'Keyboard input detected');
assert.match(ok.get('keyboard-detail').textContent,/Input detected/);
ok.get('code').value='TEST';
ok.get('continue').handlers.click();
assert.match(ok.alerts[0],/enter DEMO/);
ok.get('code').value='demo';
ok.get('continue').handlers.click();
assert.equal(ok.alerts[1],'NAV:demo.html');

const blocked=boot(state({collectorStatus:'degraded',memoryMiB:0,inputDevices:0}));
assert.equal(blocked.get('compat-status').textContent,'Blocking');
assert.match(blocked.get('compat-detail').textContent,/pre-flight inventory incomplete/);
blocked.get('code').value='DEMO';
blocked.get('continue').handlers.click();
assert.match(blocked.alerts[0],/not completed|incomplete/i);

const warning=boot(state({network:{state:'offline',managerState:'disconnected',interfaces:'lo',wifiInterfaces:'none'}}));
assert.equal(warning.get('compat-status').textContent,'Warning');

const async=boot(state({collectorStatus:'degraded'}),state({}));
assert.equal(async.get('compat-status').textContent,'Blocking');
assert.ok(async.timers.length>0,'missing preflight refresh timer');
async.timers.shift()();
assert.equal(async.get('compat-status').textContent,'Supported');

// Even after the first successful inventory, a lost route must become visible.
const changed=boot(state({}),state({network:{
  state:'offline',managerState:'connecting',interfaces:'lo,ens33',wifiInterfaces:'none'
}}));
assert.equal(changed.get('compat-status').textContent,'Supported');
changed.timers.shift()();
assert.equal(changed.get('compat-status').textContent,'Warning');
assert.match(changed.get('network-detail').textContent,/Connecting \(DHCP\)/);
assert.ok(changed.timers.length>0,'network refresh stopped after successful preflight');
assert.match(html,/focus\(\{preventScroll:true\}\)/);
assert.doesNotMatch(html,/id="typing-test"[^>]*autofocus/);


console.log('Launcher fixtures PASS: ready, warning, blocking, keyboard, exam-code guard, refresh');
