"""Local WAWARDS colour-matte proposals; manual approval remains separate."""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageOps

from background_trim import remove_edge_light
from prepare_display import material_root

ROOT = Path(__file__).resolve().parents[2]
BACKGROUND = (223, 189, 141)
TEMPLATE_SOURCE = 'assets/images/wawards_tajikistan/tjk018_medal_02.jpg'
TEMPLATE_BOX = (348, 465, 424, 491)


def propose(frame, template, maximum=12):
    import cv2
    import numpy as np

    if frame.size != (600, 600):
        raise ValueError('Manual review required for a different source layout')
    rgb = frame.convert('RGB')
    corners = [(0, 0), (599, 0), (0, 599), (599, 599)]
    if any(max(abs(a-b) for a, b in zip(rgb.getpixel(p), BACKGROUND)) > 4
           for p in corners):
        raise ValueError('Manual review required for a different background')
    search = cv2.cvtColor(np.asarray(rgb)[400:600, 100:500], cv2.COLOR_RGB2GRAY)
    scores = cv2.matchTemplate(search, template, cv2.TM_CCOEFF_NORMED)
    _, score, _, location = cv2.minMaxLoc(scores)
    if score < .90:
        raise ValueError('Source watermark location is uncertain')
    x, y = location[0]+100, location[1]+400
    # These offsets preserve the entire source wordmark, not only the matched
    # right-hand letters. Extra canvas protects faint antialiased strokes.
    rectangle = [max(0, x-202), max(0, y-9), min(599, x+78), min(599, y+31)]
    differences = [ImageChops.difference(channel, Image.new('L', frame.size, value))
                   for channel, value in zip(rgb.split(), BACKGROUND)]
    delta = ImageChops.lighter(ImageChops.lighter(differences[0], differences[1]),
                               differences[2])
    similarity = ImageOps.invert(delta)
    probe = Image.merge('RGB', (similarity, similarity, similarity)).convert('RGBA')
    probe.putalpha(frame.getchannel('A'))
    alpha = remove_edge_light(probe, 255-maximum, 0).getchannel('A')
    ImageDraw.Draw(alpha).rectangle(rectangle, fill=255)
    alpha = ImageChops.multiply(alpha, frame.getchannel('A'))
    candidate = frame.copy()
    candidate.putalpha(alpha)
    return candidate, {'templateScore': round(score, 6),
                       'templateMatch': [x, y, x+template.shape[1], y+template.shape[0]],
                       'watermarkRectangle': rectangle,
                       'removedFraction': round(alpha.histogram()[0]/360000, 6)}


def run():
    import cv2
    import numpy as np

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start', type=int, required=True)
    parser.add_argument('--count', type=int, required=True)
    parser.add_argument('--prefix', default='assets/images/wawards_tajikistan/')
    parser.add_argument('--output', default='mobile/build/colour-background-proposals')
    args = parser.parse_args()
    if args.start < 0 or args.count <= 0:
        parser.error('Select a finite, positive queue segment')
    materials = material_root(ROOT)
    output = (ROOT/args.output).resolve()
    if not output.is_relative_to(ROOT/'mobile/build'):
        parser.error('Proposal output must remain inside this project build directory')
    output.mkdir(parents=True, exist_ok=True)
    template_path = materials/TEMPLATE_SOURCE
    with Image.open(template_path) as source:
        source.load()
        if source.size != (600, 600):
            raise ValueError('Watermark template source layout changed')
        template = cv2.cvtColor(np.asarray(source.convert('RGB').crop(TEMPLATE_BOX)),
                                cv2.COLOR_RGB2GRAY)
    queue_path = ROOT/'mobile/build/background-continuation/queue.json'
    if queue_path.exists():
        queue = json.loads(queue_path.read_text(encoding='utf-8'))
    else:
        portable = json.loads((ROOT/'data/release-input.json').read_text(encoding='utf-8'))
        queue = list(portable['images'])
    selected = [(i, p) for i, p in enumerate(queue)
                if args.start <= i < args.start+args.count and p.startswith(args.prefix)]
    proposals = blocked = cached = 0
    for index, relative in selected:
        report_path = output/f'{index:05}.json'
        path = (materials/relative).resolve()
        if not path.is_relative_to(materials):
            raise ValueError('Source path escaped the material directory')
        before = path.stat()
        if report_path.exists():
            previous = json.loads(report_path.read_text(encoding='utf-8'))
            if previous['file'] != relative:
                raise ValueError('Queue changed; select a new output directory')
            if (previous.get('sourceBytes'), previous.get('sourceMtimeNs')) != (before.st_size, before.st_mtime_ns):
                raise ValueError('Cached source changed; select a new output directory')
            cached += 1
            continue
        record = {'index': index, 'file': relative, 'approved': False,
                  'algorithm': 'source-colour-exterior-with-watermark-template-v1',
                  'backgroundRGB': list(BACKGROUND), 'maximumChannelDifference': 12,
                  'templateSource': TEMPLATE_SOURCE, 'templateBox': list(TEMPLATE_BOX),
                  'sourceBytes': before.st_size, 'sourceMtimeNs': before.st_mtime_ns}
        try:
            with Image.open(path) as source:
                source.load()
                frame = ImageOps.exif_transpose(source).convert('RGBA')
            record['sourceSize'] = list(frame.size)
            candidate, details = propose(frame, template)
            record.update(details, status='proposal-needs-native-and-display-review')
            candidate.save(output/f'{index:05}-candidate.png')
            comparison = Image.new('RGB', (frame.width*2, frame.height), 'white')
            comparison.paste(frame, (0, 0))
            comparison.paste(candidate, (frame.width, 0), candidate)
            comparison.save(output/f'{index:05}-compare.png')
            proposals += 1
        except (OSError, ValueError) as error:
            record.update(status='blocked-manual-review', reason=str(error))
            blocked += 1
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ValueError('Original changed during read')
        report_path.write_text(json.dumps(record, ensure_ascii=False, indent=2),
                               encoding='utf-8')
    print(json.dumps({'planned': len(selected), 'generated': proposals,
                      'blocked': blocked, 'cached': cached, 'approved': 0,
                      'activeRulesChanged': False}))


if __name__ == '__main__':
    run()
