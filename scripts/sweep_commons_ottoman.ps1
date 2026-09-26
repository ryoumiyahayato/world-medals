Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$Root = (Get-Location).Path
$Api = 'https://commons.wikimedia.org/w/api.php'
$AsOf = '2026-09-26'
$UserAgent = 'world-medals-source-sweep/1.0 (research catalogue; no original-image downloads)'
$Out = Join-Path $Root 'data/raw_candidates/commons_ottoman.jsonl'
$StatePath = Join-Path $Root 'data/source_sweeps/commons_ottoman.json'
$Cache = Join-Path $Root 'sources/cache/commons_ottoman'
$DelayMs = 900
$BatchSize = 30

$Seeds = @(
    [ordered]@{ key = 'commons_total'; title = 'Category:Orders, decorations and medals of the Ottoman Empire' },
    [ordered]@{ key = 'orders'; title = 'Category:Orders of the Ottoman Empire' },
    [ordered]@{ key = 'medals'; title = 'Category:Medals of the Ottoman Empire' },
    [ordered]@{ key = 'military_decorations'; title = 'Category:Military decorations of the Ottoman Empire' },
    [ordered]@{ key = 'ribbon_bars'; title = 'Category:Ribbon bars of the Ottoman Empire' },
    [ordered]@{ key = 'medjidie'; title = 'Category:Order of the Medjidie' },
    [ordered]@{ key = 'osmanieh'; title = 'Category:Order of Osmanieh' },
    [ordered]@{ key = 'glory'; title = 'Category:Order of Glory (Ottoman Empire)' },
    [ordered]@{ key = 'crescent'; title = 'Category:Order of the Crescent' },
    [ordered]@{ key = 'sefkat'; title = 'Category:Şefkat Order' },
    [ordered]@{ key = 'imtiyaz'; title = 'Category:Imtiyaz Medal' },
    [ordered]@{ key = 'liyakat'; title = 'Category:Liyakat Medal' },
    [ordered]@{ key = 'gallipoli_star'; title = 'Category:Gallipoli Star' },
    [ordered]@{ key = 'turkish_crimea'; title = 'Category:Turkish Crimea Medal' },
    [ordered]@{ key = 'syrian_campaign_1840'; title = 'Category:Syrian Campaign Medal (1840)' }
)

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
    $Value | ConvertTo-Json -Depth 100 | Set-Content -Path $tmp -Encoding utf8
    Move-Item -LiteralPath $tmp -Destination $Path -Force
}

function Save-State {
    $script:State.updated_at = (Get-Date).ToUniversalTime().ToString('o')
    Save-Json $StatePath $script:State
}

function Get-PageUrl([string]$Title) {
    return 'https://commons.wikimedia.org/wiki/' + [Uri]::EscapeDataString($Title.Replace(' ', '_'))
}

function Get-MetadataValue($Metadata, [string]$Key) {
    if ($null -eq $Metadata) { return $null }
    $property = $Metadata.PSObject.Properties[$Key]
    if ($null -eq $property) { return $null }
    $item = $property.Value
    if ($null -eq $item) { return $null }
    if ($item -is [string]) { return $item }
    $valueProperty = $item.PSObject.Properties['value']
    if ($null -ne $valueProperty) { return $valueProperty.Value }
    return [string]$item
}

function Test-ScopeExcluded([string]$Title) {
    $name = $Title -replace '^Category:', ''
    return ($name -match '(?i)\bRecipients\b|\bKnights?\b|\bPeople\b|\bportrait(?:s)?\b|\bcoat(?:s)? of arms\b|\bheraldry\b|\bfamily crests?\b|\bpersonalities\b')
}

function New-State {
    return [ordered]@{
        source_id = 'commons_ottoman'
        source_name = 'Wikimedia Commons Ottoman orders, medals, decorations and ribbon-bar category sweep'
        as_of = $AsOf
        accessed = $AsOf
        status = 'running'
        started_at = (Get-Date).ToUniversalTime().ToString('o')
        updated_at = $null
        completion_rule = 'Every currently visible subcategory and file page reachable from every fixed seed was paginated until its continuation token was exhausted; failures remain listed.'
        seed_categories = [System.Collections.ArrayList]::new()
        queue = [System.Collections.ArrayList]::new()
        visited_categories = [System.Collections.ArrayList]::new()
        category_log = [ordered]@{}
        scope_excluded_categories = [System.Collections.ArrayList]::new()
        pending_file_titles = [System.Collections.ArrayList]::new()
        processed_file_titles = [System.Collections.ArrayList]::new()
        counters = [ordered]@{
            categories_discovered = 0
            categories_fetched = 0
            category_member_requests = 0
            category_member_entries_seen = 0
            file_members_seen = 0
            duplicate_file_members = 0
            unique_files = 0
            imageinfo_batches = 0
            imageinfo_files_returned = 0
            api_requests = 0
        }
        failures = [System.Collections.ArrayList]::new()
    }
}

