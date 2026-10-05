/* Explicitly scoped to this app. Controls and award images never count as taps. */
(()=>{
 const page=document.getElementById('reading-book'),scroll=document.getElementById('page-scroll');
 let taps=[],pending=0,turning=false,exiting=false,pageNumber=1;
 function turn(){if(turning||!pending||exiting)return;turning=true;pending--;if(window.readerNext)window.readerNext();
  setTimeout(()=>{turning=false;turn();},typeof motionReduced!=='undefined'&&motionReduced?40:420);
 }
 window.turnAtlasPage=()=>{pending++;turn();};
 let searchTurn=0;
 window.cancelAtlasSearchTurn=()=>{searchTurn++;if(window.cancelAtlasProjection)window.cancelAtlasProjection();page.querySelectorAll(".search-leaf").forEach(n=>n.remove());};
 window.turnAtlasPageForSearch=(callback,back=false)=>{window.cancelAtlasSearchTurn();if(window.flyAtlasPage){window.flyAtlasPage(callback,back);return;}callback();};
 function done(){if(location.host==='appassets.androidplatform.net'){location.href='medalatlas://easter-exit';return;}document.body.classList.remove('easter-running');document.body.classList.add('easter-finished');const b=document.createElement('button');b.id='restart-preview';b.textContent='重新打开图鉴';b.onclick=()=>location.reload();document.body.append(b);}
 function exit(){exiting=true;pending=0;if(window.cancelAtlasSearchTurn)window.cancelAtlasSearchTurn();document.body.classList.add('easter-running');document.body.classList.remove('book-is-open');document.getElementById('query').blur();if(window.closeAndSpinAtlasBook){window.closeAndSpinAtlasBook(done);}else{document.getElementById('book-fallback').classList.add('easter-spin');setTimeout(done,2400);}}
 window.noteAtlasTap=()=>{if(exiting)return true;const now=performance.now();taps=taps.filter(t=>now-t<2200);taps.push(now);if(taps.length>=6){exit();return true;}return false;};
 window.readerTurn=(back=false)=>{if(exiting||window.noteAtlasTap())return;if(document.body.classList.contains('page-expanding'))return;if(!document.body.classList.contains('has-results')){if(window.animateAtlasLeaf)window.animateAtlasLeaf(back?'back':'next');return;}if(back){if(window.readerBack)window.readerBack();}else if(window.readerNext)window.readerNext();};
 document.getElementById('projection-next').onclick=()=>window.readerTurn(false);
 document.getElementById('projection-previous').onclick=()=>window.readerTurn(true);
 document.getElementById('book-next').onclick=()=>window.readerTurn(false);
 document.getElementById('book-previous').onclick=()=>window.readerTurn(true);
 page.addEventListener('click',e=>{if(exiting||document.body.classList.contains('page-expanding')||e.target.closest('button,input,select,textarea,a,summary,table,details'))return;const rect=page.getBoundingClientRect();window.readerTurn(e.clientX<rect.left+rect.width/2);});
 document.addEventListener('click',e=>{if(document.body.classList.contains('page-expanding')||!document.body.classList.contains('book-is-open')||!document.body.classList.contains('page-projected')||e.target.closest('#reading-book,#home-book,.filters,nav,dialog,button,input,select,textarea,a,summary'))return;if(window.noteAtlasTap())return;if(window.withdrawAtlasPage)window.withdrawAtlasPage();});
})();
