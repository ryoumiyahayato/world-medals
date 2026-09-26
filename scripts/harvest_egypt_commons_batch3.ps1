param([string]$ProjectRoot=(Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference='Stop';Add-Type -AssemblyName System.Drawing
$source=Get-Content (Join-Path $ProjectRoot 'data\image_harvest\egypt_commons_awards_batch1.json') -Raw|ConvertFrom-Json
$outDir=Join-Path $ProjectRoot 'assets\images\egypt_commons_batch1'
$outPath=Join-Path $ProjectRoot 'data\image_harvest\egypt_commons_awards_batch3.json'
New-Item -ItemType Directory -Force -Path $outDir|Out-Null
$records=[Collections.Generic.List[object]]::new()
foreach($c in $source.candidates){
 $ext=[IO.Path]::GetExtension(([Uri]$c.original_image_url).AbsolutePath);if(-not $ext){$ext='.jpg'}
 $name=$c.candidate_id+$ext;$path=Join-Path $outDir $name
 try{
  if($c.candidate_id -eq 'EGY-COMMONS-001'){
   $cached=Join-Path $ProjectRoot 'sources\cache\egypt_commons_awards\harvest\images_batch2\EGY-COMMONS-001.png'
   Copy-Item -LiteralPath $cached -Destination $path -Force
  }else{
   Start-Sleep -Milliseconds 1200
   Invoke-WebRequest -Uri $c.original_image_url -UseBasicParsing -TimeoutSec 45 -Headers @{'User-Agent'='world-medals/1.0 (offline research catalogue)'} -OutFile $path
  }
  $im=[Drawing.Image]::FromFile($path);try{$w=[int]$im.Width;$h=[int]$im.Height}finally{$im.Dispose()}
  $records.Add([ordered]@{candidate_id=$c.candidate_id;family_id=$c.family_id;file_title=$c.file_title;role=$c.role;page_url=$c.page_url;image_url=$c.original_image_url;license=$c.license;author=$c.author_or_uploader;local_path=('assets/images/egypt_commons_batch1/'+$name);status='downloaded_decoded';width=$w;height=$h;bytes=(Get-Item $path).Length;sha256=(Get-FileHash $path -Algorithm SHA256).Hash.ToLowerInvariant();visually_reviewed=$false;body_eligible=$false})
 }catch{
  $records.Add([ordered]@{candidate_id=$c.candidate_id;family_id=$c.family_id;file_title=$c.file_title;page_url=$c.page_url;image_url=$c.original_image_url;status='failed';error=$_.Exception.Message})
 }
}
$manifest=[ordered]@{schema='image-harvest-v1';batch_id='egypt_commons_awards_batch3';as_of='2026-09-26';scope='Exact 19 candidates from batch1 only; original files downloaded sequentially at low rate';records=$records;counts=[ordered]@{candidates=$records.Count;downloaded_decoded=@($records|Where-Object{$_.status-eq'downloaded_decoded'}).Count;failed=@($records|Where-Object{$_.status-eq'failed'}).Count;visually_reviewed=0;body_eligible=0};public_files_modified=@();next_checkpoint='Visual review all decoded originals, map exact grades/variants, and build an Egypt volume from only complete correctly identified open-licence images.'}
[IO.File]::WriteAllText($outPath,($manifest|ConvertTo-Json -Depth 12),[Text.UTF8Encoding]::new($false))
$manifest.counts|ConvertTo-Json
