param([string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference='Stop'
$sweepPath=Join-Path $ProjectRoot 'data\source_sweeps\france_samlhoc_legion_honour.json'
$outPath=Join-Path $ProjectRoot 'data\normalized\france_legion_honour_batch1.json'
$conflictPath=Join-Path $ProjectRoot 'data\conflicts\france_legion_honour_batch1.json'
$checkpointPath=Join-Path $ProjectRoot 'data\checkpoints\france_legion_honour_batch1_2026-09-26.json'
$sweep=Get-Content $sweepPath -Raw|ConvertFrom-Json

$map=[ordered]@{
 'lh1emp1tar.jpg'=@('First Empire','cross, first type, obverse/reverse','formal_award')
 'lh1emp2tcol.jpg'=@('First Empire','collar, second type','formal_award')
 'lh2rep1ar.jpg'=@('Second Republic','cross, obverse/reverse','formal_award')
 'lh2restar.jpg'=@('Second Restoration','cross, obverse/reverse','formal_award')
 'lh3repchevar.jpg'=@('Third Republic','chevalier cross, obverse/reverse','formal_award')
 'lh3repcol.jpg'=@('Third Republic','collar','formal_award')
 'lh45repscol.jpg'=@('Fourth/Fifth Republics','collar','formal_award')
 'lhcentsjoursar.jpg'=@('Hundred Days','cross, obverse/reverse','formal_award')
 'lhcoma.jpg'=@('Fifth Republic','commander cross','formal_award')
 'lhcxchevoffa.jpg'=@('Fifth Republic','chevalier/officier crosses, obverse/reverse','formal_award')
 'lheduc.jpg'=@('French educational houses','institutional education-house insignia','related_not_formal_award_variant')
 'lhgc.jpg'=@('Fifth Republic','grand cross set','formal_award')
 'lhmjar.jpg'=@('July Monarchy','cross, obverse/reverse','formal_award')
 'lhplak2emp1.jpg'=@('Second Empire','grand-cross breast star','formal_award')
 'lhplak2rep.jpg'=@('Second Republic','breast star','formal_award')
 'lhplak3repgc.jpg'=@('Third Republic','grand-cross breast star','formal_award')
 'lhplakgabrod1.jpg'=@('First Empire','embroidered breast star','formal_award')
 'lhplakgc.jpg'=@('Fourth/Fifth Republics','grand-cross breast star','formal_award')
 'lhplaklp.jpg'=@('July Monarchy','breast star','formal_award')
 'cadrelh.jpg'=@('Editorial','decorative directory header','non_object')
 'napoleongerard.jpg'=@('First Empire','portrait of Napoleon in regalia','context_only')
}

$variants=[Collections.Generic.List[object]]::new()
foreach($image in $sweep.images){
 $name=[IO.Path]::GetFileName($image.local_path)
 $class=$map[$name]
 if(-not $class){$class=@('Unmapped','unmapped image','identity_review')}
 $image|Add-Member -NotePropertyName visually_reviewed -NotePropertyValue $true -Force
 $image|Add-Member -NotePropertyName visual_result -NotePropertyValue ($(if($class[2]-eq 'formal_award'){'Complete award body or complete paired/set view in the source image; no search thumbnail or screenshot.'}elseif($class[2]-eq 'related_not_formal_award_variant'){'Complete related institutional insignia; excluded from the formal award family variants.'}else{'Not an award-object image; excluded.'})) -Force
 $image|Add-Member -NotePropertyName classification -NotePropertyValue $class[2] -Force
 if($class[2]-eq 'formal_award'){
   $page=$sweep.pages|Where-Object{$_.image_urls -contains $image.url}|Select-Object -First 1
   $variants.Add([ordered]@{
      variant_id=('FRA-LEGION-'+(($class[0]+'-'+$class[1]) -replace '[^A-Za-z0-9]+','-').Trim('-').ToUpperInvariant())
      family='FRA-LEGION-HONOUR'
      regime=$class[0]
      variant=$class[1]
      source_page=$page.url
      source_title=$page.title
      image_path=$image.local_path
      image_dimensions=@([int]$image.width,[int]$image.height)
      image_sha256=$image.sha256
      completeness='visually reviewed complete reference'
      rights='SAMLHOC all-rights-reserved research cache; not HTML eligible'
      html_eligible=$false
   })
 }
}
$sweep.status='complete_direct_subpage_sweep_and_visual_review'
$sweep|Add-Member -NotePropertyName visual_review_summary -NotePropertyValue ([ordered]@{reviewed_images=$sweep.images.Count; formal_award_images=$variants.Count; related_insignia_images=1; contextual_or_nonobject_images=2; html_eligible=0}) -Force
$sweep.next_checkpoint='The 32-page direct-child directory and 21 images are complete and cached. Normalize deeper official-text sibling pages separately; seek open-licence substitutes for the 18 formal award views.'
[IO.File]::WriteAllText($sweepPath,($sweep|ConvertTo-Json -Depth 14),[Text.UTF8Encoding]::new($false))

$normalized=[ordered]@{
 schema_version='2.0';as_of='2026-09-26';batch_id='france_legion_honour_batch1';status='normalized_research_only'
 summary=[ordered]@{source_pages=32;source_images=21;family_count=1;formal_variant_views=$variants.Count;third_republic_variant_views=@($variants|Where-Object{$_.regime -eq 'Third Republic'}).Count;second_empire_variant_views=@($variants|Where-Object{$_.regime -eq 'Second Empire'}).Count;related_or_context_images=3;html_eligible_images=0}
 families=@([ordered]@{family_id='FRA-LEGION-HONOUR';names=@("Légion d’honneur","Ordre national de la Légion d’honneur",'荣誉军团勋章');established='1802-05-19';period_rule='Single continuing family across regimes; regime models and grades are variants, not new families.';variants=$variants})
}
$conflicts=[ordered]@{schema_version='2.0';as_of='2026-09-26';batch_id='france_legion_honour_batch1';conflicts=@([ordered]@{type='RIGHTS';scope='all 21 cached media';status='held';detail='SAMLHOC states all rights reserved and no open reuse licence; none may enter public HTML from this cache.'},[ordered]@{type='COVERAGE';scope='Second Empire';status='partial';detail='The direct-child sweep exposed a Second Empire breast star image but no separate Second Empire cross object page; do not infer the missing cross from another regime.'})}
$checkpoint=[ordered]@{schema_version='2.0';as_of='2026-09-26';batch_id='france_legion_honour_batch1';completed=[ordered]@{direct_pages=32;raw_rows=32;images_downloaded_decoded_reviewed=21;formal_variant_views=18;third_republic_views=3;second_empire_views=1};html_merge=[ordered]@{performed=$false;eligible_images=0};next_position='Find open-licence substitutes for Third Republic chevalier cross/collar/star and Second Empire cross/star; preserve the one-family identity across regimes.'}
[IO.File]::WriteAllText($outPath,($normalized|ConvertTo-Json -Depth 14),[Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText($conflictPath,($conflicts|ConvertTo-Json -Depth 10),[Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText($checkpointPath,($checkpoint|ConvertTo-Json -Depth 10),[Text.UTF8Encoding]::new($false))
$normalized.summary|ConvertTo-Json
