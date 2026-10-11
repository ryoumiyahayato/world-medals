"""CPU-only U2NETP alpha proposals; never changes RGB or synthesizes pixels."""
import os
from pathlib import Path
import numpy as np
import onnxruntime as ort
from PIL import Image

MODEL_URL='https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2netp.onnx'

def session(root):
    directory=Path(os.environ.get('WORLD_MEDALS_MODEL_DIR',root/'mobile/.local/models'))
    model=directory/'u2netp.onnx'
    if not model.is_file():raise FileNotFoundError('Supply u2netp.onnx in WORLD_MEDALS_MODEL_DIR; see BUILD.md')
    options=ort.SessionOptions();options.intra_op_num_threads=2;options.inter_op_num_threads=1
    return ort.InferenceSession(str(model),sess_options=options,providers=['CPUExecutionProvider'])

def predict(frame,engine):
    image=frame.convert('RGB').resize((320,320),Image.Resampling.LANCZOS)
    values=np.asarray(image,dtype=np.float32)
    scale=float(values.max())
    values=values/(scale if scale else 1)
    values=(values-np.array([.485,.456,.406],dtype=np.float32))/np.array([.229,.224,.225],dtype=np.float32)
    values=np.transpose(values,(2,0,1))[None,...]
    result=engine.run(None,{engine.get_inputs()[0].name:values})[0][0,0]
    low=float(result.min());high=float(result.max())
    result=(result-low)/(high-low) if high>low else np.zeros_like(result)
    mask=Image.fromarray(np.clip(result*255,0,255).astype('uint8'))
    return mask.resize(frame.size,Image.Resampling.LANCZOS)
