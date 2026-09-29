"""Download every image exposed by the completed MedalBook Sri Lanka sweep."""
import download_medalbook_thailand_images as download
download.INPUT=download.ROOT/"data/raw_candidates/medalbook_sri_lanka.jsonl";download.OUT_DIR=download.ROOT/"assets/raw/medalbook_sri_lanka";download.MANIFEST=download.ROOT/"data/source_sweeps/medalbook_sri_lanka_images_2026-09-28.json";download.SOURCE_ID="medalbook_sri_lanka_images";download.BOUNDARY="All original image URLs exposed by the completed Sri Lanka awards sweep"
if __name__=="__main__":download.main()
