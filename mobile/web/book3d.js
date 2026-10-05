/* Local geometry, not a flattened image: board, spine, page block and hinged leaves. */
(()=>{
 const host=document.getElementById('book-stage'),trigger=document.getElementById('book-open');
 function refreshFallback(){document.querySelector('.fallback-cover').style.backgroundImage=read('coverFront',null)?`url(${read('coverFront',null)})`:'';const back=document.querySelector('.fallback-back');if(back)back.style.backgroundImage=read('coverBack',null)?`url(${read('coverBack',null)})`:'';}
 refreshFallback();window.addEventListener('atlas-covers-changed',refreshFallback);
 let opened=false,opening=false,dragStart=null,dragMoved=false,suppressClick=0,targetYaw=.38,targetPitch=-.42,currentYaw=.38,currentPitch=-.42,velocity=0;
 function reveal(){const from=window.atlasRightPageRect?window.atlasRightPageRect():document.querySelector('.fallback-pages').getBoundingClientRect();opening=false;document.body.classList.remove('book-opening');document.body.classList.add('book-is-open');trigger.setAttribute('aria-expanded','true');if(document.body.classList.contains('has-results')&&window.projectAtlasPage)window.projectAtlasPage();}
 window.resetBook=()=>{if(window.cancelAtlasProjection)window.cancelAtlasProjection();opened=false;opening=false;document.body.classList.remove('book-is-open','book-opening','page-projected');trigger.setAttribute('aria-expanded','false');};
 window.openBookInstant=()=>{if(opened)return;opened=true;document.body.classList.add('book-is-open');trigger.setAttribute('aria-expanded','true');if(window.requestBookFrame)window.requestBookFrame();requestAnimationFrame(()=>requestAnimationFrame(()=>{if(opened&&document.body.classList.contains('has-results')&&window.projectAtlasPage)window.projectAtlasPage();}));};
 trigger.setAttribute('aria-expanded','false');
 trigger.onclick=e=>{if(performance.now()<suppressClick||opening)return;if(opened){if(window.readerTurn)window.readerTurn(e.clientX<innerWidth/2);return;}opened=true;opening=true;velocity=0;document.body.classList.add('book-opening');trigger.setAttribute('aria-expanded','true');if(window.animateAtlasBook)window.animateAtlasBook();else{setTimeout(reveal,typeof motionReduced!=='undefined'&&motionReduced?0:950);}};
 trigger.onpointerdown=e=>{if(opened||e.button>0)return;dragStart={x:e.clientX,y:e.clientY,lastX:e.clientX};dragMoved=false;velocity=0;trigger.setPointerCapture(e.pointerId);};
 trigger.onpointermove=e=>{if(!dragStart)return;const dx=e.clientX-dragStart.lastX;dragStart.lastX=e.clientX;if(Math.abs(e.clientX-dragStart.x)+Math.abs(e.clientY-dragStart.y)>7)dragMoved=true;if(dragMoved){e.preventDefault();targetYaw+=dx*.012;targetPitch=Math.max(-1.1,Math.min(1.1,targetPitch+(e.clientY-dragStart.y)*.001));velocity=dx*.006;if(window.requestBookFrame)window.requestBookFrame();else document.getElementById('book-fallback').style.transform=`translate(-50%,-50%) perspective(900px) rotateX(${targetPitch}rad) rotateY(${targetYaw}rad)`;}};
 trigger.onpointerup=()=>{if(dragMoved)suppressClick=performance.now()+350;dragStart=null;};trigger.onpointercancel=()=>{dragStart=null;velocity=0;suppressClick=performance.now()+350;};
 try{
  if(!window.THREE)throw new Error('3D library unavailable');
  const T=window.THREE,scene=new T.Scene(),camera=new T.PerspectiveCamera(36,1,.1,50);
  camera.position.set(0,0,8.4);
  const renderer=new T.WebGLRenderer({alpha:true,antialias:true,powerPreference:'low-power'});
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.35));renderer.setClearColor(0,0);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.08;
  host.append(renderer.domElement);host.classList.add('webgl-ready');
  scene.add(new T.AmbientLight(0xffffff,.42));scene.add(new T.HemisphereLight(0xe5edff,0x26303f,1.6));const key=new T.DirectionalLight(0xffecd0,2.4);key.position.set(-3,5,6);scene.add(key);const rim=new T.DirectionalLight(0xa7caff,1.5);rim.position.set(4,1,-2);scene.add(rim);
  const root=new T.Group();scene.add(root);root.rotation.set(-.42,.38,-.09);
  const grain=document.createElement('canvas');grain.width=grain.height=256;
  const gc=grain.getContext('2d'),pixels=gc.createImageData(256,256);
  let seed=71;for(let i=0;i<pixels.data.length;i+=4){seed=(seed*1664525+1013904223)>>>0;const n=115+(seed>>>26);pixels.data[i]=pixels.data[i+1]=pixels.data[i+2]=n;pixels.data[i+3]=255;}gc.putImageData(pixels,0,0);
  const bump=new T.CanvasTexture(grain);bump.wrapS=bump.wrapT=T.RepeatWrapping;bump.repeat.set(3,4);
  const cloth=new T.MeshStandardMaterial({color:0x233245,roughness:.72,metalness:.035,bumpMap:bump,bumpScale:.003});
  const trim=new T.MeshStandardMaterial({color:0x182434,roughness:.64,metalness:.02});
  const paperTexture=new T.TextureLoader().load('paper.png',()=>schedule());paperTexture.colorSpace=T.SRGBColorSpace;
  const pageCanvas=document.createElement('canvas');pageCanvas.width=512;pageCanvas.height=512;const pc=pageCanvas.getContext('2d');
  pc.fillStyle='#f3ebd9';pc.fillRect(0,0,512,512);const gutter=pc.createLinearGradient(0,0,120,0);gutter.addColorStop(0,'#756749');gutter.addColorStop(.12,'#c8bba0');gutter.addColorStop(.55,'#ede4d0');gutter.addColorStop(1,'#f3ebd9');pc.fillStyle=gutter;pc.fillRect(0,0,120,512);
  pc.globalAlpha=.14;pc.drawImage(grain,0,0,512,512);pc.globalAlpha=1;
  const pageMap=new T.CanvasTexture(pageCanvas);pageMap.colorSpace=T.SRGBColorSpace;
  const paper=new T.MeshStandardMaterial({color:0xffffff,map:pageMap,roughness:.94,bumpMap:paperTexture,bumpScale:.001,side:T.DoubleSide});
  const edgeCanvas=document.createElement('canvas');edgeCanvas.width=64;edgeCanvas.height=512;const ec=edgeCanvas.getContext('2d');ec.fillStyle='#ded2b9';ec.fillRect(0,0,64,512);
  for(let y=0;y<512;y+=4){ec.fillStyle=y%12?'#c1b398':'#b6a78a';ec.globalAlpha=.38;ec.fillRect(0,y,64,1);ec.fillStyle='#fff6e3';ec.fillRect(0,y+1,64,1);}ec.globalAlpha=1;
  const edgeMap=new T.CanvasTexture(edgeCanvas);edgeMap.colorSpace=T.SRGBColorSpace;
  const edge=new T.MeshStandardMaterial({color:0xffffff,map:edgeMap,roughness:.96,side:T.DoubleSide});
  function outline(w,h,r){const x=-w/2,y=-h/2,s=new T.Shape();s.moveTo(x+r,y);s.lineTo(x+w-r,y);s.quadraticCurveTo(x+w,y,x+w,y+r);s.lineTo(x+w,y+h-r);s.quadraticCurveTo(x+w,y+h,x+w-r,y+h);s.lineTo(x+r,y+h);s.quadraticCurveTo(x,y+h,x,y+h-r);s.lineTo(x,y+r);s.quadraticCurveTo(x,y,x+r,y);return s;}
  function board(parent,x,z){const group=new T.Group();group.position.set(x,0,z);parent.add(group);const geo=new T.ExtrudeGeometry(outline(2.02,2.84,.052),{depth:.044,bevelEnabled:true,bevelThickness:.012,bevelSize:.012,bevelSegments:3,curveSegments:6,steps:1});geo.translate(0,0,-.022);group.add(new T.Mesh(geo,[cloth,trim]));return group;}
  const backBoard=board(root,0,-.24);
  const hinge=new T.Group();hinge.position.set(-.97,0,.25);root.add(hinge);
  const frontBoard=board(hinge,.97,0);
  // A separate inset face preserves cover artwork proportions over bevelled boards.
  let coverMaterials=[],coverFaces=[];
  function updateCovers(){coverFaces.forEach(m=>{m.parent.remove(m);m.geometry.dispose();});coverMaterials.forEach(m=>{m.map.dispose();m.dispose();});coverMaterials=[];coverFaces=[];
   for(const [parent,key,back] of [[frontBoard,'coverFront',false],[backBoard,'coverBack',true]]){const data=read(key,null);if(!data)continue;const tex=new T.TextureLoader().load(data,()=>schedule());tex.colorSpace=T.SRGBColorSpace;const material=new T.MeshStandardMaterial({map:tex,roughness:.8,bumpMap:bump,bumpScale:.001});const geo=new T.ShapeGeometry(outline(1.96,2.78,.04));const uv=geo.attributes.uv,pos=geo.attributes.position;for(let i=0;i<uv.count;i++)uv.setXY(i,(pos.getX(i)+.98)/1.96,(pos.getY(i)+1.39)/2.78);const face=new T.Mesh(geo,material);face.position.z=back?-.035:.035;if(back)face.rotation.y=Math.PI;parent.add(face);coverMaterials.push(material);coverFaces.push(face);}
  }
  updateCovers();window.addEventListener('atlas-covers-changed',()=>{updateCovers();schedule();});
  const endpaper=new T.Mesh(new T.ShapeGeometry(outline(1.88,2.69,.025)),paper);endpaper.position.set(.97,0,-.036);endpaper.rotation.y=Math.PI;hinge.add(endpaper);
  // Both stacks contain deformable top/bottom sheets and ruled cut edges.
  const rightStack=new T.Mesh(AtlasPaper.geometry(T,'right'),[paper,edge]);rightStack.position.x=-.94;root.add(rightStack);
  const leftPivot=new T.Group();leftPivot.position.set(-.94,0,.18);root.add(leftPivot);
  const leftStack=new T.Mesh(AtlasPaper.geometry(T,'left'),[paper,edge]);leftPivot.add(leftStack);
  const spineGeometry=new T.PlaneGeometry(1,2.84,24,28),spinePos=spineGeometry.attributes.position;
  const spine=new T.Mesh(spineGeometry,cloth);spine.material=cloth.clone();spine.material.side=T.DoubleSide;root.add(spine);
  function bendSpine(open){for(let i=0;i<spinePos.count;i++){const u=spineGeometry.attributes.uv.getX(i),angle=(u-.5)*Math.PI;spinePos.setX(i,-.97-Math.cos(angle)*(.255-.18*open));spinePos.setZ(i,Math.sin(angle)*(.245-.21*open)-.205*open);}spinePos.needsUpdate=true;spineGeometry.computeVertexNormals();}
  const binding=new T.MeshStandardMaterial({color:0x9a8b69,roughness:.88});
  const bands=[];for(const y of [-1.36,1.36]){const band=new T.Mesh(new T.CylinderGeometry(.022,.022,.43,8),binding);band.rotation.x=Math.PI/2;band.position.set(-.965,y,-.01);root.add(band);bands.push(band);}
  const leaves=[];for(let i=0;i<4;i++){const pivot=new T.Group();pivot.position.set(-.94,0,.185+i*.004);root.add(pivot);const sheet=new T.Mesh(AtlasPaper.geometry(T,'right',true),[paper,edge]);pivot.add(sheet);leaves.push({pivot,sheet});}
  const responsePivot=new T.Group();responsePivot.position.set(-.94,0,-.01);root.add(responsePivot);
  const responseGeometries={right:AtlasPaper.geometry(T,'right',true),left:AtlasPaper.geometry(T,'left',true)};const response=new T.Mesh(responseGeometries.right,[paper,edge]);responsePivot.add(response);response.visible=false;
  let leafAt=0,leafKind='project',geometryProgress=-1;
  window.animateAtlasLeaf=kind=>{leafKind=kind;response.geometry=responseGeometries[kind==='back'?'left':'right'];leafAt=performance.now();schedule();};
  // Soft local contact shadow remains transparent around the geometry.
  const shadowCanvas=document.createElement('canvas');shadowCanvas.width=256;shadowCanvas.height=256;const sc=shadowCanvas.getContext('2d'),g=sc.createRadialGradient(128,128,1,128,128,120);g.addColorStop(0,'rgba(0,0,0,.38)');g.addColorStop(1,'rgba(0,0,0,0)');sc.fillStyle=g;sc.fillRect(0,0,256,256);const shadow=new T.Mesh(new T.PlaneGeometry(3.4,.55),new T.MeshBasicMaterial({map:new T.CanvasTexture(shadowCanvas),transparent:true,depthWrite:false}));shadow.position.set(0,-1.48,-.6);scene.add(shadow);
  let openingAt=0,progress=0,last=0,raf=0,closingAt=0,spinningAt=0,exitCallback=null,finished=false,normalClose=false;
  const resetOriginal=window.resetBook;window.resetBook=()=>{resetOriginal();openingAt=closingAt=spinningAt=leafAt=0;progress=0;finished=false;normalClose=false;exitCallback=null;schedule();};
  let viewW=0,viewH=0,units=1,spreadScale=1,spreadY=0;
  function resize(){const w=host.clientWidth,h=host.clientHeight;if(!w||!h||w===viewW&&h===viewH)return;viewW=w;viewH=h;renderer.setSize(w,h,false);camera.aspect=w/h;camera.position.z=Math.max(3.6/(2*Math.tan(Math.PI/10)),3.25/(2*Math.tan(Math.PI/10)*camera.aspect));units=2*Math.tan(Math.PI/10)*camera.position.z/h;const available=Math.max(100,h-(h<500?155:220)),pageHeight=Math.min(w-32,available*.7,460)/.7,pageEnd=Math.max(12,(available-pageHeight)/2+12)+pageHeight,top=pageEnd+8,bottom=h-(h<500?60:85),room=Math.max(45,bottom-top);const bookWidth=Math.min(w*.78,300,room*1.85);spreadScale=bookWidth*units/3.88;for(const id of ['book-previous','book-next']){const button=document.getElementById(id);button.style.width=bookWidth*.55+'px';button.style.height=room+'px';button.style.bottom=h-bottom+'px';}spreadY=(top+bottom)/2-h/2;camera.updateProjectionMatrix();schedule();}
  new ResizeObserver(resize).observe(host);resize();
  window.atlasPageRect=(side='right')=>{root.updateWorldMatrix(true,false);const bounds=renderer.domElement.getBoundingClientRect(),xs=side==='left'?[-2.80,-.97]:[-.91,.94];const points=xs.flatMap(x=>[-1.345,1.345].map(y=>new T.Vector3(x,y,-.02).applyMatrix4(root.matrixWorld).project(camera))).map(p=>({x:bounds.left+(p.x+1)*bounds.width/2,y:bounds.top+(1-p.y)*bounds.height/2}));const left=Math.min(...points.map(p=>p.x)),top=Math.min(...points.map(p=>p.y));return {left,top,width:Math.max(...points.map(p=>p.x))-left,height:Math.max(...points.map(p=>p.y))-top};};
  window.atlasRightPageRect=()=>window.atlasPageRect('right');
  window.animateAtlasBook=()=>{openingAt=performance.now();if(typeof motionReduced!=='undefined'&&motionReduced){progress=1;reveal();}schedule();};
  window.closeAndSpinAtlasBook=callback=>{normalClose=false;exitCallback=callback;closingAt=performance.now();opened=true;opening=false;document.body.classList.remove('book-is-open');schedule();};
  window.closeAtlasBook=()=>{normalClose=true;closingAt=performance.now();opened=true;opening=false;document.body.classList.remove('book-is-open');schedule();};
  function schedule(){if(!raf)raf=requestAnimationFrame(frame);}
  window.requestBookFrame=schedule;
  function frame(now){raf=0;if(finished||document.body.classList.contains('is-loading')||document.hidden||document.getElementById('home-book').hidden||document.getElementById('browse').hidden){last=0;return;}
   last=now;
   if(closingAt){progress=Math.max(0,1-(now-closingAt)/850);if(progress<=0){closingAt=0;opened=false;resize();if(!normalClose)spinningAt=now;trigger.setAttribute('aria-expanded','false');}}
   else if(!opened){progress=0;openingAt=0;}
   else if(openingAt&&opening){progress=Math.min(1,(now-openingAt)/1350);}
   else if(opened)progress=1;
   const ease=AtlasPaper.smooth(progress),still=typeof motionReduced!=='undefined'&&motionReduced;
   hinge.rotation.y=-AtlasPaper.smooth(progress/.84)*Math.PI;hinge.position.z=.25-.49*ease;
   const transfer=AtlasPaper.smooth((progress-.12)/.88);leftPivot.rotation.y=-transfer*Math.PI;leftPivot.position.z=.18-.40*ease;leftStack.visible=progress>.15;
   if(geometryProgress!==ease){rightStack.geometry.deform(ease);leftStack.geometry.deform(ease);bendSpine(ease);bands.forEach(b=>{b.scale.y=1-.82*ease;b.position.z=-.01-.205*ease;});geometryProgress=ease;}
   leaves.forEach(({pivot,sheet},i)=>{const t=AtlasPaper.smooth((progress-.16-i*.055)/(.80-i*.055));pivot.rotation.y=-t*Math.PI;pivot.position.z=.195-.20*ease+i*.008;sheet.visible=progress>.16&&progress<.96;if(sheet.visible)sheet.geometry.deform(ease,.28*Math.sin(Math.PI*t));});
   if(leafAt&&opened&&!opening){const t=Math.min(1,(now-leafAt)/(still?1:620)),pulse=Math.sin(Math.PI*t);response.visible=t<1;response.geometry.deform(1,.20*pulse);responsePivot.rotation.y=leafKind==='back'?Math.PI+.28*pulse:-.28*pulse;if(t>=1)leafAt=0;}else response.visible=false;
   shadow.scale.x=1+ease*.70;shadow.material.opacity=.8;
   if(!dragStart&&!opened&&Math.abs(velocity)>.0001){targetYaw+=velocity;velocity*=.9;}currentYaw+=(targetYaw-currentYaw)*.16;currentPitch+=(targetPitch-currentPitch)*.16;
   const modelScale=1+(spreadScale-1)*ease;root.scale.setScalar(modelScale);root.position.x=ease*.98*modelScale;root.position.y=(still||opened)?0:Math.sin(now/2300)*.065;renderer.domElement.style.transform=`translate3d(0,${ease*spreadY}px,0)`;root.rotation.y=currentYaw*(1-ease)+.08*ease;root.rotation.x=currentPitch*(1-ease)-.95*ease;root.rotation.z=-.09+ease*.075;
   if(spinningAt){const t=Math.min(1,(now-spinningAt)/(still?150:2100)),s=t*t*(3-2*t);root.rotation.z=-.09+(still?0:s*Math.PI*6);root.scale.setScalar(1-Math.max(0,(t-.75)/.25)*.95);if(t>=1){finished=true;renderer.render(scene,camera);if(exitCallback)exitCallback();return;}}
   renderer.render(scene,camera);if(opening&&progress>=1)reveal();if((!still&&!opened)||opening||closingAt||spinningAt||leafAt||dragStart||Math.abs(targetYaw-currentYaw)>.001||Math.abs(velocity)>.0001)schedule();
  }
  new MutationObserver(schedule).observe(document.body,{attributes:true,attributeFilter:['class']});document.addEventListener('visibilitychange',schedule);new IntersectionObserver(schedule).observe(host);
  renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();host.classList.remove('webgl-ready');cancelAnimationFrame(raf);window.animateAtlasBook=null;});schedule();
 }catch(error){host.dataset.renderer='css-3d';console.error('Book renderer fallback:',error.message);}
})();




