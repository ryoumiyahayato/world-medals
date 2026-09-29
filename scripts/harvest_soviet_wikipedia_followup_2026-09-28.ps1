# Isolated follow-up harvest for unresolved Soviet Wikipedia master candidates.
# Writes only follow-up source cache, raw candidates, volume/manifest, conflicts and images.
$ErrorActionPreference = 'Stop'
$root = (Get-Location).Path
$asOf = '2026-09-28'
$imgDir = Join-Path $root 'assets/images/soviet_wikipedia_master_followup_2026-09-28'
$srcDir = Join-Path $root 'sources/pages'
$rawDir = Join-Path $root 'data/raw_candidates'
$volDir = Join-Path $root 'data/volumes'
$confDir = Join-Path $root 'data/conflicts'
foreach ($d in @($imgDir,$srcDir,$rawDir,$volDir,$confDir)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }

$masterUrl = 'https://en.wikipedia.org/wiki/Orders,_decorations,_and_medals_of_the_Soviet_Union'
$commonsApi = 'https://commons.wikimedia.org/w/api.php'
$downloadMap = @(
  @{ family='USSR-MED-55'; variant='V-I'; file='MBezuprSlA.jpg'; name='无瑕服役奖章'; original='Medal For Impeccable Service / Медаль «За безупречную службу»'; date='1958-01-25'; section='Military medals — General'; level='一级；完整正面实物图' },
  @{ family='USSR-MED-55'; variant='V-II'; file='USSR15yearsofservice.jpg'; name='无瑕服役奖章'; original='Medal For Impeccable Service / Медаль «За безупречную службу»'; date='1958-01-25'; section='Military medals — General'; level='二级；完整正面实物图' },
  @{ family='USSR-MED-55'; variant='V-III'; file='MBezuprSlC.jpg'; name='无瑕服役奖章'; original='Medal For Impeccable Service / Медаль «За безупречную службу»'; date='1958-01-25'; section='Military medals — General'; level='三级；完整正面实物图' },
  @{ family='USSR-MED-40'; variant='V-LABOUR'; file='100 years Lenin OBVERSE.jpg'; name='纪念列宁诞辰一百周年奖章'; original="Jubilee Medal for the 100th Anniversary of Lenin Birth / Юбилейная медаль «В ознаменование 100-летия со дня рождения В. И. Ленина»"; date='1969-11-05'; section='Other commemorative medals'; level='劳动英勇版；总表图片为共同章体正面，具体资格由来源文字区分' },
  @{ family='USSR-MED-08'; variant='V-II-COMMONS'; file='Medal Partisan of the Patriotic War 2nd class OBVERSE.jpg'; name='卫国战争游击队员奖章'; original='Medal Partisan of the Patriotic War / Медаль «Партизану Отечественной войны»'; date='1943-02-02'; section='Military medals — General'; level='二级；独立Commons正面文件' },
  @{ family='USSR-MED-10'; variant='V-II-COMMONS'; file='Soviet For Distinction in Military Service 2nd class.jpg'; name='军事服役优异奖章'; original='Medal For Distinction in Military Service / Медаль «За отличие в воинской службе»'; date='1974-10-28'; section='Military medals — General'; level='二级；独立Commons正面文件' },
  @{ family='USSR-MED-54'; variant='V-II-COMMONS'; file='Motherhood Medal1.JPG'; name='母亲奖章'; original='Maternity Medal / Медаль Материнства'; date='1944-07-08'; section='Maternity medals'; level='二级；独立Commons正面文件' },
  @{ family='USSR-HON-04'; variant='V01'; file='Заслуженный летчик-испытатель СССР.jpg'; name='苏联功勋试飞员徽章'; original='Honoured Test Pilot of the USSR / Заслуженный лётчик-испытатель СССР'; date='1958-08-14'; section='Honorary titles'; level='荣誉称号佩饰；完整正面徽章（带绶带）' },
  @{ family='USSR-HON-05'; variant='V01'; file='Заслуженный Штурман-Испытаетль.jpg'; name='苏联功勋试飞领航员徽章'; original='Honoured Test Navigator of the USSR / Заслуженный штурман-испытатель СССР'; date='1958-08-14'; section='Honorary titles'; level='荣誉称号佩饰；完整正面徽章（带绶带）' },
  @{ family='USSR-HON-06'; variant='V01'; file='Pilot-Cosmonaut of the USSR.jpg'; name='苏联宇航员徽章'; original='Pilot-Cosmonaut of the USSR / Лётчик-космонавт СССР'; date='1961-04-14'; section='Honorary titles'; level='荣誉称号佩饰；完整正面徽章（带绶带）' },
  @{ family='USSR-HON-07'; variant='V01'; file='Distinguished Military Pilot Of The Soviet Union.jpg'; name='苏联功勋军事飞行员徽章'; original='Honoured Military Pilot of the USSR / Заслуженный военный лётчик СССР'; date='1965-01-26'; section='Honorary titles'; level='荣誉称号佩饰；完整正面徽章（带绶带）' },
  @{ family='USSR-HON-08'; variant='V01'; file='Distinguished Military Navigator Of The Soviet Union.jpg'; name='苏联功勋军事领航员徽章'; original='Honoured Military Navigator of the USSR / Заслуженный военный штурман СССР'; date='1965-01-26'; section='Honorary titles'; level='荣誉称号佩饰；完整正面徽章（带绶带）' },
  @{ family='USSR-HON-09'; variant='V01'; file='Distinguished Pilot Of The Soviet Union.jpg'; name='苏联功勋飞行员徽章'; original='Honoured Pilot of the USSR / Заслуженный пилот СССР'; date='1965-09-30'; section='Honorary titles'; level='荣誉称号佩饰；完整正面徽章（带绶带）' },
  @{ family='USSR-HON-10'; variant='V01'; file='Zasl Shturman USSR.png'; name='苏联功勋领航员徽章'; original='Honoured Navigator of the USSR / Заслуженный штурман СССР'; date='1965-09-30'; section='Honorary titles'; level='荣誉称号佩饰；完整正面徽章（带绶带）' },
  @{ family='USSR-HON-11'; variant='V01'; file='Distinguished Inventor Of The Soviet Union.jpg'; name='苏联功勋发明家徽章'; original='Honoured Inventor of the USSR / Заслуженный изобретатель СССР'; date='1981-12-28'; section='Honorary titles'; level='荣誉称号佩饰；完整正面徽章（带绶带）' },
  @{ family='USSR-HON-12'; variant='V01'; file="People's Doctor of the Soviet Union.png"; name='苏联人民医生徽章'; original="People's Doctor of the USSR / Народный врач СССР"; date='1977-10-25'; section='Honorary titles'; level='荣誉称号佩饰；完整正面徽章（带绶带）' },
  @{ family='USSR-HON-13'; variant='V01'; file="People's Architect of the USSR.png"; name='苏联人民建筑师徽章'; original="People's Architect of the USSR / Народный архитектор СССР"; date='1967-08-12'; section='Honorary titles'; level='荣誉称号佩饰；完整正面徽章（带绶带）' },
  @{ family='USSR-HON-14'; variant='V01'; file="People's teacher of the Soviet Union.png"; name='苏联人民教师徽章'; original="People's Teacher of the USSR / Народный учитель СССР"; date='1977-12-30'; section='Honorary titles'; level='荣誉称号佩饰；完整正面徽章（带绶带）' },
  @{ family='USSR-HON-15'; variant='V01'; file='People Artist of the USSR1.jpg'; name='苏联人民艺术家徽章'; original="People's Artist of the USSR / Народный артист СССР"; date='1937-01-13'; section='Honorary titles'; level='荣誉称号佩饰；完整正面徽章（带绶带）' },
  @{ family='USSR-HON-16'; variant='V01'; file='Народный художник СССР.jpg'; name='苏联人民画家徽章'; original="People's Painter of the USSR / Народный художник СССР"; date='1943-07-16'; section='Honorary titles'; level='荣誉称号佩饰；完整正面徽章（带绶带）' }
)

