$ErrorActionPreference = "Stop"

# Isolated source-first batch.  It writes only the Soviet Wikipedia master
# snapshot, raw candidates, a differential volume/manifest, and its image
# cache; it never touches index.html, site_build.py, or validators.
$root = Split-Path -Parent $PSScriptRoot
$asOf = "2026-09-28"
$wikiUrl = "https://en.wikipedia.org/wiki/Orders,_decorations,_and_medals_of_the_Soviet_Union"
$wikiApi = "https://en.wikipedia.org/w/api.php?action=parse&page=Orders%2C_decorations%2C_and_medals_of_the_Soviet_Union&prop=wikitext|revid&format=json&formatversion=2"
$pageDir = Join-Path $root "sources/pages"
$cacheDir = Join-Path $root "sources/cache/soviet_wikipedia_master_2026-09-28"
$imageDir = Join-Path $root "assets/images/soviet_wikipedia_master_awards_wiki_2026-09-28"
$rawDir = Join-Path $root "assets/raw/soviet_wikipedia_master_2026-09-28"
$candidateDir = Join-Path $root "data/raw_candidates"
$volumeDir = Join-Path $root "data/volumes"
$conflictDir = Join-Path $root "data/conflicts"
foreach ($d in @($pageDir,$cacheDir,$imageDir,$rawDir,$candidateDir,$volumeDir,$conflictDir)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }

$wikiWikitextPath = Join-Path $pageDir "soviet_wikipedia_master_2026-09-28.wikitext"
$wikiHtmlPath = Join-Path $pageDir "soviet_wikipedia_master_2026-09-28.html"
$snapshotMetaPath = Join-Path $pageDir "soviet_wikipedia_master_2026-09-28.json"
$rawPath = Join-Path $candidateDir "soviet_wikipedia_master_2026-09-28.jsonl"
$volumePath = Join-Path $volumeDir "soviet_wikipedia_master_differential_2026-09-28.json"
$manifestPath = Join-Path $volumeDir "soviet_wikipedia_master_differential_2026-09-28_manifest.json"
$exclusionPath = Join-Path $conflictDir "soviet_wikipedia_master_exclusions_2026-09-28.json"
$apiCachePath = Join-Path $cacheDir "page_metadata.json"

$headers = @{ "User-Agent" = "world-medals-research/1.0 (offline catalogue; source-first batch)" }
if (-not (Test-Path $wikiWikitextPath)) {
    $page = Invoke-RestMethod -Uri $wikiApi -Headers $headers -TimeoutSec 90
    [System.IO.File]::WriteAllText($wikiWikitextPath, [string]$page.parse.wikitext, [Text.UTF8Encoding]::new($false))
    $meta = [ordered]@{
        source_url = $wikiUrl
        api_url = $wikiApi
        page_title = "Orders, decorations, and medals of the Soviet Union"
        revision_id = $page.parse.revid
        fetched_at = (Get-Date).ToString("o")
        access_date = $asOf
        source_type = "Wikipedia table / MediaWiki API wikitext"
    }
    [System.IO.File]::WriteAllText($snapshotMetaPath, ($meta | ConvertTo-Json -Depth 6), [Text.UTF8Encoding]::new($false))
}
$htmlUrl = $wikiUrl + "?oldformat=true"
if (-not (Test-Path $wikiHtmlPath)) {
    Invoke-WebRequest -Uri $htmlUrl -Headers $headers -OutFile $wikiHtmlPath -TimeoutSec 90 | Out-Null
}

# The formal 24 already represented in the project at the start of this
# batch.  Candidate IDs are kept stable across the older Russian directory
# and the new Wikipedia table.  ORD-20 is deliberately not here: the prior
# source sweep had only a pending candidate and no formal body image row.
$existingFamilies = @(
    "USSR-ORD-01","USSR-ORD-02","USSR-ORD-03","USSR-ORD-04","USSR-ORD-05",
    "USSR-ORD-07","USSR-ORD-08","USSR-ORD-09","USSR-ORD-10","USSR-ORD-11",
    "USSR-ORD-12","USSR-ORD-13","USSR-ORD-14","USSR-ORD-15","USSR-ORD-16",
    "USSR-ORD-17","USSR-ORD-18","USSR-ORD-19","USSR-ORD-21",
    "USSR-MED-01","USSR-MED-02","USSR-MED-04","USSR-MED-17","USSR-MED-22"
)

$diffRows = @()
function Add-Diff {
    param(
        [string]$Family,[string]$Key,[string]$Name,[string]$Original,[string]$Date,
        [string]$File,[string]$Section,[string]$Variant,[string]$Kind = "formal_award"
    )
    $script:diffRows += [pscustomobject]@{
        family = $Family; key = $Key; name = $Name; original = $Original; date = $Date
        file = $File; section = $Section; variant = $Variant; kind = $Kind
    }
}

