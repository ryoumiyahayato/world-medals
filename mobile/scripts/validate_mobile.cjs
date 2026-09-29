const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../build/site'),context={window:{}};
vm.runInNewContext(fs.readFileSync(path.join(root,'catalog.js'),'utf8'),context);
vm.runInNewContext(fs.readFileSync(path.join(root,'hierarchy.js'),'utf8'),context);
const data=context.window.CATALOG,S=require('../web/search.js');
const ids=new Set();let images=new Set();
for(const r of data.rows){assert(!ids.has(r.id),'duplicate ID '+r.id);ids.add(r.id);assert(data.volumes.some(v=>v.id===r.volume));for(const p of r.photos){assert(p.src.startsWith('images/'));assert(fs.existsSync(path.join(root,p.src)),p.src);images.add(p.src);}}
const france=data.rows.filter(r=>r.id.startsWith('FRA-LEGION-'));
assert(france.length>0);assert(france.every(r=>r.family==='france-legion-of-honour'));
const indexes=data.rows.map(r=>S.prepare(r,data.volumes.find(v=>v.id===r.volume).title));
const matches=q=>data.rows.filter((r,i)=>S.score(q,indexes[i])>0).map(r=>r.id);
assert.deepEqual(matches('荣军'),matches('荣 军'));assert.deepEqual(matches('荣军'),matches('荣誉军团'));assert(france.every(r=>matches('荣军').includes(r.id)));
const uncovered=data.volumes.filter(v=>!context.window.CATEGORY_ROUTES[v.id.replace(/-unpictured$/,'')]&&!['related','unpictured'].includes(v.id));assert.equal(uncovered.length,0);
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');assert(!html.includes('全部国家与时期'));assert(!html.includes('随身查阅'));for(const m of html.matchAll(/(?:src|href)="([^"#]+)"/g)){if(!m[1].includes('://'))assert(fs.existsSync(path.join(root,m[1])),m[1]);}
const result={rows:data.rows.length,images:images.size,legionFrenchVariants:france.length,aliasResults:matches('荣军').length,unmappedVolumes:uncovered.length};fs.writeFileSync(path.resolve(__dirname,'../build/validation.json'),JSON.stringify(result,null,2));console.log(result);

