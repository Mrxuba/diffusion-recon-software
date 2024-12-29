import cv2
import numpy as np
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import os

class CropDialog(QDialog):
    def __init__(self, parent=None, file_path=None, rgbflag=True, output_size=(480, 480)):
        super().__init__(parent)
        self.setWindowTitle("裁剪图像")
        self.resize(800, 600)

        self.file_path = file_path
        self.rgbflag = rgbflag
        self.output_size = output_size
        self.image = None
        self.pts = []  # 用于存储用户点击的点
        self.scale = 1.0
        self.original_image = None

        # 主布局
        self.layout = QVBoxLayout(self)

        # 显示图像的 QLabel
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        # 保存和取消按钮
        self.save_button = QPushButton("保存裁剪图像", self)
        self.save_button.clicked.connect(self.save_image)
        self.layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("取消操作", self)
        self.cancel_button.clicked.connect(self.close)
        self.layout.addWidget(self.cancel_button)

        # 加载图像
        self.load_image()

    def load_image(self):
        """加载并显示图像"""
        if not self.rgbflag:
            self.image = cv2.imread(self.file_path, cv2.IMREAD_GRAYSCALE)
        else:
            self.image = cv2.imread(self.file_path)

        if self.image is None:
            QMessageBox.critical(self, "错误", f"无法加载图像：{self.file_path}")
            self.close()
            return

        # 缩放图像
        self.original_height, self.original_width = self.image.shape[:2]
        new_width = 800  # 显示区域宽度
        self.scale = new_width / self.original_width
        new_height = int(self.original_height * self.scale)
        self.image = cv2.resize(self.image, (new_width, new_height), interpolation=cv2.INTER_AREA)

        # 转换为 RGB 格式（如果是彩色图像）
        if self.rgbflag and len(self.image.shape) == 3:
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

        # 显示图像
        self.update_image()

    def update_image(self):
        """更新 QLabel 中显示的图像"""
        image_to_show = self.image.copy()
        if len(image_to_show.shape) == 2:  # 灰度图处理
            height, width = image_to_show.shape
            q_image = QImage(image_to_show.data, width, height, width, QImage.Format_Grayscale8)
        else:  # 彩色图处理
            height, width, channel = image_to_show.shape
            bytes_per_line = 3 * width
            q_image = QImage(image_to_show.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap)

    def mousePressEvent(self, event):
        """捕捉鼠标点击事件并记录点"""
        if event.button() == Qt.LeftButton and self.image_label.geometry().contains(event.pos()):
            # 计算点击坐标在原图中的位置
            label_x = event.pos().x() - self.image_label.geometry().x()
            label_y = event.pos().y() - self.image_label.geometry().y()
            original_x = int(label_x / self.scale)
            original_y = int(label_y / self.scale)
            self.pts.append((original_x, original_y))

            # 在图像上画点和线
            if len(self.pts) > 1:
                cv2.line(
                    self.image,
                    (int(self.pts[-2][0] * self.scale), int(self.pts[-2][1] * self.scale)),
                    (int(self.pts[-1][0] * self.scale), int(self.pts[-1][1] * self.scale)),
                    (255, 0, 0),
                    2,
                )
            cv2.circle(self.image, (label_x, label_y), 3, (0, 255, 0), -1)
            self.update_image()

    def save_image(self):
        """裁剪并保存图像"""
        if len(self.pts) != 4:
            QMessageBox.warning(self, "错误", "请选择恰好 4 个点以形成四边形！")
            return

        try:
            # 透视变换
            self.original_image = cv2.imread(self.file_path)  # 重新加载原始图像
            pts_src = np.array(self.pts, dtype=np.float32)
            pts_dst = np.array(
                [[0, 0], [self.original_width - 1, 0], [self.original_width - 1, self.original_height - 1], [0, self.original_height - 1]],
                dtype=np.float32,
            )
            matrix = cv2.getPerspectiveTransform(pts_src, pts_dst)
            result = cv2.warpPerspective(self.original_image, matrix, (self.original_width, self.original_height))

            # 保存裁剪结果
            default_name = os.path.splitext(os.path.basename(self.file_path))[0] + "_cropped.jpg"
            file_path, _ = QFileDialog.getSaveFileName(self, "保存图像", default_name, "图像文件 (*.jpg *.png *.bmp)")
            if file_path:
                result = cv2.resize(result, self.output_size)
                cv2.imwrite(file_path, result)
                QMessageBox.information(self, "成功", f"图像已保存至：{file_path}")
                self.close()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存图像失败：{e}")