# Honorary titles with a named, issued decoration or insignia in the master
# table.  They remain explicitly typed; they are not silently counted as
# medal families.
Add-Diff "USSR-HON-01" "V01" "元帅之星" "Marshal's Star / Маршальская Звезда" "1940-09-02" "Marshal-Star big1.jpg" "Honorary titles" "荣誉称号佩饰；完整正面图" "honorary_title_insignia"
Add-Diff "USSR-HON-02" "V01" "苏联英雄金星奖章" "Gold Star of the Hero of the Soviet Union / Золотая звезда Героя Советского Союза" "1934-04-16" "Hero of the USSR Gold Star.png" "Honorary titles" "金星奖章；完整正面图" "honorary_title_medal"
Add-Diff "USSR-HON-03" "V01" "社会主义劳动英雄金质奖章（镰刀锤子）" "Gold Medal Hammer and Sickle / Золотая медаль «Серп и Молот»" "1938-12-27" "Sickle and Hammer.jpg" "Honorary titles" "金质奖章；完整正面图" "honorary_title_medal"
Add-Diff "USSR-HON-04" "V01" "苏联功勋试飞员" "Honoured Test Pilot of the USSR / Заслуженный лётчик-испытатель СССР" "1958-08-14" "Заслуженный летчик-испытатель СССР.jpg" "Honorary titles" "荣誉称号佩饰；完整正面图" "honorary_title_insignia"
Add-Diff "USSR-HON-05" "V01" "苏联功勋试飞领航员" "Honoured Test Navigator of the USSR / Заслуженный штурман-испытатель СССР" "1958-08-14" "Заслуженный Штурман-Испытаетль.jpg" "Honorary titles" "荣誉称号佩饰；完整正面图" "honorary_title_insignia"
Add-Diff "USSR-HON-06" "V01" "苏联宇航员飞行员" "Pilot-Cosmonaut of the USSR / Лётчик-космонавт СССР" "1961-04-14" "Pilot-Cosmonaut of the USSR.jpg" "Honorary titles" "荣誉称号佩饰；完整正面图" "honorary_title_insignia"
Add-Diff "USSR-HON-07" "V01" "苏联功勋军事飞行员" "Honoured Military Pilot of the USSR / Заслуженный военный лётчик СССР" "1965-01-26" "Distinguished Military Pilot Of The Soviet Union.jpg" "Honorary titles" "荣誉称号佩饰；完整正面图" "honorary_title_insignia"
Add-Diff "USSR-HON-08" "V01" "苏联功勋军事领航员" "Honoured Military Navigator of the USSR / Заслуженный военный штурман СССР" "1965-01-26" "Distinguished Military Navigator Of The Soviet Union.jpg" "Honorary titles" "荣誉称号佩饰；完整正面图" "honorary_title_insignia"
Add-Diff "USSR-HON-09" "V01" "苏联功勋飞行员" "Honoured Pilot of the USSR / Заслуженный пилот СССР" "1965-09-30" "Distinguished Pilot Of The Soviet Union.jpg" "Honorary titles" "荣誉称号佩饰；完整正面图" "honorary_title_insignia"
Add-Diff "USSR-HON-10" "V01" "苏联功勋领航员" "Honoured Navigator of the USSR / Заслуженный штурман СССР" "1965-09-30" "Zasl Shturman USSR.png" "Honorary titles" "荣誉称号佩饰；完整正面图" "honorary_title_insignia"
Add-Diff "USSR-HON-11" "V01" "苏联功勋发明家" "Honoured Inventor of the USSR / Заслуженный изобретатель СССР" "1981-12-28" "Distinguished Inventor Of The Soviet Union.jpg" "Honorary titles" "荣誉称号佩饰；完整正面图" "honorary_title_insignia"
Add-Diff "USSR-HON-12" "V01" "苏联人民医生" "People's Doctor of the USSR / Народный врач СССР" "1977-10-25" "People's Doctor of the Soviet Union.png" "Honorary titles" "荣誉称号佩饰；完整正面图" "honorary_title_insignia"
Add-Diff "USSR-HON-13" "V01" "苏联人民建筑师" "People's Architect of the USSR / Народный архитектор СССР" "1967-08-12" "People's Architect of the USSR.png" "Honorary titles" "荣誉称号佩饰；完整正面图" "honorary_title_insignia"
Add-Diff "USSR-HON-14" "V01" "苏联人民教师" "People's Teacher of the USSR / Народный учитель СССР" "1977-12-30" "People's teacher of the Soviet Union.png" "Honorary titles" "荣誉称号佩饰；完整正面图" "honorary_title_insignia"
Add-Diff "USSR-HON-15" "V01" "苏联人民艺术家（表演艺术）" "People's Artist of the USSR / Народный артист СССР" "1937-01-13" "People Artist of the USSR1.jpg" "Honorary titles" "荣誉称号佩饰；完整正面图" "honorary_title_insignia"
Add-Diff "USSR-HON-16" "V01" "苏联人民画家" "People's Painter of the USSR / Народный художник СССР" "1943-07-16" "Народный художник СССР.jpg" "Honorary titles" "荣誉称号佩饰；完整正面图" "honorary_title_insignia"

# Orders not among the 24 formal families.  Each degree is a concrete row;
# all three rows share one award_family (USSR-ORD-06 or USSR-ORD-20).
Add-Diff "USSR-ORD-06" "V-I" "库图佐夫勋章" "Order of Kutuzov / Орден Кутузова" "1942-07-29" "Орден Кутузова I.jpg" "Military orders" "一级；完整正面实物图"
Add-Diff "USSR-ORD-06" "V-II" "库图佐夫勋章" "Order of Kutuzov / Орден Кутузова" "1942-07-29" "Орден Кутузова II.jpg" "Military orders" "二级；完整正面实物图"
Add-Diff "USSR-ORD-06" "V-III" "库图佐夫勋章" "Order of Kutuzov / Орден Кутузова" "1943-02-08" "Орден Кутузова III.jpg" "Military orders" "三级；完整正面实物图"
Add-Diff "USSR-ORD-20" "V-I" "在苏联武装力量中为祖国服务勋章" "Order For Service to the Homeland in the Armed Forces of the USSR / Орден «За службу Родине в Вооружённых Силах СССР»" "1974-10-28" "Order For Service to the Homeland 1.jpg" "Military orders" "一级；完整正面实物图"
Add-Diff "USSR-ORD-20" "V-II" "在苏联武装力量中为祖国服务勋章" "Order For Service to the Homeland in the Armed Forces of the USSR / Орден «За службу Родине в Вооружённых Силах СССР»" "1974-10-28" "Order For Service to the Homeland 2.jpg" "Military orders" "二级；完整正面实物图"
Add-Diff "USSR-ORD-20" "V-III" "在苏联武装力量中为祖国服务勋章" "Order For Service to the Homeland in the Armed Forces of the USSR / Орден «За службу Родине в Вооружённых Силах СССР»" "1974-10-28" "Order For Service to the Homeland 3.jpg" "Military orders" "三级；完整正面实物图"

