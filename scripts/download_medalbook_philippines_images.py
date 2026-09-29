"""Download every image exposed by the completed MedalBook Philippines sweep."""

import download_medalbook_thailand_images as download


download.INPUT = download.ROOT / "data/raw_candidates/medalbook_philippines.jsonl"
download.OUT_DIR = download.ROOT / "assets/raw/medalbook_philippines"
download.MANIFEST = download.ROOT / "data/source_sweeps/medalbook_philippines_images_2026-09-28.json"
download.SOURCE_ID = "medalbook_philippines_images"
download.BOUNDARY = "All original image URLs exposed by the completed Philippines catalogue sweep"


if __name__ == "__main__": download.main()
