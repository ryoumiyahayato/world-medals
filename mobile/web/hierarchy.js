/* Navigation geography only; a route never rewrites the historical awarding authority. */
window.CATEGORY_ROUTES={};
window.CATEGORY_ROUTES['austria-carinthia']=['欧洲','中欧','奥地利'];
function routes(continent,region,country,ids){ids.split(' ').forEach(id=>window.CATEGORY_ROUTES[id]=[continent,region,country]);}
routes('亚洲','东亚','中国','qing-empire republic-of-china peoples-republic-china manchukuo hong-kong');
routes('亚洲','东亚','日本','japan');routes('亚洲','东亚','韩国／朝鲜','korean-empire south-korea north-korea');routes('亚洲','东亚','蒙古','mongolian-peoples-republic mongolia');
routes('亚洲','东南亚','越南','annam-protectorate tai-federation democratic-vietnam state-south-vietnam south-vietnam socialist-vietnam');
routes('亚洲','东南亚','柬埔寨','cambodia-protectorate cambodia-kingdom kampuchea-peoples-republic');routes('亚洲','东南亚','老挝','laos-kingdom laos-pdr');
routes('亚洲','东南亚','马来西亚','malaysia-federal sabah sarawak johor kedah kelantan pahang perak');routes('亚洲','东南亚','缅甸','myanmar-modern konbaung');routes('亚洲','东南亚','菲律宾','philippines-republic philippines-insular');
for(const [name,id] of [['泰国','thailand'],['印度尼西亚','indonesia'],['新加坡','singapore'],['文莱','brunei']])routes('亚洲','东南亚',name,id);
routes('亚洲','南亚','印度','british-india india-republic dominion-india azad-hind baroda bikaner gwalior patiala');routes('亚洲','南亚','巴基斯坦','pakistan bahawalpur');routes('亚洲','南亚','印度／巴基斯坦 · 历史跨境体系','sikh-empire jammu-kashmir');
for(const [name,id] of [['阿富汗','afghanistan'],['尼泊尔','nepal'],['不丹','bhutan'],['孟加拉国','bangladesh'],['斯里兰卡','sri-lanka'],['马尔代夫','maldives']])routes('亚洲','南亚',name,id);
for(const [name,id] of [['哈萨克斯坦','kazakhstan'],['吉尔吉斯斯坦','kyrgyzstan'],['塔吉克斯坦','tajikistan'],['土库曼斯坦','turkmenistan'],['乌兹别克斯坦','uzbekistan']])routes('亚洲','中亚',name,id);
routes('亚洲','西亚','土耳其','ottoman turkey');
for(const [name,id] of [['伊朗','iran'],['叙利亚','syria'],['阿曼','oman'],['约旦','jordan'],['沙特阿拉伯','saudi-arabia'],['卡塔尔','qatar'],['科威特','kuwait'],['巴林','bahrain'],['阿联酋','united-arab-emirates'],['黎巴嫩','lebanon'],['以色列','israel'],['也门','yemen'],['塞浦路斯','cyprus'],['亚美尼亚','armenia'],['格鲁吉亚','georgia'],['阿塞拜疆','azerbaijan']])routes('亚洲','西亚',name,id);
routes('欧洲','东欧','俄罗斯','russian-empire rsfsr-awards soviet-union russian-federation');
for(const [name,id] of [['乌克兰','ukraine'],['白俄罗斯','belarus'],['摩尔多瓦','moldova'],['罗马尼亚','romania-kingdom']])routes('欧洲','东欧',name,id);
routes('欧洲','东欧','保加利亚','bulgaria-principality bulgaria-kingdom bulgaria-republic');
routes('欧洲','中欧','德国','germany-1933-1945 prussia-kingdom bavaria-kingdom');routes('欧洲','中欧','奥地利','habsburg-monarchy austrian-empire austro-hungary austria-republic');routes('欧洲','中欧','匈牙利','hungary');routes('欧洲','中欧','波兰','poland');routes('欧洲','中欧','捷克／斯洛伐克','czechoslovakia czech-republic slovakia');
for(const [name,id] of [['芬兰','finland'],['瑞典','sweden'],['丹麦','denmark'],['冰岛','iceland'],['挪威','norway'],['爱沙尼亚','estonia'],['拉脱维亚','latvia'],['立陶宛','lithuania']])routes('欧洲','北欧',name,id);
routes('欧洲','西欧','法国','france-kingdom france-timeline france-first-empire france-bourbon france-july france-second-republic france-second-empire france-third-republic france-fourth-fifth');
routes('欧洲','西欧','英国','uk');routes('欧洲','西欧','荷兰','netherlands');routes('欧洲','西欧','比利时','belgium');
routes('欧洲','南欧','西班牙','spain-republic spain-kingdom');routes('欧洲','南欧','葡萄牙','portugal');routes('欧洲','南欧','意大利','savoy-italy');routes('欧洲','南欧','希腊','greece');
for(const [name,id] of [['埃及','egypt'],['苏丹','sudan'],['摩洛哥','morocco'],['阿尔及利亚','algeria']])routes('非洲','北非',name,id);
routes('北美洲','北美地区','美国','united-states');
window.buildCategoryTree=function(volumes,onChoose){
 const tree=new Map(['亚洲','欧洲','非洲','北美洲','南美洲','大洋洲','国际组织'].map(c=>[c,new Map()])),appendices=[];
 volumes.forEach(v=>{const route=CATEGORY_ROUTES[v.id.replace(/-unpictured$/,'')];if(!route){appendices.push(v);return;}const [continent,region,country]=route;const regions=tree.get(continent);if(!regions.has(region))regions.set(region,new Map());const countries=regions.get(region);if(!countries.has(country))countries.set(country,[]);countries.get(country).push(v);});
 const host=document.getElementById('category-list');host.replaceChildren();
 function branch(name,depth){const d=document.createElement('details');d.className='category-branch depth-'+depth;const s=document.createElement('summary');s.textContent=name;d.append(s);return d;}
 function leaf(v,parent){const b=document.createElement('button');b.className='period-choice';b.textContent=v.title;b.onclick=()=>onChoose(v.id);parent.append(b);}
 tree.forEach((regions,continent)=>{const c=branch(continent,0);host.append(c);if(!regions.size){const p=document.createElement('p');p.className='muted';p.textContent='暂无已收录分卷';c.append(p);}regions.forEach((countries,region)=>{const r=branch(region,1);c.append(r);countries.forEach((vols,country)=>{const n=branch(country,2);r.append(n);vols.sort((a,b)=>{if(a.id==='france-timeline')return -1;if(b.id==='france-timeline')return 1;return (Number((a.title.match(/\d{4}/)||[])[0])||9999)-(Number((b.title.match(/\d{4}/)||[])[0])||9999);}).forEach(v=>leaf(v,n));});});});
 if(appendices.length){const a=branch('附编',0);host.append(a);appendices.forEach(v=>leaf(v,a));}
};

