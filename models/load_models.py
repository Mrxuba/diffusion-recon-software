from diffusers import StableDiffusionUpscalePipeline
import torch

def loading(path = "./models/upscaler_model"):
    pipeline = StableDiffusionUpscalePipeline.from_pretrained(
        path,
        torch_dtype=torch.float16,
        local_files_only=True  
    )
    pipeline = pipeline.to("cuda")
    return pipeline