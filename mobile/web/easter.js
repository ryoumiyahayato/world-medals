/* Explicitly scoped to this app. Controls and award images never count as taps. */
(()=>{
 const page=document.getElementById('reading-book'),scroll=document.getElementById('page-scroll');
 let taps=[],pending=0,turning=false,exiting=false,pageNumber=1;
 function turn(){if(turning||!pending||exiting)return;turning=true;pending--;const leaf=document.createElement('div');leaf.className='turning-leaf';leaf.setAttribute('aria-hidden','true');page.append(leaf);
  setTimeout(()=>{leaf.remove();turning=false;pageNumber++;page.dataset.page=pageNumber;if(scroll.scrollHeight>scroll.clientHeight)scroll.scrollBy({top:scroll.clientHeight*.8,behavior:'smooth'});turn();},typeof motionReduced!=='undefined'&&motionReduced?40:420);
 }
 window.turnAtlasPage=()=>{pending++;turn();};
 let searchTurn=0;
 window.cancelAtlasSearchTurn=()=>{searchTurn++;page.querySelectorAll(".search-leaf").forEach(n=>n.remove());};
 window.turnAtlasPageForSearch=callback=>{window.cancelAtlasSearchTurn();const ticket=searchTurn;const leaf=document.createElement('div');leaf.className='turning-leaf search-leaf';leaf.setAttribute('aria-hidden','true');page.append(leaf);const reduced=typeof motionReduced!=='undefined'&&motionReduced;setTimeout(()=>{if(ticket===searchTurn){callback();scroll.scrollTop=0;}},reduced?0:210);setTimeout(()=>leaf.remove(),reduced?40:450);};
 function done(){if(location.host==='appassets.androidplatform.net'){location.href='medalatlas://easter-exit';return;}document.body.classList.remove('easter-running');document.body.classList.add('easter-finished');const b=document.createElement('button');b.id='restart-preview';b.textContent='重新打开图鉴';b.onclick=()=>location.reload();document.body.append(b);}
 function exit(){exiting=true;pending=0;document.body.classList.add('easter-running');document.body.classList.remove('book-is-open');document.getElementById('query').blur();if(window.closeAndSpinAtlasBook){window.closeAndSpinAtlasBook(done);}else{document.getElementById('book-fallback').classList.add('easter-spin');setTimeout(done,2400);}}
 page.addEventListener('click',e=>{if(exiting||e.target.closest('button,input,select,textarea,a,summary,table,details'))return;const now=performance.now();taps=taps.filter(t=>now-t<2200);taps.push(now);if(taps.length>=6){exit();return;}pending++;turn();});
})();
