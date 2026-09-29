param(
    [string]$ProjectRoot = 'C:\Users\agcrf\Desktop\world-medals'
)

$ErrorActionPreference = 'Stop'
$sourceId = 'mondvor_ussr_order_index'
$sourceHome = 'https://mondvor.narod.ru/'
$indexUrl = 'https://mondvor.narod.ru/ordpage.htm'
$userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36'
$pageCache = Join-Path $ProjectRoot 'sources/cache/mondvor_soviet_orders/pages'
$imageCache = Join-Path $ProjectRoot 'sources/cache/mondvor_soviet_orders/images'
$rawOut = Join-Path $ProjectRoot 'data/raw_candidates/mondvor_soviet_orders_2026-09-29.jsonl'
$imageIndexOut = Join-Path $ProjectRoot 'sources/cache/mondvor_soviet_orders/image_inventory_2026-09-29.json'
$crawlIndexOut = Join-Path $ProjectRoot 'sources/cache/mondvor_soviet_orders/crawl_inventory_2026-09-29.json'
$today = '2026-09-29'

New-Item -ItemType Directory -Force -Path $pageCache, $imageCache | Out-Null

$script:cookieJar = [System.Net.CookieContainer]::new()
function Get-RemoteBytes([string]$Url) {
    $request = [System.Net.HttpWebRequest]::Create($Url)
    $request.UserAgent = $userAgent
    $request.CookieContainer = $script:cookieJar
    $request.Timeout = 45000
    $request.ReadWriteTimeout = 45000
    $request.AllowAutoRedirect = $true
    $request.AutomaticDecompression = [System.Net.DecompressionMethods]::GZip -bor [System.Net.DecompressionMethods]::Deflate
    $response = $request.GetResponse()
    try {
        $stream = $response.GetResponseStream()
        try {
            $memory = [System.IO.MemoryStream]::new()
            try {
                $stream.CopyTo($memory)
                return ,([pscustomobject]@{
                    Bytes = $memory.ToArray()
                    FinalUrl = $response.ResponseUri.AbsoluteUri
                    ContentType = $response.ContentType
                    StatusCode = [int]$response.StatusCode
                })
            }
            finally { $memory.Dispose() }
        }
        finally { $stream.Dispose() }
    }
    finally { $response.Dispose() }
}

function Get-LocalPagePath([string]$Url) {
    $name = [System.Uri]::new($Url).AbsolutePath.TrimStart('/')
    if (-not $name) { $name = 'index.htm' }
    $name = $name -replace '[\\/:*?"<>|]', '_'
    return Join-Path $pageCache $name
}

function Get-Page([string]$Url) {
    $path = Get-LocalPagePath $Url
    if (Test-Path -LiteralPath $path) {
        $bytes = [System.IO.File]::ReadAllBytes($path)
        return [pscustomobject]@{ Url = $Url; FinalUrl = $Url; Path = $path; Bytes = $bytes; Html = [System.Text.Encoding]::UTF8.GetString($bytes); Cached = $true }
    }
    $response = Get-RemoteBytes $Url
    if ($response.StatusCode -ne 200 -or $response.ContentType -notmatch 'text/html') {
        throw "Unexpected response for ${Url}: $($response.StatusCode) $($response.ContentType)"
    }
    [System.IO.File]::WriteAllBytes($path, $response.Bytes)
    Start-Sleep -Milliseconds 200
    return [pscustomobject]@{ Url = $Url; FinalUrl = $response.FinalUrl; Path = $path; Bytes = $response.Bytes; Html = [System.Text.Encoding]::UTF8.GetString($response.Bytes); Cached = $false }
}

function Get-Attribute([string]$Attributes, [string]$Name) {
    $pattern = '(?is)(?:^|\s)' + [regex]::Escape($Name) + '\s*=\s*(?:"([^"]*)"|''([^'']*)''|([^\s>]+))'
    $m = [regex]::Match($Attributes, $pattern)
    if (-not $m.Success) { return $null }
    foreach ($group in 1..3) { if ($m.Groups[$group].Success) { return [Net.WebUtility]::HtmlDecode($m.Groups[$group].Value) } }
    return $null
}

