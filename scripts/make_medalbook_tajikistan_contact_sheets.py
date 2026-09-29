"""Build contact sheets for the complete MedalBook Tajikistan cache."""
import make_medalbook_thailand_contact_sheets as sheets
sheets.MANIFEST=sheets.ROOT/'data/source_sweeps/medalbook_tajikistan_images_2026-09-28.json';sheets.OUT=sheets.ROOT/'sources/pages/medalbook_tajikistan/contact_sheets'
if __name__=='__main__':sheets.main()