# Military, campaign, civilian, development, maternity and commemorative
# medals.  IDs 03 and 05–55 follow the previously harvested Mondvor index;
# only rows whose family was not in $existingFamilies enter this volume.
Add-Diff "USSR-MED-03" "V01" "劳动老兵奖章" "Medal Veteran of Labour / Медаль «Ветеран труда»" "1974-01-18" "Ветеран труда 1.jpg" "Civilian medals" "完整正面实物图"
Add-Diff "USSR-MED-05" "V01" "战功奖章" "Medal For Battle Merit / Медаль «За боевые заслуги»" "1938-10-17" "Медаль За Боевые Заслуги.jpg" "Military medals — General" "完整正面实物图"
Add-Diff "USSR-MED-06" "V01" "乌沙科夫奖章" "Medal of Ushakov / Медаль Ушакова" "1944-03-03" "Medal of Ushakov.jpg" "Military medals — General" "完整正面实物图"
Add-Diff "USSR-MED-07" "V01" "纳希莫夫奖章" "Medal of Nakhimov / Медаль Нахимова" "1944-03-03" "Medal of Nakhimov.png" "Military medals — General" "完整正面实物图"
Add-Diff "USSR-MED-08" "V-I" "卫国战争游击队员奖章" "Medal Partisan of the Patriotic War / Медаль «Партизану Отечественной войны»" "1943-02-02" "Partisan Medal 1st.jpg" "Military medals — General" "一级；完整正面实物图"
Add-Diff "USSR-MED-08" "V-II" "卫国战争游击队员奖章" "Medal Partisan of the Patriotic War / Медаль «Партизану Отечественной войны»" "1943-02-02" "Medal Partisan of the Patriotic War 2nd class OBVERSE.jpg" "Military medals — General" "二级；完整正面实物图"
Add-Diff "USSR-MED-09" "V01" "保卫苏联国界优异服务奖章" "Medal For Distinction in Guarding the State Border of the USSR / Медаль «За отличие в охране государственной границы СССР»" "1950-07-13" "Guard of USSR Borders.jpg" "Military medals — General" "完整正面实物图"
Add-Diff "USSR-MED-10" "V-I" "军事服役优异奖章" "Medal For Distinction in Military Service / Медаль «За отличие в воинской службе»" "1974-10-28" "Soviet For Distinction in Military Service 1st class.jpg" "Military medals — General" "一级；完整正面实物图"
Add-Diff "USSR-MED-10" "V-II" "军事服役优异奖章" "Medal For Distinction in Military Service / Медаль «За отличие в воинской службе»" "1974-10-28" "Soviet For Distinction in Military Service 2nd class.jpg" "Military medals — General" "二级；完整正面实物图"
Add-Diff "USSR-MED-11" "V01" "苏联武装力量老兵奖章" "Medal Veteran of the Armed Forces of the USSR / Медаль «Ветеран Вооружённых Сил СССР»" "1976-05-20" "MVeterVSA.jpg" "Military medals — General" "完整正面实物图"
Add-Diff "USSR-MED-12" "V01" "加强战斗友谊奖章" "Medal For Strengthening of Brotherhood in Arms / Медаль «За укрепление боевого содружества»" "1979-05-25" "Soviet Medal For Strengthening Military Cooperation.jpg" "Military medals — General" "完整正面实物图"
Add-Diff "USSR-MED-55" "V-I" "无瑕服役奖章" "Medal For Impeccable Service / Медаль «За безупречную службу»" "1958-01-25" "MBezuprSlA.jpg" "Military medals — General" "一级；完整正面实物图"
Add-Diff "USSR-MED-55" "V-II" "无瑕服役奖章" "Medal For Impeccable Service / Медаль «За безупречную службу»" "1958-01-25" "USSR15yearsofservice.jpg" "Military medals — General" "二级；完整正面实物图"
Add-Diff "USSR-MED-55" "V-III" "无瑕服役奖章" "Medal For Impeccable Service / Медаль «За безупречную службу»" "1958-01-25" "MBezuprSlC.jpg" "Military medals — General" "三级；完整正面实物图"

Add-Diff "USSR-MED-13" "V01" "保卫列宁格勒奖章" "Medal For the Defence of Leningrad / Медаль «За оборону Ленинграда»" "1942-12-22" "Defence of Leningrad OBVERSE.jpg" "Second World War defensive campaign medals" "完整正面实物图"
Add-Diff "USSR-MED-15" "V01" "保卫敖德萨奖章" "Medal For the Defence of Odessa / Медаль «За оборону Одессы»" "1942-12-22" "Defence of Odessa OBVERSE.jpg" "Second World War defensive campaign medals" "完整正面实物图"
Add-Diff "USSR-MED-16" "V01" "保卫塞瓦斯托波尔奖章" "Medal For the Defence of Sevastopol / Медаль «За оборону Севастополя»" "1942-12-22" "Medal Defense of Sevastopol.jpg" "Second World War defensive campaign medals" "完整正面实物图"
Add-Diff "USSR-MED-14" "V01" "保卫莫斯科奖章" "Medal For the Defence of Moscow / Медаль «За оборону Москвы»" "1944-05-01" "Defense of Moscow OBVERSE.jpg" "Second World War defensive campaign medals" "完整正面实物图"
Add-Diff "USSR-MED-19" "V01" "保卫高加索奖章" "Medal For the Defence of the Caucasus / Медаль «За оборону Кавказа»" "1944-05-01" "Defense of the caucasus OBVERSE.jpg" "Second World War defensive campaign medals" "完整正面实物图"
Add-Diff "USSR-MED-20" "V01" "保卫苏联北极地区奖章" "Medal For the Defence of the Soviet Transarctic / Медаль «За оборону Советского Заполярья»" "1944-12-05" "Medal For the Defence of the Soviet Transarctic OBVERSE.jpg" "Second World War defensive campaign medals" "完整正面实物图"
Add-Diff "USSR-MED-18" "V01" "保卫基辅奖章" "Medal For the Defence of Kiev / Медаль «За оборону Киева»" "1961-06-21" "Medal-Kijev.jpg" "Second World War defensive campaign medals" "完整正面实物图"
Add-Diff "USSR-MED-26" "V01" "攻克柏林奖章" "Medal For the Capture of Berlin / Медаль «За взятие Берлина»" "1945-06-09" "Capture of Berlin OBVERSE.jpg" "Second World War offensive campaign medals" "完整正面实物图"
Add-Diff "USSR-MED-23" "V01" "攻克布达佩斯奖章" "Medal For the Capture of Budapest / Медаль «За взятие Будапешта»" "1945-06-09" "Budapest medal.jpg" "Second World War offensive campaign medals" "完整正面实物图"
Add-Diff "USSR-MED-24" "V01" "攻克柯尼斯堡奖章" "Medal For the Capture of Königsberg / Медаль «За взятие Кёнигсберга»" "1945-06-09" "MedalCaptureKoenigsberg.jpg" "Second World War offensive campaign medals" "完整正面实物图"
Add-Diff "USSR-MED-25" "V01" "攻克维也纳奖章" "Medal For the Capture of Vienna / Медаль «За взятие Вены»" "1945-06-09" "Capture of Vienna OBVERSE.jpg" "Second World War offensive campaign medals" "完整正面实物图"
Add-Diff "USSR-MED-29" "V01" "解放布拉格奖章" "Medal For the Liberation of Prague / Медаль «За освобождение Праги»" "1945-06-09" "Medal for the liberation of Prague, Soviet Union.png" "Second World War offensive campaign medals" "完整正面实物图"
Add-Diff "USSR-MED-28" "V01" "解放华沙奖章" "Medal For the Liberation of Warsaw / Медаль «За освобождение Варшавы»" "1945-06-09" "Medal For The Liberation Of Warsaw.jpeg" "Second World War offensive campaign medals" "完整正面实物图"
Add-Diff "USSR-MED-27" "V01" "解放贝尔格莱德奖章" "Medal For the Liberation of Belgrade / Медаль «За освобождение Белграда»" "1945-06-09" "Medal Liberation of Belgrad.jpg" "Second World War offensive campaign medals" "完整正面实物图"
Add-Diff "USSR-MED-21" "V01" "战胜德国奖章" "Medal For the Victory over Germany in the Great Patriotic War 1941–1945 / Медаль «За Победу над Германией...»" "1945-05-09" "WW2 Victory USSR OBVERSE.jpg" "Second World War offensive campaign medals" "完整正面实物图"