function New-ApiUrl($Params) {
    $pairs = [System.Collections.Generic.List[string]]::new()
    foreach ($item in $Params.GetEnumerator()) {
        [void]$pairs.Add(([Uri]::EscapeDataString([string]$item.Key) + '=' + [Uri]::EscapeDataString([string]$item.Value)))
    }
    [void]$pairs.Add('action=query')
    [void]$pairs.Add('format=json')
    [void]$pairs.Add('formatversion=2')
    return "${Api}?" + ($pairs -join '&')
}

function Get-ApiJson($Params, [string]$Label) {
    $url = New-ApiUrl $Params
    $cacheFile = Join-Path $Cache ((Get-Sha256 $url) + '.json')
    if (Test-Path -LiteralPath $cacheFile) {
        try { return (Get-Content -Raw -LiteralPath $cacheFile | ConvertFrom-Json -Depth 100) } catch { Remove-Item -LiteralPath $cacheFile -Force -ErrorAction SilentlyContinue }
    }
    for ($attempt = 1; $attempt -le 3; $attempt++) {
        Start-Sleep -Milliseconds $DelayMs
        try {
            $response = Invoke-WebRequest -Uri $url -Headers @{ 'User-Agent' = $UserAgent; Accept = 'application/json' } -TimeoutSec 90
            $data = $response.Content | ConvertFrom-Json -Depth 100
            $apiErrorProperty = $data.PSObject.Properties['error']
            if ($null -ne $apiErrorProperty) {
                $apiCode = [string]$data.error.code
                if ($apiCode -match 'ratelimit|maxlag|readonly') { throw "API_RETRY_429:$apiCode" }
                throw "API_ERROR:$apiCode"
            }
            $response.Content | Set-Content -LiteralPath $cacheFile -Encoding utf8
            $State.counters.api_requests++
            return $data
        } catch {
            $status = 0
            try { $status = [int]$_.Exception.Response.StatusCode } catch { }
            if ($_.Exception.Message -match 'API_RETRY_429') { $status = 429 }
            $retryable = @((429), (500), (502), (503), (504)) -contains $status
            if (-not $retryable -or $attempt -eq 3) {
                [void]$State.failures.Add([ordered]@{ stage = $Label; url = $url; error = $_.Exception.Message; status = $status; attempts = $attempt })
                return $null
            }
            $wait = [Math]::Min(180000, (10000 * [Math]::Pow(2, $attempt - 1)) + (Get-Random -Minimum 0 -Maximum 3000))
            Write-Host "retry $Label attempt $attempt/3 after ${wait}ms status=$status"
            Start-Sleep -Milliseconds ([int]$wait)
        }
    }
    return $null
}

function Load-ProcessedTitles {
    $set = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    if (-not (Test-Path -LiteralPath $Out)) { return ,$set }
    foreach ($line in Get-Content -LiteralPath $Out) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        try {
            $row = $line | ConvertFrom-Json -Depth 50
            if ($row.file_title) { [void]$set.Add([string]$row.file_title) }
        } catch { }
    }
    return ,$set
}

function Enqueue-Category([string]$Title, [string]$RootSeed, $PathParts) {
    if ([string]::IsNullOrWhiteSpace($Title)) { return }
    if ($Visited.Contains($Title)) { return }
    if ($QueueTitles.Contains($Title)) { return }
    if (Test-ScopeExcluded $Title) {
        $excluded = [ordered]@{ title = $Title; root_seed = $RootSeed; path = @($PathParts); reason = 'recipients/people/portrait or generic heraldry branch; current category is logged but descendants are not recursively traversed' }
        $alreadyExcluded = @($State.scope_excluded_categories | Where-Object { $_.title -eq $Title })
        if ($alreadyExcluded.Count -eq 0) { [void]$State.scope_excluded_categories.Add($excluded) }
        return
    }
    $entry = [ordered]@{ title = $Title; root_seed = $RootSeed; path = @($PathParts) }
    [void]$State.queue.Add($entry)
    [void]$QueueTitles.Add($Title)
    $State.counters.categories_discovered++
}

