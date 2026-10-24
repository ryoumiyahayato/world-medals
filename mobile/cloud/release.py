"""Cloud-only prepared-image updates and private APK publishing."""
import os,json,zipfile,subprocess,base64,shutil,re,io
from pathlib import Path
from PIL import Image
from ingest import apply_image
R=Path.cwd();T=Path(os.environ["RUNNER_TEMP"])/"world-medals";T.mkdir(exist_ok=True)
REPO=os.environ["GITHUB_REPOSITORY"];TAG="mobile-current";STATE="world-medals-cloud-state.zip"
def gh(*args,raw=False):
 p=subprocess.run(["gh",*args],check=True,stdout=subprocess.PIPE)
 return p.stdout if raw else p.stdout.decode()
def api(path,method="GET",data=None):
 args=["gh","api",path]
 if data is not None:args+=["--method",method,"--input","-"]
 p=subprocess.run(args,input=json.dumps(data).encode() if data is not None else None,stdout=subprocess.PIPE,check=True)
 return json.loads(p.stdout) if p.stdout else None
def release(tag):
 p=subprocess.run(["gh","api",f"repos/{REPO}/releases/tags/{tag}"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 return json.loads(p.stdout) if p.returncode==0 else None
def download(asset,dest):
 # gh authenticates private stored Release assets; files exist only on the runner.
 gh("release","download",asset["tag"],"--repo",REPO,"--pattern",asset["name"],"--output",str(dest))
def extract_selected(archive,wanted):
 with zipfile.ZipFile(archive) as z:
  for n in z.namelist():
   if not wanted(n):continue
   p=(R/n).resolve()
   if not p.is_relative_to(R):raise ValueError("Unsafe archive path")
   p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(n))
def wanted(n):
 return n.startswith("mobile/build/site/") or n=="mobile/build/image-provenance.json" or n=="mobile/web/icon.png" or n.startswith("mobile/android/res/") or n=="mobile/build/apk-build-info.json" or n=="mobile/build/world-medals-current.apk"
assert api(f"repos/{REPO}")["private"],"Private repository required"
current=release(TAG)
if current is None:
 page=1
 while True:
  releases=api(f"repos/{REPO}/releases?per_page=100&page={page}")
  current=next((r for r in releases if r["tag_name"]==TAG),None)
  if current or len(releases)<100:break
  page+=1
previous=T/"previous.apk";prior={}
git_portable_bytes=(R/"data/release-input.json").read_bytes()
if current and any(a["name"]==STATE for a in current["assets"]):
 state_asset=next(a for a in current["assets"] if a["name"]==STATE);download(dict(state_asset,tag=TAG),T/"input.zip")
 extract_selected(T/"input.zip",lambda n:True);(T/"input.zip").unlink()
 prior=json.loads((R/"cloud/state.json").read_text())
 download(dict(next(a for a in current["assets"] if a["name"]=="world-medals-current.apk"),tag=TAG),previous)
else:
 bootstrap=release("local-backup-20261024");assert bootstrap
 manifest_asset=next(a for a in bootstrap["assets"] if a["name"]=="migration.json")
 download(dict(manifest_asset,tag="local-backup-20261024"),T/"manifest.json")
 manifest=json.loads((T/"manifest.json").read_text())
 for pack in manifest["archives"]:
  if not any(wanted(m["path"]) for m in pack["members"]):continue
  asset=next(a for a in bootstrap["assets"] if a["name"]==pack["name"])
  download(dict(asset,tag="local-backup-20261024"),T/"input.zip")
  extract_selected(T/"input.zip",wanted);(T/"input.zip").unlink()
 old=R/"mobile/build/world-medals-current.apk";shutil.move(old,previous)
 prior={"version":json.loads((R/"mobile/build/apk-build-info.json").read_text())["version"],"applied_batches":[]}
# Restore only actual binary resources from the snapshot; source code comes from checkout.
site=R/"mobile/build/site";catalog=site/"catalog.js"
C=json.loads(catalog.read_text()[len("window.CATALOG="):-1])
prov_path=R/"mobile/build/image-provenance.json";prov=json.loads(prov_path.read_text())
portable_path=R/"data/release-input.json"
if (R/"cloud/portable.json").exists():
 assert (R/"cloud/base-portable.json").read_bytes()==git_portable_bytes,"Catalogue source changed: refresh the canonical cloud catalogue before image-only updates"
 portable=json.loads((R/"cloud/portable.json").read_text())
else:portable=json.loads(portable_path.read_text())

# Real private inbox transport; the view update is isolated from the real catalogue.
import copy
fixture=T/"image-routing-check";fixture.mkdir(exist_ok=True)
sample=next(r for r in C["rows"] if r["photos"] and r["id"] in portable["rows"])
sample_photo=sample["photos"][0];test_input=T/("transport-check-"+os.environ["GITHUB_RUN_ID"]+"-"+os.environ["GITHUB_RUN_ATTEMPT"]+".png")
with Image.open(site/sample_photo["src"]) as im:im.save(test_input,"PNG")
test_inbox=release("image-inbox")
if test_inbox is None:
 test_inbox=api(f"repos/{REPO}/releases","POST",{"tag_name":"image-inbox","target_commitish":os.environ["GITHUB_SHA"],"name":"待接入图片","body":"私有图片接入区；已接入当前状态的附件会移除。","draft":False,"make_latest":"false"})
gh("release","upload","image-inbox",str(test_input),"--repo",REPO)
test_asset=next(a for a in api(f"repos/{REPO}/releases/{test_inbox['id']}")["assets"] if a["name"]==test_input.name)
try:
 replay=T/"downloaded-test-image";download(dict(test_asset,tag="image-inbox"),replay)
 assert replay.read_bytes()==test_input.read_bytes()
 tc,tp,tb=copy.deepcopy(C),copy.deepcopy(prov),copy.deepcopy(portable)
 before=[(r["id"],r["family"],[p["src"] for p in r["photos"]]) for r in tc["rows"]]
 result=apply_image(fixture,tc,tp,tb,{"row_id":sample["id"],"expected_src":sample_photo["src"]},replay,"transport-check")
 target=next(r for r in tc["rows"] if r["id"]==sample["id"])
 assert result["row_id"]==sample["id"] and target["photos"][0]["src"]!=sample_photo["src"]
 for row,old in zip(tc["rows"],before):
  assert (row["id"],row["family"])==old[:2]
  if row["id"]!=sample["id"]:assert [p["src"] for p in row["photos"]]==old[2]
 for key,edge in [("src",1200),("thumb",384)]:
  with Image.open(fixture/"mobile/build/site"/target["photos"][0][key]) as im:im.load();assert max(im.size)<=edge
 try:apply_image(fixture,tc,tp,tb,{"row_id":sample["id"],"expected_src":"missing-image"},replay,"invalid-target")
 except ValueError:pass
 else:raise AssertionError("Invalid target must be rejected")
 print("Cloud image transport and isolated target routing passed")
finally:api(f"repos/{REPO}/releases/assets/{test_asset['id']}","DELETE",{})

applied=list(prior.get("applied_batches",[]));changed=0;consumed=[]
inbox=None
for descriptor in sorted((R/"cloud/updates").glob("*.json")) if (R/"cloud/updates").exists() else []:
 batch=json.loads(descriptor.read_text());bid=batch["id"]
 if bid in applied:continue
 assert re.fullmatch(r"[A-Za-z0-9_-]+",bid)
 if inbox is None:inbox=release("image-inbox")
 assert inbox,"Image inbox missing"
 for i,item in enumerate(batch["images"]):
  asset=next(a for a in inbox["assets"] if a["id"]==item["asset_id"])
  local=T/("image-"+str(i)+"-"+bid);download(dict(asset,tag="image-inbox"),local)
  apply_image(R,C,prov,portable,item,local,bid);consumed.append(asset["id"]);changed+=1
 applied.append(bid)
version=json.loads((R/"mobile/version.json").read_text())
code=max(version["code"],prior["version"]["code"]+1)
version={"name":f"0.{code:03d}","code":code,"channel":"dev"}
(R/"mobile/version.json").write_text(json.dumps(version))
catalog.write_text("window.CATALOG="+json.dumps(C,ensure_ascii=False).replace("</","<\\/")+";")
prov_path.write_text(json.dumps(prov,ensure_ascii=False));(site/"image-provenance.json").write_text(json.dumps(prov,ensure_ascii=False))
portable_path.write_text(json.dumps(portable,ensure_ascii=False))
# Persistent signing credentials are supplied by existing repository Secrets.
key=T/"atlas.keystore";key.write_bytes(base64.b64decode(os.environ.pop("ATLAS_KEYSTORE_BASE64")))
os.chmod(key,0o600)
env=dict(os.environ,CI="true",SKIP_EXPORT="1",SIGNING_KEYSTORE=str(key),SIGNING_ALIAS="atlas",SIGNING_PASSWORD=os.environ.pop("ATLAS_KEYSTORE_PASSWORD"))
subprocess.run(["python","mobile/scripts/build_apk.py"],env=env,check=True)
apk=R/"mobile/build/world-medals-current.apk"
# Compare certificate bytes using Android SDK's native APK verifier, with no manual hashes.
helper=T/"SameSigner.java"
helper.write_text('import java.io.File;import java.util.Arrays;import com.android.apksig.ApkVerifier;public class SameSigner{public static void main(String[]a)throws Exception{var x=new ApkVerifier.Builder(new File(a[0])).build().verify();var y=new ApkVerifier.Builder(new File(a[1])).build().verify();if(!x.isVerified()||!y.isVerified()||x.getSignerCertificates().size()!=y.getSignerCertificates().size())throw new Exception("APK verification failed");for(int i=0;i<x.getSignerCertificates().size();i++)if(!Arrays.equals(x.getSignerCertificates().get(i).getEncoded(),y.getSignerCertificates().get(i).getEncoded()))throw new Exception("Signing certificate changed");System.out.println("Persistent signing certificate matches previous APK");}}')
sdk=Path(os.environ["ANDROID_HOME"]);jar=sdk/"build-tools/36.0.0/lib/apksigner.jar"
subprocess.run(["java","-cp",str(jar),str(helper),str(previous),str(apk)],check=True)
C=json.loads(catalog.read_text()[len("window.CATALOG="):-1])
refs={p[k] for r in C["rows"] for p in r["photos"] for k in ("src","thumb","originalSrc") if p.get(k)}
with zipfile.ZipFile(apk) as z:
 assert z.testzip() is None
 actual={n[len("assets/site/"):] for n in z.namelist() if n.startswith(("assets/site/images/detail/","assets/site/images/thumb/"))}
 expected={p for p in refs if p.startswith(("images/detail/","images/thumb/"))}
 assert actual==expected
 for p in ("catalog.js","desktop.html","image-provenance.json","sources.json"):assert z.read("assets/site/"+p)==(site/p).read_bytes()
# Store only current build inputs and accepted processed originals. Never package keys or build intermediates.
(R/"cloud").mkdir(exist_ok=True)
state=dict(version=version,applied_batches=applied,rows=len(C["rows"]),photo_paths=C["imageCount"])
(R/"cloud/state.json").write_text(json.dumps(state))
(R/"cloud/base-portable.json").write_bytes(git_portable_bytes)
(R/"cloud/portable.json").write_text(json.dumps(portable,ensure_ascii=False))
run_id=os.environ["GITHUB_RUN_ID"]+"-"+os.environ["GITHUB_RUN_ATTEMPT"]
state_zip=T/("candidate-state-"+run_id+".zip")
with zipfile.ZipFile(state_zip,"w",zipfile.ZIP_DEFLATED,compresslevel=1) as z:
 for p in site.rglob("*"):
  if not p.is_file():continue
  rel=p.relative_to(site).as_posix()
  if rel.startswith(("images/detail/","images/thumb/")) and rel not in refs:continue
  z.write(p,p.relative_to(R).as_posix())
 for p in [prov_path,R/"mobile/web/icon.png",*list((R/"cloud").glob("*.json")),*(list((R/"cloud/processed").glob("*")) if (R/"cloud/processed").exists() else [])]:
  z.write(p,p.relative_to(R).as_posix())
info=json.loads((R/"mobile/build/apk-build-info.json").read_text())
info.update(cloudRun=f"https://github.com/{REPO}/actions/runs/"+os.environ["GITHUB_RUN_ID"],cloud_state=state,updated_images=changed,persistent_signer_matches_previous=True,offline_apk_file_set_verified=True,image_transport_and_isolated_routing_verified=True)
info_file=T/("candidate-info-"+run_id+".json");info_file.write_text(json.dumps(info,ensure_ascii=False,indent=2))
apk_stage=R/"mobile/build"/("candidate-apk-"+run_id+".apk");os.link(apk,apk_stage)
if not current:
 current=api(f"repos/{REPO}/releases","POST",{"tag_name":TAG,"target_commitish":os.environ["GITHUB_SHA"],"name":"全球勋奖章图鉴 · 最新版","body":"云端构建；固定下载地址。","draft":True,"make_latest":"false"})
candidates=[(apk_stage,"world-medals-current.apk"),(state_zip,STATE),(info_file,"build-info.json")]
for path,target in candidates:gh("release","upload",TAG,str(path),"--repo",REPO)
assets=api(f"repos/{REPO}/releases/{current['id']}")["assets"];moves=[]
try:
 for path,target in candidates:
  new=next(a for a in assets if a["name"]==path.name);assert new["size"]==path.stat().st_size
  old=next((a for a in assets if a["name"]==target),None)
  if old:api(f"repos/{REPO}/releases/assets/{old['id']}","PATCH",{"name":"previous-"+run_id+"-"+target})
  moves.append((new,old,target))
  api(f"repos/{REPO}/releases/assets/{new['id']}","PATCH",{"name":target})
except Exception:
 for new,old,target in reversed(moves):
  api(f"repos/{REPO}/releases/assets/{new['id']}","PATCH",{"name":new["name"]})
  if old:api(f"repos/{REPO}/releases/assets/{old['id']}","PATCH",{"name":target})
 raise
gh("release","edit",TAG,"--repo",REPO,"--draft=false","--latest","--notes",f"云端版本 {version['name']}；{len(C['rows'])}行，{C['imageCount']}张图。持久签名与上一包一致。APK包内离线图片集合核对通过。")
for new,old,target in moves:
 if old:api(f"repos/{REPO}/releases/assets/{old['id']}","DELETE",{})
for asset_id in consumed:api(f"repos/{REPO}/releases/assets/{asset_id}","DELETE",{})
print(json.dumps({"version":version,"updated_images":changed,"release":TAG,"workstation_files_created":0}))
