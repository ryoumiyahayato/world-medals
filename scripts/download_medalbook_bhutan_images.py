"""Download every image exposed by the completed MedalBook Bhutan sweep."""
import download_medalbook_thailand_images as download
download.INPUT=download.ROOT/"data/raw_candidates/medalbook_bhutan.jsonl"; download.OUT_DIR=download.ROOT/"assets/raw/medalbook_bhutan"; download.MANIFEST=download.ROOT/"data/source_sweeps/medalbook_bhutan_images_2026-09-28.json"; download.SOURCE_ID="medalbook_bhutan_images"; download.BOUNDARY="All original image URLs exposed by the completed Bhutan orders and medals sweep"
if __name__=="__main__": download.main()
