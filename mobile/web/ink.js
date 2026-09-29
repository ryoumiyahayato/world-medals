/* Local stroke data; IME composition is handled by the search input. */
(()=>{let generation=0,lastText='',writers=[];
window.writeBookQuery=async text=>{
 if(text===lastText)return;lastText=text;const ticket=++generation;
 writers.forEach(w=>w.hideCharacter({duration:0}));writers=[];
 const target=document.getElementById('written-query');target.replaceChildren();target.setAttribute('aria-label',text);
 const reduced=document.body.classList.contains('reduce-motion')||matchMedia('(prefers-reduced-motion: reduce)').matches;
 if(reduced){target.textContent=text;return;}
 for(const char of Array.from(text)){
  if(ticket!==generation)return;
  const span=document.createElement('span');span.className='ink-character';span.setAttribute('aria-hidden','true');target.append(span);
  if(/\p{Script=Han}/u.test(char)&&window.HanziWriter){
   try{
    const response=await fetch('vendor/strokes/'+encodeURIComponent(char)+'.json');if(!response.ok)throw Error('No stroke data');const data=await response.json();if(ticket!==generation)return;
    span.classList.add('han-writing');const size=parseFloat(getComputedStyle(target).fontSize);
    const writer=HanziWriter.create(span,char,{width:size,height:size,padding:0,showCharacter:false,showOutline:false,strokeColor:'#493e2f',strokeAnimationSpeed:18,delayBetweenStrokes:4,charDataLoader:()=>data});writers.push(writer);
    await Promise.race([writer.animateCharacter(),new Promise(r=>setTimeout(r,Math.max(45,Math.min(180,540/Array.from(text).length))))]);if(ticket!==generation)return;
    span.replaceChildren();span.classList.remove('han-writing');span.textContent=char;
   }catch{if(ticket!==generation)return;span.textContent=char;await new Promise(r=>setTimeout(r,25));}
  }else{span.textContent=char;await new Promise(r=>setTimeout(r,25));}
 }
};})();
