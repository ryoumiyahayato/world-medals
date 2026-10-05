/* Display order by awarding system. Sources and scope stay in internal metadata.
 * Orders follow the 1980 USSR wearing rules; special hero insignia are separate.
 * Different periods are never asserted to share a legal precedence system. */
(function(root){
 const sovietOrders=['列宁','十月革命','红旗','苏沃洛夫','乌沙科夫','库图佐夫','纳希莫夫','(波格丹|博格丹).*赫梅利尼茨基','亚历山大.*涅夫斯基','卫国战争','劳动红旗','各民族友谊|人民友谊','红星','武装力量.*祖国|祖国.*武装力量','荣誉徽章|荣誉勋章','光荣','劳动光荣','个人勇敢|个人英勇'];
 function rank(row){const name=(row.familyName||row.name||'')+' '+(row.original||'');
  if(/soviet|ussr/.test(row.volume)){
   if(/英雄金星|Золотая Звезда/i.test(name))return -20;if(/社会主义劳动英雄.*锤子|Серп и Молот/i.test(name))return -19;
   if(/胜利勋章|Победа/.test(name))return -.5;
   // Full name matching prevents Labour Red Banner / Labour Glory inheriting the military rank.
   const short=(row.familyName||row.name||'').replace(/勋章.*$/,'');
   const i=sovietOrders.findIndex(p=>new RegExp('^(苏联)?('+p+')$').test(short));if(i>=0)return i;
  }
  if(/russian-empire|russian-federation/.test(row.volume)&&/圣安德烈|Святого.*Андрея/.test(name))return 0;
  return Infinity;
 }
 const sources=[{url:'https://mondvor.narod.ru/OLenin.html',scope:'Soviet Order of Lenin statute; highest Soviet order'},{url:'https://base.garant.ru/183592/',scope:'USSR decree 28 March 1980 No.1806-X: wearing sequence, grouped by family and highest grade'},{url:'https://minjust.gov.ru/ru/documents/7992/',scope:'Russian Federation decree 1099: highest orders and separate distinctions'},{url:'https://www.kreml.ru/press-room/special-reports/proekt-kremlevskie-palaty-ordena-i-medali-chem-kogo-i-za-chto-nagrazhdali-v-rossii-kollektsiya-nagrad-v-oruzheynoy-palate/',scope:'Imperial and restored Saint Andrew: highest order'}];
 const api={rank,sources};if(typeof module==='object'&&module.exports)module.exports=api;else root.AwardPrecedence=api;
})(typeof window==='object'?window:this);
