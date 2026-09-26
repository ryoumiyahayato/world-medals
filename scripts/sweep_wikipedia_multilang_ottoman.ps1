Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$Root = (Get-Location).Path
$AsOf = '2026-09-26'
$UserAgent = 'world-medals-source-sweep/1.0 (research catalogue; no original-image downloads)'
$Out = Join-Path $Root 'data/raw_candidates/wikipedia_multilang_ottoman.jsonl'
$StatePath = Join-Path $Root 'data/source_sweeps/wikipedia_multilang_ottoman.json'
$Cache = Join-Path $Root 'sources/cache/wikipedia_multilang_ottoman'
$DelayMs = 1400

foreach ($dir in @((Split-Path $Out), (Split-Path $StatePath), $Cache)) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

function Get-Sha256([string]$Value) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($Value))).Replace('-', '').ToLowerInvariant()) }
    finally { $sha.Dispose() }
}

function Save-Json($Path, $Value) {
    $tmp = "$Path.tmp"
    $Value | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $tmp -Encoding utf8
    Move-Item -LiteralPath $tmp -Destination $Path -Force
}

function Html-Decode([string]$Text) {
    if ($null -eq $Text) { return $null }
    return [System.Net.WebUtility]::HtmlDecode($Text)
}

function Wiki-PageUrl([string]$Language, [string]$Title) {
    return "https://$Language.wikipedia.org/wiki/" + [Uri]::EscapeDataString($Title.Replace(' ', '_'))
}

function Raw-Url([string]$Language, [string]$Title) {
    return "https://$Language.wikipedia.org/w/index.php?title=" + [Uri]::EscapeDataString($Title) + '&action=raw'
}

function Get-Text([string]$Url, [string]$Label, [ref]$Failures, [ref]$CacheHit) {
    $cachePath = Join-Path $Cache ((Get-Sha256 $Url) + '.txt')
    if (Test-Path -LiteralPath $cachePath) {
        $CacheHit.Value = $true
        return (Get-Content -Raw -LiteralPath $cachePath)
    }
    $CacheHit.Value = $false
    for ($attempt = 1; $attempt -le 3; $attempt++) {
        Start-Sleep -Milliseconds $DelayMs
        try {
            $response = Invoke-WebRequest -Uri $Url -Headers @{ 'User-Agent' = $UserAgent; Accept = 'text/plain,text/html;q=0.9' } -TimeoutSec 90
            $response.Content | Set-Content -LiteralPath $cachePath -Encoding utf8
            return $response.Content
        } catch {
            $status = 0
            try { $status = [int]$_.Exception.Response.StatusCode } catch { }
            if ($attempt -eq 3 -or (@(429,500,502,503,504) -notcontains $status)) {
                [void]$Failures.Value.Add([ordered]@{ label = $Label; url = $Url; error = $_.Exception.Message; status = $status; attempts = $attempt })
                return $null
            }
            $wait = [Math]::Min(120000, (6000 * [Math]::Pow(2, $attempt - 1)) + (Get-Random -Minimum 0 -Maximum 2500))
            Write-Host "retry $Label attempt $attempt/3 after ${wait}ms status=$status"
            Start-Sleep -Milliseconds ([int]$wait)
        }
    }
    return $null
}

function Strip-Markup([string]$Text) {
    if ($null -eq $Text) { return '' }
    $t = $Text -replace '<ref(?:\s[^>]*)?>.*?</ref>', ' '
    $t = $t -replace '<[^>]+>', ' '
    $t = $t -replace '\{\{[^{}]*\}\}', ' '
    $t = $t -replace "''", ''
    $t = Html-Decode $t
    $t = $t -replace '\s+', ' '
    return $t.Trim()
}

function Is-IgnoredTarget([string]$Target) {
    if ([string]::IsNullOrWhiteSpace($Target)) { return $true }
    $t = $Target.Trim()
    return ($t -match '^(?i:File|Image|Datei|Bild|Fichier|Archivo|Файл|Category|Kategorie|Categoria|Категория|Template|Vorlage|Modèle|Plantilla|Шаблон|Wikipedia|Hilfe|Help|Special|Spezial|Specie|Служебная|Portal|Portale|Портал|MediaWiki|Commons):')
}

