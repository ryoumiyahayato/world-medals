import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const html=fs.readFileSync(new URL('./index.html',import.meta.url),'utf8');
const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(x=>x[1]);
assert.equal(scripts.length,2);
const makeElement=()=>({hidden:false,value:'',textContent:'',src:'',children:[],listeners:{},
  addEventListener(name,fn){this.listeners[name]=fn},
  append(child){this.children.push(child)},
  set innerHTML(_value){this.children=[]},
  get innerHTML(){return ''}});
const nodes=Object.fromEntries(['search','searchResults','viewer','closeViewer','viewerTitle','viewerImage','queueName','queue-status','showAll'].map(x=>[x,makeElement()]));
nodes.viewer.showModal=()=>nodes.viewer.open=true;
nodes.viewer.close=()=>nodes.viewer.open=false;
const pending=makeElement();pending.dataset={queued:'巴伐利亚王国'};
const photo=makeElement();photo.alt='奖章完整正面';photo.src='assets/images/ottoman/PLEVNE-1.jpg';
const document={getElementById:id=>nodes[id],createElement:()=>makeElement(),
  querySelectorAll:selector=>selector==='a[data-queued]'?[pending]:selector==='td.pictures img'?[photo]:[]};
const context={window:{},document};vm.createContext(context);
for(const script of scripts)new vm.Script(script).runInContext(context);
for(const q of ['奥斯曼帝国','Mecidi','Osmaniye','1878','Prussia','Bavaria','Meiji','France','1870','荣','勋','奖','军','章','帝','国','法','星','十','日','王','金','银','法国荣誉军团','伊朗','埃及','苏丹','亚美尼亚','英国','维多利亚十字','俄罗斯帝国','苏联','俄罗斯联邦','西班牙','战争十字章','美国','紫心勋章']){
  nodes.search.value=q;nodes.search.listeners.input();
  assert(nodes.searchResults.children.length>0,`no search results for ${q}`);
  assert(nodes.searchResults.children.some(x=>x.href),`no clickable result for ${q}`);
}
for(const [q,target] of [['Meiji','japan'],['Prussia','prussia-kingdom'],['France','france-third-republic'],['伊朗','iran'],['埃及','egypt'],['苏丹','sudan'],['亚美尼亚','armenia'],['英国','uk'],['俄罗斯帝国','russian-empire'],['苏联','soviet-union'],['俄罗斯联邦','russian-federation'],['西班牙','spain-kingdom'],['美国','united-states']]){
  nodes.search.value=q;nodes.search.listeners.input();
  assert(nodes.searchResults.children.some(x=>x.href==='#'+target),`no live volume result for ${q}`);
}
nodes.searchResults.children.find(x=>x.href).listeners.click();
assert.equal(nodes.search.value,'');assert.equal(nodes.searchResults.hidden,true);
pending.listeners.click();assert.equal(nodes['queue-status'].hidden,false);
assert.equal(nodes.queueName.textContent,'巴伐利亚王国');
photo.listeners.click();assert.equal(nodes.viewer.open,true);
assert.equal(nodes.viewerImage.src,photo.src);
nodes.closeViewer.onclick();assert.equal(nodes.viewer.open,false);
console.log('PASS: country-scoped searches, arbitrary single-character Chinese queries, live volume links, queued navigation and image preview handlers');
