/* Search headings group names; country-specific families remain separate. */
(function(root){
 function heading(row){const name=row.familyName||row.name;if(/荣誉军团|榮譽軍團/.test(name))return '荣誉军团勋章';return name;}
 function familyKey(row){return row.family||row.id;}
 function groups(matches,all){const wanted=new Set(matches.map(familyKey)),map=new Map();all.forEach(r=>{const key=familyKey(r);if(!wanted.has(key))return;if(!map.has(key))map.set(key,[]);map.get(key).push(r);});return [...map];}
 const api={heading,familyKey,groups};root.AtlasBook=api;if(typeof module!=='undefined')module.exports=api;
})(typeof window==='undefined'?globalThis:window);