function Link-Target([string]$Target) {
    $t = $Target.Trim()
    $t = $t -replace '\s+', '_'
    return $t
}

function Link-Url([string]$Language, [string]$Target) {
    return Wiki-PageUrl $Language (Link-Target $Target)
}

function New-LinkRow([string]$Language, [string]$PageTitle, [string]$PageUrl, [string]$Mode, [string]$Target, [string]$Label, [string]$Section, [int]$LineNumber, [string]$Excerpt, [string]$Role, [string]$Status) {
    $displayTarget = (Html-Decode $Target).Trim()
    $normalizedTarget = Link-Target $displayTarget
    return [ordered]@{
        source_id = 'wikipedia-ottoman-' + (Get-Sha256 ("$Language|$PageTitle|$normalizedTarget|$LineNumber|$Role")).Substring(0, 20)
        source_system = 'Wikipedia'
        source_type = 'multilingual_list_discovery'
        accessed = $AsOf
        language = $Language
        source_page_title = $PageTitle
        source_page_url = $PageUrl
        page_mode = $Mode
        linked_title = $displayTarget
        linked_title_normalized = $normalizedTarget
        entry_label = (Strip-Markup $Label)
        linked_url = (Link-Url $Language $normalizedTarget)
        section = $Section
        line_number = $LineNumber
        link_role = $Role
        source_excerpt = (Strip-Markup $Excerpt).Substring(0, [Math]::Min(700, (Strip-Markup $Excerpt).Length))
        status = $Status
        note = 'Discovery metadata from the specified Wikipedia list/category or dedicated page; no image bytes downloaded in this sweep.'
    }
}

function Extract-WikitextLinks([string]$Text, [string]$Language, [string]$PageTitle, [string]$PageUrl, [string]$Mode) {
    $rows = [System.Collections.ArrayList]::new()
    $section = ''
    $lines = $Text -split "`r?`n"
    for ($lineIndex = 0; $lineIndex -lt $lines.Count; $lineIndex++) {
        $line = [string]$lines[$lineIndex]
        if ($line -match '^\s*(={2,6})\s*(.*?)\s*\1\s*$') { $section = Strip-Markup $Matches[2] }
        $matches = [regex]::Matches($line, '\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]')
        foreach ($m in $matches) {
            $target = (Html-Decode $m.Groups[1].Value).Trim()
            if (Is-IgnoredTarget $target) { continue }
            $label = if ($m.Groups[2].Success) { $m.Groups[2].Value } else { $target }
            $trimmed = $line.TrimStart()
            $role = 'contextual_link'
            if ($line -match '^\s*#REDIRECT') { $role = 'redirect_target' }
            elseif ($trimmed.StartsWith('*')) { $role = 'list_entry_link' }
            elseif ($trimmed.StartsWith('|')) { $role = 'table_entry_or_context_link' }
            elseif ($trimmed.StartsWith('!')) { $role = 'table_header_link' }
            $row = New-LinkRow $Language $PageTitle $PageUrl $Mode $target $label $section ($lineIndex + 1) $line $role 'RAW_CANDIDATE'
            [void]$rows.Add($row)
        }
    }
    return ,$rows
}

function Get-Attr([string]$Tag, [string]$Name) {
    $pattern = '(?i)\b' + [regex]::Escape($Name) + '\s*=\s*"([^"]*)"'
    $m = [regex]::Match($Tag, $pattern)
    if ($m.Success) { return Html-Decode $m.Groups[1].Value }
    return $null
}

