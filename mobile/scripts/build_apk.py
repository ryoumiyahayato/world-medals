"""Dependency-light SDK build: aapt2 -> javac -> D8 -> zipalign -> apksigner."""
import hashlib, json, os, secrets, shutil, subprocess, zipfile
from pathlib import Path
from export_catalog import ROOT, OUT, export, stamp_web_assets

MOBILE=ROOT/'mobile'
BUILD=MOBILE/'build/android'
WIN=os.name=='nt'
def run(args, **kwargs):
    subprocess.run([str(x) for x in args], check=True, **kwargs)

def remove_obsolete_apks(output, *, confirm_permanent_delete=False):
    """Delete only after specific user confirmation; unlink bypasses Recycle Bin."""
    if confirm_permanent_delete is not True:
        raise PermissionError("Permanent APK cleanup requires specific user confirmation")
    root=(MOBILE/'build').resolve();output=output.resolve()
    if not output.is_relative_to(root) or not output.is_file():
        raise ValueError('Newest APK must exist inside the project build directory')
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:raise ValueError('Newest APK failed CRC verification')
    removed=[]
    for candidate in root.rglob('*'):
        if not candidate.is_file() or not any(candidate.name.endswith(s) for s in ('.apk','.apk.sha256','.apk.idsig')):continue
        resolved=candidate.resolve()
        if not resolved.is_relative_to(root):raise ValueError('APK cleanup outside project')
        if candidate.name in (output.name,output.name+'.sha256',output.name+'.idsig'):continue
        removed.append(dict(path=str(resolved),bytes=candidate.stat().st_size))
        candidate.unlink()
    (root/'apk-cleanup.json').write_text(json.dumps(dict(kept=str(output),removed=removed),indent=2),encoding='utf-8')
    return removed
