"""Resume local background proposals. Proposals never become approved automatically.

Usage: review_backgrounds.py [--model] [--start N] [--count N]
Original files are read-only; previews and dispositions stay in mobile/build.
"""
import argparse, json, os, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageOps, ImageDraw
from background_trim import remove_edge_light
from prepare_display import material_root

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'mobile/build/background-continuation'

def run():
    parser=argparse.ArgumentParser()
    parser.add_argument('--model',action='store_true')
    parser.add_argument('--start',type=int,default=0)
    parser.add_argument('--count',type=int,default=100000)
    parser.add_argument('--workers',type=int,default=6)
    parser.add_argument('--output',default='mobile/build/background-continuation')
    args=parser.parse_args()
    global OUT
    OUT=(ROOT/args.output).resolve()
    if not OUT.is_relative_to(ROOT/'mobile/build'):
        raise ValueError('Review output must stay inside mobile/build')
    OUT.mkdir(parents=True,exist_ok=True)
    queue=OUT/'queue.json'
    if not queue.exists():
        pending=json.loads((ROOT/'mobile/build/pending-review.json').read_text(encoding='utf-8'))
        queue.write_text(json.dumps(pending['backgroundReview'],ensure_ascii=False,indent=2),encoding='utf-8')
    files=json.loads(queue.read_text(encoding='utf-8'))
    materials=material_root(ROOT)
    session=None
    if args.model:
        from segment_mask import session as create_session
        session=create_session(ROOT)
    def process(pair):
        index,relative=pair
        report=OUT/'items'/f'{index:05}.json'
        if report.exists():
            result=json.loads(report.read_text(encoding='utf-8'))
            if result.get('file')!=relative:
                raise ValueError('Review queue changed; select a new --output directory')
            if result.get('approved') or result.get('status','').startswith('excluded-'):return result
            if not args.model or result.get('modelAttempted'):return result
        previous=json.loads(report.read_text(encoding='utf-8')) if report.exists() else {}
        report.parent.mkdir(parents=True,exist_ok=True)
        original=materials/relative
        stat=original.stat()
        result={'index':index,'file':relative,'sourceBytes':stat.st_size,'sourceMtimeNs':stat.st_mtime_ns,
                'approved':False,'status':'blocked-mask-needs-object-review'}
        try:
            with Image.open(original) as image:
                frame=ImageOps.exif_transpose(image).convert('RGBA')
            result['sourceSize']=list(frame.size)
            preview=frame.copy();preview.thumbnail((360,360),Image.Resampling.LANCZOS)
            candidate=remove_edge_light(preview,242,12)
            alpha=candidate.getchannel('A');bounds=alpha.getbbox()
            result.update(proposalBounds=list(bounds),removedFraction=round(alpha.histogram()[0]/(preview.width*preview.height),4),
                          previewSize=list(preview.size),edgeContact=bool(bounds[0]==0 or bounds[1]==0 or bounds[2]==preview.width or bounds[3]==preview.height),
                          reason='Shadows, pale metal/enamel, source marks and hanging parts require comparison before any alpha mask can be enabled.')
            if result['removedFraction']<.02:
                result.update(status='blocked-complex-background',reason='No separating edge-connected neutral-light region; a threshold matte cannot identify the object boundary.')
            if result['edgeContact']:
                result.update(status='blocked-edge-contact',reason='Foreground or source mark reaches the frame; retain the full source until completeness and boundary are visually checked.')
            if session:
                from segment_mask import predict
                mask=predict(preview,session)
                mask.save(OUT/'items'/f'{index:05}-model.png')
                result['modelAttempted']=True
                result['modelBounds']=list(mask.getbbox()) if mask.getbbox() else None
                result['modelProposalOnly']=True
                if previous.get('visualComparison'):
                    result.update(status=previous['status'],reason=previous['reason'],visualComparison=True)
            preview.save(OUT/'items'/f'{index:05}-source.png')
            candidate.save(OUT/'items'/f'{index:05}-edge.png')
            after=original.stat()
            if (stat.st_size,stat.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise ValueError('Source changed during read')
        except Exception as error:
            result.update(status='blocked-processing-error',reason=str(error))
        report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        return result
    selected=list(enumerate(files))[args.start:args.start+args.count]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for done,result in enumerate(pool.map(process,selected),1):
            if done%100==0:print(json.dumps({'processed':done,'total':len(selected),'lastIndex':result['index']}),flush=True)
    results=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((OUT/'items').glob('[0-9][0-9][0-9][0-9][0-9].json'))]
    (OUT/'dispositions.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'dispositions':len(results),'queue':len(files),'model':bool(session)}))

if __name__=='__main__':run()
