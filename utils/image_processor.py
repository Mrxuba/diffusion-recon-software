from PIL import Image
import numpy as np

class ImageProcessor:
    def __init__(self):
        pass
        
    def process_image(self, image_path, prompt, model):
        try:
            # 读取原始图片
            low_res_img = Image.open(image_path).convert("RGB")
            
            # 创建不同尺寸的重建结果
            results = []
            sizes = [(128, 128), (256, 256), (512, 512), (1024, 1024)]
            
            for size in sizes:
                resized_img = low_res_img.resize(size)
                upscaled = model(prompt=prompt, image=resized_img).images[0]
                results.append(np.array(upscaled))
                
            return results
        except Exception as e:
            print(f"处理图片失败: {str(e)}")
            return []