Add-Diff "USSR-MED-30" "V01" "伟大卫国战争英勇劳动奖章" "Medal For Valiant Labour in the Great Patriotic War 1941–1945 / Медаль «За доблестный труд...»" "1945-06-06" "Heroic Labor During The Great Patriotic War (front).jpg" "Civilian medals" "完整正面实物图"
Add-Diff "USSR-MED-39" "V01" "救生奖章" "Medal For the Salvation of the Drowning / Медаль «За спасение утопающих»" "1957-02-16" "Medal For The Rescue Of The Drowning.jpg" "Civilian medals" "完整正面实物图"
Add-Diff "USSR-MED-38" "V01" "消防勇敢奖章" "Medal For Courage in a Fire / Медаль «За отвагу на пожаре»" "1957-10-30" "Medal for Bravery in Fire Fighting.jpg" "Civilian medals" "完整正面实物图"

Add-Diff "USSR-MED-31" "V01" "恢复南方黑色冶金企业奖章" "Medal For Restoration of the Black Metallurgy Enterprises of the South / Медаль «За восстановление предприятий чёрной металлургии юга»" "1948-05-18" "За восстановление предприятий черной металлургии юга.jpg" "Development/restoration campaigns" "完整正面实物图"
Add-Diff "USSR-MED-32" "V01" "恢复顿巴斯煤矿奖章" "Medal For Restoration of the Donbass Coal Mines / Медаль «За восстановление угольных шахт Донбасса»" "1947-09-10" "Medal For Restoration of the Donbass Coal Mines.jpg" "Development/restoration campaigns" "完整正面实物图"
Add-Diff "USSR-MED-33" "V01" "开发处女地奖章" "Medal For the Development of Virgin Lands / Медаль «За освоение целинных земель»" "1956-10-20" "Medal For Development of the Virgin Lands.jpg" "Development/restoration campaigns" "完整正面实物图"
Add-Diff "USSR-MED-34" "V01" "建设贝加尔—阿穆尔铁路奖章" "Medal For Construction of the Baikal-Amur Railway / Медаль «За строительство Байкало-Амурской магистрали»" "1976-10-08" "MbamA.jpg" "Development/restoration campaigns" "完整正面实物图"
Add-Diff "USSR-MED-35" "V01" "改造俄罗斯联邦非黑土地奖章" "Medal For Transforming the Non-Black Earth of the RSFSR / Медаль «За преобразование Нечерноземья РСФСР»" "1977-09-30" "Medal For Development of the Non-Black Earth Regions of the RSFSR.jpg" "Development/restoration campaigns" "完整正面实物图"
Add-Diff "USSR-MED-36" "V01" "开发西西伯利亚石油化工综合体奖章" "Medal For the Tapping of the Subsoil and Expansion of the Petrochemical Complex of Western Siberia / Медаль «За освоение недр...»" "1978-07-28" "Medal For Development of the Petrochemical Complex of Western Siberia.jpg" "Development/restoration campaigns" "完整正面实物图"
Add-Diff "USSR-MED-54" "V-I" "母亲奖章" "Maternity Medal / Медаль Материнства" "1944-07-08" "Motherhood Medal2.JPG" "Maternity medals" "一级；完整正面实物图"
Add-Diff "USSR-MED-54" "V-II" "母亲奖章" "Maternity Medal / Медаль Материнства" "1944-07-08" "Motherhood Medal1.JPG" "Maternity medals" "二级；完整正面实物图"

Add-Diff "USSR-MED-44" "V01" "工农红军建军二十周年纪念奖章" "Jubilee Medal XX Years of the Workers' and Peasants' Red Army / Юбилейная медаль «XX лет РККА»" "1938-01-24" "Medal «20 Years Since the Creation of the Worker's and Peasants' Red Army».jpg" "Soviet Armed Forces jubilees" "完整正面实物图"
Add-Diff "USSR-MED-45" "V01" "苏联军队和海军三十周年纪念奖章" "Jubilee Medal 30 Years of the Soviet Army and Navy / Юбилейная медаль «30 лет Советской Армии и Флота»" "1948-02-22" "30YSAF.jpg" "Soviet Armed Forces jubilees" "完整正面实物图"
Add-Diff "USSR-MED-46" "V01" "苏联武装力量四十周年纪念奖章" "Jubilee Medal 40 Years of the Armed Forces of the USSR / Юбилейная медаль «40 лет Вооружённых Сил СССР»" "1957-12-18" "40YSAF.jpg" "Soviet Armed Forces jubilees" "完整正面实物图"
Add-Diff "USSR-MED-47" "V01" "苏联武装力量五十周年纪念奖章" "Jubilee Medal 50 Years of the Armed Forces of the USSR / Юбилейная медаль «50 лет Вооружённых Сил СССР»" "1967-12-26" "50YearsMilitaryForces.jpg" "Soviet Armed Forces jubilees" "完整正面实物图"
Add-Diff "USSR-MED-48" "V01" "苏联武装力量六十周年纪念奖章" "Jubilee Medal 60 Years of the Armed Forces of the USSR / Юбилейная медаль «60 лет Вооружённых Сил СССР»" "1978-01-28" "60YSAF.jpg" "Soviet Armed Forces jubilees" "完整正面实物图"
Add-Diff "USSR-MED-49" "V01" "苏联武装力量七十周年纪念奖章" "Jubilee Medal 70 Years of the Armed Forces of the USSR / Юбилейная медаль «70 лет Вооружённых Сил СССР»" "1988-01-28" "70YSAF.jpg" "Soviet Armed Forces jubilees" "完整正面实物图"
Add-Diff "USSR-MED-41" "V01" "伟大卫国战争胜利二十周年纪念奖章" "Jubilee Medal Twenty Years of Victory in the Great Patriotic War 1941–1945 / Юбилейная медаль «20 лет Победы...»" "1965-05-07" "20yearsvictory.jpg" "Second World War jubilees" "完整正面实物图"
Add-Diff "USSR-MED-42" "V01" "伟大卫国战争胜利三十周年纪念奖章" "Jubilee Medal Thirty Years of Victory in the Great Patriotic War 1941–1945 / Юбилейная медаль «30 лет Победы...»" "1975-04-25" "30yearsvictory.jpg" "Second World War jubilees" "完整正面实物图"
Add-Diff "USSR-MED-43" "V01" "伟大卫国战争胜利四十周年纪念奖章" "Jubilee Medal Forty Years of Victory in the Great Patriotic War 1941–1945 / Юбилейная медаль «40 лет Победы...»" "1985-04-12" "40yearsvictory.jpg" "Second World War jubilees" "完整正面实物图"
Add-Diff "USSR-MED-51" "V01" "纪念莫斯科建城八百周年奖章" "Medal In Commemoration of the 800th Anniversary of Moscow / Медаль «В память 800-летия Москвы»" "1947-09-20" "800th anniversary of Moscow OBVERSE.jpg" "Other commemorative medals" "完整正面实物图"
Add-Diff "USSR-MED-52" "V01" "纪念列宁格勒建城二百五十周年奖章" "Medal In Commemoration of the 250th Anniversary of Leningrad / Медаль «В память 250-летия Ленинграда»" "1957-05-16" "Medal250Leningrad.jpg" "Other commemorative medals" "完整正面实物图"
Add-Diff "USSR-MED-53" "V01" "纪念基辅建城一千五百周年奖章" "Medal In Commemoration of the 1500th Anniversary of Kiev / Медаль «В память 1500-летия Киева»" "1982-05-10" "Kiev1500.jpg" "Other commemorative medals" "完整正面实物图"
Add-Diff "USSR-MED-50" "V01" "苏联民警五十周年纪念奖章" "Jubilee Medal 50 Years of the Soviet Militia / Юбилейная медаль «50 лет советской милиции»" "1967-11-21" "50YSM.jpg" "Other commemorative medals" "完整正面实物图"
Add-Diff "USSR-MED-40" "V-LABOUR" "纪念列宁诞辰一百周年奖章" "Jubilee Medal for Valiant Labour in Commemoration of the 100th Anniversary since the Birth of Vladimir Ilyich Lenin / Юбилейная медаль «За доблестный труд...»" "1969-11-05" "100 years Lenin OBVERSE.jpg" "Other commemorative medals" "劳动英勇版；完整正面实物图"
Add-Diff "USSR-MED-40" "V-MILITARY" "纪念列宁诞辰一百周年奖章" "Jubilee Medal for Military Valour in Commemoration of the 100th Anniversary since the Birth of Vladimir Ilyich Lenin / Юбилейная медаль «За воинскую доблесть...»" "1969-11-05" "100 years Lenin OBVERSE.jpg" "Other commemorative medals" "军事英勇版；同一章体图示，完整正面实物图"
Add-Diff "USSR-MED-40" "V-FOREIGN" "纪念列宁诞辰一百周年奖章" "Jubilee Medal In Commemoration of the 100th Anniversary since the Birth of Vladimir Ilyich Lenin / Юбилейная медаль «В ознаменование...»" "1969-11-05" "100 years Lenin OBVERSE.jpg" "Other commemorative medals" "外国领导人及国际运动版；同一章体图示，完整正面实物图"

