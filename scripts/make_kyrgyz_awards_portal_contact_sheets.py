"""Build contact sheets for the downloaded part of the official Kyrgyz awards portal."""
import make_medalbook_thailand_contact_sheets as sheets
sheets.MANIFEST=sheets.ROOT/'data/source_sweeps/kyrgyz_awards_portal_2026-09-28.json';sheets.OUT=sheets.ROOT/'sources/pages/kyrgyz_awards_portal/contact_sheets'
if __name__=='__main__':sheets.main()