function Get-VisibleText([string]$Html) {
    $text = $Html -replace '(?is)<script\b.*?</script>', ' ' -replace '(?is)<style\b.*?</style>', ' ' -replace '(?is)<noscript\b.*?</noscript>', ' '
    $text = $text -replace '(?is)<br\s*/?>', "`n" -replace '(?is)</(?:p|div|tr|li|h[1-6])\s*>', "`n"
    $text = $text -replace '(?is)<[^>]+>', ' '
    $text = [Net.WebUtility]::HtmlDecode($text) -replace '&nbsp;', ' '
    return (($text -replace '[\t\r ]+', ' ' -replace '\n\s*\n+', "`n").Trim())
}

function Get-Links([string]$Html) {
    $items = [System.Collections.Generic.List[object]]::new()
    foreach ($m in [regex]::Matches($Html, '(?is)<a\b([^>]*)>(.*?)</a>')) {
        $attributes = $m.Groups[1].Value
        $inner = $m.Groups[2].Value
        $href = Get-Attribute $attributes 'href'
        if (-not $href) { continue }
        $text = Get-VisibleText $inner
        $altList = @([regex]::Matches($inner, '(?is)<img\b([^>]*)>') | ForEach-Object { Get-Attribute $_.Groups[1].Value 'alt' } | Where-Object { $_ })
        $items.Add([pscustomobject]@{ Href = $href; Text = $text; Alt = ($altList -join '; ') })
    }
    return ,$items.ToArray()
}

function Get-ImageRows([string]$Html, [string]$PageUrl, [string]$PageText) {
    $items = [System.Collections.Generic.List[object]]::new()
    $skipName = '^(?:mainbutton|herobutton|ordbutton|medbutton|badbutton|fotobutton|pagebutton\d*|banner|counter|10)\.(?:gif|png|jpe?g)$'
    foreach ($m in [regex]::Matches($Html, '(?is)<img\b([^>]*)>')) {
        $attrs = $m.Groups[1].Value
        $src = Get-Attribute $attrs 'src'
        $oldUrl = Get-Attribute $attrs 'tppabs'
        $alt = Get-Attribute $attrs 'alt'
        if (-not $src -and -not $oldUrl) { continue }
        $imageUrl = if ($oldUrl -and $oldUrl -match '^https?://') { $oldUrl } else { [System.Uri]::new([System.Uri]::new($PageUrl), ($src ?? $oldUrl)).AbsoluteUri }
        if ($imageUrl -notmatch '^https?://(?:www\.)?mondvor\.narod\.ru/' -and $imageUrl -notmatch '^https?://mondvor\.narod\.ru/') { continue }
        $name = [System.IO.Path]::GetFileName(([System.Uri]::new($imageUrl)).AbsolutePath)
        if ($name -match $skipName) { continue }
        $start = [Math]::Max(0, $m.Index - 320)
        $length = [Math]::Min($Html.Length - $start, $m.Length + 640)
        $context = Get-VisibleText $Html.Substring($start, $length)
        $items.Add([pscustomobject]@{
            source_image_url = $imageUrl
            image_page_url = $imageUrl
            source_page_url = $PageUrl
            rights_status = '许可未确认；仅保留原站URL与说明，不下载、不嵌入。'
            source_file_name = $name
            alt_and_byte_hint = $alt
            page_context = $context
            viewed_file = $null
            decoded = $false
            width = $null
            height = $null
            sha256 = $null
            content_type = $null
            local_path = $null
        })
    }
    return ,$items.ToArray()
}

function Get-TypeLabels([string]$Text) {
    $labels = [System.Collections.Generic.List[string]]::new()
    foreach ($m in [regex]::Matches($Text, '(?i)\bТип\s*(?:[IVX]{1,5}|\d{1,2})\b')) {
        $label = ($m.Value -replace '\s+', ' ').Trim()
        if (-not $labels.Contains($label)) { $labels.Add($label) }
    }
    foreach ($m in [regex]::Matches($Text, '(?i)\b(?:I|II|III|IV|V|VI|VII|VIII|IX|X)\s+(?:степени|класс(?:а)?|степень)\b')) {
        $label = ($m.Value -replace '\s+', ' ').Trim()
        if (-not $labels.Contains($label)) { $labels.Add($label) }
    }
    return ,$labels.ToArray()
}

