param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
$AccessDate = '2026-09-26'
$Headers = @{ 'User-Agent' = 'world-medals-source-sweep/2.0 (local research catalogue)' }
$CacheRoot = Join-Path $ProjectRoot 'sources\pages\wawards_egypt_sudan'
$RawRoot = Join-Path $ProjectRoot 'data\raw_candidates'
$SweepRoot = Join-Path $ProjectRoot 'data\source_sweeps'
New-Item -ItemType Directory -Force -Path $CacheRoot, $RawRoot, $SweepRoot | Out-Null

function Get-Hash([string]$Text) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($Text))).Replace('-', '').ToLowerInvariant())
    } finally { $sha.Dispose() }
}

function Get-AbsoluteUrl([string]$Base, [string]$Href) {
    if ([string]::IsNullOrWhiteSpace($Href) -or $Href.StartsWith('#')) { return $null }
    return ([Uri]::new([Uri]$Base, $Href)).AbsoluteUri
}

function Get-CleanText([string]$Html) {
    $withoutScripts = [regex]::Replace($Html, '<(script|style)[^>]*>.*?</\1>', ' ', 'Singleline,IgnoreCase')
    $withoutTags = [regex]::Replace($withoutScripts, '<[^>]+>', ' ')
    return ([Net.WebUtility]::HtmlDecode($withoutTags) -replace '\s+', ' ').Trim()
}

function Get-PageTitle([string]$Html, [string]$Fallback) {
    foreach ($tag in @('h1','h2','h3','title')) {
        $m = [regex]::Match($Html, "<$tag[^>]*>(.*?)</$tag>", 'Singleline,IgnoreCase')
        if ($m.Success) {
            $t = Get-CleanText $m.Groups[1].Value
            if ($t) { return $t }
        }
    }
    return $Fallback
}

function Save-Page([string]$Url) {
    $hash = Get-Hash $Url
    $path = Join-Path $CacheRoot ($hash + '.html')
    if (Test-Path -LiteralPath $path) {
        return [pscustomobject]@{ Url=$Url; Path=$path; Html=[IO.File]::ReadAllText($path); Cached=$true }
    }
    $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 30 -Headers $Headers
    [IO.File]::WriteAllText($path, $response.Content, [Text.UTF8Encoding]::new($false))
    Start-Sleep -Milliseconds 250
    return [pscustomobject]@{ Url=$Url; Path=$path; Html=$response.Content; Cached=$false }
}

function Get-Links([string]$Html, [string]$BaseUrl) {
    $out = [Collections.Generic.List[string]]::new()
    foreach ($m in [regex]::Matches($Html, '<a\b[^>]*\bhref=["'']([^"'']+)["'']', 'IgnoreCase')) {
        $u = Get-AbsoluteUrl $BaseUrl $m.Groups[1].Value
        if ($u) { $out.Add($u) }
    }
    return @($out | Sort-Object -Unique)
}

function Get-ImageLinks([string]$Html, [string]$BaseUrl) {
    $out = [Collections.Generic.List[string]]::new()
    foreach ($m in [regex]::Matches($Html, '<img\b[^>]*\bsrc=["'']([^"'']+)["'']', 'IgnoreCase')) {
        $u = Get-AbsoluteUrl $BaseUrl $m.Groups[1].Value
        if ($u -and $u -notmatch '(logo|flag|counter|icon)') { $out.Add($u) }
    }
    return @($out | Sort-Object -Unique)
}

