param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
$AtlasRoot = Join-Path $ProjectRoot 'data\source_atlas'
$OutPath = Join-Path $AtlasRoot 'global_source_atlas.json'
New-Item -ItemType Directory -Force -Path $AtlasRoot | Out-Null

function Normalize-Status([string]$Status) {
    if ($Status -match '^complete|completed|mirror_complete|selected_swept|selected_first_sweep|swept$|swept_card_index|existing_object_source_dedupe') { return 'completed' }
    if ($Status -match 'blocked|unreachable|access_control|fetch_failed|access_issue|image_api_blocked') { return 'blocked' }
    if ($Status -match 'partial|one_failed|item_fetch_failures|accessible_salt|cached') { return 'partial' }
    return 'not_started'
}

$records = [ordered]@{}
$scopeSummaries = [Collections.Generic.List[object]]::new()

foreach ($file in Get-ChildItem -LiteralPath $AtlasRoot -Filter '*_source_matrix.json' -File | Sort-Object Name) {
    $matrix = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
    $scopeId = if ($matrix.scope_id) { $matrix.scope_id } elseif ($matrix.source_atlas_id) { $matrix.source_atlas_id -replace '_source_matrix$','' } else { $file.BaseName -replace '_source_matrix$','' }
    $scopeLabel = if ($matrix.scope_label) { $matrix.scope_label } elseif ($matrix.scope.granting_system) { $matrix.scope.granting_system } else { $scopeId }
    if ($matrix.PSObject.Properties.Name -contains 'sources') {
        foreach ($source in $matrix.sources) {
            $copy = [ordered]@{}
            foreach ($prop in $source.PSObject.Properties) { $copy[$prop.Name] = $prop.Value }
            if (-not $copy.source_id) { $copy['source_id'] = $source.id }
            if (-not $copy.source_name) { $copy['source_name'] = if ($source.title) {$source.title} else {$source.name} }
            if (-not $copy.base_url) { $copy['base_url'] = $source.url }
            if (-not $copy.source_type) { $copy['source_type'] = $source.kind }
            if (-not $copy.status -and $source.access.status) { $copy['status'] = $source.access.status }
            if (-not $copy.last_checked) { $copy['last_checked'] = $matrix.as_of }
            $copy['scope_ids'] = @($scopeId)
            $copy['matrix_file'] = $file.FullName.Substring($ProjectRoot.Length + 1).Replace('\','/')
            $records[$copy.source_id] = $copy
        }
    }
    $scopeSummaries.Add([ordered]@{
        scope_id = $scopeId
        scope_label = $scopeLabel
        matrix_file = $file.FullName.Substring($ProjectRoot.Length + 1).Replace('\','/')
        coverage = $matrix.coverage
        next_action = $matrix.next_action
    })
}

# Import the legacy Ottoman seed matrix without rewriting the proven sweep files.
$ottomanSeedPath = Join-Path $ProjectRoot 'data\source_sweeps\ottoman_seed_matrix_2026-09-26.json'
if (Test-Path -LiteralPath $ottomanSeedPath) {
    $seed = Get-Content -LiteralPath $ottomanSeedPath -Raw | ConvertFrom-Json
    foreach ($source in $seed.source_systems) {
        $records[$source.id] = [ordered]@{
            source_id = $source.id
            source_name = $source.name
            base_url = $null
            source_type = 'imported_seed'
            languages = @('mixed')
            regions_or_polities = @('Ottoman Empire')
            date_coverage = 'Ottoman period'
            content_coverage = 'Imported from the user-supplied Ottoman seed matrix and its completed sweep records.'
            has_images = $null
            image_quality_notes = 'See the linked sweep file.'
            has_pagination = $null
            download_method = 'see_sweep'
            priority = 1
            status = Normalize-Status $source.status
            source_status_detail = $source.status
            last_checked = $seed.as_of
            sweep_file = $source.sweep_file
            scope_ids = @('ottoman_empire')
            matrix_file = 'data/source_atlas/ottoman_source_matrix.json'
        }
    }
}

$statusCounts = [ordered]@{ planned=0; completed=0; partial=0; blocked=0; not_started=0 }
foreach ($record in $records.Values) {
    $statusCounts.planned++
    $normalized = Normalize-Status ([string]$record.status)
    $record.status = $normalized
    $statusCounts[$normalized]++
}

$atlas = [ordered]@{
    schema_version = '2.0'
    as_of = '2026-09-26'
    workflow = 'AUTONOMOUS_SOURCE_DISCOVERY_V2'
    source_count = $records.Count
    coverage = $statusCounts
    scopes = @($scopeSummaries)
    sources = @($records.Values | Sort-Object { $_.source_id })
    continuation_rule = 'Consult the latest checkpoint and queues; finish high-priority partial sweeps, normalize harvested data, harvest missing images, merge HTML, checkpoint, then expand the next queued scope.'
}
[IO.File]::WriteAllText($OutPath, ($atlas | ConvertTo-Json -Depth 12), [Text.UTF8Encoding]::new($false))
$atlas.coverage | ConvertTo-Json
