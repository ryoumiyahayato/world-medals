"""Download every image exposed by the completed MedalBook Kazakhstan sweep."""
import download_medalbook_thailand_images as download
download.INPUT=download.ROOT/"data/raw_candidates/medalbook_kazakhstan.jsonl";download.OUT_DIR=download.ROOT/"assets/raw/medalbook_kazakhstan";download.MANIFEST=download.ROOT/"data/source_sweeps/medalbook_kazakhstan_images_2026-09-28.json";download.SOURCE_ID="medalbook_kazakhstan_images";download.BOUNDARY="All original image URLs exposed by the completed Kazakhstan awards sweep"
if __name__=="__main__":download.main()