function New-Candidate([string]$System, [string]$Scope, [string]$Url, [string]$Html, [string]$CachePath) {
    $slug = [IO.Path]::GetFileNameWithoutExtension(([Uri]$Url).AbsolutePath)
    $title = Get-PageTitle $Html (($slug -replace '-', ' ').Trim())
    $text = Get-CleanText $Html
    $years = @([regex]::Matches($text, '(?<!\d)(1[789]\d{2}|20\d{2})(?!\d)') | ForEach-Object { [int]$_.Value } | Sort-Object -Unique | Select-Object -First 12)
    $category = if ($title -match '(?i)medal') { 'medal' } elseif ($title -match '(?i)order|collar|sash|star|decoration') { 'order_or_decoration' } else { 'unknown' }
    $images = @(Get-ImageLinks $Html $Url)
    $excerpt = if ($text.Length -gt 900) { $text.Substring(0,900) } else { $text }
    return [ordered]@{
        source_id = ($System.ToLowerInvariant() -replace '[^a-z0-9]+','-').Trim('-') + '-' + (Get-Hash $Url).Substring(0,20)
        source_system = $System
        source_type = 'specialist_catalogue'
        scope = $Scope
        page_title = $title
        working_name_zh = '待译'
        original_name = $title
        english_name = $title
        aliases = @()
        date_candidates = $years
        category = $category
        grade_material_clues = '待核'
        page_url = $Url
        image_page_url = if ($images.Count) { $Url } else { $null }
        original_image_urls = $images
        notes = $excerpt
        status = 'RAW_CANDIDATE'
        cache_file = $CachePath.Substring($ProjectRoot.Length + 1).Replace('\','/')
        access_date = $AccessDate
    }
}

function Write-JsonLines([string]$Path, [object[]]$Rows) {
    $lines = foreach ($row in $Rows) { $row | ConvertTo-Json -Depth 8 -Compress }
    [IO.File]::WriteAllLines($Path, $lines, [Text.UTF8Encoding]::new($false))
}

$failures = [Collections.Generic.List[object]]::new()
$recordsByScope = @{ egypt=[Collections.Generic.List[object]]::new(); sudan=[Collections.Generic.List[object]]::new() }
$pagesByScope = @{ egypt=[Collections.Generic.List[string]]::new(); sudan=[Collections.Generic.List[string]]::new() }

# Wawards Egypt: root -> four period pages -> every visible award detail page.
$egyptRoot = 'https://wawards.org/en/egypt.html'
try {
    $root = Save-Page $egyptRoot
    $periods = @(Get-Links $root.Html $egyptRoot | Where-Object { $_ -match '^https://wawards\.org/egypt/[^/]+\.html$' })
    foreach ($periodUrl in $periods) {
        try {
            $period = Save-Page $periodUrl
            $pagesByScope.egypt.Add($periodUrl)
            $prefix = ([Uri]$periodUrl).AbsolutePath.Replace('.html','/')
            $details = @(Get-Links $period.Html $periodUrl | Where-Object { ([Uri]$_).Host -eq 'wawards.org' -and ([Uri]$_).AbsolutePath.StartsWith($prefix) -and $_ -match '\.html$' })
            foreach ($detailUrl in $details) {
                try {
                    $detail = Save-Page $detailUrl
                    $pagesByScope.egypt.Add($detailUrl)
                    $recordsByScope.egypt.Add((New-Candidate 'Wawards Egypt' 'egypt' $detailUrl $detail.Html $detail.Path))
                } catch { $failures.Add([ordered]@{scope='egypt'; url=$detailUrl; error=$_.Exception.Message}) }
            }
        } catch { $failures.Add([ordered]@{scope='egypt'; url=$periodUrl; error=$_.Exception.Message}) }
    }
} catch { $failures.Add([ordered]@{scope='egypt'; url=$egyptRoot; error=$_.Exception.Message}) }

# Wawards Sudan: root -> every visible Sudan detail page.
$sudanRoot = 'https://wawards.org/en/sudan.html'
try {
    $root = Save-Page $sudanRoot
    $details = @(Get-Links $root.Html $sudanRoot | Where-Object { $_ -match '^https://wawards\.org/sudan/[^/]+\.html$' })
    foreach ($detailUrl in $details) {
        try {
            $detail = Save-Page $detailUrl
            $pagesByScope.sudan.Add($detailUrl)
            $recordsByScope.sudan.Add((New-Candidate 'Wawards Sudan' 'sudan' $detailUrl $detail.Html $detail.Path))
        } catch { $failures.Add([ordered]@{scope='sudan'; url=$detailUrl; error=$_.Exception.Message}) }
    }
} catch { $failures.Add([ordered]@{scope='sudan'; url=$sudanRoot; error=$_.Exception.Message}) }

# Separate Sudan text index: each listed award is retained as an independent discovery record.
$sudanTextUrl = 'https://medals.org.uk/sudan/sudan-text.htm'
try {
    $page = Save-Page $sudanTextUrl
    $listMatches = [regex]::Matches($page.Html, '<li[^>]*>(.*?)</li>', 'Singleline,IgnoreCase')
    $n = 0
    foreach ($m in $listMatches) {
        $name = Get-CleanText $m.Groups[1].Value
        if (-not $name -or $name -match '(?i)world medals index|ribbons|links') { continue }
        $n++
        $recordsByScope.sudan.Add([ordered]@{
            source_id = 'medals-org-uk-sudan-' + $n.ToString('000')
            source_system = 'Medals.org.uk Sudan text list'
            source_type = 'specialist_catalogue'
            scope = 'sudan'
            page_title = $name
            working_name_zh = '待译'
            original_name = $name
            english_name = $name
            aliases = @()
            date_candidates = @()
            category = if ($name -match '(?i)medal') {'medal'} else {'order_or_decoration'}
            grade_material_clues = '未知'
            page_url = $sudanTextUrl
            image_page_url = $null
            original_image_urls = @()
            notes = 'Text-list entry; requires cross-source normalization and image binding.'
            status = 'RAW_CANDIDATE'
            cache_file = $page.Path.Substring($ProjectRoot.Length + 1).Replace('\','/')
            access_date = $AccessDate
        })
    }
    $pagesByScope.sudan.Add($sudanTextUrl)
} catch { $failures.Add([ordered]@{scope='sudan'; url=$sudanTextUrl; error=$_.Exception.Message}) }

Write-JsonLines (Join-Path $RawRoot 'wawards_egypt.jsonl') @($recordsByScope.egypt)
Write-JsonLines (Join-Path $RawRoot 'wawards_medalsorg_sudan.jsonl') @($recordsByScope.sudan)

$status = [ordered]@{
    as_of = $AccessDate
    method = 'SOURCE_FIRST_BULK_INGESTION'
    sources = @(
        [ordered]@{source_id='wawards_egypt'; status=if (($failures | Where-Object scope -eq 'egypt').Count) {'partial'} else {'completed'}; coverage='All four period indexes and every visible award detail link'; pages_processed=$pagesByScope.egypt.Count; candidates=$recordsByScope.egypt.Count},
        [ordered]@{source_id='wawards_sudan'; status=if (($failures | Where-Object { $_.scope -eq 'sudan' -and $_.url -like 'https://wawards.org/*' }).Count) {'partial'} else {'completed'}; coverage='Sudan index and every visible award detail link'; pages_processed=($pagesByScope.sudan | Where-Object {$_ -like 'https://wawards.org/*'}).Count; candidates=($recordsByScope.sudan | Where-Object source_system -eq 'Wawards Sudan').Count},
        [ordered]@{source_id='medals_org_uk_sudan'; status=if (($failures | Where-Object url -eq $sudanTextUrl).Count) {'blocked'} else {'completed'}; coverage='Complete current text list'; pages_processed=if ($pagesByScope.sudan -contains $sudanTextUrl) {1} else {0}; candidates=($recordsByScope.sudan | Where-Object source_system -eq 'Medals.org.uk Sudan text list').Count}
    )
    totals = [ordered]@{pages_processed=$pagesByScope.egypt.Count + $pagesByScope.sudan.Count; candidates=$recordsByScope.egypt.Count + $recordsByScope.sudan.Count; failures=$failures.Count}
    failures = @($failures)
}
[IO.File]::WriteAllText((Join-Path $SweepRoot 'egypt_sudan_first_sweep_2026-09-26.json'), ($status | ConvertTo-Json -Depth 8), [Text.UTF8Encoding]::new($false))
$status | ConvertTo-Json -Depth 8
