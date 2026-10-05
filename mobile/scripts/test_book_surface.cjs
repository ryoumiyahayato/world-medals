const assert=require('node:assert/strict');
const T=require('../web/vendor/three.min.js');
const paper=require('../web/book-surface.js');
// Closing must restore a planar, bound stack; opening must form a curved gutter.
for(const side of ['left','right']){
 const geometry=paper.geometry(T,side);
 for(let step=0;step<=100;step++){
  const open=step/100;geometry.deform(open,.2*Math.sin(Math.PI*open));
  for(const name of ['position','normal'])assert([...geometry.attributes[name].array].every(Number.isFinite),`${side}: invalid ${name}`);
  assert(geometry.boundingSphere.radius<=2.1,'paper escaped its board');
 }
 const a=paper.point(0,0,1,0,side),b=paper.point(1,1,1,0,side);
 assert.equal(a[2],b[2],'closed pages must be planar');
 const inner=paper.point(0,.5,1,1,'right'),middle=paper.point(.3,.5,1,1,'right');
 assert(middle[2]>inner[2]+.04,'binding gutter must be recessed');
 const groups=geometry.groups;assert.equal(groups.reduce((n,g)=>n+g.count,0),geometry.index.count,'all paper faces need a material');
 geometry.dispose();
}
// Actual opposing surfaces must meet at the spine, despite the left stack flipping.
for(const v of [0,.25,.5,.75,1]){
 const right=paper.point(0,v,1,1,'right');
 const left=paper.point(0,v,0,1,'left');
 assert(Math.abs(right[2]-(-.22-left[2]))<.011,'open binding seam separated');
}
assert.equal(paper.smooth(0),0);assert.equal(paper.smooth(1),1);
assert(Math.abs(paper.smooth(.0001))<1e-8,'opening starts abruptly');
console.log('Book deformation: finite geometry, board bounds, curved gutter, binding seam and smooth endpoints passed.');
