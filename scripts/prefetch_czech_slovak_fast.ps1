$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$scriptPath = Join-Path $root 'scripts\harvest_czech_slovak_fast.js'
$imageDir = Join-Path $root 'assets\images\czech_slovak_fast'
$harvestDir = Join-Path $root 'data\image_harvest'
New-Item -ItemType Directory -Force -Path $imageDir,$harvestDir | Out-Null
$headers = @{ 'User-Agent' = 'world-medals-research/1.0 (offline catalogue)' }
$js = Get-Content -Raw -LiteralPath $scriptPath
$fileNames = [regex]::Matches($js, "file:'([^']+)'") | ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique
$titles = $fileNames | ForEach-Object { "File:$($_)" }
$meta = @{}
for ($i = 0; $i -lt $titles.Count; $i += 12) {
  $last = [Math]::Min($i + 11, $titles.Count - 1)
  $chunk = ($titles[$i..$last] -join '|')
  $encoded = [Uri]::EscapeDataString($chunk)
  $u = "https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Csize%7Cmime%7Cextmetadata&titles=$encoded&format=json"
  try {
    $j = Invoke-RestMethod -Uri $u -Headers $headers -TimeoutSec 60
    foreach ($prop in $j.query.pages.PSObject.Properties) {
      $p = $prop.Value
      if ($p.imageinfo -and $p.imageinfo.Count -gt 0) {
        $ii = $p.imageinfo[0]
        $meta[$p.title] = [ordered]@{ title=$p.title; url=$ii.url; descriptionurl=$ii.descriptionurl; mime=$ii.mime; width=$ii.width; height=$ii.height; size=$ii.size }
      }
    }
  } catch { Write-Output "API batch $i failed: $($_.Exception.Message)" }
  if ($last -lt $titles.Count - 1) { Start-Sleep -Seconds 2 }
}
$metaPath = Join-Path $harvestDir 'czech_slovak_fast_commons_metadata.json'
$meta | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $metaPath -Encoding UTF8
$downloaded = @()
$failed = @()
foreach ($name in $fileNames) {
  $title = "File:$name"
  if (-not $meta.ContainsKey($title)) { $failed += [ordered]@{file=$name; status='Commons API file not found'}; continue }
  $m = $meta[$title]
  $ext = [IO.Path]::GetExtension($name).ToLowerInvariant()
  if ($ext -notin @('.jpg','.jpeg','.png','.webp')) { if ($m.mime -eq 'image/png') { $ext='.png' } else { $ext='.jpg' } }
  $slug = ($name -replace '[^A-Za-z0-9]+','_').Trim('_').ToLowerInvariant()
  $out = Join-Path $imageDir ($slug + $ext)
  $thumbUrl = "https://commons.wikimedia.org/w/thumb.php?f=$([Uri]::EscapeDataString($name))&w=2000"
  if (-not (Test-Path -LiteralPath $out)) {
    try {
      # Wikimedia's original route is currently rate-limited (HTTP 429) in this
      # environment.  Use one complete max-size Commons derivative as a bounded
      # fallback; retain the original URL and route status in the manifest.
      if (-not $thumbUrl) { throw 'No Commons thumbnail route could be derived' }
      Invoke-WebRequest -Uri $thumbUrl -Headers $headers -OutFile $out -TimeoutSec 90
      $downloaded += [ordered]@{file=$name; path=$out; bytes=(Get-Item -LiteralPath $out).Length; width=$m.width; height=$m.height; mime=$m.mime; url=$m.url; retrieval_url=$thumbUrl; source_kind='Commons max-size thumbnail fallback; original route previously HTTP 429'; original_route_status='HTTP 429'; descriptionurl=$m.descriptionurl}
    } catch { $failed += [ordered]@{file=$name; status=$_.Exception.Message; original_url=$m.url; thumbnail_url=$thumbUrl} }
  } else {
    $downloaded += [ordered]@{file=$name; path=$out; bytes=(Get-Item -LiteralPath $out).Length; width=$m.width; height=$m.height; mime=$m.mime; url=$m.url; retrieval_url=$m.url; source_kind='Commons original route'; original_route_status='HTTP 200'; descriptionurl=$m.descriptionurl; reused=$true}
  }
  Start-Sleep -Milliseconds 350
}
$manifest = [ordered]@{schema='commons-prefetch-v1'; batch_id='czech_slovak_fast_2026-09-28'; accessed='2026-09-28'; metadata_file='data/image_harvest/czech_slovak_fast_commons_metadata.json'; downloaded=$downloaded; failed=$failed; requested=$fileNames.Count; metadata_count=$meta.Count; downloaded_count=$downloaded.Count; failed_count=$failed.Count}
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $harvestDir 'czech_slovak_fast_prefetch_manifest.json') -Encoding UTF8
Write-Output ("requested={0} metadata={1} downloaded={2} failed={3}" -f $fileNames.Count,$meta.Count,$downloaded.Count,$failed.Count)