function Extract-CategoryLinks([string]$Html, [string]$Language, [string]$PageTitle, [string]$PageUrl) {
    $rows = [System.Collections.ArrayList]::new()
    $subStart = $Html.IndexOf('id="mw-subcategories"')
    $pagesStart = $Html.IndexOf('id="mw-pages"')
    $catlinksStart = $Html.IndexOf('id="catlinks"')
    $blocks = @()
    if ($subStart -ge 0 -and $pagesStart -gt $subStart) {
        $blocks += [ordered]@{ text = $Html.Substring($subStart, $pagesStart - $subStart); role = 'category_subcategory' }
    }
    if ($pagesStart -ge 0) {
        $end = if ($catlinksStart -gt $pagesStart) { $catlinksStart } else { $Html.Length }
        $blocks += [ordered]@{ text = $Html.Substring($pagesStart, $end - $pagesStart); role = 'category_member' }
    }
    foreach ($block in $blocks) {
        $anchorTags = [regex]::Matches($block.text, '(?is)<a\b[^>]*>')
        foreach ($tagMatch in $anchorTags) {
            $tag = $tagMatch.Value
            $href = Get-Attr $tag 'href'
            $title = Get-Attr $tag 'title'
            if ([string]::IsNullOrWhiteSpace($href) -or [string]::IsNullOrWhiteSpace($title)) { continue }
            if ($href -notmatch '^/wiki/') { continue }
            $target = $title.Trim()
            if ($block.role -eq 'category_subcategory') {
                if ($target -notmatch '^(?i:Category):') { continue }
            } elseif (Is-IgnoredTarget $target) { continue }
            $label = Strip-Markup (([regex]::Match($block.text.Substring(0, $tagMatch.Index), '(?is)([^<>]{0,250})$')).Groups[1].Value)
            $row = New-LinkRow $Language $PageTitle $PageUrl 'html_category' $target $label '' 0 $tag $block.role 'RAW_CANDIDATE'
            [void]$rows.Add($row)
        }
    }
    return ,$rows
}

$Specs = @(
    [ordered]@{ language = 'en'; title = 'Category:Orders, decorations, and medals of the Ottoman Empire'; mode = 'html_category'; url = 'https://en.wikipedia.org/wiki/Category:Orders,_decorations,_and_medals_of_the_Ottoman_Empire' },
    [ordered]@{ language = 'de'; title = 'Liste der osmanischen Orden und Ehrenzeichen'; mode = 'wikitext_list'; url = (Raw-Url 'de' 'Liste der osmanischen Orden und Ehrenzeichen') },
    [ordered]@{ language = 'it'; title = "Onorificenze dell'Impero ottomano"; mode = 'wikitext_list'; url = (Raw-Url 'it' "Onorificenze dell'Impero ottomano") },
    [ordered]@{ language = 'ru'; title = 'Награды Османской Империи'; mode = 'wikitext_list'; url = (Raw-Url 'ru' 'Награды Османской Империи') },
    [ordered]@{ language = 'en'; title = 'Order of the Medjidie'; mode = 'wikitext_page'; url = (Raw-Url 'en' 'Order of the Medjidie') },
    [ordered]@{ language = 'en'; title = 'Ottoman War Medal'; mode = 'wikitext_page'; url = (Raw-Url 'en' 'Ottoman War Medal') }
)

$Failures = [System.Collections.ArrayList]::new()
$Rows = [System.Collections.ArrayList]::new()
$PageSummaries = [System.Collections.ArrayList]::new()