routes('欧洲','西欧','卢森堡','luxembourg');routes('欧洲','西欧','爱尔兰','ireland');
routes('国际组织','全球组织','联合国','united-nations');routes('国际组织','区域组织','欧洲共同体／欧洲联盟','european-communities-union');routes('国际组织','区域组织','北大西洋公约组织','nato');routes('国际组织','国际会议','前南斯拉夫问题国际会议','icfy');routes('国际组织','多国部队','东帝汶国际部队','interfet');

routes("亚洲","西亚","伊拉克","iraq-kingdom");
routes("北美洲","北美","加拿大","canada");
routes("大洋洲","澳大利亚与新西兰","新西兰","new-zealand");
routes("非洲","东非","吉布提","minimum-djibouti");
routes("非洲","东非","索马里","minimum-somalia");
routes("非洲","东非","肯尼亚","minimum-kenya");
routes("非洲","东非","乌干达","minimum-uganda");
routes("非洲","东非","坦桑尼亚","minimum-tanzania");
routes("非洲","东非","卢旺达","minimum-rwanda");
routes("非洲","东非","布隆迪","minimum-burundi");
routes("非洲","东非","科摩罗","minimum-comoros");
routes("非洲","东非","埃塞俄比亚","minimum-ethiopia");
routes("非洲","东非","马达加斯加","minimum-madagascar");
routes("非洲","南部非洲","南非","minimum-south-africa");
routes("非洲","南部非洲","纳米比亚","minimum-namibia");
routes("非洲","南部非洲","博茨瓦纳","minimum-botswana");
routes("非洲","南部非洲","赞比亚","minimum-zambia");
routes("非洲","南部非洲","津巴布韦","minimum-zimbabwe");
routes("非洲","南部非洲","马拉维","minimum-malawi");
routes("非洲","南部非洲","莫桑比克","minimum-mozambique");
routes("非洲","南部非洲","莱索托","minimum-lesotho");
routes("非洲","南部非洲","斯威士兰／埃斯瓦蒂尼","minimum-swaziland");

