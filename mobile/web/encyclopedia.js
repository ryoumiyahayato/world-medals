/* Search headings group names; country-specific families remain separate. */
(function(root){
 function heading(row){const name=row.familyName||row.name;if(/荣誉军团|榮譽軍團/.test(name))return '荣誉军团勋章';return name;}
 function familyKey(row){
  const name=(row.familyName||row.name||'').trim();
  if(/^列宁勋章$/.test(name)&&/soviet|ussr/i.test(row.volume))return 'ussr-order-lenin';
  if(row.family&&row.family!==row.id)return row.family;
  return row.volume+'|'+name;
 }
 function groups(matches,all){const map=new Map(matches.map(r=>[familyKey(r),[]]));all.forEach(r=>{const key=familyKey(r);if(map.has(key))map.get(key).push(r);});return [...map].filter(([,rows])=>rows.length);}
 const phonetics=new Map();
 function phonetic(s){if(!phonetics.has(s)){const p=root.Pinyin;phonetics.set(s,(p&&p.isSupported()?p.convertToPinyin(s,' ',true):s).normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,''));}return phonetics.get(s);}
 function distance(a,b){const d=Array.from({length:b.length+1},(_,i)=>i);for(let i=1;i<=a.length;i++){let prev=d[0];d[0]=i;for(let j=1;j<=b.length;j++){const old=d[j];d[j]=Math.min(d[j]+1,d[j-1]+1,prev+(a[i-1]===b[j-1]?0:1));prev=old;}}return d[b.length];}
 // Highest awards only where the stored introductions identify their status.
 // Equal highest categories remain tied; no invented universal precedence list.
 function precedence(rows,intros){let best=Infinity;for(const r of rows){const explicit=root.AwardPrecedence?root.AwardPrecedence.rank(r):Infinity;if(Number.isFinite(explicit)){best=Math.min(best,explicit);continue;}const intro=(intros||[]).find(x=>(x.families||[]).includes(r.family)||(x.names||[]).includes(heading(r)));if(intro&&(!intro.volumePattern||new RegExp(intro.volumePattern).test(r.volume))&&intro.paragraphs.some(t=>/国家最高(?:级)?(?:勋章|奖章|荣誉)|最高(?:级)?(?:国家|民事|军事)?勋章|最高荣誉/.test(t)))best=Math.min(best,0);}return best;}
 function order(matches,all,options={}){
  const grouped=groups(all,all),scores=new Map();for(const x of matches)scores.set(familyKey(x.r),Math.max(scores.get(familyKey(x.r))||0,x.score));
  const cmp=new Intl.Collator('zh-CN',{numeric:true}).compare;
  const ranked=grouped.filter(([k])=>scores.has(k)).sort((a,b)=>(scores.get(b[0])-scores.get(a[0]))||cmp(heading(a[1][0]),heading(b[1][0])));
  if(options.countryQuery){const priority=new Map(ranked.map(([k,rs])=>[k,precedence(rs,options.intros)]));const russian=/^(俄罗斯|russia)$/i.test(String(options.query||'').replace(/\s/g,''));const period=rs=>russian&&rs.every(r=>!/russian-/.test(r.volume))?1:0;return ranked.sort((a,b)=>{const x=priority.get(a[0]),y=priority.get(b[0]);return (Number.isFinite(x)&&Number.isFinite(y)?period(a[1])-period(b[1]):0)||x-y||cmp(heading(a[1][0]),heading(b[1][0]));});}
  if(!ranked.length||!String(options.query||'').trim())return ranked;
  const first=ranked[0],anchor=first[1][0],p=phonetic(heading(anchor)),initial=p[0],country=options.countryOf||((r)=>r.volume);
  if(!initial)return ranked;
  const same=grouped.filter(([k,rs])=>k!==first[0]&&country(rs[0])===country(anchor)&&phonetic(heading(rs[0]))[0]===initial).sort((a,b)=>cmp(heading(a[1][0]),heading(b[1][0])));
  const elsewhere=grouped.filter(([k,rs])=>k!==first[0]&&country(rs[0])!==country(anchor)&&phonetic(heading(rs[0]))[0]===initial).sort((a,b)=>distance(p,phonetic(heading(a[1][0])))-distance(p,phonetic(heading(b[1][0])))||cmp(heading(a[1][0]),heading(b[1][0])));
  const result=[first,...same,...elsewhere,...ranked],seen=new Set();return result.filter(([k])=>!seen.has(k)&&seen.add(k));
 }
 function variantLabel(s){return (s||'').split('；').filter(t=>!/商业目录图片|仅限本地研究|目录所示具体等级|完整实物图/.test(t)).join('；');}
 function presentationRows(rows,replacements=root.REFERENCE_ROW_REPLACEMENTS||{}){
  // Only reviewed, matching types replace a specific source photograph.
  const ids=new Map(rows.map(r=>[r.id,r])),referenceFamilies=new Set(rows.filter(r=>r.photos.some(p=>p.reference)).map(familyKey));
  const replaced=new Set();
  for(const [source,target] of Object.entries(replacements)){const old=ids.get(source),ref=ids.get(target);if(old&&ref&&familyKey(old)===familyKey(ref)&&ref.photos.some(p=>p.reference))replaced.add(source);}
  return rows.filter(r=>!replaced.has(r.id)&&!(referenceFamilies.has(familyKey(r))&&!r.photos.some(p=>p.reference)&&/实物版本／具体版型待考/.test(r.variant)));
 }
 const api={heading,familyKey,groups,phonetic,order,presentationRows,variantLabel};root.AtlasBook=api;if(typeof module!=='undefined')module.exports=api;
})(typeof window==='undefined'?globalThis:window);