function Add-Failure($Object) { [void]$State.failures.Add($Object) }

function Make-Row($Page, $Info, [string]$RootSeed, $CategoryPath, [string]$CategoryTitle) {
    $meta = $Info.extmetadata
    return [ordered]@{
        source_id = 'commons-ottoman-' + (([System.BitConverter]::ToString((New-Object System.Security.Cryptography.SHA1Managed).ComputeHash([Text.Encoding]::UTF8.GetBytes([string]$Page.title)))).Replace('-', '').ToLowerInvariant().Substring(0, 16))
        source_system = 'Wikimedia Commons MediaWiki API'
        source_type = 'discovery_metadata_only'
        accessed = $AsOf
        category_seed = $RootSeed
        category_path = @($CategoryPath)
        category_title = $CategoryTitle
        file_title = [string]$Page.title
        pageid = $Page.pageid
        file_page = Get-PageUrl ([string]$Page.title)
        description_url = $Info.descriptionurl
        original_url = $Info.url
        file_name = if ($Info.descriptionurl) { ([string]$Info.descriptionurl).Split('/')[-1] } else { $null }
        mime = $Info.mime
        mediatype = $Info.mediatype
        width = $Info.width
        height = $Info.height
        size_bytes = $Info.size
        timestamp = $Info.timestamp
        sha1 = $Info.sha1
        extmetadata = [ordered]@{
            object_name = Get-MetadataValue $meta 'ObjectName'
            image_description = Get-MetadataValue $meta 'ImageDescription'
            date_time_original = Get-MetadataValue $meta 'DateTimeOriginal'
            date = Get-MetadataValue $meta 'Date'
            artist = Get-MetadataValue $meta 'Artist'
            author = Get-MetadataValue $meta 'Author'
            credit = Get-MetadataValue $meta 'Credit'
            source = Get-MetadataValue $meta 'Source'
            attribution = Get-MetadataValue $meta 'Attribution'
            license = Get-MetadataValue $meta 'License'
            license_short_name = Get-MetadataValue $meta 'LicenseShortName'
            usage_terms = Get-MetadataValue $meta 'UsageTerms'
            categories = Get-MetadataValue $meta 'Categories'
            depicts = Get-MetadataValue $meta 'Depicts'
        }
        status = 'RAW_CANDIDATE'
        note = 'Image URL recorded for later review; original bytes intentionally not downloaded in source sweep.'
    }
}

if (Test-Path -LiteralPath $StatePath) {
    try { $State = Get-Content -Raw -LiteralPath $StatePath | ConvertFrom-Json -Depth 100 } catch { $State = New-State }
} else { $State = New-State }

# The first Node implementation could not connect from this host.  Its empty
# seed-resolution attempt is retained only in the next run's failure history;
# rebuild the live queue from Commons here.
$hasResolvedSeed = (@($State.seed_categories | Where-Object { $_.pageid }).Count -gt 0)
if (-not $hasResolvedSeed -and @($State.queue).Count -eq 0 -and [int]$State.counters.unique_files -eq 0) {
    $priorFailures = @($State.failures)
    $State = New-State
    if ($priorFailures.Count -gt 0) { $State.prior_attempt_failures = $priorFailures }
}

# JSON deserialization returns fixed-size arrays.  Rehydrate mutable queues
# and logs before resuming an interrupted sweep.
$oldQueue = @($State.queue)
$State.queue = [System.Collections.ArrayList]::new()
foreach ($entry in $oldQueue) { [void]$State.queue.Add($entry) }
$oldSeeds = @($State.seed_categories)
$State.seed_categories = [System.Collections.ArrayList]::new()
foreach ($entry in $oldSeeds) { [void]$State.seed_categories.Add($entry) }
$oldVisited = @($State.visited_categories)
$State.visited_categories = [System.Collections.ArrayList]::new()
foreach ($entry in $oldVisited) { [void]$State.visited_categories.Add($entry) }
$oldPending = @($State.pending_file_titles)
$State.pending_file_titles = [System.Collections.ArrayList]::new()
foreach ($entry in $oldPending) { [void]$State.pending_file_titles.Add([string]$entry) }
$oldFailures = @($State.failures)
$State.failures = [System.Collections.ArrayList]::new()
foreach ($entry in $oldFailures) { [void]$State.failures.Add($entry) }
$oldLog = $State.category_log
$State.category_log = [ordered]@{}
if ($null -ne $oldLog) {
    foreach ($property in $oldLog.PSObject.Properties) {
        $logValue = $property.Value
        $fileTitlesProperty = $logValue.PSObject.Properties['files_seen_titles']
        if ($null -ne $fileTitlesProperty) {
            $oldFileTitles = @($logValue.files_seen_titles)
            $logValue.files_seen_titles = [System.Collections.ArrayList]::new()
            foreach ($fileTitle in $oldFileTitles) { [void]$logValue.files_seen_titles.Add([string]$fileTitle) }
        }
        $State.category_log[$property.Name] = $logValue
    }
}
$scopeProperty = $State.PSObject.Properties['scope_excluded_categories']
$oldScope = if ($null -ne $scopeProperty) { @($State.scope_excluded_categories) } else { @() }
if ($null -eq $scopeProperty) { $State | Add-Member -NotePropertyName scope_excluded_categories -NotePropertyValue ([System.Collections.ArrayList]::new()) }
$State.scope_excluded_categories = [System.Collections.ArrayList]::new()
foreach ($entry in $oldScope) { [void]$State.scope_excluded_categories.Add($entry) }

