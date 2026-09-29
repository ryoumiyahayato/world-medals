"""Download every image exposed by the completed MedalBook Nepal sweep."""
import download_medalbook_thailand_images as download

download.INPUT=download.ROOT/"data/raw_candidates/medalbook_nepal.jsonl"
download.OUT_DIR=download.ROOT/"assets/raw/medalbook_nepal"
download.MANIFEST=download.ROOT/"data/source_sweeps/medalbook_nepal_images_2026-09-28.json"
download.SOURCE_ID="medalbook_nepal_images"
download.BOUNDARY="All original image URLs exposed by the completed Nepal orders and medals sweep"
if __name__=="__main__": download.main()
