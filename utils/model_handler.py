from models.load_models import loading
import torch

class ModelHandler:
    def __init__(self):
        self.model = None
        
    def load_model(self, model_path):
        try:
            self.pipeline = loading()
            return True
        except Exception as e:
            print(f"加载模型失败: {str(e)}")
            return False