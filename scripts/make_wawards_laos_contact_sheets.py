"""Build contact sheets for the complete current Wawards Laos lists."""
import make_wawards_cambodia_contact_sheets as sheets

sheets.INPUT = sheets.ROOT / "assets/raw/wawards_laos"
sheets.OUTPUT = sheets.ROOT / "sources/pages/wawards_laos/contact_sheets"

if __name__ == "__main__":
    sheets.main()
