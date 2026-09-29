"""Build contact sheets for the complete ODM Bhutan cache."""
import make_medalbook_thailand_contact_sheets as sheets
sheets.MANIFEST=sheets.ROOT/"data/source_sweeps/medals_org_bhutan_2026-09-28.json"; sheets.OUT=sheets.ROOT/"sources/pages/medals_org_bhutan/contact_sheets"
if __name__=="__main__": sheets.main()
