param([string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference = 'Stop'

& (Join-Path $PSScriptRoot 'rebuild_global_source_atlas.ps1') | Out-Null
& (Join-Path $PSScriptRoot 'rebuild_autonomous_queues.ps1') | Out-Null

$atlas = Get-Content (Join-Path $ProjectRoot 'data\source_atlas\global_source_atlas.json') -Raw | ConvertFrom-Json
$progressPath = Join-Path $ProjectRoot 'data\progress.json'
$progress = Get-Content $progressPath -Raw | ConvertFrom-Json
$checkpointRel = 'data/checkpoints/autonomous_continuation_round3_2026-09-26.json'
$checkpointPath = Join-Path $ProjectRoot ($checkpointRel -replace '/','\')

$round = [ordered]@{
    schema_version='2.0'
    as_of='2026-09-26'
    workflow='AUTONOMOUS_SOURCE_DISCOVERY_V2 / SOURCE_FIRST_BULK_INGESTION'
    source_coverage=[ordered]@{
        planned=[int]$atlas.coverage.planned
        completed=[int]$atlas.coverage.completed
        partial=[int]$atlas.coverage.partial
        blocked=[int]$atlas.coverage.blocked
        not_started=[int]$atlas.coverage.not_started
    }
    work_packages=[ordered]@{
        ottoman_kuenker299_continuation=[ordered]@{
            input_unmapped_rows=79; mapped_rows=75; excluded_rows=3; unresolved_rows=1
            families=28; variants=70; remaining_unmapped=582
            next_cursor='raw line 336 / lot 7336'
            file='data/normalized/ottoman_normalized_continuation_batch3.json'
        }
        japan_official_commons=[ordered]@{
            candidates=13; existing_family_new_variants=6; new_family_candidates=7
            downloaded_decoded_reviewed_images=3; exact_candidate_bindings=2
            body_eligible_photographs=1; historical_design_only=1; excluded_related_reference=1
            blocked_original_routes=9
            file='data/normalized/japan_official_commons_batch1.json'
        }
        egypt_commons=[ordered]@{
            category_pages=16; category_memberships=102; unique_files=99
            selected_file_pages_cached=19; original_downloads=0
            blocker='HTTP 429 / Retry-After 600; no thumbnail substitution'
            file='data/image_harvest/egypt_commons_awards_batch1.json'
        }
        france_samlhoc_morocco=[ordered]@{
            source_pages=4; raw_candidates=1; families=1; variants=4
            downloaded_decoded_reviewed_images=2; complete_object_pair_files=1; diploma_files=1
            publication_eligible=0
            file='data/source_sweeps/france_samlhoc_morocco.json'
        }
    }
    html=[ordered]@{
        rebuilt=$true
        main_families=60
        main_variants=74
        decoded_local_images=111
        rows_added=0
        images_replaced=1
        replacement='The Chrysanthemum Collar row now uses the complete 1500x1950 Cabinet Office reference image under CC BY 4.0 instead of the rights-unclear National Archives image. The historical source remains preserved internally.'
    }
    validation=[ordered]@{
        json='pending final validation'
        images='pending final validation'
        site='pending final validation'
    }
    exact_resume=@(
        'Ottoman Kuenker 299: continue at raw line 336 / lot 7336; 582 rows remain unmapped.',
        'Egypt Commons: retry only the 19 recorded original URLs after the rate-limit condition changes; decode and visually inspect before merge.',
        'Japan: retry the nine recorded Commons originals only after the rate-limit condition changes; keep the Rising Sun image excluded from Paulownia/rank bindings.',
        'France: Morocco source package is complete; seek a reusable higher-resolution object source instead of re-downloading SAMLHOC.',
        'Rebuild index.html only after another rights-cleared, identity-reviewed material batch.'
    )
}

[IO.File]::WriteAllText($checkpointPath, ($round | ConvertTo-Json -Depth 12), [Text.UTF8Encoding]::new($false))
$progressRecord=[ordered]@{
    checkpoint=$checkpointRel
    planned_sources=$round.source_coverage.planned
    completed_sources=$round.source_coverage.completed
    partial_sources=$round.source_coverage.partial
    blocked_sources=$round.source_coverage.blocked
    not_started_sources=$round.source_coverage.not_started
    ottoman_rows_mapped=75
    japan_candidates=13
    egypt_commons_unique_files=99
    rights_cleared_html_image_replacements=1
    html_rebuilt=$true
}
$progress | Add-Member -NotePropertyName autonomous_continuation_round3_2026_09_26 -NotePropertyValue $progressRecord -Force
$progress.next_batch='从 round3 检查点继续：Künker 299 行336／拍品7336；埃及19条和日本9条Commons原图只在限流状态改变后低速重试；法国Morocco改找开放高分辨率替代源。'
[IO.File]::WriteAllText($progressPath, ($progress | ConvertTo-Json -Depth 12), [Text.UTF8Encoding]::new($false))
$round | ConvertTo-Json -Depth 6
