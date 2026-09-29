$ErrorActionPreference = 'Stop'
$base = 'https://www.medals.org.uk/denmark/'
$asOf = '2026-09-29'
$batch = 'denmark_master_fast_2026-09-29'
$cacheDir = 'sources/cache/medals_org_denmark'
$rawDir = 'data/raw_candidates/denmark'
$imageDir = "assets/raw/$batch"
$null = New-Item -ItemType Directory -Force -Path $cacheDir, $rawDir, $imageDir
Add-Type -AssemblyName System.Drawing

function Get-PlainText([string]$Html) {
    $s = [regex]::Replace($Html, '(?is)<script\b.*?</script>|<style\b.*?</style>', ' ')
    $s = [regex]::Replace($s, '<[^>]+>', ' ')
    $s = [System.Net.WebUtility]::HtmlDecode($s)
    return (($s -replace '\s+', ' ').Trim())
}

function Get-ImageAttribute([string]$Tag, [string]$Name) {
    $m = [regex]::Match($Tag, '(?i)\b' + [regex]::Escape($Name) + '="([^"]*)"')
    if ($m.Success) { return [System.Net.WebUtility]::HtmlDecode($m.Groups[1].Value) }
    return ''
}

function Get-ChineseName([string]$Title) {
    $t = $Title -replace '^Kingdom of Denmark:\s*', ''
    $map = @{
        'Order of the Elephant' = '大象勋章'
        'Order of the Dannebrog' = '丹麦国旗勋章'
        'Medal of Merit' = '功绩奖章'
        'Medal for Heroic Deeds' = '英勇行为奖章'
        'Distinguished Flying Medal' = '卓越飞行服务奖章'
        'Medal for those Killed or Wounded in Service' = '因公阵亡或受伤奖章'
        'Lifesaving Medal' = '救生奖章'
        'Medal for Saving from Drowning' = '救溺奖章'
        'Ingenio et Arte Medal' = 'Ingenio et Arte艺术与科学奖章'
        'Medal of Merit of Greenland' = '格陵兰功绩奖章'
        'Medal for the Battle of Copenhagen 1801' = '哥本哈根海战奖章'
        'Commemorative War Medal of 1848-50' = '1848–1850年战争纪念奖章'
        'Commemorative War Medal of 1864' = '1864年战争纪念奖章'
        'Schleswig Medal' = '石勒苏益格纪念奖章'
        'Commemorative Medal for Aid to Prisoners of War 1914-19' = '1914–1919年战俘救助纪念奖章'
        'Commemorative Medal for Aid to Sick and Wounded of the Finnish War 1939-40' = '1939–1940年芬兰战争伤病救助纪念奖章'
        'Commemorative Medal of 9 April 1940' = '1940年4月9日纪念奖章'
        "King Christian X's Medal of Freedom" = '克里斯蒂安十世自由奖章'
        'Commemorative Medal for Service in the War 1940-45' = '1940–1945年战争服役纪念奖章'
        'Red Cross Commemorative Medal 1939-45' = '1939–1945年红十字纪念奖章'
        'Korea Medal' = '朝鲜战争奖章'
        'Red Cross Commemorative Medal for Participation in the Exchange of PoWs 1953' = '1953年战俘交换红十字纪念奖章'
        'Defence Medal' = '国防奖章'
        'International Conference on the Former Yugoslavia Medal' = '前南斯拉夫国际会议奖章'
        'Iraq Special Mission medal' = '伊拉克特别任务奖章'
        'IFOR & SFOR Police Special Performance Award' = 'IFOR／SFOR警务特别表现奖章'
        "Navy Long Service Medal" = '海军长期服役奖章'
        'Army Long Service Medal' = '陆军长期服役奖章'
        'Air Force Long Service Medal' = '空军长期服役奖章'
        'Medal for Long Service in the Department of Defence' = '国防部长期服役奖章'
        'Medal for Good Service in the Reserve Forces' = '预备役优良服役奖章'
        'Reserve Preparedness Medal' = '预备役战备奖章'
        'Long Service Cross' = '长期服役十字章'
        'Police Good Service Medal' = '警察优良服役奖章'
        'Civil Defence Good Service Medal' = '民防优良服役奖章'
        'Home Guard Good Service Medal' = '国土卫队优良服役奖章'
        "Firemen's Good Service Medal" = '消防员优良服役奖章'
        'Home Guard 40 Years Service Decoration' = '国土卫队40年服役纪念章'
        'Home Guard 25 Years Service Decoration' = '国土卫队25年服役纪念章'
        'Home Guard 50 Years Jubilee Medal' = '国土卫队50周年纪念奖章'
        'Commemorative Medal of Gold Wedding 1892' = '1892年金婚纪念奖章'
        '250th Anniversary of the Royal Guard Commemorative Medal' = '皇家卫队250周年纪念奖章'
        'Commemorative Medal of Silver Wedding 1992' = '1992年银婚纪念奖章'
        'Silver Jubilee Medal of Queen Margrethe' = '玛格丽特女王银禧纪念奖章'
        'Honour Badge of the Danish Reserve Officers Association' = '丹麦预备役军官协会荣誉章'
        'Honour Badge of the League of Civil Defence' = '民防联盟荣誉章'
        "Christian X's Medal of Recompense" = '克里斯蒂安十世酬功奖章'
        "Queen's Medal of Recompense" = '女王酬功奖章'
        'Danish National Travel Association Medal' = '丹麦国家旅游协会奖章'
        'Medal of Merit of the Chamber of Danish Handicraft' = '丹麦手工业商会功绩奖章'
        'Danish Red Cross Badge of Honour' = '丹麦红十字荣誉章'
        'Danish Red Cross Service Medal' = '丹麦红十字服役奖章'
        'DANCON March Medal' = '丹麦部队行军奖章'
        'UNEF Medal' = '联合国紧急部队奖章'
        'UNTSO Medal' = '联合国停战监督组织奖章'
        'UNMOGIP Medal' = '联合国印巴观察组奖章'
        'ONUC Medal' = '联合国刚果行动奖章'
        'UNYOM Medal' = '联合国也门观察团奖章'
        'UNFICYP Medal' = '联合国塞浦路斯维和奖章'
        'UNIIMOG Medal' = '联合国伊朗–伊拉克军事观察组奖章'
        'UNTAG Medal' = '联合国纳米比亚过渡援助团奖章'
        'UNIKOM Medal' = '联合国伊拉克–科威特观察团奖章'
        'UNPROFOR Medal' = '联合国保护部队奖章'
        'UNOMIG Medal' = '联合国格鲁吉亚观察团奖章'
        'UNMOT Medal' = '联合国塔吉克斯坦观察团奖章'
        'UNMIBH Medal' = '联合国波黑特派团奖章'
        'UNMOP Medal' = '联合国普雷夫拉卡观察团奖章'
        'UNTAES Medal' = '联合国东斯拉沃尼亚过渡行政当局奖章'
        'UNPSG Medal' = '联合国民警支持组奖章'
        'UNOMSIL Medal' = '联合国塞拉利昂观察团奖章'
    }
    if ($map.ContainsKey($t)) { return $map[$t] }
    return ('丹麦' + $t)
}

