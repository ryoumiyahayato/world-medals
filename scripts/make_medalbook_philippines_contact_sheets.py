"""Build contact sheets for the complete MedalBook Philippines image cache."""

import make_medalbook_thailand_contact_sheets as sheets


sheets.MANIFEST = sheets.ROOT / "data/source_sweeps/medalbook_philippines_images_2026-09-28.json"
sheets.OUT = sheets.ROOT / "sources/pages/medalbook_philippines/contact_sheets"


if __name__ == "__main__": sheets.main()
