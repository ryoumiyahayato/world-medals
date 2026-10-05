/* Shared, bounded deformation for bound paper; no animation-time allocation. */
(function(root){
 'use strict';
 const clamp=x=>Math.max(0,Math.min(1,x));
 const smooth=x=>{x=clamp(x);return x*x*x*(x*(x*6-15)+10);};
 function point(u,v,w,open,side,lift=0,thin=false){
  const curve=.105*Math.sin(Math.PI*u)*Math.exp(-1.25*u)-.026*Math.exp(-18*u);
  const corner=.020*Math.pow(u,4)*Math.pow(Math.abs(v*2-1),6);
  const bend=open*(curve+corner)+lift*Math.sin(Math.PI*u*.85)*(.85+.15*Math.cos(v*Math.PI));
  const depth=thin?.002:side==='left'?.19:.40-.20*open;
  const top=thin?0:side==='left'?0:.18-.20*open;
  return [1.88*u-.009*Math.sin(Math.PI*v)*u*u,2.69*(v-.5),top-depth*(1-w)+(side==='left'?-bend:bend)];
 }
 function geometry(T,side,thin=false){
  const n=12,m=16,coords=[],index=[];
  function surface(a,b,c,d,nu,nv){const start=coords.length/3;for(let j=0;j<=nv;j++)for(let i=0;i<=nu;i++){const s=i/nu,t=j/nv;coords.push(...a.map((x,k)=>x*(1-s)*(1-t)+b[k]*s*(1-t)+c[k]*s*t+d[k]*(1-s)*t));}for(let j=0;j<nv;j++)for(let i=0;i<nu;i++){const p=start+j*(nu+1)+i;index.push(p,p+1,p+nu+2,p,p+nu+2,p+nu+1);}}
  surface([0,0,1],[1,0,1],[1,1,1],[0,1,1],n,m);
  surface([1,0,0],[0,0,0],[0,1,0],[1,1,0],n,m);
  surface([1,0,1],[1,0,0],[1,1,0],[1,1,1],1,m);
  surface([0,0,0],[0,0,1],[0,1,1],[0,1,0],1,m);
  surface([0,0,0],[1,0,0],[1,0,1],[0,0,1],n,1);
  surface([0,1,1],[1,1,1],[1,1,0],[0,1,0],n,1);
  const g=new T.BufferGeometry(),uv=[],positions=new Float32Array(coords.length);
  for(let i=0;i<coords.length;i+=3)uv.push(coords[i],coords[i+1]);
  g.setAttribute('position',new T.BufferAttribute(positions,3));g.setAttribute('uv',new T.Float32BufferAttribute(uv,2));g.setIndex(index);
  // Top and bottom use the paper material; cut edges use a finely ruled texture.
  const faceSize=n*m*6;g.addGroup(0,faceSize*2,0);g.addGroup(faceSize*2,index.length-faceSize*2,1);
  const edgeStart=2*(n+1)*(m+1);
  const uvAttr=g.attributes.uv;for(let i=edgeStart;i<coords.length/3;i++){uvAttr.setXY(i,coords[i*3]+coords[i*3+1],coords[i*3+2]);}
  const basis=[];for(let i=0;i<coords.length;i+=3){const u=coords[i],v=coords[i+1],w=coords[i+2],a=point(u,v,w,0,side,0,thin),b=point(u,v,w,1,side,0,thin),c=point(u,v,w,0,side,1,thin);basis.push([a[0],a[1],a[2],b[2]-a[2],c[2]-a[2]]);}g.boundingSphere=new T.Sphere(new T.Vector3(.94,0,0),2.1);let previous='';
  g.deform=(open,lift=0)=>{const key=open+':'+lift;if(key===previous)return;previous=key;for(let i=0;i<basis.length;i++){const b=basis[i],j=i*3;positions[j]=b[0];positions[j+1]=b[1];positions[j+2]=b[2]+b[3]*open+b[4]*lift;}g.attributes.position.needsUpdate=true;g.computeVertexNormals();};
  g.deform(0);return g;
 }
 const api={point,smooth,geometry};if(typeof module==='object'&&module.exports)module.exports=api;else root.AtlasPaper=api;
})(typeof window==='object'?window:this);