$chartFiles = @('denmark-ribbons.htm', 'denmark-ribbons2.htm')
$pageNames = [System.Collections.Generic.List[string]]::new()
$chartSummaries = [System.Collections.Generic.List[object]]::new()
foreach ($chart in $chartFiles) {
    $url = $base + $chart
    $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 30
    $chartCache = Join-Path $cacheDir $chart
    [System.IO.File]::WriteAllText((Join-Path (Get-Location) $chartCache), $response.Content, [System.Text.UTF8Encoding]::new($false))
    $links = @()
    foreach ($m in [regex]::Matches($response.Content, 'href="(denmark\d+\.htm)"')) {
        $n = $m.Groups[1].Value
        if (-not $pageNames.Contains($n)) { $pageNames.Add($n) }
        $links += $n
    }
    $chartSummaries.Add([pscustomobject]@{source_page=$url; pages=$links.Count; page_ids=$links})
}

$pageCandidates = [System.Collections.Generic.List[object]]::new()
$pageOrdinal = 0
foreach ($page in $pageNames) {
    $pageOrdinal++
    $url = $base + $page
    try {
        $response = Invoke-WebRequest -Uri $url -Headers @{'User-Agent'='WorldMedalsCatalogue/1.0 (local research; low-rate catalogue sweep)'} -UseBasicParsing -TimeoutSec 30
        [System.IO.File]::WriteAllText((Join-Path (Get-Location) (Join-Path $cacheDir $page)), $response.Content, [System.Text.UTF8Encoding]::new($false))
        $title = [System.Net.WebUtility]::HtmlDecode([regex]::Match($response.Content, '<title>(.*?)</title>', 'Singleline').Groups[1].Value).Trim()
        $plain = Get-PlainText $response.Content
        $awardName = ($title -replace '^ODM of Denmark:\s*', '').Trim()
        $institution = [regex]::Match($plain, 'Instituted:\s*(.*?)(?:\.\s*Awarded:|\.\s*Grades:|$)', 'IgnoreCase').Groups[1].Value.Trim()
        if (-not $institution) { $institution = [regex]::Match($plain, 'Established:\s*(.*?)(?:\.\s*Awarded:|$)', 'IgnoreCase').Groups[1].Value.Trim() }
        $dates = if ($institution) { '设立 ' + $institution } else { '待考' }
        $imgs = [System.Collections.Generic.List[object]]::new()
        foreach ($im in [regex]::Matches($response.Content, '<img\b[^>]*>', 'IgnoreCase')) {
            $tag = $im.Value
            $src = Get-ImageAttribute $tag 'src'
            if (-not $src) { continue }
            $alt = Get-ImageAttribute $tag 'alt'
            $widthText = Get-ImageAttribute $tag 'width'
            $heightText = Get-ImageAttribute $tag 'height'
            $width = if ($widthText) { [int]$widthText } else { 0 }
            $height = if ($heightText) { [int]$heightText } else { 0 }
            $isRibbon = ($src -match '(?i)r\.(gif|jpg|jpeg|png)$') -or ($alt -match '(?i)ribbon') -or (($width -le 110) -and ($height -le 40))
            if ($isRibbon) { continue }
            if ($alt -match '(?i)portrait|coat of arms|flag|case|box|certificate|ribbon bar|reverse') { continue }
            $imgUrl = [uri]::new([uri]$url, $src).AbsoluteUri
            $label = if ($alt) { $alt } else { '主图（目录未注明视面）' }
            $imgs.Add([pscustomobject]@{image_url=$imgUrl; image_page_url=$url; page_id=$page; alt=$label; width_hint=$width; height_hint=$height})
        }
        $pageCandidates.Add([pscustomobject]@{
            ordinal=$pageOrdinal
            source_id='DK-MEDALS-ORG-DIRECTORY'
            source_page_title=$title
            original_name=$awardName
            name_zh=(Get-ChineseName $awardName)
            date_candidate=$dates
            category=if ($awardName -match '(?i)order') {'order'} else {'medal_or_decoration'}
            grade_variant_clues=($imgs | ForEach-Object {$_.alt})
            object_page_url=$url
            text_excerpt=$plain.Substring(0, [Math]::Min(900, $plain.Length))
            image_candidates=$imgs.ToArray()
            status=if ($imgs.Count) {'SOURCE_CANDIDATE_IMAGE_PRESENT'} else {'SOURCE_CANDIDATE_UNPICTURED'}
            rights='本对象页未显示图片许可；仅供本地研究缓存，待逐图核权'
        })
    } catch {
        $pageCandidates.Add([pscustomobject]@{ordinal=$pageOrdinal;source_id='DK-MEDALS-ORG-DIRECTORY';source_page_title=$page;original_name='';name_zh='';date_candidate='待考';category='unresolved';grade_variant_clues=@();object_page_url=$url;text_excerpt='页面访问失败：'+$_.Exception.Message;image_candidates=@();status='FETCH_FAILED';rights='unknown'})
    }
    Start-Sleep -Milliseconds 180
}

