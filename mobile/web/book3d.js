/* Local geometry, not a flattened image: board, spine, page block and hinged leaves. */
(()=>{
 const host=document.getElementById('book-stage'),trigger=document.getElementById('book-open');
 function refreshFallback(){document.querySelector('.fallback-cover').style.backgroundImage=read('coverFront',null)?`url(${read('coverFront',null)})`:'';const back=document.querySelector('.fallback-back');if(back)back.style.backgroundImage=read('coverBack',null)?`url(${read('coverBack',null)})`:'';}
 refreshFallback();window.addEventListener('atlas-covers-changed',refreshFallback);
 let opened=false,opening=false,dragStart=null,dragMoved=false,suppressClick=0,targetYaw=.38,targetPitch=-.42,currentYaw=.38,currentPitch=-.42,velocity=0;
 function reveal(){opening=false;document.body.classList.add('book-is-open');trigger.setAttribute('aria-expanded','true');}
 window.resetBook=()=>{opened=false;opening=false;document.body.classList.remove('book-is-open');trigger.setAttribute('aria-expanded','false');};
 window.openBookInstant=()=>{opened=true;document.body.classList.add('book-is-open');};
 trigger.setAttribute('aria-expanded','false');
 trigger.onclick=()=>{if(performance.now()<suppressClick||opening||opened)return;opened=true;opening=true;velocity=0;trigger.setAttribute('aria-expanded','true');if(window.animateAtlasBook)window.animateAtlasBook();else{document.body.classList.add('book-is-open');setTimeout(reveal,typeof motionReduced!=='undefined'&&motionReduced?0:950);}};
 trigger.onpointerdown=e=>{if(opened||e.button>0)return;dragStart={x:e.clientX,y:e.clientY,lastX:e.clientX};dragMoved=false;velocity=0;trigger.setPointerCapture(e.pointerId);};
 trigger.onpointermove=e=>{if(!dragStart)return;const dx=e.clientX-dragStart.lastX;dragStart.lastX=e.clientX;if(Math.abs(e.clientX-dragStart.x)+Math.abs(e.clientY-dragStart.y)>7)dragMoved=true;if(dragMoved){e.preventDefault();targetYaw+=dx*.012;targetPitch=Math.max(-1.1,Math.min(1.1,targetPitch+(e.clientY-dragStart.y)*.001));velocity=dx*.006;if(window.requestBookFrame)window.requestBookFrame();else document.getElementById('book-fallback').style.transform=`translate(-50%,-50%) perspective(900px) rotateX(${targetPitch}rad) rotateY(${targetYaw}rad)`;}};
 trigger.onpointerup=()=>{if(dragMoved)suppressClick=performance.now()+350;dragStart=null;};trigger.onpointercancel=()=>{dragStart=null;velocity=0;suppressClick=performance.now()+350;};
 try{
  if(!window.THREE)throw new Error('3D library unavailable');
  const T=window.THREE,scene=new T.Scene(),camera=new T.PerspectiveCamera(36,1,.1,50);
  camera.position.set(0,0,8.4);
  const renderer=new T.WebGLRenderer({alpha:true,antialias:true,powerPreference:'low-power'});
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.7));renderer.setClearColor(0,0);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.3;
  host.append(renderer.domElement);host.classList.add('webgl-ready');
  scene.add(new T.AmbientLight(0xffffff,.6));scene.add(new T.HemisphereLight(0xe5edff,0x26303f,2.2));const key=new T.DirectionalLight(0xffecd0,3.1);key.position.set(-3,5,6);scene.add(key);const rim=new T.DirectionalLight(0xa7caff,2);rim.position.set(4,1,-2);scene.add(rim);
  const root=new T.Group();scene.add(root);root.rotation.set(-.42,.38,-.09);
  const canvas=document.createElement('canvas');canvas.width=canvas.height=128;const ctx=canvas.getContext('2d');const pixels=ctx.createImageData(128,128);for(let i=0;i<pixels.data.length;i+=4){const n=100+((i*17+(i%127)*29)%70);pixels.data[i]=pixels.data[i+1]=pixels.data[i+2]=n;pixels.data[i+3]=255;}ctx.putImageData(pixels,0,0);const bump=new T.CanvasTexture(canvas);bump.wrapS=bump.wrapT=T.RepeatWrapping;bump.repeat.set(6,8);
  const cloth=new T.MeshStandardMaterial({color:0x26394c,roughness:.86,metalness:.08,bumpMap:bump,bumpScale:.015});
  const paperTexture=new T.TextureLoader().load('paper.png',()=>{if(window.requestBookFrame)window.requestBookFrame();});paperTexture.colorSpace=T.SRGBColorSpace;
  const paper=new T.MeshStandardMaterial({color:0xf4eddc,map:paperTexture,roughness:.96,bumpMap:paperTexture,bumpScale:.006});
  const box=(w,h,d,mat,parent,x=0,y=0,z=0)=>{const m=new T.Mesh(new T.BoxGeometry(w,h,d),mat);m.position.set(x,y,z);parent.add(m);return m;};
  const backBoard=box(2.04,2.86,.07,cloth,root,0,0,-.24);
  box(1.94,2.72,.40,paper,root,.025,0,0);
  const edge=new T.MeshStandardMaterial({color:0xbfb297,roughness:1});for(let i=0;i<22;i++){box(1.95,.006,.006,edge,root,.026,-1.354,-.185+i*.0176);box(.005,2.70,.004,edge,root,.997,0,-.185+i*.0176);}
  const spine=new T.Mesh(new T.CylinderGeometry(.25,.25,2.84,20,1,false,Math.PI,Math.PI),cloth);spine.position.set(-.97,0,0);root.add(spine);
  const hinge=new T.Group();hinge.position.set(-1,0,.25);root.add(hinge);
  const frontBoard=box(2.04,2.86,.065,cloth,hinge,1,0,0);
  let coverMaterials=[];function updateCovers(){coverMaterials.forEach(m=>{if(m.map)m.map.dispose();m.dispose();});coverMaterials=[];for(const [board,key,face] of [[frontBoard,'coverFront',4],[backBoard,'coverBack',5]]){const mats=[cloth,cloth,cloth,cloth,cloth,cloth],data=read(key,null);if(data){const tex=new T.TextureLoader().load(data,()=>{if(window.requestBookFrame)window.requestBookFrame();});tex.colorSpace=T.SRGBColorSpace;const m=new T.MeshStandardMaterial({map:tex,roughness:.78,bumpMap:bump,bumpScale:.008});mats[face]=m;coverMaterials.push(m);}board.material=mats;}const fallback=document.querySelector('.fallback-cover');fallback.style.backgroundImage=read('coverFront',null)?`url(${read('coverFront',null)})`:'';fallback.style.backgroundSize='cover';}
  updateCovers();window.addEventListener('atlas-covers-changed',()=>{updateCovers();schedule();});
  box(1.9,2.70,.009,paper,hinge,1,0,-.038);
  const leaves=[];for(let i=0;i<3;i++){const pivot=new T.Group();pivot.position.set(-.94,0,.20-i*.007);root.add(pivot);box(1.87,2.69,.005,paper,pivot,.935,0,0);leaves.push(pivot);}
  // Soft local contact shadow remains transparent around the geometry.
  const shadowCanvas=document.createElement('canvas');shadowCanvas.width=256;shadowCanvas.height=256;const sc=shadowCanvas.getContext('2d'),g=sc.createRadialGradient(128,128,1,128,128,120);g.addColorStop(0,'rgba(0,0,0,.38)');g.addColorStop(1,'rgba(0,0,0,0)');sc.fillStyle=g;sc.fillRect(0,0,256,256);const shadow=new T.Mesh(new T.PlaneGeometry(3.4,.55),new T.MeshBasicMaterial({map:new T.CanvasTexture(shadowCanvas),transparent:true,depthWrite:false}));shadow.position.set(0,-2.2,-.5);scene.add(shadow);
  let openingAt=0,progress=0,last=0,raf=0,closingAt=0,spinningAt=0,exitCallback=null,finished=false,normalClose=false;
  function resize(){const w=host.clientWidth,h=host.clientHeight;if(!w||!h)return;renderer.setSize(w,h,false);camera.aspect=w/h;camera.position.z=Math.max(3.6/(2*Math.tan(Math.PI/10)),3.25/(2*Math.tan(Math.PI/10)*camera.aspect));camera.updateProjectionMatrix();}
  new ResizeObserver(resize).observe(host);resize();
  window.animateAtlasBook=()=>{openingAt=performance.now();if(typeof motionReduced!=='undefined'&&motionReduced){progress=1;reveal();}schedule();};
  window.closeAndSpinAtlasBook=callback=>{normalClose=false;exitCallback=callback;closingAt=performance.now();opened=true;opening=false;document.body.classList.remove('book-is-open');schedule();};
  window.closeAtlasBook=()=>{normalClose=true;closingAt=performance.now();opened=true;opening=false;document.body.classList.remove('book-is-open');schedule();};
  function schedule(){if(!raf)raf=requestAnimationFrame(frame);}
  window.requestBookFrame=schedule;
  function frame(now){raf=0;if(finished||document.body.classList.contains('is-loading')||document.hidden||document.getElementById('home-book').hidden||document.getElementById('browse').hidden||(document.body.classList.contains('book-is-open')&&!opening)){last=0;return;}
   last=now;
   if(closingAt){progress=Math.max(0,1-(now-closingAt)/650);if(progress<=0){closingAt=0;opened=false;if(!normalClose)spinningAt=now;trigger.setAttribute('aria-expanded','false');}}
   else if(!opened){progress=0;openingAt=0;}
   else if(openingAt&&opening){progress=Math.min(1,(now-openingAt)/1150);if(progress>=1)reveal();}
   else if(opened)progress=1;
   const ease=progress*progress*(3-2*progress),still=typeof motionReduced!=='undefined'&&motionReduced;
   hinge.rotation.y=-ease*Math.PI*.92;leaves.forEach((p,i)=>p.rotation.y=-Math.max(0,Math.min(1,(ease-.12-i*.09)/(1-.12-i*.09)))*Math.PI*(.985-i*.006));
   if(!dragStart&&!opened&&Math.abs(velocity)>.0001){targetYaw+=velocity;velocity*=.9;}currentYaw+=(targetYaw-currentYaw)*.16;currentPitch+=(targetPitch-currentPitch)*.16;
   root.position.x=ease*.70;root.position.y=still?0:Math.sin(now/2300)*.065;root.rotation.y=currentYaw*(1-ease)+.08*ease;root.rotation.x=currentPitch*(1-ease)-.10*ease;root.rotation.z=-.09+ease*.075;
   if(spinningAt){const t=Math.min(1,(now-spinningAt)/(still?150:2100)),s=t*t*(3-2*t);root.rotation.z=-.09+(still?0:s*Math.PI*6);root.scale.setScalar(1-Math.max(0,(t-.75)/.25)*.95);if(t>=1){finished=true;renderer.render(scene,camera);if(exitCallback)exitCallback();return;}}
   renderer.render(scene,camera);if(!still||opening||closingAt||spinningAt||dragStart||Math.abs(targetYaw-currentYaw)>.001||Math.abs(velocity)>.0001)schedule();
  }
  new MutationObserver(schedule).observe(document.body,{attributes:true,attributeFilter:['class']});document.addEventListener('visibilitychange',schedule);new IntersectionObserver(schedule).observe(host);
  renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();host.classList.remove('webgl-ready');cancelAnimationFrame(raf);window.animateAtlasBook=null;});schedule();
 }catch(error){host.dataset.renderer='css-3d';}
})();




