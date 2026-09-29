"""Download images exposed by the British India core-family sweep."""
import download_medalbook_thailand_images as download

download.INPUT = download.ROOT / "data/raw_candidates/medalbook_british_india_core.jsonl"
download.OUT_DIR = download.ROOT / "assets/raw/medalbook_british_india_core"
download.MANIFEST = download.ROOT / "data/source_sweeps/medalbook_british_india_core_images_2026-09-28.json"
download.SOURCE_ID = "medalbook_british_india_core_images"
download.BOUNDARY = "All original image URLs exposed by the complete selected British India family pages"

if __name__ == "__main__":
    download.main()