function Get-ClueSnippets([string]$Text) {
    $result = [System.Collections.Generic.List[string]]::new()
    $pattern = '(?i).{0,100}(?:тип(?:а|е|ы)?|вариант(?:а|е|ы)?|разновидност(?:ь|и|ей)|степен(?:ь|и|ей)|класс(?:а|е|ы)?|монетн(?:ый|ого|ом) двор|ЛМД|КМД|номер(?:а|ов)?|клейм[оа]|гайк[аи]|винт|штифт|нарезн(?:ый|ого) штифт|колодк[аи]).{0,180}'
    foreach ($m in [regex]::Matches($Text, $pattern)) {
        $snippet = ($m.Value -replace '\s+', ' ').Trim()
        if ($snippet -and -not $result.Contains($snippet)) { $result.Add($snippet) }
        if ($result.Count -ge 80) { break }
    }
    return ,$result.ToArray()
}

function Get-DateHints([string]$Text) {
    $dates = [System.Collections.Generic.List[string]]::new()
    foreach ($m in [regex]::Matches($Text, '(?i)(?:\d{1,2}\s+)?(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)?\s*19\d{2}\s*(?:года|г\.)?')) {
        $value = ($m.Value -replace '\s+', ' ').Trim()
        if ($value -and -not $dates.Contains($value)) { $dates.Add($value) }
    }
    return ,$dates.ToArray()
}

function Get-SourceExcerpt([string]$Text) {
    $m = [regex]::Match($Text, '(?i).{0,40}(?:учрежден|учреждена|учреждено|установлен|утвержден).{0,260}')
    if ($m.Success) { return (($m.Value -replace '\s+', ' ').Trim()) }
    return (($Text.Substring(0, [Math]::Min(300, $Text.Length)) -replace '\s+', ' ').Trim())
}

$idMap = [ordered]@{
    'OLenin' = @{ family='USSR-ORD-01'; name='列宁勋章'; original='Орден Ленина'; english='Order of Lenin' }
    'OOctRev' = @{ family='USSR-ORD-02'; name='十月革命勋章'; original='Орден Октябрьской Революции'; english='Order of the October Revolution' }
    'OPobeda' = @{ family='USSR-ORD-03'; name='胜利勋章'; original='Орден «Победа»'; english='Order of Victory' }
    'ORBan' = @{ family='USSR-ORD-04'; name='红旗勋章'; original='Орден Красного Знамени'; english='Order of the Red Banner' }
    'OSuvor' = @{ family='USSR-ORD-05'; name='苏沃洛夫勋章'; original='Орден Суворова'; english='Order of Suvorov' }
    'OKut' = @{ family='USSR-ORD-06'; name='库图佐夫勋章'; original='Орден Кутузова'; english='Order of Kutuzov' }
    'OHmel' = @{ family='USSR-ORD-07'; name='波格丹·赫梅利尼茨基勋章'; original='Орден Богдана Хмельницкого'; english='Order of Bohdan Khmelnytsky' }
    'ONevsk' = @{ family='USSR-ORD-08'; name='亚历山大·涅夫斯基勋章'; original='Орден Александра Невского'; english='Order of Alexander Nevsky' }
    'OUshak' = @{ family='USSR-ORD-09'; name='乌沙科夫勋章'; original='Орден Ушакова'; english='Order of Ushakov' }
    'ONahim' = @{ family='USSR-ORD-10'; name='纳希莫夫勋章'; original='Орден Нахимова'; english='Order of Nakhimov' }
    'ORStar' = @{ family='USSR-ORD-11'; name='红星勋章'; original='Орден Красной Звезды'; english='Order of the Red Star' }
    'OPatWar' = @{ family='USSR-ORD-12'; name='卫国战争勋章'; original='Орден Отечественной войны'; english='Order of the Patriotic War' }
    'ORbnLab' = @{ family='USSR-ORD-13'; name='劳动红旗勋章'; original='Орден Трудового Красного Знамени'; english='Order of the Red Banner of Labour' }
    'OFriend' = @{ family='USSR-ORD-14'; name='各族人民友谊勋章'; original='Орден Дружбы народов'; english='Order of Friendship of Peoples' }
    'OZnPoch' = @{ family='USSR-ORD-15'; name='荣誉勋章'; original='Орден «Знак Почёта»'; english='Order of the Badge of Honour' }
    'OSlava' = @{ family='USSR-ORD-16'; name='光荣勋章'; original='Орден Славы'; english='Order of Glory' }
    'OMatSl' = @{ family='USSR-ORD-17'; name='母亲光荣勋章'; original='Орден «Материнская слава»'; english='Order of Maternal Glory' }
    'OMatHero' = @{ family='USSR-ORD-18'; name='英雄母亲勋章'; original='Орден «Мать-героиня»'; english='Mother Heroine' }
    'OTrSlav' = @{ family='USSR-ORD-19'; name='劳动光荣勋章'; original='Орден Трудовой Славы'; english='Order of Labour Glory' }
    'OZaSlRod' = @{ family='USSR-ORD-20'; name='在苏联武装力量中为祖国服务勋章'; original='Орден «За службу Родине в Вооружённых Силах СССР»'; english='Order for Service to the Homeland in the Armed Forces of the USSR' }
    'OLMuzh' = @{ family='USSR-ORD-21'; name='个人英勇勋章'; original='Орден «За личное мужество»'; english='Order for Personal Courage' }
}

