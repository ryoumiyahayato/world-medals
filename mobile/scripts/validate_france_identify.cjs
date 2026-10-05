const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..'),site=path.join(root,'mobile/build/site'),context={window:{}};
for(const f of ['catalog.js','award-intros.js','hierarchy.js'])vm.runInNewContext(fs.readFileSync(path.join(site,f),'utf8'),context);
const data=context.window.CATALOG,records=JSON.parse(fs.readFileSync(path.join(root,'data/volumes/france_identify_20260930.json'),'utf8')).records;
const search=require('../web/search.js'),book=require('../web/encyclopedia.js');
let images=0,superseded=0;
for(const r of records){
 const exported=data.rows.find(x=>x.id===r.id);assert(exported,'Missing '+r.id);assert.equal(exported.family,r.family);
 assert(context.window.CATEGORY_ROUTES[exported.volume.replace(/-unpictured$/,'')],'Unmapped '+exported.volume);
 if(r.supersedes_id){assert(!data.rows.some(x=>x.id===r.supersedes_id),'Obsolete unpictured '+r.supersedes_id);superseded++;}
 assert.equal(exported.photos.length,r.views.length);
 for(const p of exported.photos){assert(fs.existsSync(path.join(site,p.src)));assert(p.source.includes('identifymedals.com'));assert(p.credit.includes('IdentifyMedals'));assert(p.rights);images++;}
 assert(search.score(r.name,search.prepare(exported,'法国'))>0,'Unsearchable '+r.id);
 assert.equal(book.groups(data.rows.filter(x=>x.family===r.family),data.rows).length,1,'Split family '+r.family);
}
for(const fid of ['FRA-ROYAL-ORDER-SAINT-MICHEL','FRA-ROYAL-ORDER-SAINT-ESPRIT']){
 const r=data.rows.find(x=>x.family===fid);assert(r,'Missing royal '+fid);
 assert(context.window.AWARD_INTROS.some(i=>i.families.includes(fid)&&new RegExp(i.volumePattern).test(r.volume)),'Missing royal introduction '+fid);
}
console.log(JSON.stringify({addedRows:records.length,completeImages:images,replacedUnpictured:superseded,localImagesAndCredits:true}));