function Get-ApiMetadata([string[]]$files) {
  $titles = ($files | ForEach-Object { 'File:' + $_ }) -join '|'
  $u = $commonsApi + '?action=query&format=json&formatversion=2&prop=imageinfo&iiprop=url|size|mime|sha1|extmetadata&iiurlwidth=1600&titles=' + [uri]::EscapeDataString($titles)
  return (Invoke-RestMethod -Uri $u -UseBasicParsing -TimeoutSec 60).query.pages
}

# Batch API queries in <=50 titles as required by Commons API conventions.
$allMeta = @()
for ($i=0; $i -lt $downloadMap.Count; $i += 50) {
  $end = [Math]::Min($i + 49, $downloadMap.Count - 1)
  $batch = @($downloadMap[$i..$end].file)
  try { $allMeta += @(Get-ApiMetadata $batch) } catch { Write-Warning ('Commons metadata batch failed: ' + $_.Exception.Message) }
}
$metaByFile = @{}
foreach ($p in $allMeta) { if ($p.imageinfo) { $metaByFile[$p.title.Substring(5)] = $p } }
$metaPath = Join-Path $srcDir 'soviet_followup_commons_metadata_2026-09-28.json'
@{ source_url=$commonsApi; access_date=$asOf; files=$allMeta; note='Metadata queried in Commons API batches of <=50 titles; direct downloads use Special:FilePath when upload CDN is rate-limited.' } | ConvertTo-Json -Depth 15 | Set-Content -Encoding UTF8 $metaPath