$Processed = Load-ProcessedTitles
$ProcessedList = [System.Collections.ArrayList]::new()
foreach ($title in $Processed) { [void]$ProcessedList.Add($title) }
$State.processed_file_titles = $ProcessedList
$State.counters.unique_files = $Processed.Count
$Visited = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
foreach ($title in @($State.visited_categories)) { [void]$Visited.Add([string]$title) }
$QueueTitles = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
foreach ($item in @($State.queue)) { [void]$QueueTitles.Add([string]$item.title) }

if (@($State.seed_categories).Count -eq 0) {
    $seedTitles = ($Seeds | ForEach-Object { $_.title }) -join '|'
    $seedData = Get-ApiJson ([ordered]@{ titles = $seedTitles; prop = 'info' }) 'seed_resolution'
    if ($null -eq $seedData) {
        # Fall back to one title per request so one transient API error cannot
        # erase the exact status of the other fixed roots.
        $seedPages = @()
        foreach ($seed in $Seeds) {
            $one = Get-ApiJson ([ordered]@{ titles = $seed.title; prop = 'info' }) ("seed_resolution:" + $seed.key)
            if ($null -ne $one) { $seedPages += @($one.query.pages) }
        }
    } else { $seedPages = @($seedData.query.pages) }
    $pageByTitle = @{}
    foreach ($page in $seedPages) { $pageByTitle[[string]$page.title] = $page }
    foreach ($seed in $Seeds) {
        $page = $pageByTitle[$seed.title]
        $missingProperty = if ($null -ne $page) { $page.PSObject.Properties['missing'] } else { $null }
        $resolved = ($null -ne $page -and $null -eq $missingProperty)
        $entry = [ordered]@{ key = $seed.key; title = $seed.title; pageid = if ($resolved) { $page.pageid } else { $null }; resolved = $resolved; page_url = Get-PageUrl $seed.title }
        [void]$State.seed_categories.Add($entry)
        if ($resolved) {
            Enqueue-Category $seed.title $seed.key @($seed.title)
        } else {
            Add-Failure ([ordered]@{ stage = 'seed_resolution'; category = $seed.title; error = 'category page missing from current Commons API response' })
        }
    }
    Save-State
}

$pendingTitles = [System.Collections.ArrayList]::new()
foreach ($title in @($State.pending_file_titles)) { [void]$pendingTitles.Add([string]$title) }
$State.pending_file_titles = $pendingTitles

function Write-Batch($Titles, [string]$Label, [string]$RootSeed, $CategoryPath, [string]$CategoryTitle) {
    $data = Get-ApiJson ([ordered]@{ titles = ($Titles -join '|'); prop = 'imageinfo'; iiprop = 'url|size|mime|mediatype|extmetadata|timestamp|sha1'; iilimit = '1' }) $Label
    $State.counters.imageinfo_batches++
    if ($null -eq $data) {
        foreach ($title in $Titles) { if (-not $State.pending_file_titles.Contains($title)) { [void]$State.pending_file_titles.Add($title) } }
        return
    }
    $queryProperty = $data.PSObject.Properties['query']
    if ($null -eq $queryProperty) {
        Add-Failure ([ordered]@{ stage = $Label; error = 'API response did not contain query object'; response_keys = ($data.PSObject.Properties.Name -join ',') })
        foreach ($title in $Titles) { if (-not $State.pending_file_titles.Contains($title)) { [void]$State.pending_file_titles.Add($title) } }
        return
    }
    $pages = @($data.query.pages)
    $State.counters.imageinfo_files_returned += $pages.Count
    foreach ($page in $pages) {
        $title = [string]$page.title
        if ($Processed.Contains($title)) { continue }
        $info = if (@($page.imageinfo).Count -gt 0) { $page.imageinfo[0] } else { $null }
        if ($null -eq $info) {
            Add-Failure ([ordered]@{ stage = 'imageinfo'; file_title = $title; pageid = $page.pageid; error = 'no imageinfo returned' })
            continue
        }
        $row = Make-Row $page $info $RootSeed $CategoryPath $CategoryTitle
        ($row | ConvertTo-Json -Depth 100 -Compress) | Add-Content -LiteralPath $Out -Encoding utf8
        [void]$Processed.Add($title)
        [void]$State.processed_file_titles.Add($title)
        $State.counters.unique_files++
    }
}

