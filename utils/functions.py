from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget, QProgressDialog, QApplication, QPushButton, QVBoxLayout, QDialog
from PyQt5.QtGui import QPixmap, QPainter, QFont
from PyQt5.QtCore import Qt, QRect, QSize


from models.download_models import ProgressWindow, DownloadThread
from models.load_models import loading
from models.inference import inference

from utils.crop import CropDialog

import os
import shutil
from datetime import datetime

class BadgeOverlay(QWidget):
    """
    自定义叠加层，用于在 QLabel 上显示角标
    """
    def __init__(self, parent=None, badge_text="", font_size=14):
        super().__init__(parent)
        self.badge_text = badge_text
        self.font_size = font_size  # 新增字体大小参数
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # 让叠加层不阻挡鼠标事件
        self.setStyleSheet("background: transparent;")  # 设置背景透明

    def setBadgeText(self, text):
        """动态更新角标内容"""
        self.badge_text = text
        self.update()  # 重新绘制

    def setFontSize(self, size):
        """动态更新字体大小"""
        self.font_size = size
        self.update()  # 重新绘制

    def paintEvent(self, event):
        """绘制角标"""
        super().paintEvent(event)
        if not self.badge_text:
            return  # 如果没有角标内容，不绘制

        # 使用 QPainter 绘制角标
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 设置字体
        font = QFont("Arial", self.font_size)  # 动态使用 font_size
        font.setBold(True)
        painter.setFont(font)

        # 设置角标背景颜色和文本颜色
        painter.setBrush(Qt.black)  # 红色背景
        painter.setPen(Qt.white)  # 白色文字

        # 计算角标的矩形区域
        text_padding = 10
        rect_width = painter.fontMetrics().boundingRect(self.badge_text).width() + text_padding * 2
        rect_height = painter.fontMetrics().height() + text_padding
        rect = QRect(0, 0, rect_width, rect_height)  # 左上角

        # 绘制角标背景（矩形）
        painter.drawRect(rect)

        # 绘制角标文本
        painter.drawText(rect, Qt.AlignCenter, self.badge_text)

        painter.end()

def download_model(parent, model_id, button_download):
    """
    主函数：选择路径 -> 打开进度窗口 -> 启动下载线程。
    """
    button_download.setEnabled(False)

    if not model_id:
        QMessageBox.warning(parent, "未指定模型", "默认下载 stabilityai/stable-diffusion-x4-upscaler ！")
        model_id = "stabilityai/stable-diffusion-x4-upscaler"

    # 选择保存路径
    save_path = QFileDialog.getExistingDirectory(parent, "选择保存路径")
    if not save_path:
        QMessageBox.warning(parent, "取消操作", "未选择存储路径，操作已取消。")
        return

    # 创建进度窗口
    progress_window = ProgressWindow(parent)
    progress_window.show()

    # 创建下载线程
    cache_dir = "./temp"
    parent.download_thread = DownloadThread(model_id, cache_dir, save_path)

    # 连接信号
    parent.download_thread.progress_signal.connect(progress_window.update_progress)
    parent.download_thread.finished_signal.connect(progress_window.show_finished)

    # 确保线程完成后释放资源
    def cleanup_thread():
        """
        下载完成后更新按钮内容
        """
        button_download.setText("下载模型：成功！")  # 修改按钮内容
        parent.download_thread = None  # 清除线程引用
    
    parent.download_thread.finished_signal.connect(cleanup_thread)

    # 启动线程
    parent.download_thread.start()

def import_model(parent, button_import):
    save_path = QFileDialog.getExistingDirectory(parent, "选择载入路径")
    if not save_path:
        QMessageBox.warning(parent, "取消操作", "未选择载入路径，操作已取消。")
        return
    try:
        pipeline = loading(save_path)
        button_import.setProperty("pipeline", pipeline)
        button_import.setText("载入模型：成功！")
        button_import.setEnabled(False)
    except:
        QMessageBox.warning(parent, "载入失败！", "请检查模型下载位置")

    

