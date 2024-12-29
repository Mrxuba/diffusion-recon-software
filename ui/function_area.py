

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
    button_download.clicked.connect(self.download_model)  # 绑定点击事件
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
    button_import.clicked.connect(self.import_model)  # 绑定点击事件
    left_function_layout.addWidget(button_import)

    # 推理设置
    inference_label = QLabel("推理设置")
    inference_label.setAlignment(Qt.AlignCenter)
    inference_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333333;")
    left_function_layout.addWidget(inference_label)

    # Iter 输入框
    iter_layout = QHBoxLayout()  # 横向布局
    iter_label = QLabel("Iter:")
    iter_label.setStyleSheet("font-size: 14px; color: #333333;")
    iter_input = QLineEdit()
    iter_input.setPlaceholderText("输入迭代次数")
    iter_input.setStyleSheet("""
        QLineEdit {
            border: 1px solid #dcdcdc;
            border-radius: 5px;
            padding: 5px;
        }
    """)
    iter_layout.addWidget(iter_label)
    iter_layout.addWidget(iter_input)
    left_function_layout.addLayout(iter_layout)

    # Prompt 输入框
    prompt_layout = QHBoxLayout()  # 横向布局
    prompt_label = QLabel("Prompt:")
    prompt_label.setStyleSheet("font-size: 14px; color: #333333;")
    prompt_input = QLineEdit()
    prompt_input.setPlaceholderText("输入提示词")
    prompt_input.setStyleSheet("""
        QLineEdit {
            border: 1px solid #dcdcdc;
            border-radius: 5px;
            padding: 5px;
        }
    """)
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
    button_select_image.clicked.connect(self.select_image)  # 绑定点击事件
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
    button_start_inference.clicked.connect(self.start_inference)  # 绑定点击事件
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
    button_crop.clicked.connect(self.crop_image)  # 绑定点击事件
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
    button_save.clicked.connect(self.save_image)  # 绑定点击事件
    left_function_layout.addWidget(button_save)

    return left_function_area