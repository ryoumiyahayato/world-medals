param([string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$base = 'https://www.samlhoc.fr'
$seed = "$base/phaleristique/ordres-chevalerie/legion_honneur/"
$cache = Join-Path $ProjectRoot 'sources\cache\france_samlhoc_legion_honour'
$pageDir = Join-Path $cache 'pages'
$imageDir = Join-Path $cache 'images'
$rawPath = Join-Path $ProjectRoot 'data\raw_candidates\france_samlhoc_legion_honour.jsonl'
$sweepPath = Join-Path $ProjectRoot 'data\source_sweeps\france_samlhoc_legion_honour.json'
New-Item -ItemType Directory -Force -Path $pageDir,$imageDir | Out-Null

function Get-Page([string]$Url) {
    Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 30 -Headers @{'User-Agent'='world-medals research catalogue/1.0'}
}
function Safe-Name([string]$Url, [string]$Fallback) {
    $name = [IO.Path]::GetFileName(([Uri]$Url).AbsolutePath)
    if (-not $name) { $name = $Fallback }
    $name = $name -replace '[^A-Za-z0-9._-]','_'
    return $name
}

$seedResponse = Get-Page $seed
$seedFile = Join-Path $pageDir 'legion_honneur_main.html'
[IO.File]::WriteAllText($seedFile, $seedResponse.Content, [Text.UTF8Encoding]::new($false))

$pageUrls = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$null = $pageUrls.Add($seed)
foreach ($m in [regex]::Matches($seedResponse.Content, 'href=["'']([^"''#?]+)["'']', 'IgnoreCase')) {
    $href = [Net.WebUtility]::HtmlDecode($m.Groups[1].Value)
    if ($href.StartsWith('/phaleristique/ordres-chevalerie/legion_honneur/')) {
        $null = $pageUrls.Add(([Uri]::new([Uri]$base,$href)).AbsoluteUri)
    }
}

$pages = [Collections.Generic.List[object]]::new()
$imageUrls = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$rawLines = [Collections.Generic.List[string]]::new()
$pageIndex = 0
foreach ($url in @($pageUrls | Sort-Object)) {
    $pageIndex++
    if ($url -eq $seed) { $response = $seedResponse; $fileName='legion_honneur_main.html' }
    else {
        Start-Sleep -Milliseconds 250
        try { $response = Get-Page $url } catch {
            $pages.Add([ordered]@{url=$url; status='fetch_failed'; error=$_.Exception.Message})
            continue
        }
        $slug = ([Uri]$url).AbsolutePath.Trim('/').Split('/')[-1]
        $fileName = ('{0:D2}_{1}.html' -f $pageIndex,($slug -replace '[^A-Za-z0-9._-]','_'))
        [IO.File]::WriteAllText((Join-Path $pageDir $fileName), $response.Content, [Text.UTF8Encoding]::new($false))
    }
    $titleMatch = [regex]::Match($response.Content,'<title[^>]*>(.*?)</title>','IgnoreCase,Singleline')
    $title = if ($titleMatch.Success) {[Net.WebUtility]::HtmlDecode(($titleMatch.Groups[1].Value -replace '<[^>]+>',' ' -replace '\s+',' ').Trim())} else {$url}
    $pageImages = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($im in [regex]::Matches($response.Content,'(?:data-lazy-src|src|href)=["'']([^"'']+/wp-content/uploads/import/www\.france-phaleristique\.com/images/[^"''?# ]+\.(?:jpg|jpeg|png|webp))','IgnoreCase')) {
        $src = [Net.WebUtility]::HtmlDecode($im.Groups[1].Value)
        if ($src.StartsWith('/')) { $src = ([Uri]::new([Uri]$base,$src)).AbsoluteUri }
        $null = $pageImages.Add($src); $null = $imageUrls.Add($src)
    }
    $localRel = 'sources/cache/france_samlhoc_legion_honour/pages/' + $fileName
    $pageRecord = [ordered]@{url=$url; title=$title; status='cached'; local_cache=$localRel; image_urls=@($pageImages | Sort-Object)}
    $pages.Add($pageRecord)
    $raw = [ordered]@{
        source_id='FR-SAMLHOC-LEGION-HONOUR'
        source_system='SAMLHOC / France Phaléristique'
        accessed='2026-09-26'
        page_title=$title
        page_url=$url
        local_cache=$localRel
        original_image_urls=@($pageImages | Sort-Object)
        family_guess='FRA-LEGION-HONOUR'
        status='RAW_SOURCE_PAGE'
        note='Direct subpage of the SAMLHOC Legion of Honour directory. Identity, regime/model and grade must be normalized from the page title and object caption before public use.'
    }
    $rawLines.Add(($raw | ConvertTo-Json -Depth 6 -Compress))
}

$images = [Collections.Generic.List[object]]::new()
$usedNames = @{}
foreach ($url in @($imageUrls | Sort-Object)) {
    $name = Safe-Name $url 'image.jpg'
    if ($usedNames.ContainsKey($name)) { $usedNames[$name]++; $name = ([IO.Path]::GetFileNameWithoutExtension($name) + '_' + $usedNames[$name] + [IO.Path]::GetExtension($name)) } else { $usedNames[$name]=1 }
    $path = Join-Path $imageDir $name
    try {
        Start-Sleep -Milliseconds 250
        Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 30 -Headers @{'User-Agent'='world-medals research catalogue/1.0'} -OutFile $path
        $bitmap=[Drawing.Image]::FromFile($path)
        try {$w=[int]$bitmap.Width;$h=[int]$bitmap.Height} finally {$bitmap.Dispose()}
        $images.Add([ordered]@{url=$url; local_path=('sources/cache/france_samlhoc_legion_honour/images/'+$name); status='downloaded_decoded'; width=$w; height=$h; bytes=(Get-Item $path).Length; sha256=(Get-FileHash $path -Algorithm SHA256).Hash.ToLowerInvariant(); visually_reviewed=$false; publication_eligible=$false})
    } catch {
        $images.Add([ordered]@{url=$url; local_path=('sources/cache/france_samlhoc_legion_honour/images/'+$name); status='download_failed_or_invalid'; error=$_.Exception.Message})
    }
}

[IO.File]::WriteAllLines($rawPath, $rawLines, [Text.UTF8Encoding]::new($false))
$sweep=[ordered]@{
    source_id='FR-SAMLHOC-LEGION-HONOUR'
    source_name="SAMLHOC / France Phaléristique — Légion d’honneur directory"
    as_of='2026-09-26'
    status='directory_and_direct_subpages_swept_pending_visual_image_review'
    boundary='Seed page and every distinct direct child URL under /phaleristique/ordres-chevalerie/legion_honneur/ exposed by the seed. Sibling editorial pages and unrelated decorations excluded.'
    seed_url=$seed
    discovered_page_urls=$pageUrls.Count
    cached_pages=@($pages | Where-Object {$_.status -eq 'cached'}).Count
    failed_pages=@($pages | Where-Object {$_.status -eq 'fetch_failed'}).Count
    raw_source_rows=$rawLines.Count
    distinct_award_image_urls=$imageUrls.Count
    downloaded_decoded_images=@($images | Where-Object {$_.status -eq 'downloaded_decoded'}).Count
    failed_images=@($images | Where-Object {$_.status -eq 'download_failed'}).Count
    pages=$pages
    images=$images
    rights='SAMLHOC legal notice reserves reproduction/adaptation rights; all downloaded media remain internal research evidence pending a separate reusable source.'
    next_checkpoint='Visually review downloaded images, map each page to historical regime/model and grade, then deduplicate against existing France volumes. Do not rescan these cached pages.'
}
[IO.File]::WriteAllText($sweepPath, ($sweep|ConvertTo-Json -Depth 12), [Text.UTF8Encoding]::new($false))
$sweep | Select-Object source_id,status,discovered_page_urls,cached_pages,failed_pages,raw_source_rows,distinct_award_image_urls,downloaded_decoded_images,failed_images | ConvertTo-Json
