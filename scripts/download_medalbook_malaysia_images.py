"""Download every image exposed by the completed MedalBook Malaysia sweep."""

import download_medalbook_thailand_images as download


download.INPUT = download.ROOT / "data/raw_candidates/medalbook_malaysia.jsonl"
download.OUT_DIR = download.ROOT / "assets/raw/medalbook_malaysia"
download.MANIFEST = download.ROOT / "data/source_sweeps/medalbook_malaysia_images_2026-09-28.json"
download.SOURCE_ID = "medalbook_malaysia_images"
download.BOUNDARY = "All original image URLs exposed by the completed Malaysia federal and state catalogue sweep"


if __name__ == "__main__": download.main()
