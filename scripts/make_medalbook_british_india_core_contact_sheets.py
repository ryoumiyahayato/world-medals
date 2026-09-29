"""Build contact sheets for the British India core-family cache."""
import make_medalbook_thailand_contact_sheets as sheets

sheets.MANIFEST = sheets.ROOT / "data/source_sweeps/medalbook_british_india_core_images_2026-09-28.json"
sheets.OUT = sheets.ROOT / "sources/pages/medalbook_british_india_core/contact_sheets"

if __name__ == "__main__":
    sheets.main()
