param([string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot))

$ErrorActionPreference = 'Stop'
$OutRoot = Join-Path $ProjectRoot 'data\normalized'
$ConflictRoot = Join-Path $ProjectRoot 'data\conflicts'
$CheckpointRoot = Join-Path $ProjectRoot 'data\checkpoints'
New-Item -ItemType Directory -Force -Path $OutRoot,$ConflictRoot,$CheckpointRoot | Out-Null

function Read-Jsonl([string]$RelativePath) {
    $path = Join-Path $ProjectRoot $RelativePath
    if (-not (Test-Path -LiteralPath $path)) { return @() }
    return @(Get-Content -LiteralPath $path | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object { $_ | ConvertFrom-Json })
}

function Save-Json([string]$Path, [object]$Value) {
    [IO.File]::WriteAllText($Path, ($Value | ConvertTo-Json -Depth 15), [Text.UTF8Encoding]::new($false))
}

function Slug([string]$Text) {
    $s = $Text.ToUpperInvariant() -replace '[^A-Z0-9]+','-'
    return $s.Trim('-')
}

function Key([string]$Text) {
    $s = $Text.ToLowerInvariant() -replace '[^a-z0-9]+',' '
    return ($s -replace '\s+',' ').Trim()
}

$fr = Read-Jsonl 'data/raw_candidates/france_second_third_republic_official_commemoratives.jsonl'
$jp = Read-Jsonl 'data/raw_candidates/japan_ndl_1441381_atlas.jsonl'
$de = Read-Jsonl 'data/raw_candidates/weitze_preussen_12_german_states.jsonl'
$eg = Read-Jsonl 'data/raw_candidates/wawards_egypt.jsonl'
$sd = Read-Jsonl 'data/raw_candidates/wawards_medalsorg_sudan.jsonl'

$families = [Collections.Generic.List[object]]::new()
$conflicts = [Collections.Generic.List[object]]::new()

# France: the official catalogue already supplies stable family keys and a local difference result.
foreach ($g in $fr | Where-Object { $_.local_difference_status -notlike 'boundary_excluded*' } | Group-Object family) {
    $rows = @($g.Group)
    $families.Add([ordered]@{
        scope_id = 'france_second_third_republic'
        family_id = $g.Name
        preferred_name = $rows[0].original_names[0]
        aliases = @($rows.original_names | ForEach-Object { $_ } | Sort-Object -Unique)
        period_scopes = @($rows.period_scope | Sort-Object -Unique)
        normalization_status = if ($rows.existing_family_in_local_records -contains $true) {'matched_existing_family'} else {'new_family_candidate'}
        variant_candidates = @($rows | Where-Object local_difference_status -eq 'existing_family_variant_or_coverage_gap' | ForEach-Object { $_.candidate_key })
        evidence_sources = @($rows.source_page | Sort-Object -Unique)
        raw_source_ids = @($rows.source_id)
        image_status = 'missing_complete_catalogue_image'
    })
}

# Japan: family IDs are already stable; retain grade candidates but do not promote text/table scans as object images.
foreach ($g in $jp | Group-Object family_id) {
    $rows = @($g.Group)
    $familyStatuses = @($rows.dedupe_status | Sort-Object -Unique)
    $families.Add([ordered]@{
        scope_id = 'japan_meiji_taisho'
        family_id = $g.Name
        preferred_name = $rows[0].name
        aliases = @($rows.original_name | Sort-Object -Unique)
        period_scopes = @($rows.period_scope | Sort-Object -Unique)
        normalization_status = if ($familyStatuses -contains 'new_family_candidate') {'new_family_candidate'} elseif ($familyStatuses -contains 'new_or_unresolved') {'needs_identity_review'} else {'matched_existing_family'}
        variant_candidates = @($rows | Where-Object dedupe_status -eq 'same_family_new_variant_candidate' | ForEach-Object { [ordered]@{candidate_id=$_.candidate_id; name=$_.name; grade=$_.variant_or_grade} })
        candidate_rows = @($rows.candidate_id)
        evidence_sources = @($rows.source_url | Sort-Object -Unique)
        image_status = 'source_scan_only_not_object_image'
    })
}

# German commercial cards: normalize only records with an explicit family guess; all others remain in the raw queue.
foreach ($g in $de | Where-Object { $_.family_guess } | Group-Object family_guess) {
    $rows = @($g.Group)
    $families.Add([ordered]@{
        scope_id = 'german_states'
        family_id = $g.Name
        preferred_name = $rows[0].title
        aliases = @($rows.title | Sort-Object -Unique)
        period_scopes = @($rows.page_scope_state | Sort-Object -Unique)
        normalization_status = if ($rows.difference_status -contains 'new_family_candidate') {'catalogue_family_candidate_needs_institutional_confirmation'} else {'matched_existing_family_variant_review'}
        variant_candidates = @($rows | ForEach-Object { [ordered]@{catalog_item=$_.catalog_item_number; title=$_.title; clues=@($_.variant_clues); product_page=$_.product_page} })
        evidence_sources = @($rows.source_page | Sort-Object -Unique)
        image_status = 'thumbnail_leads_only_not_accepted'
    })
}

