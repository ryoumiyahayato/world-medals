param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'

& (Join-Path $PSScriptRoot 'rebuild_global_source_atlas.ps1') | Out-Null
& (Join-Path $PSScriptRoot 'rebuild_autonomous_queues.ps1') | Out-Null

$atlasPath = Join-Path $ProjectRoot 'data\source_atlas\global_source_atlas.json'
$progressPath = Join-Path $ProjectRoot 'data\progress.json'
$checkpointPath = Join-Path $ProjectRoot 'data\checkpoints\autonomous_continuation_round2_2026-09-26.json'
$atlas = Get-Content -LiteralPath $atlasPath -Raw | ConvertFrom-Json
$progress = Get-Content -LiteralPath $progressPath -Raw | ConvertFrom-Json

$round = [ordered]@{
    schema_version = '2.0'
    as_of = '2026-09-26'
    workflow = 'AUTONOMOUS_SOURCE_DISCOVERY_V2 / SOURCE_FIRST_BULK_INGESTION'
    source_coverage = [ordered]@{
        planned = [int]$atlas.coverage.planned
        completed = [int]$atlas.coverage.completed
        partial = [int]$atlas.coverage.partial
        blocked = [int]$atlas.coverage.blocked
        not_started = [int]$atlas.coverage.not_started
    }
    continuation_sources = @(
        [ordered]@{source_id='egypt_presidency_honours'; result='completed'; raw_rows=11},
        [ordered]@{source_id='omsa_egypt_awards_appendix'; result='completed'; raw_rows=29},
        [ordered]@{source_id='medalbook_sudan'; result='partial_one_dead_object_url'; raw_rows=89},
        [ordered]@{source_id='commons_sudan_awards'; result='blocked_http_429_no_repeat_retry'; raw_rows=0},
        [ordered]@{source_id='dhm-awards-collection'; result='legacy_catalogue_pages_swept_database_pow_blocked'; raw_rows=64},
        [ordered]@{source_id='weitze-bayern-12-alternative'; result='completed'; raw_rows=60},
        [ordered]@{source_id='FR-SAMLHOC-TONKIN'; result='completed_current_tonkin_scope'; raw_rows=3},
        [ordered]@{source_id='FR-SAMLHOC-MADAGASCAR'; result='completed_current_visible_scope'; raw_rows=2},
        [ordered]@{source_id='jpn-ndl-1441381'; result='directory_and_supporting_text_pages_complete_no_object_plates'; raw_rows=30},
        [ordered]@{source_id='jpn-ndl-967000'; result='blocked_plate_image_route'; raw_rows=0}
    )
    new_raw_candidate_rows = 288
    normalization_batches = [ordered]@{
        ottoman = [ordered]@{input_rows=1825; independent_families=43; variants=280; new_family_candidates=21; conflicts=100; unmapped_rows=661; continuation_reviewed_rows=8; continuation_unresolved_families=5}
        multiscope_initial = [ordered]@{input_rows=510; family_records=153; variants=239; conflicts=14; note='Superseded for Germany, Egypt and Sudan by the later scope-specific batches below.'}
        german_states = [ordered]@{input_rows=469; independent_families=38; variants=301; new_family_candidates=27; conflicts=15; identity_review_rows=434}
        egypt = [ordered]@{input_rows=90; independent_families=62; variants=117; new_family_candidates=51; conflicts=12; excluded_rows=3; missing_complete_image_families=62}
        sudan = [ordered]@{input_rows=160; independent_families=77; variants=160; cross_source_families=31; conflicts=2}
        japan_ndl_directory = [ordered]@{raw_candidates=30; existing_overlap=14; same_family_new_variant_candidates=6; new_family_candidates=7; new_or_unresolved=3}
    }
    image_review = [ordered]@{
        downloaded_and_decoded_files = 158
        visually_accepted_complete_front_or_pair_files = 76
        breakdown = [ordered]@{
            ottoman = [ordered]@{downloaded=3; complete=3; publication_eligible=0}
            german_dhm = [ordered]@{downloaded=67; complete_front=52; local_candidates=33; publication_eligible=0}
            sudan_medalbook = [ordered]@{downloaded=77; selected_complete_front=17; publication_eligible=0}
            france_samlhoc_tonkin = [ordered]@{downloaded=7; complete_medal_pair_files=2; publication_eligible=0}
            france_samlhoc_madagascar = [ordered]@{downloaded=4; complete_medal_pair_files=2; diploma_files=2; publication_eligible=0}
        }
        publication_eligible = 0
        historical_full_page_scans_decoded = 32
        historical_plate_object_images = 0
        explanation = 'All newly harvested object images are commercial, all-rights-reserved, or institutionally accessible without a stated reuse licence. They remain internal research evidence and were not merged into index.html.'
    }
    html = [ordered]@{
        rebuilt = $false
        reason = 'No newly harvested image passed both identity and publication-rights review; preserving the valid existing catalogue is safer than adding research-only assets.'
        existing_main_families = [int]$progress.main_families
        existing_main_variants = [int]$progress.main_variants
        existing_local_images = [int]$progress.main_local_images + [int]$progress.related_local_images
    }
    files = [ordered]@{
        global_atlas = 'data/source_atlas/global_source_atlas.json'
        sweep_queue = 'data/queues/source_sweep_queue.json'
        image_queue = 'data/queues/image_harvest_queue.json'
        ottoman_normalized = 'data/normalized/ottoman_normalized_batch1.json'
        german_normalized = 'data/normalized/german_states_normalized_batch2.json'
        egypt_normalized = 'data/normalized/egypt_normalized_batch3.json'
        sudan_normalized = 'data/normalized/sudan_normalized_batch2.json'
    }
    exact_resume = @(
        'Ottoman: continue the 661 unmapped rows, beginning with the five saved NEW-* keys, then harvest from a reusable image source.',
        'Germany: resolve the 434 identity-review rows; confirm DHM reuse terms or replace the 33 local image candidates.',
        'Egypt: image-harvest the 62 normalized families, preferring Presidency/official diagrams and open museum records.',
        'Sudan: replace or clear 17 commercial-source fronts; retry Commons only after the 429 condition changes.',
        'France: find a reusable complete TONKIN-clasp image, then take the Madagascar and Morocco source packages.',
        'Japan: continue the existing Meiji/Taisho normalized batch into NDL/public-domain plate harvesting.'
    )
}

