param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
$AtlasPath = Join-Path $ProjectRoot 'data\source_atlas\global_source_atlas.json'
$QueueRoot = Join-Path $ProjectRoot 'data\queues'
New-Item -ItemType Directory -Force -Path $QueueRoot | Out-Null
$atlas = Get-Content -LiteralPath $AtlasPath -Raw | ConvertFrom-Json

function Save-Json([string]$Name, [object]$Value) {
    [IO.File]::WriteAllText((Join-Path $QueueRoot $Name), ($Value | ConvertTo-Json -Depth 12), [Text.UTF8Encoding]::new($false))
}

$requiredScopes = @(
    [ordered]@{scope_id='ottoman_empire'; label='Ottoman Empire / historical Turkey'; priority=1},
    [ordered]@{scope_id='france_second_third_republic'; label='France — Second Empire and Third Republic'; priority=1},
    [ordered]@{scope_id='german_states'; label='Prussia and German states'; priority=1},
    [ordered]@{scope_id='japan_meiji_taisho'; label='Japan — Meiji and Taisho'; priority=1},
    [ordered]@{scope_id='egypt'; label='Egypt'; priority=1},
    [ordered]@{scope_id='sudan'; label='Sudan'; priority=1}
)

$knownScopes = @($atlas.scopes.scope_id)
$discoveryItems = foreach ($scope in $requiredScopes) {
    [ordered]@{
        scope_id = $scope.scope_id
        label = $scope.label
        priority = $scope.priority
        status = if ($knownScopes -contains $scope.scope_id) {'matrix_created'} else {'not_started'}
        next_action = if ($knownScopes -contains $scope.scope_id) {'Expand uncovered source types and re-check high-value partial sources during continuation.'} else {'Create the autonomous source matrix and immediately sweep one high-priority accessible source.'}
    }
}
Save-Json 'source_discovery_queue.json' ([ordered]@{schema_version='2.0'; as_of='2026-09-26'; workflow='AUTONOMOUS_SOURCE_DISCOVERY_V2'; items=@($discoveryItems)})

$sweepItems = foreach ($source in $atlas.sources | Where-Object { $_.status -in @('partial','not_started','blocked') } | Sort-Object @{Expression={if ($_.priority) {[int]$_.priority} else {9}}}, source_id) {
    [ordered]@{
        source_id = $source.source_id
        source_name = $source.source_name
        scope_ids = @($source.scope_ids)
        priority = if ($source.priority) {$source.priority} else {9}
        status = $source.status
        base_url = $source.base_url
        matrix_file = $source.matrix_file
        next_action = if ($source.status -eq 'blocked') {'Retain exact blocker; retry only after a meaningful access-path change or use an alternate source.'} elseif ($source.status -eq 'partial') {'Finish remaining visible pagination, categories, chapters or failed object pages.'} else {'Sweep the complete accessible source or a clearly bounded chapter/lot range.'}
    }
}
Save-Json 'source_sweep_queue.json' ([ordered]@{schema_version='2.0'; as_of='2026-09-26'; ordering='priority, partial before new where operationally useful'; items=@($sweepItems)})

$imageItems = @(
    [ordered]@{scope_id='ottoman_empire'; priority=1; status='partial_harvest_rights_blocked'; source_ids=@('commons_ottoman','emedals_ottoman','kuenker299_ottoman','ottoman_bank_archive_awards'); target='Continue normalized missing-image families from an open-licence source; three complete research images are retained but not publication-cleared.'},
    [ordered]@{scope_id='france_second_third_republic'; priority=2; status='partial_harvest_rights_blocked'; source_ids=@('FR-SAMLHOC-TONKIN','FR-SAMLHOC-MADAGASCAR','FR-OFFICIAL-COMMEMORATIVE-PDF'); target='Find reusable complete TONKIN-clasp and Madagascar variant images, then continue official or historical plate figures for accepted differences.'},
    [ordered]@{scope_id='german_states'; priority=2; status='research_harvest_complete_rights_blocked'; source_ids=@('DE-DHM-ORDERS'); target='Confirm reuse permission or replace 33 local candidates with rights-cleared museum or historical-plate images.'},
    [ordered]@{scope_id='japan_meiji_taisho'; priority=2; status='partial_harvest_rate_limited'; source_ids=@('jpn-ndl-1441381','japan_official_commons_batch1'); target='Retry only the nine recorded Commons originals after the 429 condition changes; one Cabinet Office CC BY image has already replaced the rights-unclear collar image.'},
    [ordered]@{scope_id='egypt'; priority=2; status='partial_harvest_rate_limited'; source_ids=@('wawards_egypt','egypt_presidency_honours','omsa_egypt_awards_appendix','commons_egypt_awards'); target='Retry only the 19 recorded Commons original URLs after the 429 condition changes, then decode and visually inspect before binding to the 62 normalized families.'},
    [ordered]@{scope_id='sudan'; priority=2; status='research_harvest_complete_rights_blocked'; source_ids=@('wawards_sudan','medalbook_sudan','commons_sudan_awards'); target='Replace or clear the 17 complete commercial-source fronts; retry Commons only after the 429 access condition changes.'}
)
Save-Json 'image_harvest_queue.json' ([ordered]@{schema_version='2.0'; as_of='2026-09-26'; items=$imageItems})

$mergeItems = foreach ($scope in $requiredScopes) {
    [ordered]@{scope_id=$scope.scope_id; priority=$scope.priority; status='waiting_for_normalized_and_image_reviewed_batch'; target='Existing offline index.html'; ui_contract='名称＋日期｜等级／版别｜完整图样'}
}
Save-Json 'html_merge_queue.json' ([ordered]@{schema_version='2.0'; as_of='2026-09-26'; rebuild_policy='One rebuild after a material normalized and image-reviewed batch; never one item at a time.'; items=@($mergeItems)})

[ordered]@{discovery=$discoveryItems.Count; sweep=$sweepItems.Count; image=$imageItems.Count; merge=$mergeItems.Count} | ConvertTo-Json
