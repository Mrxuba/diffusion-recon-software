from diffusers import StableDiffusionUpscalePipeline
import torch

import os
import time
import random
import threading
from time import sleep

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread, pyqtSignal


def download(
    model_id="stabilityai/stable-diffusion-x4-upscaler",
    cache_dir="./models",
    save_pretrained_dir="./models/upscaler_model",
    progress_callback=None,
):
    """
    下载函数，结合模拟进度条逻辑。
    
    :param model_id: 模型ID
    :param cache_dir: 缓存目录
    :param save_pretrained_dir: 保存路径
    :param progress_callback: 进度回调，用于更新进度条
    """
    # 检查目标保存路径是否存在，不存在则创建
    if not os.path.exists(save_pretrained_dir):
        os.makedirs(save_pretrained_dir, exist_ok=True)

    simulated_progress = 0
    stop_simulation_event = threading.Event()

    def simulate_progress():
        nonlocal simulated_progress
        while simulated_progress < 99 and not stop_simulation_event.is_set():
            simulated_progress += 0.25
            if progress_callback:
                progress_callback(simulated_progress)
            sleep(random.uniform(0.5, 5))

    simulation_thread = threading.Thread(target=simulate_progress)
    simulation_thread.start()

    try:
        # 实际下载模型
        pipeline = StableDiffusionUpscalePipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            cache_dir=cache_dir,  # 指定缓存目录
            local_files_only=False,  # 如果为 True 则仅使用本地缓存
        )
        pipeline.save_pretrained(save_pretrained_dir)

        # 下载完成后，将进度条设置为 100%
        if progress_callback:
            progress_callback(100)

    finally:
        stop_simulation_event.set()
        simulation_thread.join()

class DownloadThread(QThread):
    """
    后台线程，用于执行下载任务并更新进度。
    """
    progress_signal = pyqtSignal(int)  # 信号：传递下载进度
    finished_signal = pyqtSignal()    # 信号：通知下载完成

    def __init__(self, model_id, cache_dir, save_pretrained_dir):
        super().__init__()
        self.model_id = model_id
        self.cache_dir = cache_dir
        self.save_pretrained_dir = save_pretrained_dir

    def run(self):
        """
        执行下载任务。
        """
        try:
            download(
                model_id=self.model_id,
                cache_dir=self.cache_dir,
                save_pretrained_dir=self.save_pretrained_dir,
                progress_callback=self.update_progress
            )
            self.finished_signal.emit()  # 下载完成后发射信号
        except Exception as e:
            print(f"下载失败：{e}")

    def update_progress(self, value):
        """
        更新进度（由下载函数调用）。
        """
        self.progress_signal.emit(value)


class ProgressWindow(QWidget):
    """
    用于显示下载进度的新窗口。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("下载进度")
        self.setGeometry(500, 300, 300, 150)

        # 创建布局
        self.layout = QVBoxLayout()

        # 添加标签
        self.label = QLabel("正在下载，请稍候...")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        # 添加进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.layout.addWidget(self.progress_bar)

        # 设置布局
        self.setLayout(self.layout)

    def update_progress(self, value):
        """
        更新进度条的值。
        """
        self.progress_bar.setValue(value)

    def show_finished(self):
        """
        下载完成后更新窗口显示内容。
        """
        # 更新提示文字
        self.label.setText("下载完成！")  # 显示下载完成提示

        # 隐藏进度条
        self.progress_bar.hide()

        # 动态添加“确定”按钮
        self.confirm_button = QPushButton("确定", self)
        self.confirm_button.clicked.connect(self.close)  # 点击“确定”按钮关闭窗口
        self.layout.addWidget(self.confirm_button)  # 将按钮添加到布局中