# Egypt: one detail page is one provisional family until cross-checked with official sources.
foreach ($row in $eg) {
    $dates = @($row.date_candidates | Where-Object { $_ -notin @(2007,2026) })
    $families.Add([ordered]@{
        scope_id = 'egypt'
        family_id = 'EGY-CAND-' + (Slug $row.page_title)
        preferred_name = $row.page_title
        aliases = @($row.original_name,$row.english_name | Where-Object { $_ } | Sort-Object -Unique)
        date_candidates = $dates
        normalization_status = 'provisional_family_needs_official_crosscheck'
        variant_candidates = @()
        evidence_sources = @($row.page_url)
        raw_source_ids = @($row.source_id)
        image_status = 'page_chrome_only_no_accepted_object_image'
    })
}

# Sudan: collapse exact titles and a small set of explicit spelling/order aliases across the two catalogues.
$sudanAliasMap = @{
    'cordon of honour' = 'collar of honour'
    'order of loyal son of sudan' = 'order of the loyal son of sudan'
    'order of persistance' = 'order of persistence'
    'duty medal' = 'medal of duty'
}
$sudanRows = foreach ($row in $sd) {
    $k = Key $row.page_title
    if ($sudanAliasMap.ContainsKey($k)) { $k = $sudanAliasMap[$k] }
    [pscustomobject]@{ key=$k; row=$row }
}
foreach ($g in $sudanRows | Group-Object key) {
    $rows = @($g.Group.row)
    $dates = @($rows.date_candidates | ForEach-Object { $_ } | Where-Object { $_ -notin @(2007,2026) } | Sort-Object -Unique)
    $families.Add([ordered]@{
        scope_id = 'sudan'
        family_id = 'SDN-CAND-' + (Slug $g.Name)
        preferred_name = $rows[0].page_title
        aliases = @($rows.page_title | Sort-Object -Unique)
        date_candidates = $dates
        normalization_status = if (($rows.source_system | Sort-Object -Unique).Count -gt 1) {'cross_source_name_match'} else {'single_source_provisional_family'}
        variant_candidates = @()
        evidence_sources = @($rows.page_url | Sort-Object -Unique)
        raw_source_ids = @($rows.source_id)
        image_status = 'no_accepted_object_image'
    })
}

# Keep date/name conflicts explicit without blocking ordinary families.
foreach ($f in $families | Where-Object { $_.date_candidates.Count -gt 1 }) {
    $conflicts.Add([ordered]@{scope_id=$f.scope_id; family_id=$f.family_id; type='DATE_CANDIDATES'; values=@($f.date_candidates); status='UNRESOLVED'})
}

$summary = [ordered]@{
    input_rows = [ordered]@{france=$fr.Count; german_states=$de.Count; japan=$jp.Count; egypt=$eg.Count; sudan=$sd.Count; total=$fr.Count+$de.Count+$jp.Count+$eg.Count+$sd.Count}
    normalized_family_records = $families.Count
    by_scope = [ordered]@{}
    new_family_candidates = @($families | Where-Object normalization_status -match '^new_family_candidate|catalogue_family_candidate|provisional_family|single_source_provisional').Count
    matched_existing_or_cross_source = @($families | Where-Object normalization_status -match 'matched_existing|cross_source').Count
    needs_identity_review = @($families | Where-Object normalization_status -match 'needs_identity_review').Count
    variant_candidates = @($families | ForEach-Object { @($_.variant_candidates).Count } | Measure-Object -Sum).Sum
    conflicts = $conflicts.Count
    catalogue_ready_images = 0
}
foreach ($scope in @('france_second_third_republic','german_states','japan_meiji_taisho','egypt','sudan')) {
    $summary.by_scope[$scope] = @($families | Where-Object scope_id -eq $scope).Count
}

$payload = [ordered]@{
    schema_version = '2.0'
    as_of = '2026-09-26'
    batch_id = 'multiscope_normalized_batch1'
    status = 'normalized_draft_not_html_approved'
    summary = $summary
    families = @($families)
    remaining_raw_boundaries = [ordered]@{
        german_cards_without_family_guess = @($de | Where-Object { -not $_.family_guess }).Count
        france_boundary_exclusions = @($fr | Where-Object local_difference_status -like 'boundary_excluded*').Count
        note = 'Provisional families require official/institutional cross-check and image review before HTML promotion.'
    }
}
Save-Json (Join-Path $OutRoot 'multiscope_normalized_batch1.json') $payload
Save-Json (Join-Path $ConflictRoot 'multiscope_normalization_batch1.json') ([ordered]@{schema_version='2.0'; as_of='2026-09-26'; conflicts=@($conflicts)})
Save-Json (Join-Path $CheckpointRoot 'multiscope_normalization_batch1_2026-09-26.json') ([ordered]@{schema_version='2.0'; as_of='2026-09-26'; batch='multiscope_normalized_batch1'; summary=$summary; output='data/normalized/multiscope_normalized_batch1.json'; next_action='Cross-check provisional Egypt/Sudan and German catalogue families against official/institutional sources, then create image-harvest packs for accepted differences.'})
$summary | ConvertTo-Json -Depth 8