$rawPath = Join-Path $rawDir 'soviet_wikipedia_master_followup_2026-09-28.jsonl'
if (Test-Path $rawPath) { Remove-Item -LiteralPath $rawPath -Force }
$records = @()
$manifest = @()
$rejected = @()
$manifestRelDir = 'assets/images/soviet_wikipedia_master_followup_2026-09-28'

foreach ($d in $downloadMap) {
  $safe = ($d.file -replace '[^\p{L}\p{Nd}._-]','_')
  $local = Join-Path $imgDir ($d.family + '-' + $d.variant + '-' + $safe)
  $fileUrl = 'https://commons.wikimedia.org/wiki/Special:FilePath/' + [uri]::EscapeDataString($d.file)
  $pageUrl = 'https://commons.wikimedia.org/wiki/File:' + [uri]::EscapeDataString($d.file)
  $p = $metaByFile[$d.file]
  if (-not $p -or -not $p.imageinfo) { $rejected += @{family=$d.family;file_title=$d.file;reason='Commons API did not resolve file'}; continue }
  try {
    Invoke-WebRequest -Uri $fileUrl -UseBasicParsing -OutFile $local -TimeoutSec 60 -MaximumRedirection 5
    Add-Type -AssemblyName System.Drawing
    $im = [Drawing.Image]::FromFile($local)
    $w = $im.Width; $h = $im.Height; $im.Dispose()
    if ($w -lt 100 -or $h -lt 100) { throw ('decoded image too small: ' + $w + 'x' + $h) }
  } catch {
    if (Test-Path $local) { Remove-Item -LiteralPath $local -Force }
    $rejected += @{family=$d.family;file_title=$d.file;reason=('download/decode failed: ' + $_.Exception.Message)}
    continue
  }
  $ii = $p.imageinfo[0]
  $em = $ii.extmetadata
  $author = if ($em.Artist.value) { [string]$em.Artist.value } else { $null }
  $lic = if ($em.LicenseShortName.value) { [string]$em.LicenseShortName.value } else { $null }
  $sha = (Get-FileHash -Algorithm SHA256 -LiteralPath $local).Hash.ToLowerInvariant()
  $raw = [ordered]@{ source_id='soviet_wikipedia_master_followup_2026-09-28'; source_row=$null; table_section=$d.section; page_title=$d.original; date_candidate=$d.date; image_files=@($d.file); image_page_urls=@($pageUrl); source_page_url=$masterUrl; candidate_family_id=$d.family; status='downloaded_complete_front'; note='Follow-up from the Wikipedia master candidate universe; verified Commons file page and locally decoded full front.' }
  ($raw | ConvertTo-Json -Compress -Depth 10) | Add-Content -Encoding UTF8 $rawPath
  $rec = [ordered]@{
    id=($d.family + '-' + $d.variant + '-FOLLOWUP'); family=$d.family; country_zh='苏联'; period='苏联（1922–1991）'; name=$d.name; original=$d.original; date=($d.date + '设立（Wikipedia总表日期；非具体实物颁发日）'); variant=($d.level + '；来源图像实际对应本行；生产版型／制造商待考'); views=@([ordered]@{key=('USSR-FOLLOWUP-' + $d.family + '-' + $d.variant + '-FRONT');label='完整正面；Commons文件页原图'}); source_ids=@($masterUrl,$pageUrl); source_evidence=[ordered]@{wikipedia_table_section=$d.section; wikipedia_image_file=('File:' + $d.file); commons_file_page=$pageUrl; commons_direct_url=$fileUrl; commons_sha1=$ii.sha1; access_date=$asOf; image_type='Commons object image; complete front candidate'; author=$author; license=$lic}
  }
  $records += $rec
  $manifest += [ordered]@{asset_id=($d.family + '-' + $d.variant + '-FRONT');family=$d.family;variant_id=($d.family + '-' + $d.variant + '-FOLLOWUP');view_key=('USSR-FOLLOWUP-' + $d.family + '-' + $d.variant + '-FRONT');local_path=($manifestRelDir + '/' + [IO.Path]::GetFileName($local));source_page_url=$pageUrl;source_master_page=$masterUrl;original_image_url=$ii.url;download_url=$fileUrl;file_title=('File:' + $d.file);sha256=$sha;width=[int]$w;height=[int]$h;mime=[string]$ii.mime;author=$author;license=$lic;rights_note='Commons metadata captured at access date; verify publication rights before redistribution.';view_assessment='complete front object image; low-resolution reference where long edge is below 1200px; medal/badge body and suspension structure visible; not ribbon-only, certificate, person-only, box-only, or back-only'}
}

