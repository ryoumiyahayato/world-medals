"""Sweep the complete World Awards Brunei reference catalogue."""
import sweep_wawards_cambodia as sweep

sweep.PDFS = [("brunei", sweep.ROOT / "sources/books/brunei/wawards_brunei.pdf")]
sweep.PAGE_DIR = sweep.ROOT / "sources/pages/wawards_brunei"
sweep.RAW_DIR = sweep.ROOT / "assets/raw/wawards_brunei"
sweep.RAW_OUT = sweep.ROOT / "data/raw_candidates/wawards_brunei.jsonl"
sweep.SWEEP_OUT = sweep.ROOT / "data/source_sweeps/wawards_brunei_2026-09-28.json"
sweep.COUNTRY_SLUG = "brunei"
sweep.URL_SCOPE = "/en/brunei/"
sweep.IMAGE_SCOPE = "/images/brunei/"
sweep.CATALOG_ID_PATTERN = r"BRN\d{3}"
sweep.SOURCE_URLS = ["https://wawards.org/images/brunei/brunei.pdf"]

if __name__ == "__main__":
    sweep.main()
