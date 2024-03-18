import sys
import base64
import torch
import argparse
from io import BytesIO
from diffusers import StableDiffusionPipeline

parser = argparse.ArgumentParser()
parser.add_argument('--prompt', default="a photo of an astronaut riding a horse on mars", type=str)
args = parser.parse_args()

def run_sd(prompt):
    model_id = "runwayml/stable-diffusion-v1-5"
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    pipe = pipe.to("cuda")

    image = pipe(prompt).images[0]
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return img_str

if __name__ == "__main__":
    try:
        img_base64 = run_sd(prompt=args.prompt)
        print(img_base64)
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)  