/* FRANCE_COMPLETION_START */
window.CATEGORY_ROUTES["france-source-national"]=["欧洲", "西欧", "法国"];
window.CATEGORY_ROUTES["france-source-italy"]=["欧洲", "南欧", "意大利"];
window.CATEGORY_ROUTES["france-source-anjouan"]=["非洲", "东非", "科摩罗"];
window.CATEGORY_ROUTES["france-source-dahomey"]=["非洲", "西非", "贝宁"];
window.CATEGORY_ROUTES["france-source-cameroon"]=["非洲", "中非", "喀麦隆"];
window.CATEGORY_ROUTES["france-source-indochina"]=["亚洲", "东南亚", "法属印度支那"];
window.CATEGORY_ROUTES["france-source-madagascar"]=["非洲", "东非", "马达加斯加"];
window.CATEGORY_ROUTES["france-source-tadjoura"]=["非洲", "东非", "吉布提"];
window.CATEGORY_ROUTES["france-source-polynesia"]=["大洋洲", "波利尼西亚", "法属波利尼西亚"];
window.CATEGORY_ROUTES["france-source-related"]=["欧洲", "西欧", "法国"];
window.CATEGORY_ROUTES["france-source-algeria"]=["非洲", "北非", "阿尔及利亚"];
window.CATEGORY_ROUTES["france-source-india"]=["亚洲", "南亚", "印度"];
window.CATEGORY_ROUTES["france-source-saar"]=["欧洲", "西欧", "德国"];
/* FRANCE_COMPLETION_END */

/* GERMAN_COMPLETION_START */
window.CATEGORY_ROUTES["saxony-kingdom"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["saxony-electorate-kingdom"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["hanover-kingdom"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["oldenburg-grand-duchy"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["anhalt-duchies"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["baden-grand-duchy"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["baden-durlach-grand-duchy"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["brunswick-duchy"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["hesse-darmstadt-grand-duchy"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["hesse-kassel-landgraviate-electorate"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["mecklenburg-duchies-shared"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["lippe-detmold-principality"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["saxe-ernestine-duchies"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["wuerttemberg-kingdom"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["germany-federal-republic"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["baden-wuerttemberg-state"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["bavaria-state"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["berlin-state"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["brandenburg-state"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["hessen-state"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["mecklenburg-vorpommern-state"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["lower-saxony-state"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["north-rhine-westphalia-state"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["rhineland-palatinate-state"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["saarland-state"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["saxony-free-state"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["saxony-anhalt-state"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["schleswig-holstein-state"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["thuringia-free-state"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["germany-related"]=["欧洲", "中欧", "德国"];
window.CATEGORY_ROUTES["hamburg-state"]=["欧洲", "中欧", "德国"];
/* GERMAN_COMPLETION_END */