def select_image(parent, button_select_image):
    save_path = QFileDialog.getOpenFileName(parent, "选择原始图像", "", "图像文件 (*.png *.jpg *.jpeg)")
    if not save_path:
        QMessageBox.warning(parent, "取消操作", "未选择图像存储路径，操作已取消！")
        return
    try:
        if show_image(parent, parent.center_big_window, save_path[0], font_size=10, img_size=parent.center_big_window.size()):
            button_select_image.setText("图像加载成功！")
            button_select_image.setProperty("image_path", save_path)
            # button_select_image.setEnabled(False)
    except:
        QMessageBox.warning(parent, "载入失败！", "请检查图像位置")
        return
    
    return

def show_image(parent, box, save_path, font_size, img_size):
    """
    点击按钮后展示图片
    """
    # 加载图片
    pixmap = QPixmap(save_path)
    if pixmap.isNull():
        box.setText("加载图片失败！")
        return False
    else:
        # 根据文件名生成角标文字
        basename = os.path.splitext(os.path.basename(save_path))[0]
        pixmap_text = "upscaled_0" if "upscaled_" not in basename else basename

        # 显示图片到 QLabel

        max_width = box.width()  # 或者父控件的宽度
        max_height = box.height()  # 或者父控件的高度

        new_width = min(img_size.width() * 0.95, max_width)
        new_height = min(img_size.height() * 0.95, max_height)

        img_size = QSize(int(new_width), int(new_height))

        # 创建新的 QSize
        img_size = QSize(int(new_width), int(new_height))

        box.setPixmap(pixmap.scaled(
            img_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))
        box.setProperty("image_path", save_path)

        # 添加或更新角标叠加层
        if not hasattr(box, "badge_overlay"):  # 如果当前 box 没有叠加层，创建一个
            box.badge_overlay = BadgeOverlay(box, badge_text=pixmap_text, font_size=font_size)
        else:
            # 如果已经存在叠加层，更新角标内容和字体大小
            box.badge_overlay.setBadgeText(pixmap_text)
            box.badge_overlay.setFontSize(font_size)

        # 调整叠加层大小和位置
        box.badge_overlay.resize(img_size)
        box.badge_overlay.show()

        return True

def start_inference(parent, button_import, button_start_inference, button_select_image, prompt, iter):
    try:
        # 获取图像路径和模型
        image_path = button_select_image.property("image_path")[0]
        pipeline = button_import.property("pipeline")
    except:
        QMessageBox.warning(parent, "启动模型失败", "请检查是否已正确载入模型与图像")
        return

    # 初始化图像路径和临时目录
    images_path = [image_path]
    current_time = datetime.now()
    temp_dir = os.path.abspath(os.path.join('./temp/img_temp/', current_time.strftime("%Y-%m-%d_%H-%M-%S")))
    os.makedirs(temp_dir, exist_ok=True)

    # 检查 prompt 和 iter 的合法性
    if prompt.isalpha() and prompt.isascii() and iter.isdigit():
        try:
            iter = int(iter)
        except:
            QMessageBox.warning(parent, "启动模型失败", "输入了非法的提示词和iter次数！")
            return

        # 创建进度对话框
        progress_dialog = QProgressDialog("推理中，请稍候...", "取消", 0, iter, parent)
        progress_dialog.setWindowTitle("模型推理")
        progress_dialog.setWindowModality(True)  # 模态对话框，阻止其他操作
        progress_dialog.setAutoClose(True)      # 推理完成后自动关闭
        progress_dialog.setAutoReset(True)      # 自动重置
        progress_dialog.show()

        # 将原始图像复制到临时目录
        shutil.copy(image_path, os.path.join(temp_dir, f"upscaled_{0}.png"))

        # 执行推理任务
        img_size = parent.small_windows[0].size()
        for i in range(iter):
            if progress_dialog.wasCanceled():  # 如果用户点击“取消”，提前中断
                QMessageBox.information(parent, "中止", "推理任务已被取消")
                return

            # 调用推理函数
            image = inference(pipeline, images_path[i], prompt)
            
            image.save(os.path.join(temp_dir, f"upscaled_{i+1}.png"))
            images_path.append(os.path.join(temp_dir, f"upscaled_{i+1}.png"))

            # 更新小窗口展示最新的图像
            for idx, img in enumerate(images_path[::-1]):
                if idx<=3:
                    show_image(parent, parent.small_windows[idx], img, font_size=8, img_size=img_size)
                    show_image(parent, parent.center_big_window, images_path[-1], font_size=10, img_size=parent.center_big_window.size())
                    parent.small_windows[idx].setProperty("image_path", img)

            # 更新进度条
            progress_dialog.setValue(i + 1)
            QApplication.processEvents()  # 保持界面响应，实时更新进度

        # 推理完成
        progress_dialog.setValue(iter)
        button_start_inference.setText("模型推理完成！")
        button_start_inference.setProperty("images_path", images_path)

    else:
        QMessageBox.warning(parent, "启动模型失败", "输入了非法的提示词和iter次数！")
        return

