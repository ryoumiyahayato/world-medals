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
const shapes=[['皇冠','M3 9 8 14 12 5 16 14 21 9 19 21H5Z'],['火炬','M10 15h4l-1 8h-2Zm2-13c6 5 7 9 2 11H9C4 10 9 6 12 2Z'],['镰锤','M7 3C21 3 24 17 13 21M13 21 4 12M5 16 17 4M13 3l6 6M4 19l2 2'],['和平鸽','M3 14 10 13 7 4 15 10C20 5 23 9 20 12L23 14 19 15C15 23 8 19 3 21L7 16Z'],['铁十字','M8 2h8l-2 7 8-1v8l-8-2 2 8H8l2-8-8 2V8l8 1Z']];
function makeMotifs(){
 $('motifs').replaceChildren();for(let i=0;i<20;i++){const [name,path]=shapes[i%5],b=document.createElement('button');b.setAttribute('aria-label',name+'，点击掉落');
 const col=i%4,row=Math.floor(i/4);b.style.left=(4+col*24+(row%2)*2)+'%';b.style.top=(5+row*16+(col%2)*3)+'%';b.style.width=b.style.height=(42+(i%3)*5)+'px';b.style.animationDuration=(7+(i%7)*.65)+'s';b.style.animationDelay=(-i*.71)+'s';
 b.innerHTML=`<svg viewBox="0 0 24 26" aria-hidden="true"><path d="${path}"/></svg>`;b.onclick=()=>{b.classList.add('falling');b.disabled=true;setTimeout(()=>b.remove(),motionReduced?0:800);};$('motifs').append(b);}
}
let animationFrame=0,animationStarted=0,skipRequested=false;
function finishSplash(){if(!state.ready){skipRequested=true;return;}$('splash').hidden=true;$('splash').style.display='none';document.body.classList.remove('is-loading');cancelAnimationFrame(animationFrame);}
function playSplash(){cancelAnimationFrame(animationFrame);skipRequested=false;makeMotifs();document.body.classList.add('is-loading');$('splash').hidden=false;$('splash').style.display='flex';animationStarted=performance.now();
 const resize=()=>{$('track').style.setProperty('--travel',Math.max(0,$('track').clientWidth-56)+'px');};resize();window.addEventListener('resize',resize,{once:true});
 const tick=now=>{if(state.ready&&(skipRequested||now-animationStarted>(motionReduced?150:2650))){finishSplash();return;}animationFrame=requestAnimationFrame(tick);};animationFrame=requestAnimationFrame(tick);
}
$('skip').onclick=finishSplash;$('replay').onclick=playSplash;$('reduced').checked=motionReduced;
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
 row.photos.forEach((p,i)=>{const b=el('button',null,'photo-button');b.setAttribute('aria-label','放大：'+(p.alt||row.name));const im=el('img');im.src=p.src;im.alt=p.alt||row.name;im.loading='lazy';im.decoding='async';b.append(im,el('span',p.caption));b.onclick=()=>openPhoto(row,i);picture.append(b);});if(!row.photos.length)picture.textContent='有记载未配图';tr.append(name,kind,picture);return tr;
}
let expanded=new Set(), selectedAward=null, readerScope="", readerGroups=[], pendingPeriod=null;
function bookRenderTurn(){requestPageRender();}
window.readerBack=()=>{if(selectedAward){selectedAward=null;bookRenderTurn();return true;}if($("volume").value){$("volume").value="";bookRenderTurn();return true;}return false;};
window.readerNext=()=>{if(!selectedAward)return false;const i=readerGroups.findIndex(([key])=>key===selectedAward);if(i<readerGroups.length-1){selectedAward=readerGroups[i+1][0];bookRenderTurn();}return true;};
function render(){
 if(!window.CATALOG)return;
 const query=$('query').value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean),volume=$('volume').value;
 const matching=CATALOG.rows.map(r=>({r,score:AtlasSearch.score($('query').value,r.searchIndex)})).filter(x=>x.score>0&&(state.tab!=='favorites'||state.favorites.has(x.r.id))).sort((a,b)=>b.score-a.score).map(x=>x.r);
 const browsing=!!volume;
 document.body.classList.toggle('has-results',browsing||query.length>0||state.tab==='favorites');
 if((browsing||query.length>0||state.tab==='favorites')&&window.openBookInstant)window.openBookInstant();
 const scope=volume+'|'+$('query').value+'|'+state.tab;if(scope!==readerScope){selectedAward=null;readerScope=scope;}
 $('home-book').hidden=false;writeBookQuery('');document.body.classList.remove('query-writing');
 const active=browsing||query.length>0||state.tab==='favorites';
 document.querySelector('.section-heading').hidden=!active;
 $('country-matches').replaceChildren();$('country-matches').hidden=true;$('results').replaceChildren();$('more').hidden=true;$('empty').hidden=true;
 if(!active)return;
 const scoped=matching.filter(r=>!volume||(volume==='france-timeline'?scopeOf(r)===volume:r.volume===volume));
 const allowed=CATALOG.rows.filter(r=>(!volume||(volume==='france-timeline'?scopeOf(r)===volume:r.volume===volume))&&(state.tab!=='favorites'||state.favorites.has(r.id)));
 readerGroups=AtlasBook.groups(scoped,allowed);
 const total=readerGroups.reduce((n,[,items])=>n+items.length,0);$('count').textContent=`${readerGroups.length}章种 · ${total}版型`;
 if(!readerGroups.length){$('empty').hidden=false;return;}
 if(!selectedAward){
  $('results').append(el('h2','目录','directory-title'));
  const headings=new Map();readerGroups.forEach(entry=>{const title=AtlasBook.heading(entry[1][0]);if(!headings.has(title))headings.set(title,[]);headings.get(title).push(entry);});
  headings.forEach((entries,title)=>{
   const fold=el('details',null,'encyclopedia-directory'),summary=el('summary',title);fold.append(summary);fold.open=!!query.length;
   entries.forEach(([key,items])=>{const branch=el('div',null,'country-family');const first=items[0],route=window.CATEGORY_ROUTES[first.volume];const country=route?route[2]:scopeTitle(first.volume);
    const open=el('button',country,'country-family-title');open.onclick=()=>{selectedAward=key;pendingPeriod=null;bookRenderTurn();};branch.append(open);
    const periods=[...new Set(items.slice().sort((a,b)=>editionKey(a)-editionKey(b)).map(r=>r.volume))];periods.forEach(period=>{const link=el('button',scopeTitle(period),'period-link');link.onclick=()=>{selectedAward=key;pendingPeriod=period;bookRenderTurn();};branch.append(link);});fold.append(branch);
   });$('results').append(fold);
  });return;
 }
 const index=readerGroups.findIndex(([key])=>key===selectedAward);if(index<0){selectedAward=null;render();return;}
 const items=readerGroups[index][1];items.sort((a,b)=>editionKey(a)-editionKey(b));
 const article=el('article',null,'award-article'),hero=el('div',null,'article-hero'),titleBlock=el('div');
 titleBlock.append(el('h2',AtlasBook.heading(items[0]),'award-page-title'));const route=window.CATEGORY_ROUTES[items[0].volume];titleBlock.append(el('p',scopeTitle(items[0].volume),'article-country'));hero.append(titleBlock);
 const representative=items.find(r=>r.photos.length);if(representative)hero.append(articlePhoto(representative,0));article.append(hero);
 const originals=[...new Set(items.map(r=>r.original).filter(Boolean))];if(originals.length)article.append(el('p',originals[0],'article-original'));
 $('count').textContent=items.length+'版型';
 const intro=(window.AWARD_INTROS||[]).find(entry=>entry.names.includes(AtlasBook.heading(items[0]))&&(!entry.volumePattern||new RegExp(entry.volumePattern).test(items[0].volume)));
 if(intro){intro.paragraphs.forEach(text=>article.append(el('p',text,'article-intro')));
  if(intro.variants&&intro.variants.length){const history=el('section',null,'article-history');history.append(el('h3','版型沿革'));intro.variants.forEach(v=>{history.append(el('h4',v.title),el('p',v.text));});article.append(history);}
  if(intro.sources&&intro.sources.length){const refs=el('details',null,'article-references');refs.append(el('summary','参考资料'));intro.sources.forEach(source=>{if(!/^https?:\/\//.test(source.url))return;const link=el('a',source.title);link.href=source.url;link.target='_blank';link.rel='noopener noreferrer';refs.append(link);});article.append(refs);}
 }else{const dates=[...new Set(items.map(r=>r.date).filter(Boolean))];if(dates.length)article.append(el('p',dates.join('；'),'article-intro'));}

 const periods=new Map();items.forEach(r=>{if(!periods.has(r.volume))periods.set(r.volume,[]);periods.get(r.volume).push(r);});
 periods.forEach((variants,period)=>{const section=el('section',null,'article-period');section.id='period-'+period;section.append(el('h3',scopeTitle(period)));
  variants.forEach(row=>{const variant=el('section',null,'article-variant');variant.append(el('h4',row.variant||row.name));if(row.date)variant.append(el('p',row.date,'article-date'));if(row.original)variant.append(el('p',row.original,'article-original'));if(row.note)variant.append(el('p',row.note));
   const pictures=el('div',null,'article-photos');row.photos.forEach((p,i)=>pictures.append(articlePhoto(row,i)));variant.append(pictures);if(!row.photos.length)variant.append(el('p','有记载未配图'));
   const bookmark=el('button',state.favorites.has(row.id)?'已收藏':'收藏','bookmark');bookmark.onclick=()=>toggleFavorite(row);variant.append(bookmark);section.append(variant);
  });article.append(section);
 });$('results').append(article);
 if(pendingPeriod){const id=pendingPeriod;pendingPeriod=null;requestAnimationFrame(()=>{const section=document.getElementById('period-'+id);if(section)$('page-scroll').scrollTop=section.offsetTop-$('page-scroll').offsetTop-10;});}


}
function articlePhoto(row,index){const p=row.photos[index],figure=el('figure'),b=el('button',null,'photo-button'),im=el('img');im.src=p.src;im.alt=p.alt||row.name;im.loading='lazy';b.setAttribute('aria-label','放大：'+(p.alt||row.name));b.append(im);b.onclick=()=>openPhoto(row,index);figure.append(b,el('figcaption',p.caption||''));return figure;}
function openPhoto(row,index){state.row=row;state.photo=index;updatePhoto();if(!$('viewer').open)$('viewer').showModal();}
function updatePhoto(){const r=state.row,p=r.photos[state.photo];$('full-photo').classList.remove('zoomed');$('zoom').textContent='放大';$('full-photo').src=p.src;$('full-photo').alt=p.alt||r.name;$('photo-caption').textContent=p.caption||p.alt;$('photo-number').textContent=`${state.photo+1} / ${r.photos.length}`;$('previous').disabled=state.photo===0;$('next').disabled=state.photo===r.photos.length-1;$('save').textContent=state.favorites.has(r.id)?'取消收藏':'收藏';$('detail').replaceChildren(el('p',r.name+' · '+r.original),el('p',r.date),el('p',r.variant));if(r.note)$('detail').append(el('p',r.note));r.sources.forEach(s=>{if(s.summary)$('detail').append(el('p',s.summary));if(/^https?:\/\//.test(s.page||'')){const a=el('a','打开来源网页');a.href=s.page;a.rel='noopener noreferrer';a.target='_blank';$('detail').append(a);}});if(p.originalSrc){const originalButton=el('button','查看来源原图');let showingOriginal=false;originalButton.onclick=()=>{showingOriginal=!showingOriginal;$('full-photo').src=showingOriginal?p.originalSrc:p.src;originalButton.textContent=showingOriginal?'查看处理图':'查看来源原图';};$('detail').append(el('p',p.processing),originalButton);}if(p.rights)$('detail').append(el('p',p.rights));if(p.credit)$('detail').append(el('p',p.credit));if(/^https?:\/\//.test(p.source||'')){const a=el('a','本图来源');a.href=p.source;a.target='_blank';a.rel='noopener noreferrer';$('detail').append(a);}if(!r.sources.length&&!p.source)$('detail').append(el('p','详细出处见原研究库对应条目。'));}
$('close-viewer').onclick=()=>$('viewer').close();$('zoom').onclick=()=>{$('full-photo').classList.toggle('zoomed');$('zoom').textContent=$('full-photo').classList.contains('zoomed')?'适应屏幕':'放大';};$('previous').onclick=()=>openPhoto(state.row,state.photo-1);$('next').onclick=()=>openPhoto(state.row,state.photo+1);$('save').onclick=()=>toggleFavorite(state.row);
let searchTimer=0,queryRevision=0,inkReady=Promise.resolve(),lastQuery=null;
function requestPageRender(){clearTimeout(searchTimer);if(window.turnAtlasPageForSearch&&document.body.classList.contains('book-is-open'))window.turnAtlasPageForSearch(render);else render();}
let composing=false;
function cancelQueryTransition(){queryRevision++;clearTimeout(searchTimer);if(window.cancelAtlasSearchTurn)window.cancelAtlasSearchTurn();}
$('query').oncompositionstart=()=>{composing=true;lastQuery=null;cancelQueryTransition();};
$('query').oncompositionend=()=>{composing=false;$('query').oninput();};
$('query').oninput=()=>{if(composing)return;const text=$('query').value.trim();if(text===lastQuery)return;lastQuery=text;cancelQueryTransition();const revision=queryRevision;state.limit=30;document.body.classList.add('query-writing');inkReady=Promise.resolve(writeBookQuery($('query').value.trim()));inkReady.then(()=>{if(revision===queryRevision)searchTimer=setTimeout(requestPageRender,120);});};
$('query').onkeydown=e=>{if(e.key==='Enter'&&!composing){e.preventDefault();$('query').blur();clearTimeout(searchTimer);const revision=queryRevision;inkReady.then(()=>{if(revision===queryRevision)requestPageRender();});}};
$('volume').onchange=()=>{state.limit=30;requestPageRender();};$('more').onclick=()=>{state.limit+=30;render();};
function navigate(tab){lastQuery=null;cancelQueryTransition();state.tab=tab;document.querySelectorAll('nav button').forEach(n=>{n.removeAttribute('aria-current');if(n.dataset.tab===(tab==='favorites'?'categories':tab))n.setAttribute('aria-current','page');});$('browse').hidden=tab==='settings'||tab==='categories';$('settings').hidden=tab!=='settings';$('categories').hidden=tab!=='categories';$('section-title').textContent=tab==='favorites'?'收藏':'图鉴';state.limit=30;render();window.scrollTo(0,0);}
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{if(b.dataset.tab==='catalog'){$('query').value='';$('volume').value='';if(window.resetBook)window.resetBook();}navigate(b.dataset.tab);});
$('favorite-entry').onclick=()=>{$('query').value='';$('volume').value='';navigate('favorites');};
$('updates').onclick=()=>{if(location.host==='appassets.androidplatform.net'){location.href='medalatlas://updates';}else{window.open('https://github.com/ryoumiyahayato/world-medals/releases','_blank','noopener');$('update-status').textContent='';}};
async function startCatalog(){if(!window.CATALOG){catalogFailed();return;}const titles=new Map(CATALOG.volumes.map(v=>[v.id,v.title]));for(let i=0;i<CATALOG.rows.length;){const deadline=performance.now()+7;do{const r=CATALOG.rows[i++];r.searchIndex=AtlasSearch.prepare(r,titles.get(r.volume));}while(i<CATALOG.rows.length&&performance.now()<deadline);await new Promise(resolve=>setTimeout(resolve,0));}[{id:'france-timeline',title:'法国 · 历代奖励'},...CATALOG.volumes].forEach(v=>{const o=el('option',v.title);o.value=v.id;$('volume').append(o);});buildCategoryTree([{id:'france-timeline',title:'历代版型总览'},...CATALOG.volumes],id=>{$('query').value='';$('volume').value=id;navigate('catalog');});$('edition').textContent=`图鉴版本 v${(window.APP_VERSION||{name:"0.001"}).name}（dev）`;render();state.ready=true;}









$('authorize-updates').onclick=()=>{if(location.host==='appassets.androidplatform.net')location.href='medalatlas://authorize';else{window.open('https://github.com/settings/personal-access-tokens/new?name=World%20Medals%20Android&target_name=ryoumiyahayato&expires_in=90&contents=read','_blank','noopener');$('update-status').textContent='只选择 world-medals，Contents 设为 Read-only；生成后在手机 APK 的本机授权框填写。';}};