def build():
    try:
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
        source_modified=subprocess.run(['git','diff','--quiet','HEAD','--','mobile','data/release-input.json','data/display_images','assets/site.css'],cwd=ROOT).returncode!=0
    except (OSError,subprocess.CalledProcessError):
        source_commit=source_modified=None
    if not os.environ.get('SKIP_EXPORT'): export()
    sdk=Path(os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT') or str(Path.home()/'AppData/Local/Android/Sdk'))
    java=Path(os.environ['JAVA_HOME'])/'bin' if os.environ.get('JAVA_HOME') else Path(shutil.which('java') or '').parent
    if not (java/('java.exe' if WIN else 'java')).exists():raise RuntimeError('Set JAVA_HOME to JDK 17+ or add java to PATH')
    platform=sdk/'platforms/android-36/android.jar'
    bt=sdk/'build-tools/36.1.0'
    if not bt.exists(): bt=sdk/'build-tools/36.0.0'
    if not platform.exists() or not bt.exists(): raise RuntimeError('Install Android SDK platform 36 and build-tools 36.1.0 or 36.0.0')
    BUILD.mkdir(parents=True,exist_ok=True)
    classes=BUILD/'classes';classes.mkdir(exist_ok=True)
    dex=BUILD/'dex';dex.mkdir(exist_ok=True)
    res=BUILD/'res';shutil.copytree(MOBILE/'android/res',res,dirs_exist_ok=True)
    shutil.copyfile(MOBILE/'web/icon.png',res/'drawable/icon.png')
    ver=json.loads((MOBILE/'version.json').read_text())
    # SKIP_EXPORT must still refresh the UI edition from the canonical version.
    (OUT/'version.js').write_text('window.APP_VERSION='+json.dumps(ver)+';',encoding='utf-8')
    stamp_web_assets()
    # Refresh the shared desktop artifact before bundling, including SKIP_EXPORT.
    # Otherwise a prior edition's desktop.html can survive beside a new catalogue.
    from package_release import desktop
    desktop()
    tool=lambda name:bt/(name+('.exe' if WIN else ''))
    jtool=lambda name:java/(name+('.exe' if WIN else ''))
    run([tool('aapt2'),'compile','--dir',res,'-o',BUILD/'resources.zip'])
    assets=BUILD/'assets';assets.mkdir(exist_ok=True)
    # aapt2 accepts an asset directory; avoid a second copy of the image corpus.
    # The exported site is linked below by explicit zip entries.
    run([tool('aapt2'),'link','-o',BUILD/'resources.apk','--manifest',MOBILE/'android/AndroidManifest.xml','-I',platform,'--min-sdk-version','26','--target-sdk-version','35','--version-code',str(ver['code']),'--version-name',ver['name'],BUILD/'resources.zip'])
    source_files=[]
    for source in sorted((MOBILE/'android/src').rglob('*.java')):
        clean=BUILD/'src'/source.relative_to(MOBILE/'android/src')
        clean.parent.mkdir(parents=True,exist_ok=True)
        clean.write_text(source.read_text(encoding='utf-8-sig'),encoding='utf-8')
        source_files.append(clean)
    run([jtool('javac'),'-encoding','UTF-8','-source','8','-target','8','-classpath',platform,'-d',classes,*source_files])
    jar=BUILD/'classes.jar'
    with zipfile.ZipFile(jar,'w') as z:
        for p in classes.rglob('*.class'):z.write(p,p.relative_to(classes).as_posix())
    run([jtool('java'),'-cp',bt/'lib/d8.jar','com.android.tools.r8.D8','--lib',platform,'--min-api','26','--output',dex,jar])
    unsigned=BUILD/'unsigned.apk';shutil.copyfile(BUILD/'resources.apk',unsigned)
    with zipfile.ZipFile(unsigned,'a',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in dex.glob('*.dex'):z.write(p,p.name)
        for p in OUT.rglob('*'):
            if p.is_file():z.write(p,'assets/site/'+p.relative_to(OUT).as_posix())
    run([tool('zipalign'),'-f','-p','4',unsigned,BUILD/'aligned.apk'])
    local=MOBILE/'.local';local.mkdir(exist_ok=True)
    store=Path(os.environ.get('SIGNING_KEYSTORE',local/'atlas.keystore'))
    credentials=local/'signing.json'
    alias=os.environ.get('SIGNING_ALIAS','atlas')
    password=os.environ.get('SIGNING_PASSWORD')
    if not password:
        if os.environ.get('CI'):raise RuntimeError('CI requires persistent signing secrets; no disposable signing key is created')
        if credentials.exists():password=json.loads(credentials.read_text())['password']
        else:
            password=secrets.token_urlsafe(32)
            credentials.write_text(json.dumps({'password':password,'alias':alias}),encoding='utf-8')
    env=dict(os.environ,ATLAS_KEY_PASSWORD=password)
    if not store.exists():
        if os.environ.get('CI'):raise RuntimeError('Signing keystore missing')
        run([jtool('keytool'),'-genkeypair','-keystore',store,'-storepass:env','ATLAS_KEY_PASSWORD','-keypass:env','ATLAS_KEY_PASSWORD','-alias',alias,'-keyalg','RSA','-keysize','3072','-validity','10000','-dname','CN=World Medals Personal Research'],env=env)
    output=MOBILE/'build'/f'world-medals-{ver["name"]}.apk'
    run([jtool('java'),'-jar',bt/'lib/apksigner.jar','sign','--ks',store,'--ks-key-alias',alias,'--ks-pass','env:ATLAS_KEY_PASSWORD','--key-pass','env:ATLAS_KEY_PASSWORD','--out',output,BUILD/'aligned.apk'],env=env)
    run([jtool('java'),'-jar',bt/'lib/apksigner.jar','verify','--verbose',output])
    sha=hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix('.apk.sha256').write_text(sha+'  '+output.name+'\n')
    (MOBILE/'build/apk-build-info.json').write_text(json.dumps({
        'artifact':output.name,'version':ver,'sourceCommit':source_commit,
        'trackedBuildSourcesModified':source_modified,'androidPlatform':36,
        'androidBuildTools':bt.name,'apksignerVerification':'passed',
        'bytes':output.stat().st_size},indent=2),encoding='utf-8')
    # Preserve installers and intermediates. Cleanup is a separate confirmed action.
    removed=[]  # Building or publishing does not authorize permanent deletion.
    print(json.dumps({'obsolete_apk_files_removed':len(removed),'bytes_reclaimed':sum(x['bytes'] for x in removed)}))
    print(json.dumps({'apk':str(output),'bytes':output.stat().st_size,'sha256':sha}))
if __name__=='__main__':build()
