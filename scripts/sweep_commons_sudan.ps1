param([string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot))

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$Api = 'https://commons.wikimedia.org/w/api.php'
$AsOf = '2026-09-26'
$UserAgent = 'world-medals-source-sweep/2.0 (local research catalogue)'
$Out = Join-Path $ProjectRoot 'data\raw_candidates\commons_sudan.jsonl'
$StatePath = Join-Path $ProjectRoot 'data\source_sweeps\commons_sudan.json'
$CacheRoot = Join-Path $ProjectRoot 'sources\cache\commons_sudan'
$ImageRoot = Join-Path $ProjectRoot 'assets\raw\sudan_commons'
New-Item -ItemType Directory -Force -Path (Split-Path $Out), (Split-Path $StatePath), $CacheRoot, $ImageRoot | Out-Null

function Api-Get([hashtable]$Params) {
    $Params.action = 'query'; $Params.format = 'json'; $Params.formatversion = '2'
    $pairs = foreach ($kv in $Params.GetEnumerator()) { [Uri]::EscapeDataString([string]$kv.Key) + '=' + [Uri]::EscapeDataString([string]$kv.Value) }
    $url = $Api + '?' + ($pairs -join '&')
    $result = Invoke-RestMethod -Uri $url -Headers @{'User-Agent'=$UserAgent} -TimeoutSec 30
    Start-Sleep -Milliseconds 200
    return $result
}

function Hash([string]$Value) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($Value))).Replace('-','').ToLowerInvariant()) }
    finally { $sha.Dispose() }
}

function Meta($Object,[string]$Name) {
    if (-not $Object) { return $null }
    $p = $Object.PSObject.Properties[$Name]
    if (-not $p) { return $null }
    $v = $p.Value
    if ($v.PSObject.Properties['value']) { return $v.value }
    return $v
}

$queue = [Collections.Generic.Queue[string]]::new()
$queue.Enqueue('Category:Orders, decorations and medals of Sudan')
$visited = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$fileTitles = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$categoryLog = [Collections.Generic.List[object]]::new()
$failures = [Collections.Generic.List[object]]::new()
$excluded = [Collections.Generic.List[string]]::new()

while ($queue.Count -gt 0) {
    $category = $queue.Dequeue()
    if (-not $visited.Add($category)) { continue }
    $continuation = $null
    $membersSeen = 0
    do {
        $params = @{list='categorymembers'; cmtitle=$category; cmtype='file|subcat'; cmlimit='max'}
        if ($continuation) { $params.cmcontinue = $continuation }
        try {
            $data = Api-Get $params
            foreach ($member in @($data.query.categorymembers)) {
                $membersSeen++
                if ($member.ns -eq 6) { [void]$fileTitles.Add($member.title) }
                elseif ($member.ns -eq 14) {
                    if ($member.title -match '(?i)recipients|people|ribbon bars|barnstar|portraits|coat of arms') { $excluded.Add($member.title); continue }
                    if (-not $visited.Contains($member.title)) { $queue.Enqueue($member.title) }
                }
            }
            $continuation = if ($data.continue) { $data.continue.cmcontinue } else { $null }
        } catch {
            $failures.Add([ordered]@{stage='categorymembers'; category=$category; continuation=$continuation; error=$_.Exception.Message})
            $continuation = $null
        }
    } while ($continuation)
    $categoryLog.Add([ordered]@{category=$category; members_seen=$membersSeen})
}