# Parse every named image-bearing row in the downloaded source table.  This
# is the candidate universe; the hand-normalized differential above is only
# the subset whose family is outside the 24 formal baseline.
function Get-RowObjects {
    param([string[]]$Lines)
    $section = ""
    $row = @()
    $rowNo = 0
    $out = @()
    foreach ($line in $Lines) {
        if ($line -match '^={2,4}([^=].*?)={2,4}$') { $section = $Matches[1].Trim() }
        if ($line -eq "|-") {
            if ($row.Count -gt 0) {
                $rowNo++
                $files = @()
                foreach ($rl in $row) {
                    foreach ($m in [regex]::Matches($rl, '\[\[File:([^\]|]+)')) { $files += $m.Groups[1].Value.Trim() }
                }
                if ($files.Count -gt 0) {
                    $nameLine = $row | Where-Object { $_ -match '^\|.*\[\[' -and $_ -notmatch '\[\[File:' -and $_ -notmatch '^\|\s*(width|bgcolor)' } | Select-Object -First 1
                    $dateLine = $row | Where-Object { $_ -match '^\|\s*(\d{1,2}\s+\w+\s+\d{4}|\d{1,2}\s+\w+\s+\d{4}\s*<|\d{4})' } | Select-Object -First 1
                    $out += [pscustomobject]@{
                        source_row = $rowNo; table_section = $section; name_markup = [string]$nameLine
                        date_markup = [string]$dateLine; image_files = @($files | Select-Object -Unique)
                        image_pages = @($files | Select-Object -Unique | ForEach-Object { "https://commons.wikimedia.org/wiki/File:" + [uri]::EscapeDataString($_).Replace('%2F','/') })
                        source_url = $wikiUrl
                    }
                }
            }
            $row = @()
            continue
        }
        if ($row.Count -gt 0 -or $line -match '^\|\[\[File:') { $row += $line }
    }
    return $out
}

$lines = Get-Content -Path $wikiWikitextPath
$rawRows = @(Get-RowObjects -Lines $lines)

# Attach a stable family/status to the raw rows wherever the table's first
# image is one of the normalized differential files.  All other rows remain
# candidates and are not silently promoted to formal records.
$diffFiles = @{}
foreach ($dr in $diffRows) { $diffFiles[$dr.file] = $dr.family }
$rawOut = @()
foreach ($rr in $rawRows) {
    $first = $rr.image_files | Select-Object -First 1
    $fam = if ($diffFiles.ContainsKey($first)) { $diffFiles[$first] } else { $null }
    $status = if ($fam) { "differential_candidate" } else { "candidate_unclassified_or_existing_family" }
    $rawOut += [ordered]@{
        source_id = "soviet_wikipedia_master_2026-09-28"
        source_row = $rr.source_row; table_section = $rr.table_section; page_title = $rr.name_markup
        date_candidate = $rr.date_markup; image_files = $rr.image_files; image_page_urls = $rr.image_pages
        source_page_url = $wikiUrl; candidate_family_id = $fam; status = $status
        note = "从Wikipedia总表wikitext表行提取；图片文件名仅作发现线索，正文只使用实际打开的Commons文件页原图。"
    }
}
[System.IO.File]::WriteAllLines($rawPath, @($rawOut | ForEach-Object { $_ | ConvertTo-Json -Depth 8 -Compress }), [Text.UTF8Encoding]::new($false))

$apiInfo = @{}
$bad = @("ribbon","bar","certificate","diplom","portrait","parade","monument","postage","stamp","document","award certificate")
function Get-ImageInfo {
    param([string]$File)
    if ($apiInfo.ContainsKey($File)) { return $apiInfo[$File] }
    $p = @{ action = "query"; titles = "File:$File"; prop = "imageinfo"; iiprop = "url|size|mime|extmetadata"; format = "json"; formatversion = "2" }
    $qs = ($p.GetEnumerator() | ForEach-Object { [uri]::EscapeDataString([string]$_.Key) + "=" + [uri]::EscapeDataString([string]$_.Value) }) -join "&"
    $uri = "https://commons.wikimedia.org/w/api.php?$qs"
    $answer = $null
    for ($attempt=0; $attempt -lt 4; $attempt++) {
        try {
            $answer = Invoke-RestMethod -Uri $uri -Headers $headers -TimeoutSec 90
            if ($answer.query.pages -and @($answer.query.pages).Count -gt 0) { break }
        } catch {
            if ($attempt -eq 3) { throw }
            Start-Sleep -Seconds ([int](5 * [math]::Pow(2,$attempt)))
        }
    }
    $pg = @($answer.query.pages) | Select-Object -First 1
    $ii = if ($pg.imageinfo) { @($pg.imageinfo) | Select-Object -First 1 } else { $null }
    $apiInfo[$File] = $ii
    Start-Sleep -Milliseconds 250
    return $ii
}

