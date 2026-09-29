"""Download every image exposed by the completed MedalBook Brunei sweep."""

import download_medalbook_thailand_images as download


download.INPUT = download.ROOT / "data/raw_candidates/medalbook_brunei.jsonl"
download.OUT_DIR = download.ROOT / "assets/raw/medalbook_brunei"
download.MANIFEST = download.ROOT / "data/source_sweeps/medalbook_brunei_images_2026-09-28.json"
download.SOURCE_ID = "medalbook_brunei_images"
download.BOUNDARY = "All original image URLs exposed by the completed Brunei catalogue sweep"


if __name__ == "__main__":
    download.main()
