import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QPixmap, QColor, QIcon, QPainter
from PyQt5.QtSvg import QSvgRenderer

from utils.functions import download_model, import_model, select_image, start_inference, crop_image, save_image, show_image, setting
from utils.style import HoverableLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(100, 100, 1920, 1080)
        
        # 主窗口的中央小部件
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # 主布局为垂直方向
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)  # 去除边距

        # 顶部区域
        self.title_bar = self.create_top_area()
        main_layout.addWidget(self.title_bar, 1)  # 顶部占比1份

        # 中间区域
        middle_widget = self.create_middle_area()
        main_layout.addWidget(middle_widget, 8)  # 中间区域占比8份

        self.offset = None

    def create_top_area(self):
        """创建自定义标题栏"""
        # 创建标题栏框架
        title_bar = QFrame()
        title_bar.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.8); /* 半透明白色背景 */
                border-bottom: 2px solid #dddddd;
            }
        """)
        title_bar.setFixedHeight(60)

        # 顶部主布局
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(10, 0, 10, 0)  # 设置边距
        layout.setSpacing(0)

        # 左侧 Logo
        logo_label = QLabel()
        pixmap = QPixmap(r".\icons\logo.png")  # 替换为你的 Logo 文件路径
        pixmap = pixmap.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # 保持宽高比
        logo_label.setPixmap(pixmap)
        layout.addWidget(logo_label)  # 添加到布局左侧

        # 添加左侧空白弹性项（QSpacerItem 或 QStretch）
        layout.addStretch(1)

        # 中间标题
        title_label = QLabel("基于Diffusion的多级重建软件")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #333333;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)  # 确保标题文本居中
        layout.addWidget(title_label)

        # 添加右侧空白弹性项
        layout.addStretch(1)

        # 右侧操作按钮布局
        button_layout = QHBoxLayout()  # 单独创建一个按钮布局
        button_layout.setContentsMargins(0, 0, 0, 0)  # 按钮布局无边距
        button_layout.setSpacing(5)  # 按钮之间间距

        # 最小化按钮
        button_minimize = QPushButton("-")
        button_minimize.setFixedSize(45, 45)
        button_minimize.setStyleSheet("""
            QPushButton {
                font-size: 16px; 
                font-weight: bold; /* 设置文字加粗 */
                border: none;  /* 去除边框 */
                outline: none; /* 去除焦点时的边框 */
                box-shadow: none; /* 去除阴影 */
            }
            QPushButton:hover {
                background-color: #dddddd;
            }
        """)
        button_minimize.clicked.connect(self.showMinimized)

        # 创建设置按钮
        button_setting = QPushButton("")
        button_setting.setFixedSize(45, 45)

        # 创建按钮
        button_setting = QPushButton("☰")
        button_setting.setFixedSize(45, 45)

        # 设置样式
        button_setting.setStyleSheet("""
            QPushButton {
                font-size: 16px; 
                border: none;  /* 去除边框 */
                outline: none; /* 去除焦点时的边框 */
                box-shadow: none; /* 去除阴影 */
            }
            QPushButton:hover {
                background-color: #dddddd;
            }
        """)

        # 绑定点击事件
        button_setting.clicked.connect(lambda: setting(self))  # 绑定点击事件

        # 关闭按钮      
        button_close = QPushButton("×")
        button_close.setFixedSize(45, 45)
        button_close.setStyleSheet("""
            QPushButton {
                font-size: 16px; 
                font-weight: bold; /* 设置文字加粗 */
                border: none;  /* 去除边框 */
                outline: none; /* 去除焦点时的边框 */
                box-shadow: none; /* 去除阴影 */
            }
            QPushButton:hover {
                background-color: #ffdddd;
            }
        """)
        button_close.clicked.connect(self.close)

        # 添加按钮到按钮布局
        button_layout.addWidget(button_minimize)
        button_layout.addWidget(button_setting)
        button_layout.addWidget(button_close)

        # 将按钮布局添加到主布局
        layout.addLayout(button_layout)  # 添加到布局右侧

        return title_bar

    def create_left_function_area(self):
        """创建左侧功能设置区域"""

        # 主框架
        left_function_area = QFrame()
        left_function_area.setStyleSheet("""
            background-color: #ffffff;
            border: 2px solid #dcdcdc;
            border-radius: 10px;
        """)
        left_function_layout = QVBoxLayout(left_function_area)
        left_function_layout.setContentsMargins(10, 10, 10, 10)  # 设置内边距
        left_function_layout.setSpacing(15)  # 设置控件间距

        # 模型设置
        model_label = QLabel("模型设置")
        model_label.setAlignment(Qt.AlignCenter)
        model_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333333;")
        left_function_layout.addWidget(model_label)

        button_download = QPushButton("模型下载")
        button_download.setFixedHeight(40)
        button_download.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                font-size: 14px;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """)

        # model_id 输入框
        model_id_layout = QHBoxLayout()  # 横向布局
        model_id_label = QLabel("Model Id:")
        model_id_label.setStyleSheet("font-size: 14px; color: #333333; border: None;")
        model_id_input = QLineEdit()
        model_id_input.setPlaceholderText("")
        model_id_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        model_id_label.setAlignment(Qt.AlignCenter)
        model_id_layout.addWidget(model_id_label)
        model_id_layout.addWidget(model_id_input)
        left_function_layout.addLayout(model_id_layout)
        button_download.clicked.connect(lambda: download_model(self, model_id_input.text(), button_download))  # 绑定点击事件
        left_function_layout.addWidget(button_download)

        button_import = QPushButton("模型导入")
        button_import.setFixedHeight(40)
        button_import.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                font-size: 14px;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """)
        button_import.clicked.connect(lambda: import_model(self, button_import))
        left_function_layout.addWidget(button_import)

        # 推理设置
        inference_label = QLabel("推理设置")
        inference_label.setAlignment(Qt.AlignCenter)
        inference_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333333;")
        left_function_layout.addWidget(inference_label)

        # Iter 输入框
        iter_layout = QHBoxLayout()  # 横向布局
        iter_label = QLabel("Iter:")
        iter_label.setStyleSheet("font-size: 14px; color: #333333; border: None;")
        iter_input = QLineEdit()
        iter_input.setPlaceholderText("输入迭代次数")
        iter_input.setStyleSheet("""
            QLineEdit {
                # border: 1px solid #dcdcdc;
                padding: 5px;
            }
        """)
        iter_input.setAlignment(Qt.AlignCenter)
        iter_layout.addWidget(iter_label)
        iter_layout.addWidget(iter_input)
        left_function_layout.addLayout(iter_layout)

        # Prompt 输入框
        prompt_layout = QHBoxLayout()  # 横向布局
        prompt_label = QLabel("Prompt:")
        prompt_label.setStyleSheet("font-size: 14px; color: #333333; border: None;")
        prompt_input = QLineEdit()
        prompt_input.setPlaceholderText("输入提示词, diffuser model请使用英文提示词")
        prompt_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        prompt_input.setAlignment(Qt.AlignCenter)
        prompt_layout.addWidget(prompt_label)
        prompt_layout.addWidget(prompt_input)
        left_function_layout.addLayout(prompt_layout)

        # 推理按钮
        button_select_image = QPushButton("选择图像")
        button_select_image.setFixedHeight(40)
        button_select_image.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                font-size: 14px;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """)
        button_select_image.clicked.connect(lambda: select_image(self, button_select_image))  # 绑定点击事件
        left_function_layout.addWidget(button_select_image)

        button_start_inference = QPushButton("启动模型")
        button_start_inference.setFixedHeight(40)
        button_start_inference.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                font-size: 14px;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """)
        button_start_inference.clicked.connect(lambda: start_inference(self, button_import, button_start_inference, button_select_image, prompt_input.text(), iter_input.text()))  # 绑定点击事件
        left_function_layout.addWidget(button_start_inference)

        # 保存设置
        save_label = QLabel("保存设置")
        save_label.setAlignment(Qt.AlignCenter)
        save_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333333;")
        left_function_layout.addWidget(save_label)

        button_crop = QPushButton("裁剪映射")
        button_crop.setFixedHeight(40)
        button_crop.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                font-size: 14px;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """)
        button_crop.clicked.connect(lambda: crop_image(self))  # 绑定点击事件
        left_function_layout.addWidget(button_crop)

        button_save = QPushButton("保存图像")
        button_save.setFixedHeight(40)
        button_save.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                font-size: 14px;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """)
        button_save.clicked.connect(lambda: save_image(self, button_start_inference))  # 绑定点击事件
        left_function_layout.addWidget(button_save)

        return left_function_area

    def create_middle_area(self):
        """创建中间区域"""
        middle_area = QFrame()
        middle_area.setFrameShape(QFrame.StyledPanel)
        middle_layout = QHBoxLayout(middle_area)
        middle_layout.setSpacing(10)

        # 左侧功能设置区域
        left_function_area = self.create_left_function_area()
        middle_layout.addWidget(left_function_area, 1)

        # 中间大边框区域（框住大窗口和小窗口）
        right_visual_area = QFrame()
        right_visual_area.setStyleSheet("""
            background-color: #ffffff;
            border: 3px solid #333333;
            border-radius: 10px;
        """)
        right_visual_layout = QHBoxLayout(right_visual_area)
        right_visual_layout.setSpacing(10)

        # 大窗口
        self.center_big_window = QLabel("等待模型推理结果......")
        self.center_big_window.setAlignment(Qt.AlignCenter)
        self.center_big_window.setStyleSheet("""
            background-color: #ffffff;
            border: 2px solid #dcdcdc;
            border-radius: 10px;
            font-size: 16px;
            padding: 20px;
        """)
        right_visual_layout.addWidget(self.center_big_window, 3)  # 占比3份

        # 小窗口（垂直排列）
        right_small_windows = QFrame()
        right_small_windows_layout = QVBoxLayout(right_small_windows)
        right_small_windows_layout.setSpacing(10)
        # 用于存储小窗口引用的列表
        self.small_windows = []
        for _ in range(4):  # 创建4个小窗口
            small_window = HoverableLabel("等待模型推理结果......")
            small_window.mousePressEvent = lambda event, window=small_window: self.update_large_image(window)
            right_small_windows_layout.addWidget(small_window)
            self.small_windows.append(small_window)

        right_visual_layout.addWidget(right_small_windows, 1)  # 占比1份

        middle_layout.addWidget(right_visual_area, 4)  # 大边框区域占比4份

        return middle_area

    def update_large_image(self, small_window):
        # 检查 small_window 是否具有属性 "image_path"
        if not small_window.property("image_path"):
            QMessageBox.warning(self, "提示", "不是有效的可预览图像！")
            return
        else:
            # 调用 show_image 函数更新大图
            show_image(
                self,
                self.center_big_window,
                small_window.property("image_path"),
                font_size=10,
                img_size=self.center_big_window.size()
            )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 检查鼠标是否在标题栏区域
            if self.title_bar.rect().contains(event.pos() - self.title_bar.pos()):
                self.offset = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.offset and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        self.offset = None



def runner():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())