# Wikimedia API metadata is fetched in batches (the source table has many
# rows, while image files repeat across a few variants).  This keeps the
# discovery step source-first without making one network request per row.
$allFiles = @($diffRows | ForEach-Object { $_.file } | Select-Object -Unique)
Write-Output ("wikipedia master: diffRows=$($diffRows.Count) uniqueFiles=$($allFiles.Count) rawRows=$($rawRows.Count)")
for ($offset = 0; $offset -lt $allFiles.Count; $offset += 40) {
    $batch = @($allFiles[$offset..([math]::Min($offset + 39, $allFiles.Count - 1))])
    $titles = ($batch | ForEach-Object { "File:$($_)" }) -join "|"
    $p = @{ action = "query"; titles = $titles; prop = "imageinfo"; iiprop = "url|size|mime|extmetadata"; format = "json"; formatversion = "2" }
    $qs = ($p.GetEnumerator() | ForEach-Object { [uri]::EscapeDataString([string]$_.Key) + "=" + [uri]::EscapeDataString([string]$_.Value) }) -join "&"
    $batchUri = "https://commons.wikimedia.org/w/api.php?$qs"
    Write-Output ("wikipedia master: metadata batch offset=$offset count=$($batch.Count)")
    $answer = $null
    for ($attempt=0; $attempt -lt 4; $attempt++) {
        try { $answer = Invoke-RestMethod -Uri $batchUri -Headers $headers -TimeoutSec 60; break }
        catch { if ($attempt -eq 3) { throw }; Start-Sleep -Seconds ([int](3 * [math]::Pow(2,$attempt))) }
    }
    foreach ($pg in @($answer.query.pages)) {
        if ($pg.imageinfo) {
            $key = ([string]$pg.title) -replace '^File:',''
            $apiInfo[$key] = @($pg.imageinfo) | Select-Object -First 1
        }
    }
    Write-Output ("wikipedia master: metadata batch done offset=$offset")
}

function Get-MetaValue { param($Ext,[string]$Key)
    if ($Ext -and $Ext.$Key) { return [string]$Ext.$Key.value }
    return $null
}

Add-Type -AssemblyName System.Drawing
$seenHashes = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($old in Get-ChildItem -Path (Join-Path $root "assets") -Recurse -File -ErrorAction SilentlyContinue) {
    if ($old.Extension.ToLowerInvariant() -in @(".jpg",".jpeg",".png",".gif",".webp")) {
        try { [void]$seenHashes.Add((Get-FileHash -Algorithm SHA256 -LiteralPath $old.FullName).Hash.ToLowerInvariant()) } catch {}
    }
}