# Retry metadata that was left pending by an interrupted or rate-limited run.
if ($State.pending_file_titles.Count -gt 0) {
    $retry = @($State.pending_file_titles)
    $State.pending_file_titles = [System.Collections.ArrayList]::new()
    for ($i = 0; $i -lt $retry.Count; $i += $BatchSize) {
        $batch = @($retry[$i..([Math]::Min($i + $BatchSize - 1, $retry.Count - 1))] | Where-Object { -not $Processed.Contains([string]$_) })
        if ($batch.Count -gt 0) { Write-Batch $batch ("imageinfo:pending:$i") 'pending_retry' @() $null }
    }
    Save-State
}

while ($State.queue.Count -gt 0) {
    $item = $State.queue[0]
    $State.queue.RemoveAt(0)
    if ($Visited.Contains([string]$item.title)) { continue }
    $title = [string]$item.title
    $excludedAncestor = $null
    foreach ($pathPart in @($item.path)) {
        if ($pathPart -ne $title -and (Test-ScopeExcluded ([string]$pathPart))) { $excludedAncestor = [string]$pathPart; break }
    }
    if ($null -ne $excludedAncestor) {
        $alreadyExcluded = @($State.scope_excluded_categories | Where-Object { $_.title -eq $title })
        if ($alreadyExcluded.Count -eq 0) { [void]$State.scope_excluded_categories.Add([ordered]@{ title = $title; root_seed = $item.root_seed; path = @($item.path); reason = "descendant of scope-excluded category $excludedAncestor; not recursively traversed" }) }
        Save-State
        continue
    }
    $log = if ($State.category_log.Contains($title)) { $State.category_log[$title] } else {
        [ordered]@{ title = $title; root_seed = $item.root_seed; path = @($item.path); status = 'running'; api_requests = 0; members_seen = 0; file_members = 0; subcategories = 0; continuation_pages = 0; continuation_exhausted = $false; scope_excluded = (Test-ScopeExcluded $title); scope_excluded_subcategories = [System.Collections.ArrayList]::new(); files_seen_titles = [System.Collections.ArrayList]::new() }
    }
    $State.category_log[$title] = $log
    if ($null -eq $log.PSObject.Properties['scope_excluded']) { $log | Add-Member -NotePropertyName scope_excluded -NotePropertyValue (Test-ScopeExcluded $title) }
    if ($null -eq $log.PSObject.Properties['scope_excluded_subcategories']) { $log | Add-Member -NotePropertyName scope_excluded_subcategories -NotePropertyValue ([System.Collections.ArrayList]::new()) }
    $log.scope_excluded = Test-ScopeExcluded $title
    $newFiles = [System.Collections.ArrayList]::new()
    $continuation = $null
    $failed = $false
    do {
        $params = [ordered]@{ list = 'categorymembers'; cmtitle = $title; cmtype = 'file|subcat'; cmlimit = 'max' }
        if ($continuation) { $params.cmcontinue = $continuation }
        $data = Get-ApiJson $params ("categorymembers:$title")
        $log.api_requests++
        $State.counters.category_member_requests++
        if ($null -eq $data) {
            $failed = $true
            $log.status = 'failed'
            $log.error = 'categorymembers request failed; remaining continuation position is in failed_pages'
            break
        }
        $categoryQueryProperty = $data.PSObject.Properties['query']
        if ($null -eq $categoryQueryProperty) {
            $failed = $true
            $log.status = 'failed'
            $log.error = 'categorymembers response did not contain query object'
            Add-Failure ([ordered]@{ stage = "categorymembers:$title"; error = 'API response did not contain query object'; response_keys = ($data.PSObject.Properties.Name -join ',') })
            break
        }
        $members = @($data.query.categorymembers)
        $log.continuation_pages++
        $log.members_seen += $members.Count
        $State.counters.category_member_entries_seen += $members.Count
        foreach ($member in $members) {
            if ([int]$member.ns -eq 14) {
                $log.subcategories++
                if ($log.scope_excluded) {
                    if (-not $log.scope_excluded_subcategories.Contains([string]$member.title)) { [void]$log.scope_excluded_subcategories.Add([string]$member.title) }
                } else {
                    Enqueue-Category ([string]$member.title) ([string]$item.root_seed) (@($item.path) + @([string]$member.title))
                }
            } elseif ([int]$member.ns -eq 6) {
                $State.counters.file_members_seen++
                if (-not $log.files_seen_titles.Contains([string]$member.title)) { [void]$log.files_seen_titles.Add([string]$member.title) }
                if ($Processed.Contains([string]$member.title) -or $newFiles.Contains([string]$member.title)) { $State.counters.duplicate_file_members++ } else { [void]$newFiles.Add([string]$member.title); $log.file_members++ }
            }
        }
        $continueProperty = $data.PSObject.Properties['continue']
        $continuation = if ($null -ne $continueProperty) { $data.continue.cmcontinue } else { $null }
        if ($continuation) { Start-Sleep -Milliseconds $DelayMs }
    } while ($continuation)

    if (-not $failed) {
        $log.status = 'complete'
        $log.continuation_exhausted = $true
        $State.counters.categories_fetched++
        [void]$Visited.Add($title)
        [void]$State.visited_categories.Add($title)
    } else {
        # Keep the category at the head of the checkpointed queue.  A later
        # invocation can retry it after the API rate-limit window clears.
        $State.queue.Insert(0, $item)
        Save-State
        break
    }
    for ($i = 0; $i -lt $newFiles.Count; $i += $BatchSize) {
        $batch = @($newFiles[$i..([Math]::Min($i + $BatchSize - 1, $newFiles.Count - 1))])
        Write-Batch $batch ("imageinfo:${title}:$i") ([string]$item.root_seed) $item.path $title
    }
    $filteredPending = [System.Collections.ArrayList]::new()
    foreach ($pendingTitle in @($State.pending_file_titles)) { if (-not $Processed.Contains([string]$pendingTitle)) { [void]$filteredPending.Add([string]$pendingTitle) } }
    $State.pending_file_titles = $filteredPending
    Save-State
    if (($State.counters.categories_fetched % 10) -eq 0 -or ($State.counters.unique_files % 100) -eq 0) {
        Write-Output (ConvertTo-Json ([ordered]@{ categories = $State.counters.categories_fetched; queue = $State.queue.Count; files = $State.counters.unique_files; failures = $State.failures.Count }) -Compress)
    }
}

