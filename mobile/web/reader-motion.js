/* Input policy is shared by projected paper and the two physical leaves. */
(function(root){
 function gesture(dx,dy){if(Math.abs(dy)>50&&Math.abs(dy)>Math.abs(dx)*1.35)return dy<0?'directory':'close';if(Math.abs(dx)>55&&Math.abs(dx)>Math.abs(dy)*1.35)return dx>0?'back':'next';return null;}
 function articleStep(index,length,page,pages,direction){
  if(direction>0)return page+1<pages?{index,page:page+1}:index+1<length?{index:index+1,page:0}:null;
  return page>0?{index,page:page-1}:index>0?{index:index-1,page:'last'}:{directory:true};
 }
 const api={gesture,articleStep};if(typeof module==='object'&&module.exports)module.exports=api;else root.AtlasReaderMotion=api;
})(typeof window==='object'?window:this);