$records = [Collections.Generic.List[object]]::new()
$downloaded = 0
$decoded = 0
$titles = @($fileTitles | Sort-Object)
for ($i=0; $i -lt $titles.Count; $i += 25) {
    $batch = @($titles[$i..([Math]::Min($i+24,$titles.Count-1))])
    try {
        $data = Api-Get @{titles=($batch -join '|'); prop='imageinfo'; iiprop='url|size|mime|mediatype|extmetadata|timestamp|sha1'; iilimit='1'}
        $cachePath = Join-Path $CacheRoot ('imageinfo_' + $i.ToString('0000') + '.json')
        [IO.File]::WriteAllText($cachePath, ($data | ConvertTo-Json -Depth 30), [Text.UTF8Encoding]::new($false))
        foreach ($page in @($data.query.pages)) {
            $info = @($page.imageinfo)[0]
            if (-not $info) { $failures.Add([ordered]@{stage='imageinfo'; title=$page.title; error='no imageinfo'}); continue }
            $license = Meta $info.extmetadata 'LicenseShortName'
            $artist = Meta $info.extmetadata 'Artist'
            $credit = Meta $info.extmetadata 'Credit'
            $description = Meta $info.extmetadata 'ImageDescription'
            $localPath = $null
            $downloadStatus = 'metadata_only'
            if ($info.mime -in @('image/jpeg','image/png','image/webp')) {
                $ext = switch ($info.mime) {'image/jpeg'{'.jpg'} 'image/png'{'.png'} 'image/webp'{'.webp'}}
                $localPath = Join-Path $ImageRoot ((Hash $page.title).Substring(0,20) + $ext)
                try {
                    if (-not (Test-Path -LiteralPath $localPath)) { Invoke-WebRequest -Uri $info.url -OutFile $localPath -Headers @{'User-Agent'=$UserAgent} -TimeoutSec 60; Start-Sleep -Milliseconds 250 }
                    $downloaded++
                    $bytes = [IO.File]::ReadAllBytes($localPath)
                    if ($bytes.Length -gt 128) { $decoded++; $downloadStatus='downloaded_raster_pending_visual_review' } else { throw 'download too small' }
                } catch { $failures.Add([ordered]@{stage='download'; title=$page.title; url=$info.url; error=$_.Exception.Message}); $downloadStatus='download_failed'; $localPath=$null }
            }
            $records.Add([ordered]@{
                source_id = 'commons-sudan-' + (Hash $page.title).Substring(0,16)
                source_system = 'Wikimedia Commons Sudan category tree'
                source_type = 'commons_file'
                scope = 'sudan'
                file_title = $page.title
                page_url = 'https://commons.wikimedia.org/wiki/' + [Uri]::EscapeDataString($page.title.Replace(' ','_'))
                original_image_url = $info.url
                width = $info.width
                height = $info.height
                mime = $info.mime
                sha1 = $info.sha1
                license = $license
                artist = $artist
                credit = $credit
                description = $description
                local_file = if ($localPath) { $localPath.Substring($ProjectRoot.Length+1).Replace('\','/') } else { $null }
                image_status = $downloadStatus
                status = 'RAW_IMAGE_CANDIDATE'
                access_date = $AsOf
            })
        }
    } catch { $failures.Add([ordered]@{stage='imageinfo_batch'; start=$i; error=$_.Exception.Message}) }
}

$lines = foreach ($row in $records) { $row | ConvertTo-Json -Depth 12 -Compress }
[IO.File]::WriteAllLines($Out,@($lines),[Text.UTF8Encoding]::new($false))
$state = [ordered]@{
    schema_version='2.0'; as_of=$AsOf; source_id='commons_sudan_awards'; status=if($failures.Count){'partial'}else{'completed'}
    seed='Category:Orders, decorations and medals of Sudan'
    coverage='Recursive category tree; all current pagination exhausted; person/ribbon/barnstar categories excluded'
    categories_fetched=$visited.Count; excluded_categories=@($excluded); unique_files=$fileTitles.Count
    candidate_rows=$records.Count; raster_files_downloaded=$downloaded; raster_files_byte_valid=$decoded
    failures=@($failures); raw_candidate_file='data/raw_candidates/commons_sudan.jsonl'; image_directory='assets/raw/sudan_commons'
    note='Downloaded files remain raw image candidates pending complete-object visual review and family binding; no file was promoted to index.html.'
}
[IO.File]::WriteAllText($StatePath,($state|ConvertTo-Json -Depth 15),[Text.UTF8Encoding]::new($false))
$state | ConvertTo-Json -Depth 6
