const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const B=require('../web/encyclopedia.js'),ctx={window:{}};
vm.runInNewContext(fs.readFileSync(require('node:path').join(__dirname,'../build/site/catalog.js'),'utf8'),ctx);
const rows=ctx.window.CATALOG.rows;const manifest=JSON.parse(fs.readFileSync(require('node:path').join(__dirname,'../../data/display_images/row_replacements.json'),'utf8'));const policy=Object.fromEntries(Object.entries(manifest.rows).filter(([,v])=>v.approved).map(([k,v])=>[k,v.reference_record]));
for(const [source,reference] of [
 ['USSR-ORD-01-TYPE-II-COMPLETE-20260929','USSR-ORD-01-USER-REF-20261003-054'],
 ['USSR-ORD-13-MB-V01','USSR-ORD-13-USER-REF-20261003-098']
]){
 const src=rows.find(r=>r.id===source),ref=rows.find(r=>r.id===reference);
 assert(src&&ref);assert.equal(B.familyKey(src),B.familyKey(ref));
 const result=B.presentationRows(rows.filter(r=>B.familyKey(r)===B.familyKey(src)),policy);
 assert(result.some(r=>r.id===reference));assert(!result.some(r=>r.id===source));
 // Missing reviewed replacements must never hide unrelated source variants.
 assert(B.presentationRows([src],policy).some(r=>r.id===source));
 assert(B.presentationRows([src,{...ref,family:'different-family',familyName:'different',name:'different',volume:'another-country'}],policy).some(r=>r.id===source));
}
assert(!B.variantLabel('第一级；商业目录图片，仅限本地研究').includes('商业'));
console.log('Reviewed type replacements win; missing or different-family references preserve source variants.');
