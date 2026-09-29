"""Download every image exposed by the completed MedalBook Tajikistan sweep."""
import download_medalbook_thailand_images as download
download.INPUT=download.ROOT/'data/raw_candidates/medalbook_tajikistan.jsonl';download.OUT_DIR=download.ROOT/'assets/raw/medalbook_tajikistan';download.MANIFEST=download.ROOT/'data/source_sweeps/medalbook_tajikistan_images_2026-09-28.json';download.SOURCE_ID='medalbook_tajikistan_images';download.BOUNDARY='All original image URLs exposed by the completed Tajikistan order and medal sweeps'
if __name__=='__main__':download.main()
