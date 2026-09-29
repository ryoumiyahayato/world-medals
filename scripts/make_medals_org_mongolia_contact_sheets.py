"""Build contact sheets for the complete medals.org.uk Mongolia source."""

import make_medalbook_thailand_contact_sheets as sheets


sheets.MANIFEST = sheets.ROOT / "data/source_sweeps/medals_org_mongolia_2026-09-28.json"
sheets.OUT = sheets.ROOT / "sources/pages/medals_org_mongolia/contact_sheets"


if __name__ == "__main__":
    sheets.main()
