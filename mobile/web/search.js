/* Shared by the browser and node tests. Aliases are search aids, not catalogue names. */
(function(root){
 const fold=s=>String(s||'').normalize('NFKD').replace(/[\u0300-\u036f]/g,'').normalize('NFKC').toLocaleLowerCase().replace(/[’‘`]/g,"'");
 const aliases=new Map([['荣军','荣誉军团'],['榮軍','荣誉军团'],['榮譽軍團','荣誉军团'],['荣誉军团勋章','荣誉军团'],['legiondhonneur','legion d honneur'],['legionofhonour','legion of honour'],['legionofhonor','legion of honor']]);
 const compact=s=>fold(s).replace(/[\s'’·.\-／/]/g,'');
 function canonical(raw){const key=compact(raw);return aliases.get(key)||fold(raw);}
 function prepare(row,scope){
  const fields=[row.name,row.original,row.familyName,row.variant,row.date,scope,...(row.searchAliases||[])].map(fold);
  const named=[fields[0],fields[1],fields[2],...(row.searchAliases||[]).map(fold)];
  const extra=[];if(named.some(s=>/荣誉军团|legion d.honneur|legion of hono[u]?r/.test(s)))extra.push('荣誉军团','荣军','legion d honneur','legion of honour','legion of honor');
  const all=fields.concat(extra);return {fields:all,names:named.concat(extra),text:all.join(' '),compactFields:all.map(compact),compactNames:named.concat(extra).map(compact),compactText:compact(all.join(' '))};
 }
 function subsequence(needle,haystack){let i=0;for(const c of haystack){if(c===needle[i])i++;if(i===needle.length)return true;}return false;}
 function score(raw,index){
  if(!String(raw).trim())return 1;
  const q=canonical(raw),cq=compact(q),names=index.compactNames;
  if(names.some(n=>n===cq))return 120;
  if(names.some(n=>n.includes(cq)))return 100;
  if(index.compactText.includes(cq))return 80;
  const tokens=q.trim().split(/[\s,，;；]+/).filter(Boolean).map(canonical);
  let total=0;for(const t of tokens){const ct=compact(t);if(index.compactFields.some(f=>f.includes(ct))){total+=60;continue;}
   // Short Han abbreviations must remain ordered inside a name; dates/materials
   // cannot accidentally supply scattered characters to invent a name match.
   if(/^[\p{Script=Han}]{2,8}$/u.test(ct)&&names.some(n=>subsequence(ct,n))){total+=25;continue;}
   return 0;
  }return total/tokens.length;
 }
 const api={fold,compact,canonical,prepare,score};root.AtlasSearch=api;if(typeof module!=='undefined')module.exports=api;
})(typeof window==='undefined'?globalThis:window);
