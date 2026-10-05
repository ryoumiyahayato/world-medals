const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..'),site=path.join(root,'mobile/build/site'),context={window:{}};
for(const file of ['catalog.js','award-intros.js','hierarchy.js'])vm.runInNewContext(fs.readFileSync(path.join(site,file),'utf8'),context);
const data=context.window.CATALOG,intros=context.window.AWARD_INTROS;
const expected=JSON.parse(fs.readFileSync(path.join(root,'data/volumes/uk_mod_completion_20260930.json'),'utf8')).records;
const search=require('../web/search.js'),book=require('../web/encyclopedia.js');
const added=expected.map(e=>{
 const r=data.rows.find(r=>r.id===e.id);assert(r,'Missing exported '+e.id);assert.equal(r.family,e.family);
 assert(intros.some(i=>i.families.includes(r.family)&&new RegExp(i.volumePattern).test(r.volume)),'Missing introduction '+e.id);
 assert(context.window.CATEGORY_ROUTES[r.volume.replace(/-unpictured$/,'')],'Missing route '+r.volume);
 assert.equal(r.variant,e.variant,'Lost grade/version metadata '+r.id);
 for(const p of r.photos)assert(fs.existsSync(path.join(site,p.src)),'Missing image '+p.src);
 assert(search.score(r.name,search.prepare(r,'英国'))>0,'Unsearchable '+r.id);
 return r;
});
for(const family of ['GB-UK-ROYAL-RED-CROSS','GB-UK-OPERATIONAL-SERVICE-MEDAL']){
 const rows=data.rows.filter(r=>r.family===family);assert(rows.length>1);assert.equal(book.groups(rows,data.rows).length,1,'Family incorrectly split '+family);
}
assert(!added.some(r=>/PINGAT|LEGION-D|KUWAIT|SAUDI/.test(r.family)),'Foreign award misclassified');
console.log(JSON.stringify({addedRows:added.length,picturedRows:added.filter(r=>r.photos.length).length,unpicturedRows:added.filter(r=>!r.photos.length).length,introductionsAndLocalImages:true}));
