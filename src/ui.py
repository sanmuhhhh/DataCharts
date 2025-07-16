from PyQt5.QtWidgets import QMainWindow

# 主窗口类
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataCharts")
        self.setGeometry(100, 100, 800, 600)