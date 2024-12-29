from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QPropertyAnimation


class HoverableLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

        # 初始样式
        self.setStyleSheet("""
            background-color: #ffffff;
            border: 2px solid #dcdcdc;
            border-radius: 10px;
            font-size: 14px;
            padding: 10px;
        """)
        self.setAlignment(Qt.AlignCenter)

        # 创建阴影效果
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(0)  # 初始模糊半径为 0（不显示阴影）
        self.shadow_effect.setOffset(0, 0)
        self.shadow_effect.setColor(Qt.gray)
        self.setGraphicsEffect(self.shadow_effect)

        # 创建动画
        self.animation = QPropertyAnimation(self.shadow_effect, b"blurRadius")
        self.animation.setDuration(200)  # 动画持续时间（毫秒）

    def enterEvent(self, event):
        """鼠标进入控件时触发"""
        self.animation.stop()  # 停止当前动画
        self.animation.setStartValue(self.shadow_effect.blurRadius())  # 起始值为当前模糊半径
        self.animation.setEndValue(20)  # 目标模糊半径
        self.animation.start()

    def leaveEvent(self, event):
        """鼠标离开控件时触发"""
        self.animation.stop()
        self.animation.setStartValue(self.shadow_effect.blurRadius())
        self.animation.setEndValue(0)  # 恢复到没有阴影
        self.animation.start()