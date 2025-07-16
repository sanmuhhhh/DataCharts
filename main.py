# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication
from src.ui import MainWindow # 导入自定义主窗口


if __name__ == "__main__":
    # 创建应用
    app = QApplication(sys.argv)
    # 创建主窗口
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())