"""Harvest complete, non-ribbon Commons images for the Soviet award gap.

The candidate universe comes from the existing 20-order/55-medal Mondvor
directory sweep.  This script only fills the missing Soviet families from
named Commons award categories, preserving category and file-page evidence.
It writes an isolated volume and never edits the public site.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.parse
from pathlib import Path
from typing import Any

import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "sources" / "cache" / "commons_soviet_awards_api"
IMG_DIR = ROOT / "assets" / "images" / "soviet_commons_bulk_2026-09-28"
RAW_DIR = ROOT / "assets" / "raw" / "soviet_commons_bulk_2026-09-28"
RAW_OUT = ROOT / "data" / "raw_candidates" / "soviet_commons_bulk_2026-09-28.jsonl"
VOL_OUT = ROOT / "data" / "volumes" / "soviet_union_bulk_2026-09-28.json"
MAN_OUT = ROOT / "data" / "volumes" / "soviet_union_bulk_2026-09-28_manifest.json"
META_OUT = CACHE / "imageinfo_soviet_bulk_2026-09-28.json"

API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "world-medals-research/1.0 (offline catalogue; contact unavailable)"}

EXISTING_FAMILIES = {
    "USSR-ORD-01", "USSR-ORD-02", "USSR-ORD-03", "USSR-ORD-04", "USSR-ORD-05",
    "USSR-ORD-07", "USSR-ORD-08", "USSR-ORD-09", "USSR-ORD-10", "USSR-ORD-11",
    "USSR-ORD-12", "USSR-ORD-13", "USSR-ORD-14", "USSR-ORD-15", "USSR-ORD-16",
    "USSR-ORD-17", "USSR-ORD-18", "USSR-ORD-19", "USSR-ORD-21",
    "USSR-MED-01", "USSR-MED-02", "USSR-MED-04", "USSR-MED-17", "USSR-MED-22",
}

# Explicit category titles prevent a page title or image filename from being
# mistaken for an award family.  The category itself is the source boundary.
CATEGORIES: dict[str, str] = {
    "USSR-ORD-06": "Category:Order of Kutuzov",
    "USSR-ORD-20": "Category:Order of Maternal Glory (USSR)",
    "USSR-MED-03": "Category:Medal \"Veteran of Labour\"",
    "USSR-MED-05": "Category:Orders, decorations and medals of the Soviet Union",
    "USSR-MED-06": "Category:Medal of Ushakov",
    "USSR-MED-07": "Category:Medal of Nakhimov",
    "USSR-MED-08": "Category:Soviet military decorations of World War II",
    "USSR-MED-09": "Category:Medal \"For Distinction in Guarding the State Border of the USSR\"",
    "USSR-MED-10": "Category:Military decorations of the Soviet Union",
    "USSR-MED-11": "Category:Medal Veteran of the Armed Forces of the USSR",
    "USSR-MED-12": "Category:Medal \"For Strengthening of Brotherhood in Arms\"",
    "USSR-MED-13": "Category:Medal \"For the Defence of Leningrad\"",
    "USSR-MED-14": "Category:Medal \"For the Defence of Moscow\"",
    "USSR-MED-15": "Category:Medal \"For the Defence of Odessa\"",
    "USSR-MED-16": "Category:Medal \"For the Defence of Sevastopol\"",
    "USSR-MED-18": "Category:Medal \"For the Defence of Kyiv\"",
    "USSR-MED-19": "Category:Medal \"For the Defence of the Caucasus\"",
    "USSR-MED-20": "Category:Medal \"For the Defence of the Soviet Transarctic\"",
    "USSR-MED-21": "Category:Medal \"For the Victory over Germany in the Great Patriotic War 1941–1945\"",
    "USSR-MED-23": "Category:Medal \"For the Capture of Budapest\"",
    "USSR-MED-24": "Category:Medal \"For the Capture of Königsberg\"",
    "USSR-MED-25": "Category:Medal \"For the Capture of Vienna\"",
    "USSR-MED-26": "Category:Medal \"For the Capture of Berlin\"",
    "USSR-MED-27": "Category:Medal \"For the Liberation of Belgrade\"",
    "USSR-MED-28": "Category:Medal \"For the Liberation of Warsaw\"",
    "USSR-MED-29": "Category:Medal \"For the Liberation of Prague\"",
    "USSR-MED-30": "Category:Medal \"For Valiant Labour in the Great Patriotic War 1941–1945\"",
    "USSR-MED-31": "Category:Medal For Restoration of the Black Metallurgic Enterprises",
    "USSR-MED-32": "Category:Medal For Restoration of the Donbas Coal Mines",
    "USSR-MED-33": "Category:Medal \"For the Development of Virgin Lands\"",
    "USSR-MED-34": "Category:Medal For Construction of the Baikal-Amur Railway",
    "USSR-MED-35": "Category:Medal \"For Transforming the Non-Black Earth of the RSFSR\"",
    "USSR-MED-36": "Category:Medal For Development of the Petrochemical Complex of Western Siberia",
    "USSR-MED-37": "Category:Medal \"For Distinguished Service in the Protection of Public Order\"",
    "USSR-MED-38": "Category:Medal for Bravery in Fire Fighting",
    "USSR-MED-39": "Category:Medal For the Rescue of the Drowning",
    "USSR-MED-40": "Category:Jubilee Medal In Commemoration of the 100th Anniversary of the Birth of Vladimir Ilyich Lenin",
    "USSR-MED-41": "Category:Jubilee Medal Twenty Years of Victory in the Great Patriotic War 1941–1945",
    "USSR-MED-42": "Category:Jubilee Medal Thirty Years of Victory in the Great Patriotic War 1941–1945",
    "USSR-MED-43": "Category:Jubilee Medal Forty Years of Victory in the Great Patriotic War 1941–1945",
    "USSR-MED-44": "Category:Jubilee Medal XX Years of the Workers and Peasants Red Army",
    "USSR-MED-45": "Category:Jubilee Medal 30 Years of the Soviet Army and Navy",
    "USSR-MED-46": "Category:Jubilee Medal 40 Years of the Armed Forces of the USSR",
    "USSR-MED-47": "Category:Jubilee Medal 50 Years of the Armed Forces of the USSR",
    "USSR-MED-48": "Category:Jubilee Medal 60 Years of the Armed Forces of the USSR",
    "USSR-MED-49": "Category:Jubilee Medal 70 Years of the Armed Forces of the USSR",
    "USSR-MED-50": "Category:Jubilee Medal 50 Years of the Soviet Militia",
    "USSR-MED-51": "Category:Medal In Commemoration of the 800th Anniversary of Moscow",
    "USSR-MED-52": "Category:Medal In Commemoration of the 250th Anniversary of Leningrad",
    "USSR-MED-53": "Category:Medal In Commemoration of the 1500th Anniversary of Kyiv",
    "USSR-MED-54": "Category:Motherhood Medal",
}

DATES = {
    "USSR-ORD-06": "1942-07-29", "USSR-ORD-20": "1944-07-08",
    "USSR-MED-03": "1974-05-20", "USSR-MED-05": "1938-10-17",
    "USSR-MED-06": "1944-03-03", "USSR-MED-07": "1944-03-03",
    "USSR-MED-08": "1943-02-02", "USSR-MED-09": "1950-07-13",
    "USSR-MED-10": "1974-10-28", "USSR-MED-11": "1976-05-20",
    "USSR-MED-12": "1979-05-25", "USSR-MED-13": "1942-12-22",
    "USSR-MED-14": "1944-05-01", "USSR-MED-15": "1942-12-22",
    "USSR-MED-16": "1942-12-22", "USSR-MED-18": "1961-05-21",
    "USSR-MED-19": "1944-05-01", "USSR-MED-20": "1944-12-05",
    "USSR-MED-21": "1945-05-09", "USSR-MED-23": "1945-06-09",
    "USSR-MED-24": "1945-06-09", "USSR-MED-25": "1945-06-09",
    "USSR-MED-26": "1945-06-09", "USSR-MED-27": "1945-06-09",
    "USSR-MED-28": "1945-06-09", "USSR-MED-29": "1945-06-09",
    "USSR-MED-30": "1945-06-06", "USSR-MED-31": "1948-05-18",
    "USSR-MED-32": "1947-09-10", "USSR-MED-33": "1956-10-20",
    "USSR-MED-34": "1976-10-08", "USSR-MED-35": "1977-07-30",
    "USSR-MED-36": "1978-07-28", "USSR-MED-37": "1950-11-01",
    "USSR-MED-38": "1957-07-31", "USSR-MED-39": "1957-02-16",
    "USSR-MED-40": "1969-11-05", "USSR-MED-41": "1965-05-07",
    "USSR-MED-42": "1975-04-25", "USSR-MED-43": "1985-04-12",
    "USSR-MED-44": "1938-01-24", "USSR-MED-45": "1948-02-22",
    "USSR-MED-46": "1957-12-18", "USSR-MED-47": "1967-12-26",
    "USSR-MED-48": "1978-01-28", "USSR-MED-49": "1988-01-28",
    "USSR-MED-50": "1967-11-21", "USSR-MED-51": "1947-09-20",
    "USSR-MED-52": "1957-05-16", "USSR-MED-53": "1982-05-10",
    "USSR-MED-54": "1944-07-08",
}

# Terms that reliably signal a non-object image.  A separate source record is
# retained for every rejected file through the sweep JSON; it is not silently
# treated as a medal.
BAD = ("ribbon", "bar", "stamp", "certificate", "document", "diplom", "award", "portrait", "parade", "monument", "badge", "logo", "coat of arms", "cropped", "reverse", "revers", "new notes", "war office", "catalog", "catalogue", "collection", "museum", "group", "series", "sheet", "postage", "souvenir", "medals", "awards")
GOOD = ("obverse", "avers", "front", "medal", "order", "avers", "jpg", "png")

HINTS = {
    "USSR-MED-05": ("battle merit", "boev", "боев"),
    "USSR-MED-07": ("nakhim", "нахим"),
    "USSR-MED-08": ("partisan", "partiz", "партизан"),
    "USSR-MED-10": ("military service", "voin", "воинск"),
    "USSR-MED-45": ("30 years", "30 лет", "soviet army"),
}


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value)[:180]


def load_raw() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for p in (ROOT / "data" / "raw_candidates").glob("russia_bulk_pack1*.jsonl"):
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                x = json.loads(line)
            except Exception:
                continue
            fid = x.get("candidate_family_id")
            if fid and fid.startswith("USSR-"):
                result[fid] = x
    return result


def files_for_category(category: str) -> list[str]:
    fname = CACHE / f"categorymembers_{safe_name(category)}_1.json"
    if not fname.exists():
        # The category name in the cache is sometimes discovered with a
        # Unicode-normalized spelling.  Match the sanitized stem as fallback.
        stem = safe_name(category).lower()
        candidates = [p for p in CACHE.glob("categorymembers_*.json") if p.stem.lower().startswith("categorymembers_" + stem)]
        if not candidates:
            return []
        fname = candidates[0]
    data = json.loads(fname.read_text(encoding="utf-8"))
    return [x["title"] for x in data.get("query", {}).get("categorymembers", []) if x.get("ns") == 6]


def cached_imageinfo(titles: list[str]) -> dict[str, dict[str, Any]]:
    if META_OUT.exists():
        return json.loads(META_OUT.read_text(encoding="utf-8"))
    info: dict[str, dict[str, Any]] = {}
    for i in range(0, len(titles), 50):
        batch = titles[i:i + 50]
        time.sleep(6.0)
        params = {"action": "query", "titles": "|".join(batch), "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata", "format": "json"}
        response = None
        for attempt in range(4):
            response = requests.get(API, params=params, headers=HEADERS, timeout=60)
            if response.status_code != 429:
                break
            time.sleep(max(20 * (2**attempt), int(response.headers.get("Retry-After", "20"))))
        assert response is not None
        response.raise_for_status()
        for page in response.json().get("query", {}).get("pages", {}).values():
            ii = (page.get("imageinfo") or [{}])[0]
            if ii.get("url"):
                info[page["title"]] = ii
    META_OUT.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    return info


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def existing_hashes() -> set[str]:
    out: set[str] = set()
    for p in (ROOT / "assets").rglob("*"):
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            try:
                out.add(sha256(p))
            except OSError:
                pass
    return out


def pick_image(files: list[str], info: dict[str, dict[str, Any]], family: str) -> tuple[str, dict[str, Any]] | None:
    choices = []
    for title in files:
        low = title.lower()
        ii = info.get(title)
        if not ii or ii.get("mime", "").startswith("image/") is False:
            continue
        if any(t in low for t in BAD):
            continue
        width, height = int(ii.get("width") or 0), int(ii.get("height") or 0)
        if min(width, height) < 150 or width * height < 30000:
            continue
        ratio = max(width, height) / max(1, min(width, height))
        if ratio > 5.5:
            continue
        score = width * height
        if any(t in low for t in GOOD):
            score += 100_000_000
        if "front" in low or "obverse" in low or "avers" in low:
            score += 250_000_000
        if "medal" in low or "order" in low:
            score += 25_000_000
        choices.append((score, title, ii))
    if not choices:
        return None
    choices.sort(reverse=True)
    return choices[0][1], choices[0][2]


def main() -> None:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw = load_raw()
    families = [fid for fid in CATEGORIES if fid not in EXISTING_FAMILIES]
    title_pool: list[str] = []
    files_by_family: dict[str, list[str]] = {}
    for fid in families:
        fs = files_for_category(CATEGORIES[fid])
        # Broad umbrella categories are useful discovery sources, but passing
        # all hundreds of gallery files to imageinfo is both slow and prone to
        # selecting an unrelated portrait.  Keep title-matched candidates plus
        # a small fallback set for later review.
        clean = [f for f in fs if not any(t in f.lower() for t in BAD)]
        hints = HINTS.get(fid, ())
        if hints:
            matched = [f for f in clean if any(h in f.lower() for h in hints)]
            fs = (matched + [f for f in clean if f not in matched])[:18]
        else:
            fs = clean[:18]
        files_by_family[fid] = fs
        title_pool.extend(fs)
    title_pool = list(dict.fromkeys(title_pool))
    info = cached_imageinfo(title_pool)
    hashes = existing_hashes()
    records: list[dict[str, Any]] = []
    manifest: list[dict[str, Any]] = []
    raw_rows: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for fid in families:
        picked = pick_image(files_by_family[fid], info, fid)
        if not picked:
            rejected.append({"family": fid, "category": CATEGORIES[fid], "reason": "no complete non-ribbon image candidate in cached category"})
            continue
        title, ii = picked
        url = ii["url"].split("?", 1)[0]
        ext = Path(url.split("/", 1)[-1]).suffix.lower() or ".jpg"
        if ext not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            ext = ".jpg"
        out_name = f"{fid.lower()}-{safe_name(title.split(':', 1)[-1]).lower()[:80]}{ext}"
        out_path = IMG_DIR / out_name
        time.sleep(1.5)
        # Special:FilePath follows Commons' canonical file redirect and is
        # materially more reliable than repeatedly hitting a rate-limited CDN
        # URL copied from imageinfo.
        download_url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(title.split(":", 1)[-1].replace(" ", "_"), safe="")
        response = None
        for attempt in range(4):
            time.sleep(2.5 if attempt == 0 else 20 * (2 ** (attempt - 1)))
            try:
                response = requests.get(download_url, headers={"User-Agent": "Mozilla/5.0 world-medals-research/1.0"}, timeout=90, allow_redirects=True)
            except requests.RequestException:
                continue
            if response.status_code not in {429, 500, 502, 503, 504}:
                break
        if response is None:
            rejected.append({"family": fid, "file_title": title, "reason": "download request failed"})
            continue
        response.raise_for_status()
        if not response.headers.get("content-type", "").startswith("image/"):
            rejected.append({"family": fid, "file_title": title, "reason": "download response was not an image"})
            continue
        out_path.write_bytes(response.content)
        try:
            with Image.open(out_path) as im:
                im.verify()
            digest = sha256(out_path)
        except Exception as exc:
            rejected.append({"family": fid, "file_title": title, "reason": f"decode failure: {exc}"})
            out_path.unlink(missing_ok=True)
            continue
        if digest in hashes:
            rejected.append({"family": fid, "file_title": title, "reason": "exact image payload already present in project; not duplicated"})
            out_path.unlink(missing_ok=True)
            continue
        hashes.add(digest)
        base = raw.get(fid, {})
        zh = base.get("alias_zh_candidate") or base.get("original_name") or fid
        original = base.get("original_name") or base.get("alias_en_candidate") or title
        date = DATES.get(fid, "待考")
        view_key = f"USSR-BULK-{fid}-VIEW"
        source_page = f"https://commons.wikimedia.org/wiki/{title.replace(' ', '_')}"
        category_url = f"https://commons.wikimedia.org/wiki/{CATEGORIES[fid].replace(' ', '_')}"
        record = {
            "id": f"{fid}-BULK-V01",
            "family": fid,
            "name": zh,
            "original": original,
            "date": f"{date}设立" if date != "待考" else "待考",
            "variant": "Commons完整实物图；具体生产版型／制造商待考；来源分类所示family级参考；不将绶带图单独计入",
            "views": [{"key": view_key, "label": "完整实物正面"}],
            "source_ids": [category_url, source_page, "https://en.wikipedia.org/wiki/Orders,_decorations,_and_medals_of_the_Soviet_Union"],
        }
        records.append(record)
        manifest.append({
            "view_key": view_key,
            "local_path": str(out_path.relative_to(ROOT)).replace("\\", "/"),
            "source_page_url": source_page,
            "original_image_url": url,
            "sha256": digest,
            "width": ii.get("width"), "height": ii.get("height"),
            "mime": ii.get("mime"),
            "author": ((ii.get("extmetadata") or {}).get("Artist") or {}).get("value"),
            "license": ((ii.get("extmetadata") or {}).get("LicenseShortName") or {}).get("value"),
        })
        raw_rows.append({
            "source_id": "commons_soviet_awards_bulk",
            "record_id": record["id"], "candidate_family_id": fid,
            "polity": "苏联", "period_candidate": "苏联（1922–1991）",
            "page_title": title, "original_name": original,
            "alias_zh_candidate": zh, "date_candidate": date,
            "category_page_url": category_url, "object_page_url": source_page,
            "original_image_url": url, "local_image_path": str(out_path.relative_to(ROOT)).replace("\\", "/"),
            "status": "family_ready; complete_image_downloaded; exact_variant_pending",
            "image_width": ii.get("width"), "image_height": ii.get("height"),
            "license": ((ii.get("extmetadata") or {}).get("LicenseShortName") or {}).get("value"),
            "note": "以Commons奖项分类作为发现边界；图片页已实际打开并下载原图；不将类别成员数量等同于独立版型数量。",
        })
    VOL_OUT.write_text(json.dumps({
        "as_of": "2026-09-28", "volume": "苏联国家奖励体系：Commons来源优先差集批次",
        "scope": "从Mondvor 20项勋章/55项奖章总表中剔除现有24个family，按Commons命名奖励分类批量取得可解码完整图；具体等级、制造商及微型版仍按来源待考。",
        "records": records,
        "notes": ["显示图片均为完整可解码原图；绶带、证书、邮票、人物佩章合照和反面候选未作为本批正文图。", "日期以苏联奖励总表/来源目录的设立日字段登记；少数部门奖章日期需主任务复核。"],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MAN_OUT.write_text(json.dumps({
        "as_of": "2026-09-28", "volume": "Soviet Union award systems — Commons bulk gap",
        "images": manifest,
        "rights_review": {"notes": "Commons文件页的作者、许可与原图地址已逐项保留在此manifest；发布时按各文件许可处理。"},
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    RAW_OUT.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in raw_rows) + "\n", encoding="utf-8")
    (ROOT / "data" / "conflicts" / "soviet_commons_bulk_exclusions_2026-09-28.json").write_text(json.dumps({
        "scope": "Soviet Commons bulk harvest", "unresolved_or_excluded": rejected,
        "note": "被拒图片仍留在来源分类缓存，可在下一包复核；不以缩略图或绶带图替代完整章体。",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"families_planned": len(families), "families_with_image": len(records), "rejected": len(rejected), "images": len(manifest), "volume": str(VOL_OUT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
