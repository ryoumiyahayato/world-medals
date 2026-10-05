const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..'),site=path.join(root,'mobile/build/site'),context={window:{}};
for(const file of ['catalog.js','award-intros.js','hierarchy.js'])vm.runInNewContext(fs.readFileSync(path.join(site,file),'utf8'),context);
const data=context.window.CATALOG,intros=context.window.AWARD_INTROS;
const expected=JSON.parse(fs.readFileSync(path.join(root,'data/volumes/german_completion_20260929.json'),'utf8')).records;
const search=require('../web/search.js'),book=require('../web/encyclopedia.js');
const added=expected.map(e=>{const r=data.rows.find(r=>r.id===e.id);assert(r,'Missing exported '+e.id);assert.equal(r.family,e.family);return r;});
for(const r of added){
 assert(intros.some(i=>i.families.includes(r.family)&&new RegExp(i.volumePattern).test(r.volume)),'No encyclopedia introduction '+r.id);
 assert(context.window.CATEGORY_ROUTES[r.volume.replace(/-unpictured$/,'')],'No country route '+r.volume);
 for(const p of r.photos)assert(fs.existsSync(path.join(site,p.src)),'Missing local image '+p.src);
 const volume=data.volumes.find(v=>v.id===r.volume);assert(search.score(r.name,search.prepare(r,volume.title))>0,'Cannot search '+r.id);
}
const bvo=added.filter(r=>r.family==='GER-FED-BUNDESVERDIENSTORDEN');
assert.equal(bvo.length,19,'BVO common-photo duplicate should be removed');
assert.equal(book.groups(bvo,data.rows).length,1,'BVO variants split into different families');
assert(!added.some(r=>r.id.includes('VETERANENABZEICHEN')),'Veteran identification badge entered formal rewards');
console.log(JSON.stringify({addedRows:added.length,picturedRows:added.filter(r=>r.photos.length).length,families:new Set(added.map(r=>r.family)).size,allIntros:true,localPhotos:true,bvoGroupedVariants:bvo.length}));
