from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
import numpy as np

class ImageDisplayWidget(QWidget):
    clicked = pyqtSignal()
    
    def __init__(self, is_thumbnail=True):
        super().__init__()
        self.is_thumbnail = is_thumbnail
        self.current_image = None
        
        layout = QVBoxLayout()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if is_thumbnail:
            self.setFixedSize(200, 200)
            self.image_label.setFixedSize(180, 180)
        else:
            self.setMinimumSize(600, 600)
            
        layout.addWidget(self.image_label)
        self.setLayout(layout)
        
    def mousePressEvent(self, event):
        if self.is_thumbnail:
            self.clicked.emit()
            
    def set_image(self, image_data):
        self.current_image = image_data
        if isinstance(image_data, str):
            pixmap = QPixmap(image_data)
        elif isinstance(image_data, np.ndarray):
            height, width, channel = image_data.shape
            bytes_per_line = 3 * width
            q_img = QImage(image_data.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
        else:
            return
            
        if self.is_thumbnail:
            pixmap = pixmap.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio)
        else:
            pixmap = pixmap.scaled(580, 580, Qt.AspectRatioMode.KeepAspectRatio)
            
        self.image_label.setPixmap(pixmap)