def crop_image(parent):
    save_path = QFileDialog.getExistingDirectory(parent, "选择存储路径")
    if not save_path:
        QMessageBox.warning(parent, "取消操作", "未选择存储路径，操作已取消。")
        return
    try:
        image_path = parent.center_big_window.property("image_path")
        dialog = CropDialog(parent, file_path=image_path, rgbflag=True)
        dialog.exec_()
        # if process_image(image_path, rgbflag=True, size=(128, 128)):
            # QMessageBox.warning(parent, "成功！", "成功映射转存，请检查存储位置")
        # else:
        #     QMessageBox.warning(parent, "裁剪映射存储失败！", "请检查是否选择了合法的映射锚点")
    except:
        QMessageBox.warning(parent, "裁剪映射存储失败！", "请检查指定存储位置")

def save_image(parent, button_start_inference):
    save_path = QFileDialog.getExistingDirectory(parent, "选择存储路径")
    if not save_path:
        QMessageBox.warning(parent, "取消操作", "未选择存储路径，操作已取消。")
        return
    try:
        images_path = button_start_inference.property("images_path")
        for img_path in images_path:
            shutil.copy(img_path, save_path)
        QMessageBox.warning(parent, "成功！", "成功转存，请检查存储位置")
    except:
        QMessageBox.warning(parent, "转存失败！", "请检查指定存储位置")


class TwiceWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("警告, 您确定要清除模型缓存？（下次运行模型将需要大量的下载时间）")
        self.resize(300, 150)

        # 创建布局
        layout = QVBoxLayout(self)
        # 清除模型缓存按钮
        clear_model_cache_button = QPushButton("确定清除模型缓存", self)
        clear_model_cache_button.clicked.connect(self.clear_model_cache)
        layout.addWidget(clear_model_cache_button)

        # 清除模型缓存按钮
        cancel_button = QPushButton("取消操作", self)
        cancel_button.clicked.connect(self.close)
        layout.addWidget(cancel_button)

    def clear_model_cache(self):
        """清除模型缓存"""
        try:
            shutil.rmtree('./temp/models--stabilityai--stable-diffusion-x4-upscaler')
            QMessageBox.information(self, "提示", "模型缓存已清除！")
        except:
            QMessageBox.information(self, "提示", "模型缓存清除操作异常终止，请手动清除")

class SettingWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.resize(300, 150)

        # 创建布局
        layout = QVBoxLayout(self)

        # 清除运行缓存按钮
        clear_runtime_cache_button = QPushButton("清除运行缓存", self)
        clear_runtime_cache_button.clicked.connect(self.clear_runtime_cache)
        layout.addWidget(clear_runtime_cache_button)

        # 清除模型缓存按钮
        clear_model_cache_button = QPushButton("清除模型缓存(不建议)", self)
        clear_model_cache_button.clicked.connect(self.clear_model_cache)
        layout.addWidget(clear_model_cache_button)

        # 清除模型缓存按钮
        cancel_button = QPushButton("取消操作", self)
        cancel_button.clicked.connect(self.close)
        layout.addWidget(cancel_button)

    def clear_runtime_cache(self):
        """清除运行缓存"""
        try:
            shutil.rmtree('./temp/img_temp')
            QMessageBox.information(self, "提示", "运行缓存已清除！")
        except:
            QMessageBox.information(self, "提示", "缓存清除操作异常终止，请手动清除")

    def clear_model_cache(self):
        """清除模型缓存"""
        try:
            # QMessageBox.information(self, "警告", "您确定要清除模型缓存？（下次运行模型将需要大量的下载时间）")
            twice_window = TwiceWindow(self)
            twice_window.exec_()
        except:
            QMessageBox.information(self, "提示", "缓存清除操作异常终止，请手动清除")

def setting(parent):
    setting_window = SettingWindow(parent)
    setting_window.exec_()