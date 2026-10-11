'use strict';
const $ = id => document.getElementById(id);
const read = (key, fallback) => { try {const value=JSON.parse(localStorage.getItem(key));return value==null?fallback:value;} catch {return fallback;} };
const write = (key, value) => { try {localStorage.setItem(key, JSON.stringify(value));return true;} catch { $('update-status').textContent='本机存储空间不足，设置未能保存。';return false;} };
const state = {tab:'catalog',limit:30,favorites:new Set(read('favorites',[])),row:null,photo:0,ready:false};
const systemDark = matchMedia('(prefers-color-scheme: dark)');
const systemMotion = matchMedia('(prefers-reduced-motion: reduce)');
let motionReduced = read('reduced',systemMotion.matches), theme = read('theme','system');
function applyTheme(){
 document.documentElement.dataset.theme = theme === 'system' ? ((window.nativeSystemDark==null?systemDark.matches:window.nativeSystemDark)?'dark':'light') : theme;
 document.documentElement.style.setProperty('--custom-bg',read('backgroundColor','var(--space)'));
 document.documentElement.style.setProperty('--fog-a',read('fogColorA','#66819c'));document.documentElement.style.setProperty('--fog-b',read('fogColorB','#756389'));document.body.dataset.space=read('spaceEffect','fog');
 $('personal-background').style.backgroundImage = read('backgroundImage',null) ? `url(${read('backgroundImage',null)})` : '';
 document.documentElement.style.setProperty('--background-blur',read('backgroundBlur',18)+'px');
 document.body.classList.toggle('custom-background',!!read('backgroundImage',null)||!!read('backgroundColor',null));
}
if(systemDark.addEventListener)systemDark.addEventListener('change',applyTheme);else systemDark.addListener(applyTheme);applyTheme();
$('theme').value=theme;$('theme').onchange=e=>{theme=e.target.value;write('theme',theme);applyTheme();};
$('background-color').value=read('backgroundColor',document.documentElement.dataset.theme==='dark'?'#101419':'#e2e7e9');
$('background-color').oninput=e=>{write('backgroundColor',e.target.value);applyTheme();};
$('background-blur').value=read('backgroundBlur',18);$('blur-value').textContent=$('background-blur').value;
$('background-blur').oninput=e=>{write('backgroundBlur',Number(e.target.value));$('blur-value').textContent=e.target.value;applyTheme();};
$('space-effect').value=read('spaceEffect','fog');$('space-effect').onchange=e=>{write('spaceEffect',e.target.value);applyTheme();};
for(const [id,key,initial] of [['fog-color-a','fogColorA','#66819c'],['fog-color-b','fogColorB','#756389']]){$(id).value=read(key,initial);$(id).oninput=e=>{write(key,e.target.value);applyTheme();};}
$('reset-background').onclick=()=>{['backgroundImage','backgroundColor','backgroundBlur','fogColorA','fogColorB','spaceEffect'].forEach(k=>localStorage.removeItem(k));$('background-file').value='';$('background-blur').value=18;$('blur-value').textContent='18';$('fog-color-a').value='#66819c';$('fog-color-b').value='#756389';$('space-effect').value='fog';applyTheme();$('background-color').value=document.documentElement.dataset.theme==='dark'?'#101419':'#e2e7e9';};
$('background-file').onchange=async e=>{
 const file=e.target.files[0];if(!file)return;
 if(!file.type.startsWith('image/')||file.size>25*1024*1024){$('update-status').textContent='请选择25 MB以内的图片。';return;}
 const url=URL.createObjectURL(file),img=new Image();
 try{await new Promise((ok,no)=>{img.onload=ok;img.onerror=no;img.src=url;});const canvas=document.createElement('canvas');const ratio=Math.min(1,1600/Math.max(img.width,img.height));canvas.width=Math.round(img.width*ratio);canvas.height=Math.round(img.height*ratio);canvas.getContext('2d').drawImage(img,0,0,canvas.width,canvas.height);if(write('backgroundImage',canvas.toDataURL('image/jpeg',.8)))applyTheme();}
 catch{$('update-status').textContent='无法读取这张图片，请换一张。';}finally{URL.revokeObjectURL(url);}
};
const shapes=[
 ['皇冠','M2 8L6 12 9 4 12 11 15 4 18 12 22 8 20 20H4ZM4 23H20M3 5H3.01M9 2H9.01M15 2H15.01M21 5H21.01M5 17H19'],
 ['火炬','M10 14H14L13.3 24H10.7ZM8 13H16M10 3C8 7 4 8 8 12H15C20 8 15 5 14 1 14 7 10 9 10 3ZM10 17H14M11 21H13'],
 ['荣誉章','M12.000 6.400L14.292 11.845L20.179 12.342L15.709 16.205L17.055 21.958L12.000 18.900L6.945 21.958L8.291 16.205L3.821 12.342L9.708 11.845ZM12.000 8.200L13.763 12.573L18.467 12.899L14.853 15.927L15.997 20.501L12.000 18.000L8.003 20.501L9.147 15.927L5.533 12.899L10.237 12.573ZM8 0.6H16L15 3.1H9ZM9.1 1.5H14.9L14.6 2.2H9.4ZM12 2.4A1.9 1.9 0 1 1 11.999 6.2A1.9 1.9 0 1 1 12 2.4ZM12 3.25A1.05 1.05 0 1 0 12.001 5.35A1.05 1.05 0 1 0 12 3.25ZM4.0 8.0Q3.2 5.0 6.4 6.0Q4.3 6.6 4.0 8.0ZM2.4 11.0Q0.8 7.4 3.4 8.0Q2.6999999999999997 9.6 2.4 11.0ZM2.1 14.3Q0.0 11.2 2.7 11.7Q2.4 12.9 2.1 14.3ZM3.0 18.0Q0.1 15.2 2.2 15.0Q3.3 16.6 3.0 18.0ZM5.5 21.0Q2.4 20.0 3.0 17.8Q5.8 19.6 5.5 21.0ZM8.0 23.0Q4.1 23.5 5.5 21.0Q8.3 21.6 8.0 23.0ZM20.0 8.0Q20.8 5.0 17.6 6.0Q19.7 6.6 20.0 8.0ZM21.6 11.0Q23.2 7.4 20.6 8.0Q21.3 9.6 21.6 11.0ZM21.9 14.3Q24.0 11.2 21.3 11.7Q21.599999999999998 12.9 21.9 14.3ZM21.0 18.0Q23.9 15.2 21.8 15.0Q20.7 16.6 21.0 18.0ZM18.5 21.0Q21.6 20.0 21.0 17.8Q18.2 19.6 18.5 21.0ZM16.0 23.0Q19.9 23.5 18.5 21.0Q15.7 21.6 16.0 23.0ZM10.8 22.5H13.2V25H10.8Z'],
 ['和平鸽','M3 15C7 15 8 12 7 7L8 2C11 5 13 9 16 10 18 6 21 7 21 10L24 11 21 12C20 19 15 21 10 18L2 21 5 17ZM9 8L13 13M12 6L16 11M18 10H18.1M18 18L21 23M20 21L24 20M21 22L24 24'],
 ['铁十字','M8 2H16L14 9 21 7V17L14 15 16 24H8L10 15 3 17V7L10 9ZM10 5H14L12.7 10.5 18 9V15L12.7 13.5 14 21H10L11.3 13.5 6 15V9L11.3 10.5Z']
];
function makeMotifs(){
 $('motifs').replaceChildren();for(let i=0;i<20;i++){const [name,path]=shapes[i%5],b=document.createElement('button');b.setAttribute('aria-label',name+'，点击掉落');
 const col=i%4,row=Math.floor(i/4);b.style.left=(4+col*24+(row%2)*2)+'%';b.style.top=(5+row*16+(col%2)*3)+'%';b.style.width=b.style.height=(42+(i%3)*5)+'px';b.style.animationDuration=(7+(i%7)*.65)+'s';b.style.animationDelay=(-i*.71)+'s';
 b.innerHTML=`<svg viewBox="-2 -1 28 28" aria-hidden="true"><defs><linearGradient id="motif-${i}" x2="1" y2="1"><stop stop-color="#f2d79d"/><stop offset=".5" stop-color="#b99352"/><stop offset="1" stop-color="#e3c58a"/></linearGradient></defs><path d="${path}" fill="${i%5===2?`url(#motif-${i})`:"none"}" stroke="url(#motif-${i})" stroke-width="1.2" stroke-linejoin="round" stroke-linecap="round" fill-rule="evenodd"/></svg>`;b.onclick=()=>{b.classList.add('falling');b.disabled=true;setTimeout(()=>b.remove(),motionReduced?0:800);};$('motifs').append(b);}
}
let animationFrame=0,animationStarted=0,skipRequested=false;
function finishSplash(){if(!state.ready){skipRequested=true;return;}$('splash').hidden=true;$('splash').style.display='none';document.body.classList.remove('is-loading');cancelAnimationFrame(animationFrame);}
function playSplash(){cancelAnimationFrame(animationFrame);skipRequested=false;makeMotifs();document.body.classList.add('is-loading');$('splash').hidden=false;$('splash').style.display='flex';animationStarted=performance.now();
 const resize=()=>{$('track').style.setProperty('--travel',Math.max(0,$('track').clientWidth-56)+'px');};resize();window.addEventListener('resize',resize,{once:true});
 const tick=now=>{if(state.ready&&(skipRequested||now-animationStarted>(motionReduced?150:2650))){finishSplash();return;}animationFrame=requestAnimationFrame(tick);};animationFrame=requestAnimationFrame(tick);
}
$('skip').onclick=finishSplash;$('reduced').checked=motionReduced;
$('reduced').onchange=e=>{motionReduced=e.target.checked;write('reduced',motionReduced);document.body.classList.toggle('reduce-motion',motionReduced);};document.body.classList.toggle('reduce-motion',motionReduced);playSplash();
function catalogFailed(){$('load-message').hidden=false;$('skip').hidden=false;$('load-message').textContent='图鉴文件未能读取，请重新安装完整 APK。';$('skip').textContent='查看设置';state.ready=true;}
function chronologicalKey(row){
 const d=row.date||'';const gregorian=d.match(/(?:约|公元|\(|（)?((?:1[5-9]|20)\d{2})/);return gregorian?Number(gregorian[1]):Infinity;
}
function editionKey(row){const period=scopeTitle(row.volume).match(/(?:1[0-9]|20)\d{2}/);return period?Number(period[0]):chronologicalKey(row);}
const scopeOf=r=>r.volume.startsWith('france-')?'france-timeline':r.volume;
function scopeTitle(id){return id==='france-timeline'?'法国 · 历代奖励':(CATALOG.volumes.find(v=>v.id===id)||{}).title||id;}
function el(tag,text,className){const n=document.createElement(tag);if(text)n.textContent=text;if(className)n.className=className;return n;}
function toggleFavorite(row){state.favorites.has(row.id)?state.favorites.delete(row.id):state.favorites.add(row.id);write('favorites',[...state.favorites]);render();if(state.row)$('save').textContent=state.favorites.has(state.row.id)?'取消收藏':'收藏';}
function renderRow(row){
 const tr=el('tr'),name=el('td'),kind=el('td',row.variant),picture=el('td');
 name.append(el('strong',row.name),el('span',row.original,'original'),el('span',row.date,'date'));if(row.volume.startsWith('france-'))name.append(el('span',scopeTitle(row.volume),'date'));
 const bookmark=el('button',state.favorites.has(row.id)?'已收藏':'收藏','bookmark');bookmark.setAttribute('aria-label',(state.favorites.has(row.id)?'取消收藏':'收藏')+row.name);bookmark.setAttribute('aria-pressed',String(state.favorites.has(row.id)));bookmark.onclick=()=>toggleFavorite(row);name.append(bookmark);
 row.photos.forEach((p,i)=>{const b=el('button',null,'photo-button');b.setAttribute('aria-label','放大：'+(p.alt||row.name));const im=el('img');im.src=p.thumb||p.src;im.alt=p.alt||row.name;im.loading='lazy';im.decoding='async';b.append(im,el('span',p.caption));b.onclick=()=>openPhoto(row,i);picture.append(b);});if(!row.photos.length)picture.textContent='有记载未配图';tr.append(name,kind,picture);return tr;
}
let expanded=new Set(), selectedAward=null, readerScope="", readerGroups=[], pendingPeriod=null, directoryPage=0, pendingFolio=null;
function bookRenderTurn(back=false){requestPageRender(back);}
function articleTurn(back){
 const index=readerGroups.findIndex(([key])=>key===selectedAward);if(index<0)return false;
 const position=window.AtlasFolio?AtlasFolio.position():{page:0,total:1};
 const step=AtlasReaderMotion.articleStep(index,readerGroups.length,position.page,position.total,back?-1:1);if(!step)return false;
 if(step.directory){selectedAward=null;bookRenderTurn(true);return true;}
 if(step.index===index&&window.AtlasFolio)return back?AtlasFolio.previous():AtlasFolio.next();
 selectedAward=readerGroups[step.index][0];pendingFolio=step.page;bookRenderTurn(back);return true;
}
window.readerBack=()=>{if(selectedAward)return articleTurn(true);if(directoryPage>0){directoryPage--;bookRenderTurn(true);return true;}return false;};
window.readerNext=()=>{if(selectedAward)return articleTurn(false);const size=directorySize();if((directoryPage+1)*size<readerGroups.length){directoryPage++;bookRenderTurn();return true;}return false;};
window.readerDirectory=()=>{if(!document.body.classList.contains('has-results'))return;cancelQueryTransition();if(selectedAward){const i=readerGroups.findIndex(([key])=>key===selectedAward);directoryPage=Math.max(0,Math.floor(i/directorySize()));}selectedAward=null;pendingFolio=null;requestPageRender('up');};
function directorySize(){const line=$('results').clientWidth<450?72:53;return Math.max(1,Math.min(9,Math.floor(Math.max(line,($('results').clientHeight||320)-65)/line)));}
let directoryResize=0;window.addEventListener('resize',()=>{clearTimeout(directoryResize);directoryResize=setTimeout(()=>{if(document.body.classList.contains('has-results')&&!selectedAward)render();},120);});
function countryOf(row){const route=window.CATEGORY_ROUTES[row.volume.replace(/-unpictured$/,'')];if(route)return route[2];const title=scopeTitle(row.volume);const country=[...new Set(Object.values(window.CATEGORY_ROUTES).map(r=>r[2]))].sort((a,b)=>b.length-a.length).find(c=>title.startsWith(c));return country||title.split(/[·（(]/)[0].trim();}
function isCountryQuery(query){const q=AtlasSearch.compact(query);if(!q)return false;const known={ussr:'soviet-union',sovietunion:'soviet-union',france:'france-timeline',japan:'japan',egypt:'egypt'};if(known[q])return true;return CATALOG.volumes.some(v=>AtlasSearch.compact(v.title.replace(/[（(].*$/,''))===q)||Object.values(window.CATEGORY_ROUTES).some(route=>AtlasSearch.compact(route[2])===q);}
function countryVolumes(query){
 const q=AtlasSearch.compact(query),aliases={ussr:'苏联',sovietunion:'苏联',russia:'俄罗斯',russianfederation:'俄罗斯联邦',france:'法国',japan:'日本',egypt:'埃及'},target=aliases[q]||q;
 const volumes=CATALOG.volumes.filter(v=>{const route=window.CATEGORY_ROUTES[v.id.replace(/-unpictured$/,'')];return [v.title.replace(/·.*$/,'').replace(/[（(].*$/,'').trim(),...(route?[route[2],route[3]]:[])].some(s=>AtlasSearch.compact(s)===AtlasSearch.compact(target));});return volumes.length?new Set(volumes.map(v=>v.id)):null;
}
function render(){
 if(!window.CATALOG)return;
 const query=$('query').value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean),volume=$('volume').value;
 const matching=CATALOG.rows.map(r=>({r,score:AtlasSearch.score($('query').value,r.searchIndex)})).filter(x=>x.score>0&&(state.tab!=='favorites'||state.favorites.has(x.r.id))).sort((a,b)=>b.score-a.score).map(x=>x.r);
 const browsing=!!volume;
 document.body.classList.toggle('has-results',browsing||query.length>0||state.tab==='favorites');
 if((browsing||query.length>0||state.tab==='favorites')&&window.openBookInstant)window.openBookInstant();
 const scope=volume+'|'+$('query').value+'|'+state.tab;if(scope!==readerScope){selectedAward=null;directoryPage=0;readerScope=scope;if(document.body.classList.contains('book-is-open')&&window.projectAtlasPage)window.projectAtlasPage();}
 $('home-book').hidden=false;writeBookQuery('');document.body.classList.remove('query-writing');
 const active=browsing||query.length>0||state.tab==='favorites';
 document.querySelector('.section-heading').hidden=!active;
 $('country-matches').replaceChildren();$('country-matches').hidden=true;$('results').replaceChildren();$('more').hidden=true;$('empty').hidden=true;
 if(!active){document.body.classList.remove('article-reading','page-projected');$('reading-book').removeAttribute('data-page');return;}
 const countrySet=!volume&&isCountryQuery($('query').value)?countryVolumes($('query').value):null;
 const countryPool=countrySet?CATALOG.rows.filter(r=>state.tab!=='favorites'||state.favorites.has(r.id)):matching;
 const scoped=countryPool.filter(r=>(!countrySet||countrySet.has(r.volume))&&(!volume||(volume==='france-timeline'?scopeOf(r)===volume:r.volume===volume)));
 const allowed=CATALOG.rows.filter(r=>(!countrySet||countrySet.has(r.volume))&&(!volume||(volume==='france-timeline'?scopeOf(r)===volume:r.volume===volume))&&(state.tab!=='favorites'||state.favorites.has(r.id)));
 readerGroups=AtlasBook.order(scoped.map(r=>({r,score:countrySet?100:AtlasSearch.score($('query').value,r.searchIndex)})),allowed,{query:$('query').value,countryQuery:!!volume||isCountryQuery($('query').value),countryOf,intros:window.AWARD_INTROS});
 const total=readerGroups.reduce((n,[,items])=>n+items.length,0);$('count').textContent=`${readerGroups.length}章种 · ${total}版型`;
 if(!readerGroups.length){$('empty').hidden=false;$('reading-book').removeAttribute('data-page');return;}
 if(!selectedAward){
  document.body.classList.remove('article-reading');
  $('results').append(el('h2','目录','directory-title'));
  const size=directorySize(),pages=Math.ceil(readerGroups.length/size);directoryPage=Math.min(directoryPage,pages-1);
  const titles=new Map();readerGroups.forEach(([,items])=>{const h=AtlasBook.heading(items[0]);titles.set(h,(titles.get(h)||0)+1);});
  readerGroups.slice(directoryPage*size,(directoryPage+1)*size).forEach(([key,items])=>{
   const title=AtlasBook.heading(items[0]),entry=el('button',null,'printed-entry');
   entry.append(el('span',title+(titles.get(title)>1?' · '+countryOf(items[0]):''),'printed-name'));
   const periods=[...new Set(items.map(r=>scopeTitle(r.volume).replace(/\s*·\s*(有记载|暂缺|待核).*$/,'').trim()))];entry.append(el('span',periods.join(' · '),'printed-period'));
   entry.onclick=()=>{selectedAward=key;pendingPeriod=null;bookRenderTurn();};$('results').append(entry);
  });
  $('reading-book').dataset.page=(directoryPage+1)+' / '+pages;
  return;
 }
 document.body.classList.add('article-reading');
 const index=readerGroups.findIndex(([key])=>key===selectedAward);if(index<0){selectedAward=null;render();return;}
 const items=AtlasBook.presentationRows(readerGroups[index][1]);items.sort((a,b)=>editionKey(a)-editionKey(b));
 const article=el('article',null,'award-article'),hero=el('div',null,'article-hero'),titleBlock=el('div');
 titleBlock.append(el('h2',AtlasBook.heading(items[0]),'award-page-title'));const route=window.CATEGORY_ROUTES[items[0].volume];titleBlock.append(el('p',scopeTitle(items[0].volume),'article-country'));hero.append(titleBlock);
 const representative=items.find(r=>r.photos.some(p=>p.reference))||items.find(r=>r.photos.length);if(representative)hero.append(articlePhoto(representative,0));article.append(hero);
 const originals=[...new Set(items.map(r=>r.original).filter(Boolean))];if(originals.length)article.append(el('p',originals[0],'article-original'));
 $('count').textContent=items.length+'版型';
 const intro=(window.AWARD_INTROS||[]).find(entry=>((entry.families||[]).includes(items[0].family)||entry.names.includes(AtlasBook.heading(items[0])))&&(!entry.volumePattern||new RegExp(entry.volumePattern).test(items[0].volume)));
 if(intro){intro.paragraphs.forEach(text=>article.append(el('p',text,'article-intro')));
  if(intro.variants&&intro.variants.length){const history=el('section',null,'article-history');history.append(el('h3','版型沿革'));intro.variants.forEach(v=>{const entry=el('section',null,'history-entry');entry.append(el('h4',v.title));const reference=items.find(r=>r.id===v.referenceRecord&&r.photos.length);if(reference){const thumbnail=articlePhoto(reference,0);thumbnail.classList.add('history-thumbnail');entry.append(thumbnail);}entry.append(el('p',v.text));history.append(entry);});article.append(history);}
  if(intro.sources&&intro.sources.length){const refs=el('details',null,'article-references');refs.append(el('summary','参考资料'));intro.sources.forEach(source=>{if(!/^https?:\/\//.test(source.url))return;const link=el('a',source.title);link.href=source.url;link.target='_blank';link.rel='noopener noreferrer';refs.append(link);});article.append(refs);}
 }else{const dates=[...new Set(items.map(r=>r.date).filter(Boolean))];if(dates.length)article.append(el('p',dates.join('；'),'article-intro'));}

 const periods=new Map();items.forEach(r=>{if(!periods.has(r.volume))periods.set(r.volume,[]);periods.get(r.volume).push(r);});
 periods.forEach((variants,period)=>{const section=el('section',null,'article-period');section.id='period-'+period;section.append(el('h3',scopeTitle(period)));
  variants.forEach(row=>{const variant=el('section',null,'article-variant');variant.append(el('h4',AtlasBook.variantLabel(row.variant)||row.name));if(row.date)variant.append(el('p',row.date,'article-date'));if(row.original)variant.append(el('p',row.original,'article-original'));if(row.note)variant.append(el('p',row.note));
   const pictures=el('div',null,'article-photos');row.photos.forEach((p,i)=>pictures.append(articlePhoto(row,i)));variant.append(pictures);if(!row.photos.length)variant.append(el('p','有记载未配图'));
   const bookmark=el('button',state.favorites.has(row.id)?'已收藏':'收藏','bookmark');bookmark.onclick=()=>toggleFavorite(row);variant.append(bookmark);section.append(variant);
  });article.append(section);
 });$('results').append(article);
 if(window.AtlasFolio){const hint=pendingFolio;pendingFolio=null;requestAnimationFrame(()=>AtlasFolio.layout(selectedAward,hint));}


}
function articlePhoto(row,index){const p=row.photos[index],figure=el('figure'),b=el('button',null,'photo-button'),im=el('img');im.src=p.thumb||p.src;im.alt=p.alt||row.name;im.loading='lazy';b.setAttribute('aria-label','放大：'+(p.alt||row.name));b.append(im);b.onclick=()=>openPhoto(row,index);figure.append(b,el('figcaption',p.caption||''));return figure;}
function openPhoto(row,index){state.row=row;state.photo=index;updatePhoto();if(!$('viewer').open)$('viewer').showModal();}
function updatePhoto(){const r=state.row,p=r.photos[state.photo];$('full-photo').classList.remove('zoomed');$('zoom').textContent='放大';$('full-photo').src=p.src;$('full-photo').alt=p.alt||r.name;$('photo-caption').textContent=p.caption||p.alt;$('photo-number').textContent=`${state.photo+1} / ${r.photos.length}`;$('previous').disabled=state.photo===0;$('next').disabled=state.photo===r.photos.length-1;$('save').textContent=state.favorites.has(r.id)?'取消收藏':'收藏';$('detail').replaceChildren(el('p',r.name+' · '+r.original),el('p',r.date),el('p',r.variant));if(r.note)$('detail').append(el('p',r.note));r.sources.forEach(s=>{if(s.summary&&!r.photos.some(p=>p.reference))$('detail').append(el('p',s.summary));if(/^https?:\/\//.test(s.page||'')){const a=el('a','打开来源网页');a.href=s.page;a.rel='noopener noreferrer';a.target='_blank';$('detail').append(a);}});if(p.originalSrc){const originalButton=el('button','查看来源原图');let showingOriginal=false;originalButton.onclick=()=>{showingOriginal=!showingOriginal;$('full-photo').src=showingOriginal?p.originalSrc:p.src;originalButton.textContent=showingOriginal?'查看处理图':'查看来源原图';};$('detail').append(el('p',p.processing),originalButton);}if(p.credit)$('detail').append(el('p',p.credit));if(/^https?:\/\//.test(p.source||'')){const a=el('a','本图来源');a.href=p.source;a.target='_blank';a.rel='noopener noreferrer';$('detail').append(a);}if(!r.sources.length&&!p.source)$('detail').append(el('p','详细出处见原研究库对应条目。'));}
$('close-viewer').onclick=()=>$('viewer').close();$('zoom').onclick=()=>{$('full-photo').classList.toggle('zoomed');$('zoom').textContent=$('full-photo').classList.contains('zoomed')?'适应屏幕':'放大';};$('previous').onclick=()=>openPhoto(state.row,state.photo-1);$('next').onclick=()=>openPhoto(state.row,state.photo+1);$('save').onclick=()=>toggleFavorite(state.row);
let searchTimer=0,queryRevision=0,inkReady=Promise.resolve(),lastQuery=null;
function requestPageRender(back=false){clearTimeout(searchTimer);if(window.turnAtlasPageForSearch&&document.body.classList.contains('book-is-open'))window.turnAtlasPageForSearch(render,back);else render();}
let composing=false;
function cancelQueryTransition(){queryRevision++;clearTimeout(searchTimer);if(window.cancelAtlasSearchTurn)window.cancelAtlasSearchTurn();}
$('query').oncompositionstart=()=>{composing=true;lastQuery=null;cancelQueryTransition();};
$('query').oncompositionend=()=>{composing=false;$('query').oninput();};
$('query').oninput=()=>{if(composing)return;const text=$('query').value.trim();if(text===lastQuery)return;lastQuery=text;cancelQueryTransition();if(!text){if(window.withdrawAtlasPage)window.withdrawAtlasPage();render();return;}document.body.classList.add('has-results');if(document.body.classList.contains('book-is-open')&&window.projectAtlasPage)window.projectAtlasPage();const revision=queryRevision;state.limit=30;document.body.classList.add('query-writing');inkReady=Promise.resolve(writeBookQuery($('query').value.trim()));inkReady.then(()=>{if(revision===queryRevision)searchTimer=setTimeout(requestPageRender,120);});};
$('query').onkeydown=e=>{if(e.key==='Enter'&&!composing){e.preventDefault();$('query').blur();clearTimeout(searchTimer);const revision=queryRevision;inkReady.then(()=>{if(revision===queryRevision)requestPageRender();});}};
$('volume').onchange=()=>{state.limit=30;requestPageRender();};$('more').onclick=()=>{state.limit+=30;render();};
function navigate(tab){lastQuery=null;cancelQueryTransition();state.tab=tab;document.querySelectorAll('nav button').forEach(n=>{n.removeAttribute('aria-current');if(n.dataset.tab===(tab==='favorites'?'categories':tab))n.setAttribute('aria-current','page');});$('browse').hidden=tab==='settings'||tab==='categories';$('settings').hidden=tab!=='settings';$('categories').hidden=tab!=='categories';$('section-title').textContent=tab==='favorites'?'收藏':'图鉴';state.limit=30;render();window.scrollTo(0,0);if(tab==='categories'||tab==='settings'){document.body.classList.remove('book-is-open','has-results');if(window.resetBook)window.resetBook();}}
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{if(b.dataset.tab==='catalog'){$('query').value='';$('volume').value='';if(window.resetBook)window.resetBook();}navigate(b.dataset.tab);});
$('favorite-entry').onclick=()=>{$('query').value='';$('volume').value='';navigate('favorites');};
$('updates').onclick=()=>{if(location.host==='appassets.androidplatform.net'){location.href='medalatlas://updates';}else{window.open('https://github.com/ryoumiyahayato/world-medals/releases','_blank','noopener');$('update-status').textContent='';}};
async function startCatalog(){if(!window.CATALOG){catalogFailed();return;}const titles=new Map(CATALOG.volumes.map(v=>[v.id,v.title]));for(let i=0;i<CATALOG.rows.length;){const deadline=performance.now()+7;do{const r=CATALOG.rows[i++];r.searchIndex=AtlasSearch.prepare(r,titles.get(r.volume));}while(i<CATALOG.rows.length&&performance.now()<deadline);await new Promise(resolve=>setTimeout(resolve,0));}[{id:'france-timeline',title:'法国 · 历代奖励'},...CATALOG.volumes].forEach(v=>{const o=el('option',v.title);o.value=v.id;$('volume').append(o);});buildCategoryTree([{id:'france-timeline',title:'历代版型总览'},...CATALOG.volumes],id=>{$('query').value='';$('volume').value=id;navigate('catalog');});$('edition').textContent=`图鉴版本 v${(window.APP_VERSION||{name:"0.001"}).name}（dev）`;render();state.ready=true;}









