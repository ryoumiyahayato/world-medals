param([string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot))

$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue'
$Base='https://www.medalbook.com'; $Scope='/africa-north/sudan'
$Indexes=@(
  'https://www.medalbook.com/africa-north/sudan-1',
  'https://www.medalbook.com/africa-north/sudan-1?page=2'
)
$Cache=Join-Path $ProjectRoot 'sources\pages\medalbook_sudan'
$ImageRoot=Join-Path $ProjectRoot 'assets\raw\medalbook_sudan'
$Out=Join-Path $ProjectRoot 'data\raw_candidates\medalbook_sudan.jsonl'
$State=Join-Path $ProjectRoot 'data\source_sweeps\medalbook_sudan.json'
$Headers=@{'User-Agent'='world-medals-source-sweep/2.0 (local research catalogue)'}
New-Item -ItemType Directory -Force -Path $Cache,$ImageRoot,(Split-Path $Out),(Split-Path $State)|Out-Null

function Hash([string]$s){$h=[Security.Cryptography.SHA256]::Create();try{return([BitConverter]::ToString($h.ComputeHash([Text.Encoding]::UTF8.GetBytes($s))).Replace('-','').ToLowerInvariant())}finally{$h.Dispose()}}
function Fetch([string]$url){$p=Join-Path $Cache ((Hash $url)+'.html');if(Test-Path $p){return [IO.File]::ReadAllText($p)};$r=Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 35 -Headers $Headers;[IO.File]::WriteAllText($p,$r.Content,[Text.UTF8Encoding]::new($false));Start-Sleep -Milliseconds 250;return $r.Content}
function Clean([string]$s){return([Net.WebUtility]::HtmlDecode(([regex]::Replace($s,'<[^>]+>',' '))) -replace '\s+',' ').Trim()}
function Meta([string]$html,[string]$name){$m=[regex]::Match($html,'<meta[^>]+(?:property|name)=["'']'+[regex]::Escape($name)+'["''][^>]+content=["'']([^"'']*)["'']','IgnoreCase');if(-not$m.Success){$m=[regex]::Match($html,'<meta[^>]+content=["'']([^"'']*)["''][^>]+(?:property|name)=["'']'+[regex]::Escape($name)+'["'']','IgnoreCase')};if($m.Success){return Clean $m.Groups[1].Value};return $null}
function Links([string]$html,[string]$base){$a=foreach($m in [regex]::Matches($html,'<a\b[^>]*href=["'']([^"'']+)["'']','IgnoreCase')){try{([Uri]::new([Uri]$base,$m.Groups[1].Value)).AbsoluteUri}catch{}};return @($a|Sort-Object -Unique)}
function Images([string]$html,[string]$base){$a=foreach($m in [regex]::Matches($html,'<(?:img|source)\b[^>]*(?:src|data-src)=["'']([^"'']+)["'']','IgnoreCase')){$u=$m.Groups[1].Value;if($u -match '/attachments/' -and $u -match '\.(?:jpe?g|png)(?:\?|$)'){try{([Uri]::new([Uri]$base,$u)).AbsoluteUri}catch{}}};return @($a|Sort-Object -Unique)}

$itemUrls=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase);$fail=[Collections.Generic.List[object]]::new();$indexCounts=[ordered]@{}
foreach($url in $Indexes){try{$html=Fetch $url;$found=0;foreach($link in Links $html $url){$uri=[Uri]$link;if($uri.Host -ne 'www.medalbook.com'){continue};$path=$uri.AbsolutePath.TrimEnd('/');if($path -match '^/africa-north/sudan/(orders|medals-decorations)/[^/]+/[^/]+$'){[void]$itemUrls.Add($Base+$path);$found++}};$indexCounts[$url]=$found}catch{$fail.Add([ordered]@{url=$url;stage='index';error=$_.Exception.Message})}}

$rows=[Collections.Generic.List[object]]::new();$imageDownloaded=0;$imageByteValid=0
foreach($url in @($itemUrls|Sort-Object)){
 try{$html=Fetch $url;$title=Meta $html 'og:title';if(-not$title){$title=([Uri]$url).Segments[-1].Trim('/') -replace '-',' '};$desc=Meta $html 'og:description';$imgs=@(Images $html $url);$locals=[Collections.Generic.List[string]]::new();foreach($img in $imgs){try{$ext=if(([Uri]$img).AbsolutePath -match '\.png$'){'.png'}else{'.jpg'};$p=Join-Path $ImageRoot ((Hash $img).Substring(0,24)+$ext);if(-not(Test-Path $p)){Invoke-WebRequest -Uri $img -OutFile $p -TimeoutSec 60 -Headers $Headers;Start-Sleep -Milliseconds 180};$imageDownloaded++;if((Get-Item $p).Length -gt 256){$imageByteValid++;$locals.Add($p.Substring($ProjectRoot.Length+1).Replace('\','/'))}}catch{$fail.Add([ordered]@{url=$img;stage='image';error=$_.Exception.Message})}};$dates=@([regex]::Matches(($title+' '+$desc),'(?<!\d)(1[5-9]\d{2}|20\d{2})(?!\d)')|ForEach-Object{[int]$_.Value}|Sort-Object -Unique);$path=([Uri]$url).AbsolutePath;$parts=$path.Trim('/').Split('/');$family=$parts[-2] -replace '-',' ';$category=$parts[-3];$rows.Add([ordered]@{source_id='medalbook-sudan-'+(Hash $url).Substring(0,16);source_system='MedalBook Sudan catalogue';scope='sudan';page_title=$title;original_name=$title;date_candidates=$dates;category=$category;family_hint=$family;grade_material_clues=$title;page_url=$url;original_image_urls=$imgs;local_raw_images=@($locals);notes=$desc;status='RAW_CANDIDATE';cache_file='sources/pages/medalbook_sudan/'+(Hash $url)+'.html';access_date='2026-09-26'})}catch{$fail.Add([ordered]@{url=$url;stage='item';error=$_.Exception.Message})}
}
$lines=foreach($row in $rows){$row|ConvertTo-Json -Depth 10 -Compress};[IO.File]::WriteAllLines($Out,@($lines),[Text.UTF8Encoding]::new($false))
$imageUrlCount=0;foreach($row in $rows){$imageUrlCount+=@($row.original_image_urls).Count}
$state=[ordered]@{schema_version='2.0';as_of='2026-09-26';source_id='medalbook_sudan';status=if($fail.Count){'partial'}else{'completed'};planned_index_pages=$Indexes.Count;processed_index_pages=$indexCounts.Count;index_counts=$indexCounts;discovered_item_pages=$itemUrls.Count;processed_item_pages=$rows.Count;original_image_urls=$imageUrlCount;raw_images_downloaded=$imageDownloaded;raw_images_byte_valid=$imageByteValid;failures=@($fail);raw_candidate_file='data/raw_candidates/medalbook_sudan.jsonl';image_directory='assets/raw/medalbook_sudan';note='Commercial images retained for internal review only; no image promoted to HTML.'};[IO.File]::WriteAllText($State,($state|ConvertTo-Json -Depth 12),[Text.UTF8Encoding]::new($false));$state|ConvertTo-Json -Depth 6