$rawPath = Join-Path $rawDir 'medals_org_denmark_full_directory_2026-09-29.jsonl'
$rawLines = [System.Collections.Generic.List[string]]::new()
$volumeRows = [System.Collections.Generic.List[object]]::new()
$manifestImages = [System.Collections.Generic.List[object]]::new()
$seenImageUrls = @{}
$familyOrdinal = 0
foreach ($candidate in $pageCandidates) {
    $imageEntries = @($candidate.image_candidates)
    foreach ($image in $imageEntries) {
        $rawLines.Add(($candidate | Select-Object -ExcludeProperty image_candidates | Add-Member -NotePropertyName image_candidate -NotePropertyValue $image -PassThru | ConvertTo-Json -Depth 8 -Compress))
    }
    if ($volumeRows.Count -ge 28) { continue }
    if ($imageEntries.Count -eq 0) { continue }
    $image = $imageEntries[0]
    if ($seenImageUrls.ContainsKey($image.image_url)) { continue }
    $seenImageUrls[$image.image_url] = $true
    $familyOrdinal++
    $familyId = 'DK-MO-' + ('{0:d3}' -f $candidate.ordinal)
    $safe = (($candidate.original_name -replace '[^A-Za-z0-9]+','-').Trim('-').ToLower())
    if (-not $safe) { $safe = 'award-' + $candidate.ordinal }
    $ext = [System.IO.Path]::GetExtension(([uri]$image.image_url).AbsolutePath)
    if (-not $ext) { $ext = '.jpg' }
    $viewKey = $familyId + '-V01'
    $localPath = Join-Path $imageDir ($safe + $ext.ToLower())
    $downloadStatus = 'DOWNLOAD_FAILED'
    $width = 0; $height = 0; $bytes = 0; $sha256 = ''
    try {
        $imgResponse = Invoke-WebRequest -Uri $image.image_url -Headers @{'User-Agent'='WorldMedalsCatalogue/1.0 (local research; low-rate image download)'} -OutFile $localPath -PassThru -TimeoutSec 35
        $file = Get-Item $localPath
        $bytes = $file.Length
        $decoded = [System.Drawing.Image]::FromFile($file.FullName)
        $width = $decoded.Width; $height = $decoded.Height; $decoded.Dispose()
        $sha256 = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLower()
        $downloadStatus = 'DOWNLOADED_DECODED'
    } catch {
        $downloadStatus = 'DOWNLOAD_OR_DECODE_FAILED: ' + $_.Exception.Message
        if (Test-Path -LiteralPath $localPath) { Remove-Item -LiteralPath $localPath -Force }
    }
    if ($downloadStatus -eq 'DOWNLOADED_DECODED') {
        $kind = if (($width -le 400) -or ($height -le 400)) {'专业目录低清图式；未作插值'} else {'专业目录图像；待作逐图实物／绘图分类'}
        $variant = if ($image.alt -match '(?i)obverse|front') { '正面图式；' + $image.alt } else { '目录主图；' + $image.alt }
        $variant += '；' + $kind + '；材质待考'
        $views = @([pscustomobject]@{key=$viewKey;label='完整正面图式'})
        $volumeRows.Add([pscustomobject]@{
            id=$familyId
            family=$familyId
            name=$candidate.name_zh
            original=$candidate.original_name
            date=$candidate.date_candidate
            variant=$variant
            views=$views
            source_ids=@('DK-MEDALS-ORG-DIRECTORY','DK-COURT-HONOURS-LIST','DK-WIKIPEDIA-DENMARK-HONOURS')
        })
        $manifestImages.Add([pscustomobject]@{
            view_key=$viewKey; local_path=$localPath.Replace('\','/'); source_page=$candidate.object_page_url; image_page=$image.image_page_url; original_url=$image.image_url
            source_image_label=$image.alt; width=$width; height=$height; bytes=$bytes; sha256=$sha256; content_type=$imgResponse.Headers['Content-Type']
            image_kind=$kind; author_or_institution='Medals.org.uk目录，个人图片作者未标'; license='未标示；本地研究副本，不作公开发布'; downloaded=$asOf
        })
    }
    Start-Sleep -Milliseconds 220
}
foreach ($candidate in $pageCandidates) {
    if ($candidate.image_candidates.Count -eq 0) {
        $rawLines.Add(($candidate | Select-Object -ExcludeProperty image_candidates | ConvertTo-Json -Depth 8 -Compress))
    }
}
[System.IO.File]::WriteAllLines((Join-Path (Get-Location) $rawPath), $rawLines, [System.Text.UTF8Encoding]::new($false))

$sourceNotes = @(
    [pscustomobject]@{source_id='DK-MEDALS-ORG-DIRECTORY';source_name='Medals of the World — Denmark ribbon charts and linked object pages';base_url='https://www.medals.org.uk/denmark/denmark-ribbons.htm';source_type='specialist_catalogue_full_directory';languages=@('en');date_coverage='Medal establishment dates and service-period clues as stated on individual catalogue pages';content_coverage=('{0} linked detail pages from two ribbon-chart indexes fetched and cached; {1} image-bearing page candidates; {2} complete images downloaded and decoded; other candidates remain raw/unpictured.' -f $pageNames.Count,(@($pageCandidates|Where-Object {$_.image_candidates.Count -gt 0}).Count),$volumeRows.Count);has_images=$true;image_quality_notes='The selected original directory images are complete page-embedded object drawings/illustrations or photos; visual medium is marked per dimensions and remains subject to visual review; small originals are explicitly low-resolution.';has_pagination=$true;download_method='Two ribbon-chart pages followed to all linked denmarkNNN.htm detail pages; direct original image paths downloaded from the same site with rate-limited sequential requests.';priority=1;status=if($pageCandidates.Count -eq $pageNames.Count -and $volumeRows.Count -ge 20){'completed_first_ingest'}else{'partial'};last_checked=$asOf;local_cache=$cacheDir;rights_note='No per-image license statement found on the catalogue pages. Keep local for research only pending rights review.'},
    [pscustomobject]@{source_id='DK-COURT-HONOURS-LIST';source_name='Kongehuset — Danish decorations in order of precedence';base_url='https://www.kongehuset.dk/monarkiet-i-danmark/ordener-og-medaljer/danske-dekorationers-indbyrdes-raekkefoelge/';source_type='official_awards_list';languages=@('da');date_coverage='Institution, approval and service-eligibility dates for royal, public, military and approved decorations';content_coverage='Official list opened and checked for grade descriptions and dates. It supports a selection of award identities but does not constitute a full historical directory.';has_images=$false;image_quality_notes='No image batch collected from this source.';has_pagination=$false;download_method='Official web page opened and relevant sections reviewed.';priority=1;status='partially_reviewed';last_checked=$asOf;local_cache='web capture only';rights_note='Official facts page; no image rights implicated.'},
    [pscustomobject]@{source_id='DK-WIKIPEDIA-DENMARK-HONOURS';source_name='Orders, decorations, and medals of Denmark; Wikimedia Commons Denmark medal categories';base_url='https://en.wikipedia.org/wiki/Orders,_decorations,_and_medals_of_Denmark';source_type='multilingual_directory_and_commons_category';languages=@('en','da','nl');date_coverage='Historical and current award family discovery';content_coverage='English main table opened; Commons Medals of Denmark category lists 33 subcategories and 66 direct files; 17 subcategory pages were opened for triage. Commons API returned HTTP 429 and was stopped. No Commons image files were added in this batch.';has_images=$true;image_quality_notes='Several direct files are low-resolution schematic illustrations; many subcategories contain unrelated historical commemorative pieces. They are not counted in this batch.';has_pagination=$true;download_method='Public category pages via browser; direct image API was unavailable due to 429.';priority=2;status='partial';last_checked=$asOf;local_cache='Web access only; category names/counts recorded in checkpoint.';rights_note='Per-file rights must be checked on each Commons object page before any reuse.'}
)

$volume = [pscustomobject]@{as_of=$asOf;volume='丹麦王国勋章与国家奖章首批目录图像包';records=$volumeRows.ToArray()}
$manifest = [pscustomobject]@{as_of=$asOf;volume=$volume.volume;batch_id=$batch;scope='丹麦王国 formal honours first image-bearing directory batch';sources=$sourceNotes;images=$manifestImages.ToArray();rights='Medals.org.uk pages do not state item-level image licenses; downloaded copies are retained locally for research, not marked as redistributable.';validation=[pscustomobject]@{record_count=$volumeRows.Count;decoded_image_count=$manifestImages.Count;all_images_exist=(@($manifestImages|Where-Object {-not (Test-Path -LiteralPath $_.local_path)}).Count -eq 0);all_decoded=($manifestImages.Count -eq $volumeRows.Count);public_html_touched=$false;site_build_touched=$false}}
[System.IO.File]::WriteAllText((Join-Path (Get-Location) "data/volumes/$batch.json"), ($volume | ConvertTo-Json -Depth 10), [System.Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllText((Join-Path (Get-Location) "data/volumes/${batch}_manifest.json"), ($manifest | ConvertTo-Json -Depth 10), [System.Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllText((Join-Path (Get-Location) 'data/source_atlas/denmark_source_matrix.json'), ([pscustomobject]@{schema_version='2.0';as_of=$asOf;scope_id='denmark_master_fast';scope_label='Kingdom of Denmark — source-first national honours directory batch';languages=@('da','en','nl');existing_coverage=@{volumes_checked=@{files_checked=@('No earlier Denmark volume, candidate, checkpoint or image manifest found in data/volumes; image_manifest.json showed no Denmark batch.')};deduplication='No existing Denmark volume found; family-level cross-check against data/volumes and global volume names remains required by parent before site merge.'};sources=$sourceNotes;scan_counts=@{planned_sources=3;completed_sources=1;partial_sources=2;unstarted_sources=0;raw_candidates=$rawLines.Count;image_bearing_detail_pages=@($pageCandidates|Where-Object {$_.image_candidates.Count -gt 0}).Count;merged_families=$volumeRows.Count;body_families=0;variants=$volumeRows.Count;local_images=$manifestImages.Count;unresolved_pages=@($pageCandidates|Where-Object {$_.status -eq 'FETCH_FAILED'}).Count};next_actions=@('Review local sheet of 20+ directory images to mark drawing versus specimen photograph per item.','Check whether Greenland subrange should be a separate award authority; do not duplicate those families under Denmark.','Resume Commons subcategory image metadata only after rate limit clears and only for distinct gaps.','Check additional Danish statutes / sources before merging to body and after parent deduplicates.') } | ConvertTo-Json -Depth 9), [System.Text.UTF8Encoding]::new($false))
$checkpoint = [pscustomobject]@{checkpoint_id=$batch;as_of=$asOf;scope='丹麦国家奖励体系快速总目录与首批配图';plan=@('扫完medals.org.uk丹麦两页 ribbon chart和所有链接对象页','与现有丹麦卷做差集','至少取得20个独立章种/主要等级的完整本地图','保存raw、volume/manifest、matrix与checkpoint；不改公共HTML/site_build/validate_site');source_counts=@{planned=3;completed=1;partial=2;not_started=0};counts=@{chart_detail_pages_listed=$pageNames.Count;detail_pages_fetched=$pageCandidates.Count;raw_candidates=$rawLines.Count;image_bearing_detail_pages=@($pageCandidates|Where-Object {$_.image_candidates.Count -gt 0}).Count;merged_families=$volumeRows.Count;body_families=0;variants=$volumeRows.Count;decoded_local_images=$manifestImages.Count;unresolved_pages=@($pageCandidates|Where-Object {$_.status -eq 'FETCH_FAILED'}).Count};files=@($rawPath,"data/volumes/$batch.json","data/volumes/${batch}_manifest.json",'data/source_atlas/denmark_source_matrix.json',"assets/raw/$batch/",$cacheDir);status=if($volumeRows.Count -ge 20 -and $pageCandidates.Count -eq $pageNames.Count){'first_batch_complete_directory_sweep'}else{'partial'};next_action='主任务逐图复核图像性质和rights，将图式与实物照片分开；继续补齐遗漏/未配图并查重后方可合并公共HTML。';site_build_touched=$false;public_html_touched=$false;notes='图像源版权未知；只保留本地研究，不得据此公开分发。'}
[System.IO.File]::WriteAllText((Join-Path (Get-Location) "data/checkpoints/${batch}.json"), ($checkpoint | ConvertTo-Json -Depth 10), [System.Text.UTF8Encoding]::new($false))
Write-Output (([pscustomobject]@{charts=$chartSummaries;detail_pages_listed=$pageNames.Count;detail_pages_fetched=$pageCandidates.Count;raw_candidates=$rawLines.Count;image_bearing_pages=@($pageCandidates|Where-Object {$_.image_candidates.Count -gt 0}).Count;volume_rows=$volumeRows.Count;decoded_images=$manifestImages.Count;unresolved=@($pageCandidates|Where-Object {$_.status -eq 'FETCH_FAILED'}).Count;output_volume="data/volumes/$batch.json";output_manifest="data/volumes/${batch}_manifest.json";matrix='data/source_atlas/denmark_source_matrix.json';checkpoint="data/checkpoints/${batch}.json"} | ConvertTo-Json -Depth 5))