foreach ($spec in $Specs) {
    $cacheHit = $false
    $text = Get-Text $spec.url ("$($spec.language):$($spec.title)") ([ref]$Failures) ([ref]$cacheHit)
    if ($null -eq $text) {
        [void]$PageSummaries.Add([ordered]@{ language = $spec.language; title = $spec.title; url = $spec.url; mode = $spec.mode; status = 'failed'; rows = 0; cache_hit = $cacheHit })
        continue
    }
    $pageUrl = if ($spec.mode -eq 'html_category') { Wiki-PageUrl $spec.language $spec.title } else { Wiki-PageUrl $spec.language $spec.title }
    $pageRows = if ($spec.mode -eq 'html_category') { Extract-CategoryLinks $text $spec.language $spec.title $pageUrl } else { Extract-WikitextLinks $text $spec.language $spec.title $pageUrl $spec.mode }
    foreach ($row in $pageRows) { [void]$Rows.Add($row) }
    $pageSummary = [ordered]@{ language = $spec.language; title = $spec.title; page_url = $pageUrl; fetch_url = $spec.url; mode = $spec.mode; status = 'complete'; bytes = ([Text.Encoding]::UTF8.GetByteCount($text)); rows = $pageRows.Count; cache_hit = $cacheHit; pagination_exhausted = $true }
    if ($spec.mode -eq 'html_category') {
        $pageSummary.category_subcategories = @($pageRows | Where-Object { $_.link_role -eq 'category_subcategory' } | ForEach-Object { $_.linked_title })
        $pageSummary.category_members = @($pageRows | Where-Object { $_.link_role -eq 'category_member' } | ForEach-Object { $_.linked_title })
        $report = [regex]::Match($text, 'The following\s+(\d+)\s+pages are in this category, out of\s+(\d+)\s+total', 'IgnoreCase')
        if ($report.Success) { $pageSummary.reported_pages_in_category = [int]$report.Groups[1].Value; $pageSummary.reported_pages_total = [int]$report.Groups[2].Value }
    }
    [void]$PageSummaries.Add($pageSummary)
}

# Keep one row for each source occurrence.  A second occurrence of the same
# target is useful evidence of where it appears in a table/list and is not a
# second medal record; downstream catalogue merging can deduplicate by target.
$tmpOut = "$Out.tmp"
if (Test-Path -LiteralPath $tmpOut) { Remove-Item -LiteralPath $tmpOut -Force }
foreach ($row in $Rows) { ($row | ConvertTo-Json -Depth 100 -Compress) | Add-Content -LiteralPath $tmpOut -Encoding utf8 }
Move-Item -LiteralPath $tmpOut -Destination $Out -Force

$uniqueTargets = @($Rows | ForEach-Object { "$($_.language)|$($_.linked_title)" } | Sort-Object -Unique)
$summary = [ordered]@{
    source_id = 'wikipedia_multilang_ottoman'
    source_name = 'Specified Wikipedia multilingual Ottoman awards lists, English category, and Medjidie/War Medal pages'
    as_of = $AsOf
    accessed = $AsOf
    status = if ($Failures.Count -gt 0) { 'complete_with_failures' } else { 'complete' }
    source_complete = ($Failures.Count -eq 0)
    started_at = (Get-Date).ToUniversalTime().ToString('o')
    completed_at = (Get-Date).ToUniversalTime().ToString('o')
    completion_rule = 'Each fixed page was fetched once or read from the local cache; all internal links in the specified list/page wikitext and current English category member/subcategory blocks were recorded. No image bytes were downloaded.'
    fixed_sources = @($Specs | ForEach-Object { [ordered]@{ language = $_.language; title = $_.title; mode = $_.mode; fetch_url = $_.url; page_url = (Wiki-PageUrl $_.language $_.title) } })
    languages = @('en','de','it','ru')
    pages_requested = $Specs.Count
    pages_completed = @($PageSummaries | Where-Object { $_.status -eq 'complete' }).Count
    pages_failed = @($PageSummaries | Where-Object { $_.status -eq 'failed' }).Count
    candidate_rows = $Rows.Count
    unique_language_target_links = $uniqueTargets.Count
    page_summaries = $PageSummaries
    failures = $Failures
    continuation_tokens_exhausted = $true
    pagination_notes = @('The English source is a current HTML category page; its visible member and subcategory blocks were exhausted. The three multilingual lists and two dedicated pages were fetched as current raw wikitext, so MediaWiki continuation tokens do not apply.')
    raw_candidate_file = 'data/raw_candidates/wikipedia_multilang_ottoman.jsonl'
    metadata_cache_directory = 'sources/cache/wikipedia_multilang_ottoman'
    no_original_image_downloads = $true
}
Save-Json $StatePath $summary
Write-Output (ConvertTo-Json ([ordered]@{ status = $summary.status; pages = $summary.pages_completed; rows = $Rows.Count; unique_targets = $uniqueTargets.Count; failures = $Failures.Count; output = $Out; state = $StatePath }) -Compress)
