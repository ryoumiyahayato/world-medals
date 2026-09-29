"""Download every image exposed by the completed MedalBook Pakistan sweep."""
import download_medalbook_thailand_images as download

download.INPUT = download.ROOT / "data/raw_candidates/medalbook_pakistan.jsonl"
download.OUT_DIR = download.ROOT / "assets/raw/medalbook_pakistan"
download.MANIFEST = download.ROOT / "data/source_sweeps/medalbook_pakistan_images_2026-09-28.json"
download.SOURCE_ID = "medalbook_pakistan_images"
download.BOUNDARY = "All original image URLs exposed by the completed Pakistan orders and medals sweep"

if __name__ == "__main__":
    download.main()