$index = Get-Page $indexUrl
$indexLinks = Get-Links $index.Html
$pageMap = [ordered]@{}
$indexEntryList = [System.Collections.Generic.List[object]]::new()
foreach ($link in $indexLinks) {
    $file = [System.IO.Path]::GetFileName(([System.Uri]::new([System.Uri]::new($indexUrl), $link.Href)).AbsolutePath)
    $stem = [System.IO.Path]::GetFileNameWithoutExtension($file)
    if (-not $idMap.Contains($stem)) { continue }
    $entry = $idMap[$stem]
    $entry['index_title'] = if ($link.Text) { $link.Text } elseif ($link.Alt) { $link.Alt } else { $null }
    $entry['index_page_url'] = [System.Uri]::new([System.Uri]::new($indexUrl), $link.Href).AbsoluteUri
    $entry['stem'] = $stem
    $pageMap[$entry['index_page_url']] = $entry
    $indexEntryList.Add([pscustomobject]@{ page_url=$entry['index_page_url']; page_title=$entry['index_title']; family=$entry['family']; order_name=$entry['original'] })
}

$allPages = [System.Collections.Generic.List[object]]::new()
$allImages = [System.Collections.Generic.List[object]]::new()
$allFamilies = [System.Collections.Generic.List[object]]::new()
$unvisited = [System.Collections.Generic.Queue[object]]::new()
foreach ($entry in $pageMap.Values) { $unvisited.Enqueue([pscustomobject]@{ Url=$entry['index_page_url']; Family=$entry['family']; Stem=$entry['stem'] }) }
$seenPages = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)

