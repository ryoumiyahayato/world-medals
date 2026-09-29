"""Download every image exposed by the completed MedalBook Cambodia sweep."""
import download_medalbook_thailand_images as download

download.INPUT = download.ROOT / "data/raw_candidates/medalbook_cambodia.jsonl"
download.OUT_DIR = download.ROOT / "assets/raw/medalbook_cambodia"
download.MANIFEST = download.ROOT / "data/source_sweeps/medalbook_cambodia_images_2026-09-28.json"
download.SOURCE_ID = "medalbook_cambodia_images"
download.BOUNDARY = "All original image URLs exposed by the completed Cambodia catalogue sweep"

if __name__ == "__main__":
    download.main()