$records = @()
$manifest = @()
$harvestedRaw = @()
$rejected = @()
$seenFileView = @{}
$awardsWikiUrl = "https://awards.wiki/en/awards_ussr.html"
$awardImageByFamily = @{
    "USSR-HON-01"="/img/sssr/marshalskaja_zvezda.jpg"; "USSR-HON-02"="/img/sssr/zolotaj_zvezda.jpg"; "USSR-HON-03"="/img/sssr/medal_serp_i_molot.jpg"
    "USSR-ORD-06"="/img/sssr/orden_kutuzova.jpg"; "USSR-ORD-20"="/img/sssr/za_sluzhbu_rodine_v_vs_sssr.jpg"
    "USSR-MED-03"="/img/sssr/medal_veteran_truda.jpg"; "USSR-MED-05"="/img/sssr/za_boevie_zaslugi.jpg"; "USSR-MED-06"="/img/sssr/medal_ushakova.jpg"; "USSR-MED-07"="/img/sssr/medal_nahimova.jpg"
    "USSR-MED-08"="/img/sssr/partizanu_vov.jpg"; "USSR-MED-09"="/img/sssr/medal_za_otlichie_v_ohrane_gosudarstvennoj_granicy.jpg"; "USSR-MED-10"="/img/sssr/medal_za_otlichie_v_voinskoj_sluzhbe.jpg"
    "USSR-MED-11"="/img/sssr/medal_veteran_vooruzhennyh_sil.jpg"; "USSR-MED-12"="/img/sssr/medal_za_ukreplenie_boevogo_sodruzhestva.jpg"; "USSR-MED-13"="/img/sssr/za_oboronu_leningrada.jpg"
    "USSR-MED-14"="/img/sssr/za_oboronu_moskvi.jpg"; "USSR-MED-15"="/img/sssr/za_oboronu_odessi.jpg"; "USSR-MED-16"="/img/sssr/za_oboronu_sevastopolj.jpg"
    "USSR-MED-18"="/img/sssr/za_oboronu_kieva.jpg"; "USSR-MED-19"="/img/sssr/za_oboronu_kavkaza.jpg"; "USSR-MED-20"="/img/sssr/za_oboronu_zapoljrj.jpg"
    "USSR-MED-21"="/img/sssr/za_pobedu.jpg"; "USSR-MED-23"="/img/sssr/za_vzjtie_budapechta.jpg"; "USSR-MED-24"="/img/sssr/za_vzjtie_kenigsberga.jpg"
    "USSR-MED-25"="/img/sssr/za_vzjtie_veni.jpg"; "USSR-MED-26"="/img/sssr/za_vzjtie_berlina.jpg"; "USSR-MED-27"="/img/sssr/za_osvobozhdenie_belgrada.jpg"
    "USSR-MED-28"="/img/sssr/za_osvobozhdenie_varchavi.jpg"; "USSR-MED-29"="/img/sssr/za_osvobozhdenie_pragi.jpg"; "USSR-MED-30"="/img/sssr/za_doblesniy_trud.jpg"
    "USSR-MED-31"="/img/sssr/za_vosstanovlenie_predprijatij_chjornoj_metallurgii_juga.jpg"; "USSR-MED-32"="/img/sssr/za_vosstanovlenie_ugolnyh_shaht_donbassa.jpg"; "USSR-MED-33"="/img/sssr/za_osvoenie_celinnyh_zemel.jpg"
    "USSR-MED-34"="/img/sssr/medal_za_stroitelstvo_bam.jpg"; "USSR-MED-35"="/img/sssr/medal_za_preobrazovanie_nechernozemja_rsfsr.jpg"; "USSR-MED-36"="/img/sssr/medal_za_osvoenie_nedr_i_razvitie_neftegazovogo_kompleksa.jpg"
    "USSR-MED-37"="/img/sssr/medal_za_otlichnuju_sluzhbu_po_ohrane_obshhestvennogo_porjadka.jpg"; "USSR-MED-38"="/img/sssr/medal_za_otvagu_na_pozhare.jpg"; "USSR-MED-39"="/img/sssr/medal_za_spasenie_utopajushhih.jpg"
    "USSR-MED-41"="/img/sssr/medal_dvadcat_let_pobedy_v_velikoj_otechestvennoj_vojne.jpg"; "USSR-MED-42"="/img/sssr/30_let_pobedy_v_vov.jpg"; "USSR-MED-43"="/img/sssr/medal_40_let_pobedy_v_vov.jpg"
    "USSR-MED-44"="/img/sssr/medal_xx_let_rkka.jpg"; "USSR-MED-45"="/img/sssr/30_let_sovetskoj_armii_i_flota.jpg"; "USSR-MED-46"="/img/sssr/40_let_vooruzhennyh_sil_sssr.jpg"
    "USSR-MED-47"="/img/sssr/50_let_vooruzhjonnyh_sil_sssr.jpg"; "USSR-MED-48"="/img/sssr/60_let_vooruzhennyh_sil_sssr.jpg"; "USSR-MED-49"="/img/sssr/70_let_vooruzhennyh_sil_sssr.jpg"
    "USSR-MED-50"="/img/sssr/medal_50_let_sovetskoj_milicii.jpg"; "USSR-MED-51"="/img/sssr/medal_v_pamjat_800_letija_moskvy.jpg"; "USSR-MED-52"="/img/sssr/v_pamjat_250_letija_leningrada.jpg"
    "USSR-MED-53"="/img/sssr/medal_v_pamjat_1500_letija_kieva.jpg"; "USSR-MED-54"="/img/sssr/medal_materinstva.jpg"
}
$awardDetailImageByKey = @{
    "USSR-ORD-06-V-I"="/img/sssr/orden_kutuzova_1_stepeni.jpg"; "USSR-ORD-06-V-II"="/img/sssr/orden_kutuzova_2_stepeni.jpg"; "USSR-ORD-06-V-III"="/img/sssr/orden_kutuzova_3_stepeni.jpg"
    "USSR-ORD-20-V-I"="/img/sssr/za_sluzhbu_rodine_v_vs_sssr_1.jpg"; "USSR-ORD-20-V-II"="/img/sssr/za_sluzhbu_rodine_v_vs_sssr_2.jpg"; "USSR-ORD-20-V-III"="/img/sssr/za_sluzhbu_rodine_v_vs_sssr_3.jpg"
}
$rowIndex = 0
foreach ($dr in $diffRows) {
    $rowIndex++
    Write-Output ("wikipedia master: image row $rowIndex/$($diffRows.Count) $($dr.family) $($dr.file)")
    if ($dr.file -match ($bad -join "|")) {
        $rejected += [ordered]@{ family = $dr.family; file_title = $dr.file; reason = "file name matched explicit ribbon/certificate/person/document exclusion" }
        continue
    }
    $mapKey = "$($dr.family)-$($dr.key)"
    $awardPath = if ($awardDetailImageByKey.ContainsKey($mapKey)) { $awardDetailImageByKey[$mapKey] } elseif ($awardImageByFamily.ContainsKey($dr.family)) { $awardImageByFamily[$dr.family] } else { $null }
    if ([string]::IsNullOrWhiteSpace($awardPath) -and ($dr.kind -eq "honorary_title_insignia" -or $dr.family -in @("USSR-MED-40","USSR-MED-55"))) {
        $rejected += [ordered]@{ family=$dr.family; file_title=$dr.file; reason="alternate awards.wiki page has no mapped complete object image; Commons CDN rate-limited, retained as unresolved candidate" }
        continue
    }
    $usingAwardsWiki = -not [string]::IsNullOrWhiteSpace($awardPath)
    if ($usingAwardsWiki) {
        $sourcePage = $awardsWikiUrl
        $url = "https://awards.wiki$awardPath"
        $downloadUrl = $url
        $sourceFileLabel = "awards.wiki:$awardPath"
        $sourceKey = $downloadUrl
        $ii = [pscustomobject]@{ mime = "image/jpeg"; extmetadata = $null }
    } else {
        $ii = Get-ImageInfo -File $dr.file
        if (-not $ii -or -not ([string]$ii.mime).StartsWith("image/")) {
            $rejected += [ordered]@{ family = $dr.family; file_title = $dr.file; reason = "no alternate awards.wiki image and Commons file page has no imageinfo image" }
            continue
        }
        $sourcePage = "https://commons.wikimedia.org/wiki/File:" + [uri]::EscapeDataString($dr.file).Replace('%2F','/')
        $url = ([string]$ii.url) -replace '\?.*$',''
        # Wikimedia is rate-limiting original-file CDN requests from this
        # workspace.  Use an explicit 500px Commons thumb path (not a search
        # preview) while preserving the original URL for later replacement.
        $downloadUrl = [string]$ii.thumburl
        $op = ([uri]$url).AbsolutePath.Trim('/').Split('/')
        if ($op.Count -ge 5 -and ($downloadUrl -notmatch '/thumb/' -or $downloadUrl -notmatch '/[0-9]+px-')) {
            $encodedName = $op[$op.Count - 1]
            $downloadUrl = "https://upload.wikimedia.org/wikipedia/commons/thumb/$($op[2])/$($op[3])/$encodedName/500px-$encodedName"
        }
        $sourceFileLabel = "File:$($dr.file)"
        $sourceKey = $dr.file
    }
    $ext = [System.IO.Path]::GetExtension(([uri]$url).AbsolutePath).ToLowerInvariant()
    if ($ext -notin @(".jpg",".jpeg",".png",".gif",".webp")) { $ext = ".img" }
    $safe = (($dr.family + "-" + $dr.key + "-" + $dr.file) -replace '[^A-Za-z0-9._-]+','_')
    $path = Join-Path $imageDir ($safe.Substring(0,[math]::Min(150,$safe.Length)) + $ext)
    $hash = $null; $width = $null; $height = $null
    if ($seenFileView.ContainsKey($sourceKey)) {
        $prior = $seenFileView[$sourceKey]
        $path = Join-Path $root $prior.local_path
        $hash = $prior.sha256; $width = $prior.width; $height = $prior.height
    } else {
        for ($attempt=0; $attempt -lt 4; $attempt++) {
            try {
                Invoke-WebRequest -Uri $downloadUrl -Headers $headers -OutFile $path -TimeoutSec 45 | Out-Null
                break
            } catch {
                if ($attempt -eq 3) { $rejected += [ordered]@{ family=$dr.family; file_title=$dr.file; reason="download failed: $($_.Exception.Message)" }; $path=$null; break }
                Start-Sleep -Seconds ([int](5 * [math]::Pow(2,$attempt)))
            }
        }
        if (-not $path -or -not (Test-Path $path)) { continue }
        try {
            $img = [System.Drawing.Image]::FromFile((Resolve-Path $path))
            $width = $img.Width; $height = $img.Height; $img.Dispose()
            if ($width -lt 120 -or $height -lt 120) { throw "decoded image too small: ${width}x${height}" }
            $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant()
        } catch {
            $rejected += [ordered]@{ family=$dr.family; file_title=$dr.file; reason="decode failure: $($_.Exception.Message)" }
            Remove-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue
            continue
        }
        if ($seenHashes.Contains($hash)) {
            $rejected += [ordered]@{ family=$dr.family; file_title=$dr.file; reason="exact image payload already present; duplicate not added" }
            Remove-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue
            continue
        }
        [void]$seenHashes.Add($hash)
        $relative = (Resolve-Path $path).Path.Substring($root.Length + 1).Replace('\','/')
        $seenFileView[$sourceKey] = [ordered]@{ local_path=$relative; sha256=$hash; width=$width; height=$height; original_image_url=$url; download_url=$downloadUrl; source_page_url=$sourcePage }
    }
    $relative = (Resolve-Path $path).Path.Substring($root.Length + 1).Replace('\','/')
    $viewKey = "USSR-WIKI-$($dr.family)-$($dr.key)-FRONT"
    $record = [ordered]@{
        id = "$($dr.family)-$($dr.key)-WIKI"
        family = $dr.family
        country_zh = "苏联"
        period = "苏联（1922–1991）"
        name = $dr.name
        original = $dr.original
        date = "$($dr.date)设立（Wikipedia总表日期；非具体实物颁发日）"
        variant = "$($dr.variant)；Commons图片页原图；具体生产版型／制造商待考"
        views = @([ordered]@{ key=$viewKey; label="完整正面；来源图片页原图" })
        source_ids = @($wikiUrl,$sourcePage)
        source_evidence = [ordered]@{ wikipedia_table_section=$dr.section; wikipedia_image_file="File:$($dr.file)"; alternate_image_source=$sourceFileLabel; access_date=$asOf; image_type=$(if($usingAwardsWiki){"awards.wiki page image; complete front candidate"}else{"Commons file-page thumb; complete front candidate"}) }
    }
    $records += $record
    $extMeta = $ii.extmetadata
    $manifest += [ordered]@{
        view_key=$viewKey; family=$dr.family; variant_id=$record.id; local_path=$relative
        source_page_url=$sourcePage; original_image_url=$url; download_url=$downloadUrl; sha256=$hash
        width=$width; height=$height; mime=[string]$ii.mime
        author=(Get-MetaValue $extMeta "Artist"); license=(Get-MetaValue $extMeta "LicenseShortName")
        license_url=(Get-MetaValue $extMeta "LicenseUrl"); image_description=(Get-MetaValue $extMeta "ImageDescription")
        source_table=$wikiUrl; table_section=$dr.section; file_title=$sourceFileLabel
        view_assessment="完整章体正面候选；拒绝绶带、证书、人物照、仅背面；具体实物／版型仍需主任务复核"
    }
    $harvestedRaw += [ordered]@{
        source_id="soviet_wikipedia_master_2026-09-28"; record_id=$record.id; candidate_family_id=$dr.family
        polity="苏联"; period_candidate="苏联（1922–1991）"; page_title=$dr.name; original_name=$dr.original
        date_candidate=$dr.date; table_section=$dr.section; source_page_url=$wikiUrl; object_page_url=$sourcePage
        original_image_url=$url; download_url=$downloadUrl; local_image_path=$relative; image_width=$width; image_height=$height
        sha256=$hash; license=(Get-MetaValue $extMeta "LicenseShortName"); status="downloaded_decoded_differential"
        note=$(if($usingAwardsWiki){"Wikipedia总表命名行与awards.wiki目录页已实际核对；图片为该站公开完整正面图，原Commons文件名仅作候选线索。"}else{"Wikipedia总表命名行与Commons文件页已实际核对；仅取完整正面候选图。"})
    }
}

$volume = [ordered]@{
    as_of=$asOf
    volume="苏联：Wikipedia总表差集（完整正面图批次）"
    scope="以 Orders, decorations, and medals of the Soviet Union 当前总表的全部带名图片表行为候选全集；剔除已正式落盘的24个family，对剩余family批量取得 awards.wiki 目录页公开完整正面图，未映射项保留为未解析候选。"
    source_table=$wikiUrl
    source_snapshot=$wikiWikitextPath.Substring($root.Length+1).Replace('\','/')
    existing_formal_family_count=24; existing_formal_family_ids=$existingFamilies
    candidate_universe_rows=$rawRows.Count; candidate_universe_image_files=(@($rawRows | ForEach-Object {$_.image_files}) | Select-Object -Unique).Count
    differential_planned_rows=$diffRows.Count; records=$records
    counts=[ordered]@{ differential_variant_rows=$records.Count; differential_families=(@($records | ForEach-Object {$_.family}) | Select-Object -Unique).Count; complete_local_images=(@($manifest | ForEach-Object {$_.sha256}) | Select-Object -Unique).Count; rejected_or_unresolved=$rejected.Count }
    notes=@("总表表行、日期和图片文件名先批量保存至raw_candidates；正文只采用实际取得、可解码的 awards.wiki 公开图像或已保留的 Commons 图像。","同一family的等级／版型保持同一family；同一来源图被多个资格／等级行共用，不重复保存图片。","图片为来源公开图像；不将搜索预览、绶带、证书、人物照或仅背面当作正文图。")
}
[System.IO.File]::WriteAllText($volumePath, ($volume | ConvertTo-Json -Depth 12), [Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllText($manifestPath, ([ordered]@{as_of=$asOf; volume=$volume.volume; images=$manifest; rights_review=@{note="作者、许可、来源页和原图地址按Commons文件页逐项保留。"}} | ConvertTo-Json -Depth 12), [Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllText($exclusionPath, ([ordered]@{as_of=$asOf; scope=$volume.scope; unresolved_or_excluded=$rejected; note="未通过完整图、可解码或重复校验的候选不进入正文记录。"} | ConvertTo-Json -Depth 12), [Text.UTF8Encoding]::new($false))

$summary = [ordered]@{
    source_rows=$rawRows.Count; source_unique_images=(@($rawRows | ForEach-Object {$_.image_files}) | Select-Object -Unique).Count
    differential_planned=$diffRows.Count; differential_records=$records.Count
    differential_families=(@($records | ForEach-Object {$_.family}) | Select-Object -Unique).Count
    local_images=(@($manifest | ForEach-Object {$_.sha256}) | Select-Object -Unique).Count
    rejected=$rejected.Count; volume=$volumePath.Substring($root.Length+1).Replace('\','/'); manifest=$manifestPath.Substring($root.Length+1).Replace('\','/')
}
Write-Output ($summary | ConvertTo-Json -Depth 8)
