"""Build contact sheets for the complete World Awards Brunei catalogue."""
import make_wawards_cambodia_contact_sheets as sheets

sheets.INPUT = sheets.ROOT / "assets/raw/wawards_brunei"
sheets.OUTPUT = sheets.ROOT / "sources/pages/wawards_brunei/contact_sheets"

if __name__ == "__main__":
    sheets.main()
