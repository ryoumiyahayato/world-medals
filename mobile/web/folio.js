/* A printed text column is one physical page; vertical scrolling is disabled. */
(()=>{
 const host=document.getElementById('results'),book=document.getElementById('reading-book');
 let key='',page=0,total=1,frame=0;
 function show(){const article=host.querySelector('.award-article');if(!article||!host.clientWidth||!host.clientHeight)return;const step=host.clientWidth+32;total=Math.max(1,Math.ceil((article.scrollWidth+32)/step));page=Math.min(page,total-1);article.style.transform=`translateX(${-page*step}px)`;book.dataset.page=(page+1)+' / '+total;}
 function layout(next,hint=null){if(key!==next){key=next;page=0;}if(hint==='last')page=Number.MAX_SAFE_INTEGER;else if(Number.isInteger(hint))page=hint;const article=host.querySelector('.award-article');if(!article||!host.clientWidth||!host.clientHeight)return;article.style.columnWidth=host.clientWidth+'px';article.querySelectorAll('img').forEach(im=>{im.loading='eager';im.addEventListener('load',show,{once:true});});cancelAnimationFrame(frame);frame=requestAnimationFrame(show);}
 function move(delta){if(!delta||page+delta<0||page+delta>=total)return false;const go=()=>{page+=delta;show();};if(window.turnAtlasPageForSearch)window.turnAtlasPageForSearch(go,delta<0);else go();return true;}
 window.AtlasFolio={layout,position:()=>({page,total}),next:()=>move(1),previous:()=>move(-1),first:()=>move(-page),last:()=>move(total-1-page)};
 let effect=null,motion=0,withdrawing=false;
 const reduced=()=>typeof motionReduced!=='undefined'&&motionReduced;
 function fitProjection(){
  const h=window.visualViewport?visualViewport.height:innerHeight,w=window.visualViewport?visualViewport.width:innerWidth;
  const available=Math.max(100,h-(h<500?155:220));
  const width=Math.min(w-32,available*.7,460),height=width/ .7;
  document.documentElement.style.setProperty('--projection-width',width+'px');
  document.documentElement.style.setProperty('--projection-height',height+'px');
  document.documentElement.style.setProperty('--projection-top',Math.max(12,(available-height)/2+12)+'px');
 }
 function origin(side='right'){const from=window.atlasPageRect?window.atlasPageRect(side):window.atlasRightPageRect?window.atlasRightPageRect():document.querySelector('.fallback-pages').getBoundingClientRect();const to=book.getBoundingClientRect();return `translate(calc(-50% + ${from.left+from.width/2-to.left-to.width/2}px),${from.top+from.height/2-to.top-to.height/2}px) perspective(1000px) rotateX(55deg) scale(${Math.min(.6,from.width/to.width)})`;}
 function cancel(){motion++;if(effect){effect.cancel();effect=null;}withdrawing=false;document.body.classList.remove('page-expanding');}
 function animate(frames,duration,callback){const ticket=motion;if(reduced()||!book.animate){if(callback)callback();return;}effect=book.animate(frames,{duration,easing:'cubic-bezier(.22,.72,.25,1)',fill:'both'});effect.onfinish=()=>{if(ticket!==motion)return;effect.cancel();effect=null;if(callback)callback();};}
 window.cancelAtlasProjection=cancel;
 window.projectAtlasPage=(side='right')=>{
  if(!document.body.classList.contains('has-results')||!document.body.classList.contains('book-is-open')||document.body.classList.contains('easter-running')||document.body.classList.contains('page-projected'))return;
  cancel();fitProjection();if(window.animateAtlasLeaf)window.animateAtlasLeaf(side==='left'?'back':'project');document.body.classList.add('page-projected','page-expanding');
  animate([{transform:origin(side),opacity:0,filter:'blur(2px)'},{transform:'translateX(-50%)',opacity:1,filter:'blur(0px)'}],560,()=>document.body.classList.remove('page-expanding'));
 };
 window.expandAtlasPage=window.projectAtlasPage;
 window.withdrawAtlasPage=callback=>{
  if(withdrawing)return;if(!document.body.classList.contains('page-projected')){if(callback)callback();return;}
  cancel();withdrawing=true;if(window.animateAtlasLeaf)window.animateAtlasLeaf('withdraw');
  animate([{transform:'translateX(-50%)',opacity:1},{transform:origin(),opacity:0,filter:'blur(2px)'}],360,()=>{withdrawing=false;document.body.classList.remove('page-projected');if(callback)callback();});
 };
 window.flyAtlasPage=(callback,back=false)=>{
  cancel();const side=back===true?'left':'right';if(!document.body.classList.contains('page-projected')){callback();window.projectAtlasPage(side);return;}
  if(window.animateAtlasLeaf)window.animateAtlasLeaf(back===true?'back':'next');const direction=back===true?-1:1;document.body.classList.add('page-expanding');
  animate([{transform:'translateX(-50%)',opacity:1},{transform:back==='up'?`translate(-50%,-${innerHeight}px)`:`translateX(calc(-50% + ${direction*innerWidth}px)) rotate(${direction*8}deg)`,opacity:0}],180,()=>{
   callback();fitProjection();if(!document.body.classList.contains('has-results')){document.body.classList.remove('page-projected','page-expanding');return;}
   animate([{transform:origin(side),opacity:0},{transform:'translateX(-50%)',opacity:1}],360,()=>document.body.classList.remove('page-expanding'));
  });
 };
 fitProjection();
 window.addEventListener('resize',fitProjection);
 if(window.visualViewport)visualViewport.addEventListener('resize',fitProjection);
 if(window.ResizeObserver)new ResizeObserver(()=>{if(document.body.classList.contains('article-reading'))layout(key);}).observe(host);
 window.addEventListener('resize',()=>{if(document.body.classList.contains('article-reading'))layout(key);});
 if(document.fonts)document.fonts.ready.then(()=>{if(document.body.classList.contains('article-reading'))layout(key);});
})();
