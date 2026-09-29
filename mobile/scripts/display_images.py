"""Explicit, reviewed display substitutions. Source files are never modified."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageOps
LABELS={'background-removed':'背景已处理','ai-enhanced':'AI处理图','ai-generated':'AI生成示意图（非实物照片）'}
def load(root):
 p=root/'data/display_images/overrides.json'
 data=json.loads(p.read_text(encoding='utf-8-sig')) if p.exists() else {'schema':1,'images':{}}
 if data.get('schema')!=1 or not isinstance(data.get('images'),dict):raise ValueError('Invalid display override manifest')
 return data['images']
def prepare(root,out,original,digest,entry):
 if not entry or entry.get('approved') is not True:return None
 if entry.get('original_sha256')!=digest:raise ValueError('Source changed: '+original)
 kind=entry.get('processing');label=LABELS.get(kind)
 if not label or not entry.get('reviewed_by') or not entry.get('reviewed_at'):raise ValueError('Review metadata missing: '+original)
 relative=Path(entry['file']);path=(root/relative).resolve();allowed=(root/'assets/processed').resolve()
 if relative.is_absolute() or not path.is_relative_to(allowed) or not path.is_file():raise ValueError('Invalid processed image path')
 with Image.open(path) as im:
  im.load();rgba=ImageOps.exif_transpose(im).convert('RGBA')
  if rgba.getchannel('A').getextrema()[0]==255:raise ValueError('Display image requires transparent background')
  if rgba.getchannel('A').getextrema()[1]==0:raise ValueError('Display image is empty')
  sha=hashlib.sha256(path.read_bytes()).hexdigest();dest='images/display-'+sha[:24]+'.webp'
  rgba.thumbnail((1600,1600),Image.Resampling.LANCZOS);(out/'images').mkdir(parents=True,exist_ok=True);rgba.save(out/dest,'WEBP',lossless=True)
 return {'src':dest,'processing':label,'processedOriginal':str(relative).replace('\\','/'),'processedSha256':sha,'model':entry.get('model','')}
