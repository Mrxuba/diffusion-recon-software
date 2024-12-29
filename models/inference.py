from PIL import Image

def inference(pipeline, img_path, prompt):
    low_res_img = Image.open(img_path).convert("RGB")
    low_res_img = low_res_img.resize((128, 128))
    upscaled_image = pipeline(prompt=prompt, image=low_res_img).images[0]
    return upscaled_image