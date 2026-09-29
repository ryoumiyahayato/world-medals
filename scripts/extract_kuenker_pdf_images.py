"""Extract embedded catalogue photographs from selected Kuenker 299 pages.

The PDF keeps each object face as a separate JPEG.  This helper preserves those
embedded files verbatim (apart from Pillow's normal file wrapper) so that they
can be reviewed and paired before inclusion in the catalogue.
"""

from pathlib import Path
import sys

from pypdf import PdfReader


PDF = Path("sources/ottoman_atlas_packB_cache/kuenker-299-web.pdf")
OUT = Path("tmp/pdfs/kuenker299_embedded")


def main() -> None:
    pages = [int(value) for value in sys.argv[1:]]
    if not pages:
        raise SystemExit("Pass one or more one-based PDF page numbers")

    reader = PdfReader(PDF)
    for page_number in pages:
        page_dir = OUT / f"page_{page_number:03d}"
        page_dir.mkdir(parents=True, exist_ok=True)
        page = reader.pages[page_number - 1]
        for index, image_file in enumerate(page.images, start=1):
            # Im1 is the repeated page masthead; retain it in the review cache,
            # but never promote it into the public catalogue.
            image = image_file.image
            suffix = ".png" if image_file.name.lower().endswith(".png") else ".jpg"
            image.save(page_dir / f"{index:02d}_{image_file.name}{suffix}")
        print(f"page {page_number}: {len(page.images)} embedded images")


if __name__ == "__main__":
    main()
