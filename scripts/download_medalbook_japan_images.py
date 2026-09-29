"""Download every image exposed by the completed MedalBook Japan sweep."""

import download_medalbook_thailand_images as download


download.INPUT = download.ROOT / "data/raw_candidates/medalbook_japan.jsonl"
download.OUT_DIR = download.ROOT / "assets/raw/medalbook_japan"
download.MANIFEST = download.ROOT / "data/source_sweeps/medalbook_japan_images_2026-09-28.json"
download.SOURCE_ID = "medalbook_japan_images"
download.BOUNDARY = "All original image URLs exposed by the completed 117-page MedalBook Japan sweep"


if __name__ == "__main__":
    download.main()
