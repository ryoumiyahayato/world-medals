"""Recreate the reviewed Kuenker7375 back from the external source PDF."""
import argparse
import subprocess
import tempfile
from pathlib import Path
from PIL import Image

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--material-root', type=Path, required=True)
    args = parser.parse_args()
    root = args.material_root.resolve()
    target = root / 'assets/images/ottoman_kuenker299_batch5/lot_7375_back_pdf230.png'
    if target.exists():
        print('Existing recovered crop retained')
        return
    with tempfile.TemporaryDirectory(dir=root / 'mobile/build') as temporary:
        prefix = Path(temporary) / 'page230'
        subprocess.run(['pdftoppm', '-f', '230', '-l', '230', '-scale-to', '3200',
                        '-singlefile', '-png', str(root / 'sources/ottoman_atlas_packB_cache/kuenker-299-web.pdf'),
                        str(prefix)], check=True)
        with Image.open(prefix.with_suffix('.png')) as page:
            if page.size != (2262, 3200):
                raise ValueError('Unexpected source page dimensions')
            target.parent.mkdir(parents=True, exist_ok=True)
            page.crop((1140, 2165, 1680, 2720)).save(target)
    print('Recovered lot7375 back; source PDF and earlier wrong crop retained')

if __name__ == '__main__':
    main()