$complete = ($State.queue.Count -eq 0 -and $State.pending_file_titles.Count -eq 0)
$State.status = if ($complete -and $State.failures.Count -gt 0) { 'complete_with_failures' } elseif ($complete) { 'complete' } else { 'partial' }
$stateProperties = @('completed_at', 'queue_remaining', 'pending_file_titles_remaining', 'continuation_tokens_exhausted', 'raw_candidate_file', 'metadata_cache_directory', 'failed_pages', 'scope_excluded_count')
foreach ($propertyName in $stateProperties) {
    if ($null -eq $State.PSObject.Properties[$propertyName]) { $State | Add-Member -NotePropertyName $propertyName -NotePropertyValue $null }
}
$State.completed_at = if ($complete) { (Get-Date).ToUniversalTime().ToString('o') } else { $null }
$State.queue_remaining = $State.queue.Count
$State.pending_file_titles_remaining = $State.pending_file_titles.Count
$State.continuation_tokens_exhausted = ($complete -and (@($State.category_log.Values | Where-Object { -not $_.continuation_exhausted }).Count -eq 0))
$State.raw_candidate_file = 'data/raw_candidates/commons_ottoman.jsonl'
$State.metadata_cache_directory = 'sources/cache/commons_ottoman'
$State.failed_pages = $State.failures
$State.scope_excluded_count = $State.scope_excluded_categories.Count
Save-State
Write-Output (ConvertTo-Json ([ordered]@{ status = $State.status; categories = $State.counters.categories_fetched; files = $State.counters.unique_files; failures = $State.failures.Count; queue_remaining = $State.queue.Count; pending = $State.pending_file_titles.Count }) -Compress)
