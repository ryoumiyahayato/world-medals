"""Extract the reviewed native Kuenker7375 back from the external source PDF."""
import argparse
from pathlib import Path
from pypdf import PdfReader

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--material-root', type=Path, required=True)
    args = parser.parse_args()
    root = args.material_root.resolve()
    target = root / 'assets/images/ottoman_kuenker299_batch5/lot_7375_back_pdf230_native.jpg'
    if target.exists():
        print('Existing recovered crop retained')
        return
    page = PdfReader(root / 'sources/ottoman_atlas_packB_cache/kuenker-299-web.pdf').pages[229]
    matches = [image for image in page.images if image.name == 'Im7.jpg']
    if len(matches) != 1 or matches[0].image.size != (286, 278):
        raise ValueError('Unexpected page230 image object or dimensions; review required')
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as output:
        output.write(matches[0].data)
    print('Extracted native286x278 lot7375 back; source PDF and earlier crops retained')

if __name__ == '__main__':
    main()