while ($unvisited.Count -gt 0) {
    $task = $unvisited.Dequeue()
    if (-not $seenPages.Add($task.Url)) { continue }
    $page = Get-Page $task.Url
    $title = [regex]::Match($page.Html, '(?is)<title[^>]*>(.*?)</title>').Groups[1].Value
    $title = (Get-VisibleText $title).Trim()
    $plain = Get-VisibleText $page.Html
    $links = Get-Links $page.Html
    $images = Get-ImageRows $page.Html $page.Url $plain
    $cleanImages = @($images | Sort-Object source_image_url -Unique)
    foreach ($img in $cleanImages) {
        $img.source_page_url = $page.Url
        $img.rights_status = '许可未确认；仅保留原站URL与说明，不下载、不嵌入。'
        $allImages.Add($img)
    }
    $familyMeta = $null
    foreach ($entry in $idMap.Values) { if ($entry.family -eq $task.Family) { $familyMeta = $entry; break } }
    $stemPattern = '^' + [regex]::Escape($task.Stem) + '\d+\.(?:htm|html?)$'
    $childLinks = [System.Collections.Generic.List[string]]::new()
    foreach ($link in $links) {
        if ($link.Href -match '^https?://') { $linkUrl = $link.Href } else { $linkUrl = [System.Uri]::new([System.Uri]::new($page.Url), $link.Href).AbsoluteUri }
        $linkFile = [System.IO.Path]::GetFileName(([System.Uri]::new($linkUrl)).AbsolutePath)
        if ($linkUrl -match '^https?://(?:www\.)?mondvor\.narod\.ru/' -and $linkFile -match $stemPattern) {
            if (-not $childLinks.Contains($linkUrl)) { $childLinks.Add($linkUrl) }
            if (-not $seenPages.Contains($linkUrl)) { $unvisited.Enqueue([pscustomobject]@{ Url=$linkUrl; Family=$task.Family; Stem=$task.Stem }) }
        }
    }
    $typeLabels = Get-TypeLabels $plain
    $candidate = [ordered]@{
        source_id = $sourceId
        source_row = $allPages.Count + 1
        scope = '苏联国家勋章目录；单枚章种及其具体实物版型/类型；1922–1991覆盖线索'
        page_title = $title
        page_title_original = $title
        english_name = $familyMeta.english
        original_name = $familyMeta.original
        aliases = @($familyMeta.name, $familyMeta.english, $familyMeta.original)
        date_candidate = @(Get-DateHints $plain)
        category = '苏联勋章'
        candidate_family_id = $familyMeta.family
        type_or_variant_clues = $typeLabels
        mint_maker_serial_attachment_clues = @(Get-ClueSnippets $plain)
        object_page_url = $page.Url
        parent_index_page_url = $indexUrl
        pagination_or_type_pages = @($childLinks)
        image_page_urls = @($cleanImages | ForEach-Object { $_.image_page_url })
        image_files = @($cleanImages | ForEach-Object { $_.source_file_name })
        source_short_excerpt = Get-SourceExcerpt $plain
        source_summary = 'Mondvor 原文页面；目录按其页面题名和正文分类记录。日期仅为页面提及候选，版型与具体实物对应仍按对象及图片上下文复核。'
        rights_status = 'Mondvor 图片复用许可未确认；本批只缓存页面及图片引用，不下载或嵌入图片。'
        image_inventory = $cleanImages
        status = 'raw_source_page_swept'
        checked_at = $today
        cache_path = $page.Path.Replace($ProjectRoot + '\', '').Replace('\','/')
        page_sha256 = [Convert]::ToHexString([System.Security.Cryptography.SHA256]::HashData($page.Bytes)).ToLowerInvariant()
    }
    $allPages.Add([pscustomobject]$candidate)
    $allFamilies.Add([pscustomobject]@{ family=$task.Family; page_url=$page.Url; title=$title; type_labels=$typeLabels; article_characters=$plain.Length; image_files=$cleanImages.Count; child_pages=@($childLinks) })
    Write-Host ("SCANNED {0} | {1} | labels={2} images={3} children={4}" -f $task.Family, $title, $typeLabels.Count, $cleanImages.Count, $childLinks.Count)
}

$rawLines = foreach ($pageRecord in $allPages) { $pageRecord | ConvertTo-Json -Depth 15 -Compress }
[System.IO.File]::WriteAllLines($rawOut, [string[]]$rawLines, [System.Text.UTF8Encoding]::new($false))

$serializedImages = @($allImages | Sort-Object source_image_url -Unique)
$serializedImages | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $imageIndexOut -Encoding UTF8
$crawlIndex = [ordered]@{
    as_of = $today
    source_id = $sourceId
    index_url = $indexUrl
    index_title = 'ОРДЕНА СССР'
    index_entries = @($indexEntryList)
    pages = @($allFamilies)
    page_count = $allPages.Count
    image_reference_count = $serializedImages.Count
    downloaded_image_count = @($serializedImages | Where-Object { $_.sha256 }).Count
    decoded_image_count = @($serializedImages | Where-Object { $_.decoded }).Count
    image_download_pending_count = @($serializedImages | Where-Object { -not $_.decoded }).Count
    image_download_status = 'Not downloaded: reuse permission was not confirmed for this source.'
    raw_candidates_path = $rawOut.Replace($ProjectRoot + '\', '').Replace('\','/')
    image_inventory_path = $imageIndexOut.Replace($ProjectRoot + '\', '').Replace('\','/')
    completion_rule = 'All 20 linked order articles and every same-stem numbered type/continuation page discovered from their internal page navigation; direct in-article image references inventoried and retained as URL-only references pending permission.'
}
$crawlIndex | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $crawlIndexOut -Encoding UTF8

Write-Host "RESULT pages=$($allPages.Count) families=$(@($allFamilies | Select-Object -ExpandProperty family -Unique).Count) image_refs=$($serializedImages.Count) downloaded=$($crawlIndex.downloaded_image_count) decoded=$($crawlIndex.decoded_image_count) raw=$rawOut"
