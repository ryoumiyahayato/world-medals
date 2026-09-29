const assert=require('node:assert/strict');
const S=require('../web/search.js');
const legion=S.prepare({name:'法国荣誉军团勋章',original:'Légion d’honneur',familyName:'荣誉军团勋章',variant:'军官级 银质',date:'1870–1940'},'法国第三共和国');
for(const q of ['荣军','荣 军','荣  军','荣','军','荣誉军团','榮軍','榮譽軍團','LEGION D HONNEUR',"legion d'honneur",'法国 军官 1870','荣誉 军团','荣团'])assert(S.score(q,legion)>0,q);
for(const q of ['苏联','金质','1871','海军服役'])assert.equal(S.score(q,legion),0,q);
const unrelated=S.prepare({name:'军人荣誉奖章',original:'',variant:'',date:''},'其他');assert.equal(S.score('荣军',unrelated),0,'Alias must not match unrelated scattered words');
assert(S.score('荣誉军团',legion)>S.score('荣团',legion));
console.log('Search aliases, whitespace, Han characters, multi-keywords and accent folding passed.');
