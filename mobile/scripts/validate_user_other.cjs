const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..'),site=path.join(root,'mobile/build/site'),ctx={window:{}};
vm.runInNewContext(fs.readFileSync(path.join(site,'catalog.js'),'utf8'),ctx);
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const rows=read('data/volumes/user_other_20261003.json').records;
const integration=read('data/volumes/user_other_20261003_integration.json').volume_rows;
const review=read('data/staging/user_other_20261003/review.json').items;
const byId=new Map(ctx.window.CATALOG.rows.map(r=>[r.id,r]));let images=0;
for(const r of rows){
 const exported=byId.get(r.id);assert(exported,'Missing export: '+r.id);
 assert.equal(exported.family,r.family);assert.equal(exported.photos.length,r.views.length);
 assert(exported.variant.includes('参考'));
 assert(integration[exported.volume].includes(r.id));
 for(const p of exported.photos){assert(fs.existsSync(path.join(site,p.src)));assert(p.caption.includes('参考'));images++;}
}
assert.equal(review.length,28);assert.equal(new Set(review.map(a=>a.number)).size,28);
assert.equal(images,18);assert.equal(rows.length,17);
for(const a of review.filter(a=>a.status==='held_for_verification'))assert(!rows.some(r=>r.id===a.record_id));
assert(fs.readFileSync(path.join(site,'index.html'),'utf8').includes('<title>WODM-world medals</title>'));
assert(fs.readFileSync(path.join(root,'mobile/android/AndroidManifest.xml'),'utf8').includes('android:label="WODM-world medals"'));
console.log(JSON.stringify({referenceRows:rows.length,referenceImages:images,reviewed:review.length,held:review.filter(a=>a.status==='held_for_verification').length,appName:'WODM-world medals'}));
