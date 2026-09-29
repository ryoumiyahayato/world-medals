"""Build contact sheets for the complete MedalBook Republic of China cache."""

import make_medalbook_thailand_contact_sheets as sheets

sheets.MANIFEST = sheets.ROOT / "data/source_sweeps/medalbook_republic_of_china_images_2026-09-28.json"
sheets.OUT = sheets.ROOT / "sources/pages/medalbook_republic_of_china/contact_sheets"

if __name__ == "__main__":
    sheets.main()
