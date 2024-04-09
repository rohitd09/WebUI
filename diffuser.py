import sys
import base64
import torch
import argparse
import os
from diffusers import StableDiffusionPipeline
from text import add_text

parser = argparse.ArgumentParser()
parser.add_argument('--prompt', default="a photo of an astronaut riding a horse on mars", type=str)
args = parser.parse_args()

def run_sd(prompt):
    model_id = "runwayml/stable-diffusion-v1-5"
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    pipe = pipe.to("cuda")
    image = pipe(prompt).images[0]
    return add_text(image, prompt)

if __name__ == "__main__":
    try:
        result = run_sd(prompt=args.prompt)
        print(f"Result: {result}")
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
