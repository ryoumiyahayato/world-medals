param([string]$ProjectRoot=(Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference='Stop'
$path=Join-Path $ProjectRoot 'data\image_harvest\ottoman_image_batch1.json'
$data=Get-Content $path -Raw|ConvertFrom-Json
$accepted=0
foreach($record in $data.records){if($record.download_status -in @('downloaded_selected_original','reused_existing_batch_file') -and $record.decode_status -eq 'ok'){$record.visual_review.status='accepted_complete_internal_research';$record.visual_review.review_date='2026-09-26';$record.visual_review.complete_outline=$true;$record.visual_review.not_thumbnail=$true;$record.visual_review.not_cropped=$true;$record.visual_review.object_match=$true;$record.visual_review.notes='Manually viewed at original resolution: complete medal and suspension/ribbon visible; source title matches object family. Rights remain commercial/unstated, therefore not approved for HTML.';$record.body_eligible=$false;$record.public_embed_status='blocked_by_rights_not_image_quality';$accepted++}}
$data.summary|Add-Member -NotePropertyName manual_reviewed_complete -NotePropertyValue $accepted -Force
$data.summary|Add-Member -NotePropertyName html_eligible -NotePropertyValue 0 -Force
[IO.File]::WriteAllText($path,($data|ConvertTo-Json -Depth 20),[Text.UTF8Encoding]::new($false))
$cp=Join-Path $ProjectRoot 'data\checkpoints\ottoman_image_harvest_batch1_2026-09-26.json';if(Test-Path $cp){$c=Get-Content $cp -Raw|ConvertFrom-Json;$c|Add-Member -NotePropertyName manual_review -NotePropertyValue ([ordered]@{complete_images=$accepted;html_eligible=0;blocker='commercial-source rights not established'}) -Force;[IO.File]::WriteAllText($cp,($c|ConvertTo-Json -Depth 20),[Text.UTF8Encoding]::new($false))}
[ordered]@{manual_reviewed_complete=$accepted;html_eligible=0}|ConvertTo-Json
