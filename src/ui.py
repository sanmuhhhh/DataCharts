from PyQt5.QtWidgets import (QMainWindow, QMenuBar, QVBoxLayout, QWidget, 
                             QPushButton, QHBoxLayout, QAction, QSplitter)
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtChart import QChartView, QChart, QLineSeries

# 主窗口类
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 集中初始化所有变量和组件
        self.initVariables()
        self.initUI() 
    # 初始化变量
    def initVariables(self):
        # ==================== 1. 布局组件 ====================
        self.central_widget = QWidget()
        self.main_layout = QHBoxLayout()
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()
        
        # ==================== 2. 图表组件 ====================
        self.chart = QChart()
        self.chart.setTitle("数据图表 - 欢迎使用DataCharts")
        self.chart.setTheme(1)  # 使用蓝色主题
        
        self.view = QChartView(self.chart)
        self.view.setStyleSheet("""
            QChartView {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: white;
            }
        """)
        
        self.series = QLineSeries()
        self.series.setName("示例数据")
        
        # 添加示例数据
        sample_data = [
            (0, 6), (2, 4), (3, 8), (7, 4), (10, 5),
            (11, 2), (13, 3), (17, 6), (18, 3), (20, 2)
        ]
        for x, y in sample_data:
            self.series.append(x, y)
        
        # 将系列添加到图表并创建坐标轴
        self.chart.addSeries(self.series)
        self.chart.createDefaultAxes()
        
        # ==================== 3. 按钮组件 ====================
        # 定义按钮样式
        self.button_style = """
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 4px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
        
        self.title_button_style = """
            QPushButton {
                background-color: #e0e0e0;
                color: #666;
                font-weight: bold;
                border: none;
                padding: 8px;
                margin: 2px;
            }
        """
        
        # 创建所有按钮并设置样式
        self.import_button = QPushButton("导入数据")
        self.import_button.setStyleSheet(self.button_style)
        
        self.export_button = QPushButton("导出数据")
        self.export_button.setStyleSheet(self.button_style)
        
        self.algorithm_button = QPushButton("算法选择")
        self.algorithm_button.setStyleSheet(self.button_style)
        
        self.charts_button = QPushButton("图表类型")
        self.charts_button.setStyleSheet(self.button_style)
        
        self.help_button = QPushButton("帮助")
        self.help_button.setStyleSheet(self.button_style)
        
        self.about_button = QPushButton("关于")
        self.about_button.setStyleSheet(self.button_style)
        
        self.exit_button = QPushButton("退出")
        self.exit_button.setStyleSheet(self.button_style)
        
        # 创建标题按钮
        self.data_title = QPushButton("数据操作")
        self.data_title.setEnabled(False)
        self.data_title.setStyleSheet(self.title_button_style)
        
        self.tools_title = QPushButton("分析工具")
        self.tools_title.setEnabled(False)
        self.tools_title.setStyleSheet(self.title_button_style)
        
        self.system_title = QPushButton("系统")
        self.system_title.setEnabled(False)
        self.system_title.setStyleSheet(self.title_button_style)
        
        # ==================== 4. 布局容器组件 ====================
        self.splitter = QSplitter(Qt.Horizontal)
        
        # 左侧面板
        self.left_widget = QWidget()
        self.left_widget.setLayout(self.left_layout)
        self.left_widget.setMaximumWidth(250)
        self.left_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        
        # 右侧面板
        self.right_widget = QWidget()
        self.right_widget.setLayout(self.right_layout)
        self.right_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        
        # ==================== 5. 菜单栏样式 ====================
        self.menubar_style = """
            QMenuBar {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 4px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #1976D2;
            }
            QMenu {
                background-color: white;
                color: black;
                border: 1px solid #ccc;
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: #e3f2fd;
            }
        """
        
        # ==================== 6. 主窗口样式 ====================
        self.main_window_style = """
            QMainWindow {
                background-color: #f5f5f5;
            }
        """
    
    # 初始化UI
    def initUI(self):
        self.setWindowTitle("DataCharts - 数据图表分析工具") # 设置窗口标题
        self.setGeometry(100, 100, 1200, 800) # 设置窗口位置和大小
        self.setMinimumSize(800, 600) # 设置最小窗口大小
        
        # 应用主窗口样式
        self.setStyleSheet(self.main_window_style)
        
        self.initMenu() 
        self.initLayout() 
        
        # 连接信号
        self.connectSignals()
    
    # 初始化菜单
    def initMenu(self):
        menubar = self.menuBar()
        menubar.setStyleSheet(self.menubar_style)
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        import_action = QAction('导入数据', self)
        import_action.setShortcut('Ctrl+O')
        import_action.triggered.connect(self.import_data)
        file_menu.addAction(import_action)
        
        export_action = QAction('导出数据', self)
        export_action.setShortcut('Ctrl+S')
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu('工具')
        
        algorithm_action = QAction('算法选择', self)
        algorithm_action.triggered.connect(self.select_algorithm)
        tools_menu.addAction(algorithm_action)
        
        chart_action = QAction('图表类型', self)
        chart_action.triggered.connect(self.select_chart_type)
        tools_menu.addAction(chart_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        help_action = QAction('帮助', self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    # 初始化布局
    def initLayout(self):
        # 设置中央控件
        self.setCentralWidget(self.central_widget)
        
        # 添加按钮到左侧布局（使用已初始化的变量）
        self.left_layout.addWidget(self.data_title)
        self.left_layout.addWidget(self.import_button)
        self.left_layout.addWidget(self.export_button)
        
        self.left_layout.addWidget(self.tools_title)
        self.left_layout.addWidget(self.algorithm_button)
        self.left_layout.addWidget(self.charts_button)
        
        self.left_layout.addWidget(self.system_title)
        self.left_layout.addWidget(self.help_button)
        self.left_layout.addWidget(self.about_button)
        self.left_layout.addWidget(self.exit_button)
        
        # 添加弹性空间
        self.left_layout.addStretch()
        
        # 添加图表到右侧布局
        self.right_layout.addWidget(self.view)
        
        # 添加到分割器
        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.right_widget)
        self.splitter.setSizes([250, 950])  # 设置初始大小比例
        
        # 设置主布局
        self.main_layout.addWidget(self.splitter)
        self.central_widget.setLayout(self.main_layout)
    # 连接信号
    def connectSignals(self):
        self.import_button.clicked.connect(self.import_data)
        self.export_button.clicked.connect(self.export_data)
        self.algorithm_button.clicked.connect(self.select_algorithm)
        self.charts_button.clicked.connect(self.select_chart_type)
        self.help_button.clicked.connect(self.show_help)
        self.about_button.clicked.connect(self.show_about)
        self.exit_button.clicked.connect(self.close)
    
    # 槽函数
    def import_data(self):
        print("导入数据功能")
    
    def export_data(self):
        print("导出数据功能")
    
    def select_algorithm(self):
        print("算法选择功能")
    
    def select_chart_type(self):
        print("图表类型选择功能")
    
    def show_help(self):
        print("显示帮助")
    
    def show_about(self):
        print("显示关于信息")
