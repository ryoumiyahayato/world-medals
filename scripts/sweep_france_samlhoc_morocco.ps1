param([string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$cache = Join-Path $ProjectRoot 'sources\cache\france_samlhoc_morocco'
$rawPath = Join-Path $ProjectRoot 'data\raw_candidates\france_samlhoc_morocco.jsonl'
$sweepPath = Join-Path $ProjectRoot 'data\source_sweeps\france_samlhoc_morocco.json'
New-Item -ItemType Directory -Force -Path $cache | Out-Null

$pages = @(
    [ordered]@{role='main_history_legal_and_type'; url='https://www.samlhoc.fr/phaleristique/medailles/medaille_commemorative_maroc/'; file='morocco_main.html'},
    [ordered]@{role='object_image_page'; url='https://www.samlhoc.fr/phaleristique/medailles/medaille_commemorative_maroc/medaille_commemorative_maroc_insigne/'; file='morocco_insigne.html'},
    [ordered]@{role='diploma_image_page'; url='https://www.samlhoc.fr/phaleristique/medailles/medaille_commemorative_maroc/medaille_commemorative_maroc_diplome/'; file='morocco_diplome.html'},
    [ordered]@{role='rights'; url='https://www.samlhoc.fr/mentions-legales/'; file='mentions_legales.html'}
)
foreach ($page in $pages) {
    $response = Invoke-WebRequest -Uri $page.url -UseBasicParsing -TimeoutSec 30
    [IO.File]::WriteAllText((Join-Path $cache $page.file), $response.Content, [Text.UTF8Encoding]::new($false))
    $page['http_status'] = [int]$response.StatusCode
    $page['local_cache'] = ('sources/cache/france_samlhoc_morocco/' + $page.file)
}

$images = @(
    [ordered]@{role='complete obverse/reverse pair with ribbon and three visible clasps'; url='https://www.samlhoc.fr/wp-content/uploads/import/www.france-phaleristique.com/images/marocar.jpg'; file='marocar.jpg'; object_image=$true},
    [ordered]@{role='award diploma; document only'; url='https://www.samlhoc.fr/wp-content/uploads/import/www.france-phaleristique.com/images/marocdip.jpg'; file='marocdip.jpg'; object_image=$false}
)
foreach ($item in $images) {
    $path = Join-Path $cache $item.file
    Invoke-WebRequest -Uri $item.url -UseBasicParsing -TimeoutSec 30 -OutFile $path
    $bitmap = [Drawing.Image]::FromFile($path)
    try { $item['width']=[int]$bitmap.Width; $item['height']=[int]$bitmap.Height } finally { $bitmap.Dispose() }
    $item['bytes']=(Get-Item -LiteralPath $path).Length
    $item['sha256']=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    $item['local_path']='sources/cache/france_samlhoc_morocco/' + $item.file
    $item['decoded']=$true
    $item['visually_reviewed']=$false
}

$candidate = [ordered]@{
    source_id='FR-SAMLHOC-MOROCCO'
    source_system='SAMLHOC / France Phaléristique'
    source_type='specialist_history_legal_and_type_page'
    accessed='2026-09-26'
    candidate_key='FRA-III-MOROCCO-1909'
    family='FRA-III-MOROCCO-COMMEMORATIVE'
    original_names=@('Médaille commémorative du Maroc','Médaille commémorative des opérations effectuées au Maroc')
    period_scope='Law of 22 July 1909; qualifying operations from 1907, with the MAROC clasp extending to 19 July 1912'
    granting_body='French Republic'
    category='campaign commemorative medal'
    establishment='Law of 22 July 1909'
    eligibility_summary='Military, naval, indigenous, civil-service and military-aid-society personnel within the operation categories and periods transcribed on the source page; individual award dates are not inferred.'
    physical_description='30 mm silver round medal by Georges Lemaire; helmeted Republic obverse; MAROC and army/navy attributes reverse; 36 mm green ribbon with three white vertical stripes.'
    variants=@(
        [ordered]@{variant_key='FRA-III-MOROCCO-CASABLANCA'; label='Agrafe CASABLANCA'; period='5 August 1907–15 June 1909'},
        [ordered]@{variant_key='FRA-III-MOROCCO-OUDJDA'; label='Agrafe OUDJDA'; period='29 March 1907–1 January 1909'},
        [ordered]@{variant_key='FRA-III-MOROCCO-HAUT-GUIR'; label='Agrafe HAUT-GUIR'; period='6 March–10 June 1908 and 15 August–7 October 1908'},
        [ordered]@{variant_key='FRA-III-MOROCCO-MAROC'; label='Agrafe MAROC'; period='23 February 1910–19 July 1912'}
    )
    image_resources=$images
    source_pages=$pages
    existing_family_in_local_records=$true
    local_difference_status='existing_family_variant_or_coverage_gap'
    status='RAW_CANDIDATE'
    rights_note='SAMLHOC legal notice states reproduction/adaptation requires prior written permission; cached files are internal research evidence and are not publication-cleared.'
}
[IO.File]::WriteAllText($rawPath, ($candidate | ConvertTo-Json -Depth 10 -Compress) + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))

$sweep = [ordered]@{
    source_id='FR-SAMLHOC-MOROCCO'
    source_name='SAMLHOC / France Phaléristique — Morocco commemorative medal'
    as_of='2026-09-26'
    status='complete_current_visible_scope_pending_manual_image_review'
    scope_rule='Main Morocco page plus its explicit object, diploma and rights pages only.'
    source_pages_processed=$pages.Count
    source_pages=$pages
    candidate_rows=1
    families_in_candidates=1
    variant_candidates=4
    image_audit=[ordered]@{found=2; downloaded=2; decoded=2; complete_object_pair_files=1; diploma_files=1; manually_reviewed=0; publication_eligible=0; resources=$images}
    raw_candidate_file='data/raw_candidates/france_samlhoc_morocco.jsonl'
    metadata_cache_directory='sources/cache/france_samlhoc_morocco'
    failures=@([ordered]@{scope='rights'; result='No open reuse licence found; object and diploma files remain internal research evidence.'})
    next_checkpoint='Manually inspect marocar.jpg and marocdip.jpg, then mark image roles/completeness; do not broaden to unrelated SAMLHOC pages.'
}
[IO.File]::WriteAllText($sweepPath, ($sweep | ConvertTo-Json -Depth 12), [Text.UTF8Encoding]::new($false))
$sweep | ConvertTo-Json -Depth 4
