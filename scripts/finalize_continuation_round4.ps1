param([string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'rebuild_global_source_atlas.ps1')|Out-Null
& (Join-Path $PSScriptRoot 'rebuild_autonomous_queues.ps1')|Out-Null
$atlas=Get-Content (Join-Path $ProjectRoot 'data\source_atlas\global_source_atlas.json') -Raw|ConvertFrom-Json
$progressPath=Join-Path $ProjectRoot 'data\progress.json'
$progress=Get-Content $progressPath -Raw|ConvertFrom-Json
$rel='data/checkpoints/autonomous_continuation_round4_2026-09-26.json'
$path=Join-Path $ProjectRoot ($rel-replace '/','\')
$round=[ordered]@{
 schema_version='2.0';as_of='2026-09-26';workflow='AUTONOMOUS_SOURCE_DISCOVERY_V2 / SOURCE_FIRST_BULK_INGESTION'
 source_coverage=[ordered]@{planned=[int]$atlas.coverage.planned;completed=[int]$atlas.coverage.completed;partial=[int]$atlas.coverage.partial;blocked=[int]$atlas.coverage.blocked;not_started=[int]$atlas.coverage.not_started}
 packages=[ordered]@{
  ottoman_kuenker299_batch4=[ordered]@{input_unmapped=46;mapped=36;families=20;variants=34;excluded=9;unresolved=1;remaining_unmapped=536;next_cursor='Künker earlier unresolved segment, first raw line 107 / lot 7107'}
  france_legion_honour=[ordered]@{directory_pages=32;raw_rows=32;images_downloaded_decoded_reviewed=21;formal_variant_views=18;third_republic_views=3;second_empire_views=1;html_eligible=0;family_rule='One continuing award family across regimes'}
  japan_commons_retry=[ordered]@{routes=9;downloaded_decoded_reviewed=5;historical_designs=2;complete_object_views=2;cropped_excluded=1;blocked=4;new_public_families=2}
  egypt_commons_retry=[ordered]@{attempted_candidates=2;downloaded_decoded_reviewed=1;result='Complete Nile collar vector diagram, not established as an official object image';public_images=0;first_unattempted='EGY-COMMONS-003';blocked='EGY-COMMONS-002'}
 }
 html=[ordered]@{rebuilt=$true;official_rows=76;families=62;local_images=113;new_rows=2;new_families=2;new_volume='Japan Taisho';note='Added Taisho Enthronement Medal and First National Census Commemorative Medal with complete CC BY-SA 3.0 single-object views; did not claim missing companion views as a front/back pair.'}
 validation=[ordered]@{json='pending';images='pending';site='PASS before final aggregate: 76 official rows, 62 families, 113 local images; interactions passed'}
 exact_resume=@('Ottoman: Künker 299 earlier unresolved segment begins at raw line 107 / lot 7107; 536 unmapped rows remain overall.','Egypt: EGY-COMMONS-002 remains blocked and EGY-COMMONS-003 is the first unattempted original; retry only after a meaningful cooldown.','Japan: four exact Commons companion routes remain blocked; keep existing single views honestly labelled.','France: seek open-licence substitutes for the 18 normalized Legion of Honour historical views; do not re-download the 32 cached SAMLHOC pages.')
}
[IO.File]::WriteAllText($path,($round|ConvertTo-Json -Depth 12),[Text.UTF8Encoding]::new($false))
$progress.main_families=62;$progress.main_variants=76;$progress.main_local_images=107
$progress.active_volumes|Add-Member -NotePropertyName japan_taisho -NotePropertyValue ([ordered]@{families=2;variants=2;images=2}) -Force
$progress|Add-Member -NotePropertyName autonomous_continuation_round4_2026_09_26 -NotePropertyValue ([ordered]@{checkpoint=$rel;planned_sources=$round.source_coverage.planned;completed_sources=$round.source_coverage.completed;partial_sources=$round.source_coverage.partial;blocked_sources=$round.source_coverage.blocked;not_started_sources=$round.source_coverage.not_started;new_formal_families=2;new_formal_variants=2;new_formal_images=2;html_rebuilt=$true}) -Force
$progress.next_batch='从round4继续：奥斯曼Künker早期未决段行107/拍品7107；埃及EGY-COMMONS-002/003限流断点；日本4条伴随图；法国荣誉军团18种历史图改找开放许可替代源。'
[IO.File]::WriteAllText($progressPath,($progress|ConvertTo-Json -Depth 12),[Text.UTF8Encoding]::new($false))
$round|ConvertTo-Json -Depth 5
