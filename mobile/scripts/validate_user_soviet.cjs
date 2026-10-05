const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..'),site=path.join(root,'mobile/build/site'),context={window:{}};
for(const f of ['catalog.js','award-intros.js','hierarchy.js'])vm.runInNewContext(fs.readFileSync(path.join(site,f),'utf8'),context);
const data=context.window.CATALOG,records=JSON.parse(fs.readFileSync(path.join(root,'data/volumes/user_soviet_20261003.json'),'utf8')).records;
const review=JSON.parse(fs.readFileSync(path.join(root,'data/staging/user_soviet_20261003/review.json'),'utf8'));
const byId=new Map(data.rows.map(x=>[x.id,x]));let images=0;
for(const r of records){
 const x=byId.get(r.id);assert(x,'Missing export '+r.id);assert.equal(x.family,r.family);assert.equal(x.photos.length,r.views.length);
 assert(x.variant.includes('参考'));assert.equal(x.volume,r.family.startsWith('RSFSR-')?'rsfsr-awards':'soviet-union');
 for(const p of x.photos){assert(fs.existsSync(path.join(site,p.src)));assert(p.caption.includes('参考'));images++;}
 if(x.photos.length>1)assert(x.photos[1].caption.includes('未经证实为同一实物'));
}
for(const a of context.window.AWARD_INTROS)for(const v of a.variants||[]){if(v.referenceRecord){const r=byId.get(v.referenceRecord);assert(r,'Broken timeline reference');assert(a.families.includes(r.family),'Wrong timeline family');assert(r.photos.length);}}
assert.equal(review.items.length,266);assert.equal(new Set(review.items.map(x=>x.number)).size,266);
for(const n of [212,213,227,228,140,155])assert.equal(review.items.find(x=>x.number===n).status,'held_for_verification');
const honour=records.find(x=>x.family==='USSR-ORD-15'&&x.variant.includes('1988'));assert(honour&&byId.has(honour.id));
console.log(JSON.stringify({referenceRows:records.length,referenceImages:images,inventoryReviewed:review.items.length,foreignAndUnresolvedExcluded:true,timelineReferencesValid:true}));