$vol = [ordered]@{as_of=$asOf;volume='苏联：Wikipedia总表剩余差集补图（MED-40/MED-55、独立等级及荣誉称号佩饰）';scope='仅收录主批已合入52行之外、由Wikipedia总表候选指向的独立完整正面图；优先奖章，另保留总表中的正式荣誉称号佩饰。';source_table=$masterUrl;source_snapshot='sources/pages/soviet_wikipedia_master_2026-09-28.wikitext';candidate_universe_rows=112;previous_batch_volume='data/volumes/soviet_wikipedia_master_differential_2026-09-28.json';records=$records;counts=[ordered]@{records=$records.Count;families=(@($records.family|Sort-Object -Unique)).Count;complete_local_images=$manifest.Count;rejected_or_unresolved=$rejected.Count};notes=@('Commons API metadata was queried in a batch <=50 titles; direct Special:FilePath downloads were decoded locally.','MED-40 image is one shared obverse for the three qualification descriptions in the Wikipedia table; only the labour qualification is represented here to avoid duplicating the same object image across levels.','Rows marked COMMONS are independent file objects, added only where the main awards.wiki image was generic or absent.','Honorary-title rows are badges/佩饰 from the master table, not ordinary qualification certificates; any non-object or person-only image would be excluded.')}
$vol | ConvertTo-Json -Depth 20 | Set-Content -Encoding UTF8 (Join-Path $volDir 'soviet_wikipedia_master_followup_2026-09-28.json')
$man = [ordered]@{as_of=$asOf;volume='soviet_wikipedia_master_followup_2026-09-28';images=$manifest;counts=[ordered]@{images=$manifest.Count;local_unique_images=(@($manifest.local_path|Sort-Object -Unique)).Count};notes=@('All images are local decoded files and local_path is relative to the project root.','Original Commons URLs, file pages, dimensions, SHA-256 and rights metadata are retained.','All rows are low-resolution references when their long edge is below 1200px; no interpolation is claimed.','No generated, search-preview, ribbon-only, certificate, person-only, box-only, or back-only image is included.')}
$man | ConvertTo-Json -Depth 20 | Set-Content -Encoding UTF8 (Join-Path $volDir 'soviet_wikipedia_master_followup_2026-09-28_manifest.json')
@{as_of=$asOf;scope='follow-up unresolved/excluded candidates';unresolved_or_excluded=$rejected;note='Failed or unresolved candidates remain outside正文 records.'} | ConvertTo-Json -Depth 12 | Set-Content -Encoding UTF8 (Join-Path $confDir 'soviet_wikipedia_master_followup_exclusions_2026-09-28.json')
Write-Output ('followup records=' + $records.Count + ' families=' + (@($records.family|Sort-Object -Unique)).Count + ' images=' + $manifest.Count + ' rejected=' + $rejected.Count)