[IO.File]::WriteAllText($checkpointPath, ($round | ConvertTo-Json -Depth 12), [Text.UTF8Encoding]::new($false))

$progressRecord = [ordered]@{
    checkpoint = 'data/checkpoints/autonomous_continuation_round2_2026-09-26.json'
    planned_sources = $round.source_coverage.planned
    completed_sources = $round.source_coverage.completed
    partial_sources = $round.source_coverage.partial
    blocked_sources = $round.source_coverage.blocked
    not_started_sources = $round.source_coverage.not_started
    new_raw_candidate_rows = $round.new_raw_candidate_rows
    downloaded_and_decoded_images = $round.image_review.downloaded_and_decoded_files
    visually_accepted_complete_images = $round.image_review.visually_accepted_complete_front_or_pair_files
    publication_eligible_images = 0
    html_rebuilt = $false
}
$progress | Add-Member -NotePropertyName autonomous_continuation_round2_2026_09_26 -NotePropertyValue $progressRecord -Force
$progress.next_batch = '从 round2 检查点继续：先推进奥斯曼661条未映射记录与日本NDL公开图版；并行处理德国身份复核、埃及62个family和苏丹17张候选图的开放许可替代源。仅在形成身份正确且可用的完整图批次后统一重建index.html。'
[IO.File]::WriteAllText($progressPath, ($progress | ConvertTo-Json -Depth 12), [Text.UTF8Encoding]::new($false))

$round | ConvertTo-Json -Depth 5
