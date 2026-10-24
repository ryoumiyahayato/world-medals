"""Apply an approved image to one uniquely identified existing view."""
import copy,re,shutil
from PIL import Image
from bs4 import BeautifulSoup
def apply_image(root,catalogue,provenance,portable,item,input_path,batch_id):
 rows=[r for r in catalogue["rows"] if r["id"]==item["row_id"]]
 if len(rows)!=1:raise ValueError("Missing or ambiguous row")
 row=rows[0];photos=[p for p in row["photos"] if p["src"]==item["expected_src"]]
 if len(photos)!=1:raise ValueError("Expected source must identify exactly one view")
 photo=photos[0];index=row["photos"].index(photo)
 if not re.fullmatch(r"[A-Za-z0-9_-]+",row["id"]):raise ValueError("Unsafe row identifier")
 cell=BeautifulSoup(portable["rows"][row["id"]][2],"html.parser")
 origins=[tag["src"] for tag in cell.select("img[src]") if tag["src"] in provenance and provenance[tag["src"]]["src"]==photo["src"]]
 if len(origins)!=1:raise ValueError("Desktop and mobile must identify the same unique view")
 old_key=origins[0]
 entry=copy.deepcopy(provenance[old_key]);meta=copy.deepcopy(portable["images"].get(old_key,entry["provenance"]))
 label="AI处理展示图" if item.get("kind")=="ai_processed_display" else "用户处理展示图"
 with Image.open(input_path) as im:
  im.load()
  if im.format not in ("PNG","JPEG","WEBP"):raise ValueError("PNG, JPEG or WebP required")
  ext={"PNG":"png","JPEG":"jpg","WEBP":"webp"}[im.format];stem=row["id"]+"-"+str(index)
  canonical=root/"cloud/processed"/(stem+"."+ext);canonical.parent.mkdir(parents=True,exist_ok=True)
  for old in canonical.parent.glob(stem+".*"):old.unlink()
  shutil.copyfile(input_path,canonical);new_key=canonical.relative_to(root).as_posix()
  image=im.convert("RGBA") if "A" in im.getbands() else im.convert("RGB")
  processing=dict(status="user-ai-display" if item.get("kind")=="ai_processed_display" else "user-processed-display",sourceSize=list(im.size),crop=[0,0,im.width,im.height],margin=0,cloudProcessedSource=new_key)
  for key,edge,quality,folder in [("src",1200,90,"detail"),("thumb",384,86,"thumb")]:
   relative="images/"+folder+"/cloud/processed/"+stem+".webp";out=root/"mobile/build/site"/relative
   out.parent.mkdir(parents=True,exist_ok=True);display=image.copy();display.thumbnail((edge,edge),Image.Resampling.LANCZOS);display.save(out,"WEBP",quality=quality,method=6)
   photo[key]=relative;entry[key]=relative;processing["detail" if key=="src" else "thumb"]=relative;processing["detailSize" if key=="src" else "thumbSize"]=list(display.size)
 if photo.get("originalSrc"):photo["originalSrc"]=photo["src"]
 if label not in photo["caption"]:photo["caption"]+=" · "+label
 entry.update(original=new_key,processing=processing);entry["provenance"].update(display_note=label,approved_batch=batch_id,prior_source_key=old_key)
 provenance[new_key]=entry;meta.update(local_path=new_key,display_note=label,approved_batch=batch_id,prior_source_key=old_key);portable["images"][new_key]=meta
 cell=BeautifulSoup(portable["rows"][row["id"]][2],"html.parser");found=0
 for tag in cell.select("img[src]"):
  if tag["src"]==old_key:
   found+=1;tag["src"]=new_key;fig=tag.find_parent("figure")
   if fig:
    caption=fig.find("figcaption")
    if caption is None:caption=cell.new_tag("figcaption");fig.append(caption)
    caption.string=photo["caption"]
 if found!=1:raise ValueError("Desktop row must identify the same single view")
 portable["rows"][row["id"]][2]=str(cell)
 return {"row_id":row["id"],"view_index":index,"processed_source":new_key}
