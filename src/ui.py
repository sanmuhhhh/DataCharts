from PyQt5.QtWidgets import (QMainWindow, QMenuBar, QVBoxLayout, QWidget, 
                             QPushButton, QHBoxLayout, QAction, QSplitter)
from PyQt5.QtWidgets import (QDialog, QFileDialog, QLabel, QComboBox, QGridLayout,
                            QTableWidget, QTableWidgetItem, QTabWidget, QTextEdit,
                            QMessageBox, QGroupBox, QRadioButton, QCheckBox,
                            QProgressDialog, QApplication, QSlider, QButtonGroup,
                            QColorDialog, QInputDialog)
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtChart import QChartView, QChart, QLineSeries
import time

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

# 数据导入窗口类
class ImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("导入数据")
        self.setMinimumSize(600, 400)
        self.initUI()
    
    def initUI(self):
        # 创建布局
        layout = QVBoxLayout()
        
        # 文件选择部分
        file_group = QGroupBox("选择数据文件")
        file_layout = QGridLayout()
        
        self.file_path_label = QLabel("未选择文件")
        self.browse_button = QPushButton("浏览...")
        self.browse_button.clicked.connect(self.browse_file)
        
        file_layout.addWidget(QLabel("文件路径:"), 0, 0)
        file_layout.addWidget(self.file_path_label, 0, 1)
        file_layout.addWidget(self.browse_button, 0, 2)
        
        # 文件类型选择
        file_layout.addWidget(QLabel("文件类型:"), 1, 0)
        self.file_type_combo = QComboBox()
        self.file_type_combo.addItems(["CSV", "Excel", "JSON", "TXT"])
        file_layout.addWidget(self.file_type_combo, 1, 1, 1, 2)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 数据预览部分
        preview_group = QGroupBox("数据预览")
        preview_layout = QVBoxLayout()
        
        self.preview_table = QTableWidget(10, 5)
        preview_layout.addWidget(self.preview_table)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # 导入选项部分
        options_group = QGroupBox("导入选项")
        options_layout = QGridLayout()
        
        options_layout.addWidget(QLabel("包含表头:"), 0, 0)
        self.header_check = QCheckBox()
        self.header_check.setChecked(True)
        options_layout.addWidget(self.header_check, 0, 1)
        
        options_layout.addWidget(QLabel("分隔符:"), 1, 0)
        self.delimiter_combo = QComboBox()
        self.delimiter_combo.addItems([",", ";", "Tab", "Space", "其他"])
        options_layout.addWidget(self.delimiter_combo, 1, 1)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # 按钮部分
        button_layout = QHBoxLayout()
        self.import_button = QPushButton("导入")
        self.import_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择数据文件", "", 
            "CSV文件 (*.csv);;Excel文件 (*.xlsx *.xls);;JSON文件 (*.json);;文本文件 (*.txt);;所有文件 (*.*)"
        )
        
        if file_path:
            self.file_path_label.setText(file_path)
            # 这里可以添加预览数据的代码


# 数据导出窗口类
class ExportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("导出数据")
        self.setMinimumSize(500, 300)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # 导出选项
        export_group = QGroupBox("导出选项")
        export_layout = QGridLayout()
        
        export_layout.addWidget(QLabel("导出格式:"), 0, 0)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV", "Excel", "JSON", "PDF", "PNG"])
        export_layout.addWidget(self.format_combo, 0, 1)
        
        export_layout.addWidget(QLabel("导出内容:"), 1, 0)
        self.content_combo = QComboBox()
        self.content_combo.addItems(["当前数据", "当前图表", "全部"])
        export_layout.addWidget(self.content_combo, 1, 1)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # 文件选择部分
        file_group = QGroupBox("保存位置")
        file_layout = QGridLayout()
        
        self.file_path_label = QLabel("未选择保存路径")
        self.browse_button = QPushButton("浏览...")
        self.browse_button.clicked.connect(self.browse_file)
        
        file_layout.addWidget(QLabel("文件路径:"), 0, 0)
        file_layout.addWidget(self.file_path_label, 0, 1)
        file_layout.addWidget(self.browse_button, 0, 2)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 按钮部分
        button_layout = QHBoxLayout()
        self.export_button = QPushButton("导出")
        self.export_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def browse_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "选择保存位置", "", 
            "CSV文件 (*.csv);;Excel文件 (*.xlsx);;JSON文件 (*.json);;PDF文件 (*.pdf);;PNG图像 (*.png)"
        )
        
        if file_path:
            self.file_path_label.setText(file_path)


# 算法选择窗口类
class AlgorithmDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("算法选择")
        self.setMinimumSize(600, 500)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # 创建选项卡
        self.tabs = QTabWidget()
        
        # 回归分析选项卡
        regression_tab = QWidget()
        regression_layout = QVBoxLayout()
        
        regression_group = QGroupBox("回归算法")
        regression_options = QVBoxLayout()
        
        self.linear_radio = QRadioButton("线性回归")
        self.linear_radio.setChecked(True)
        self.polynomial_radio = QRadioButton("多项式回归")
        self.ridge_radio = QRadioButton("岭回归")
        self.lasso_radio = QRadioButton("Lasso回归")
        
        regression_options.addWidget(self.linear_radio)
        regression_options.addWidget(self.polynomial_radio)
        regression_options.addWidget(self.ridge_radio)
        regression_options.addWidget(self.lasso_radio)
        
        regression_group.setLayout(regression_options)
        regression_layout.addWidget(regression_group)
        
        # 回归参数设置
        regression_params = QGroupBox("参数设置")
        params_layout = QGridLayout()
        
        params_layout.addWidget(QLabel("多项式阶数:"), 0, 0)
        self.poly_degree = QComboBox()
        self.poly_degree.addItems(["2", "3", "4", "5", "6"])
        params_layout.addWidget(self.poly_degree, 0, 1)
        
        params_layout.addWidget(QLabel("正则化系数:"), 1, 0)
        self.alpha_combo = QComboBox()
        self.alpha_combo.addItems(["0.01", "0.1", "1.0", "10.0", "100.0"])
        params_layout.addWidget(self.alpha_combo, 1, 1)
        
        regression_params.setLayout(params_layout)
        regression_layout.addWidget(regression_params)
        
        regression_tab.setLayout(regression_layout)
        
        # 分类分析选项卡
        classification_tab = QWidget()
        classification_layout = QVBoxLayout()
        
        classification_group = QGroupBox("分类算法")
        classification_options = QVBoxLayout()
        
        self.knn_radio = QRadioButton("K近邻")
        self.knn_radio.setChecked(True)
        self.svm_radio = QRadioButton("支持向量机")
        self.dt_radio = QRadioButton("决策树")
        self.rf_radio = QRadioButton("随机森林")
        
        classification_options.addWidget(self.knn_radio)
        classification_options.addWidget(self.svm_radio)
        classification_options.addWidget(self.dt_radio)
        classification_options.addWidget(self.rf_radio)
        
        classification_group.setLayout(classification_options)
        classification_layout.addWidget(classification_group)
        
        classification_tab.setLayout(classification_layout)
        
        # 聚类分析选项卡
        clustering_tab = QWidget()
        clustering_layout = QVBoxLayout()
        
        clustering_group = QGroupBox("聚类算法")
        clustering_options = QVBoxLayout()
        
        self.kmeans_radio = QRadioButton("K-Means")
        self.kmeans_radio.setChecked(True)
        self.hierarchical_radio = QRadioButton("层次聚类")
        self.dbscan_radio = QRadioButton("DBSCAN")
        
        clustering_options.addWidget(self.kmeans_radio)
        clustering_options.addWidget(self.hierarchical_radio)
        clustering_options.addWidget(self.dbscan_radio)
        
        clustering_group.setLayout(clustering_options)
        clustering_layout.addWidget(clustering_group)
        
        clustering_tab.setLayout(clustering_layout)
        
        # 添加选项卡
        self.tabs.addTab(regression_tab, "回归分析")
        self.tabs.addTab(classification_tab, "分类分析")
        self.tabs.addTab(clustering_tab, "聚类分析")
        
        layout.addWidget(self.tabs)
        
        # 按钮部分
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("应用")
        self.apply_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)


# 图表类型选择窗口类
class ChartTypeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("图表类型选择")
        self.setMinimumSize(700, 500)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # 创建选项卡
        self.tabs = QTabWidget()
        
        # 基础图表选项卡
        basic_tab = QWidget()
        basic_layout = QGridLayout()
        
        # 添加各种图表类型按钮
        self.line_button = QPushButton("折线图")
        self.line_button.setCheckable(True)
        self.line_button.setChecked(True)
        basic_layout.addWidget(self.line_button, 0, 0)
        
        self.bar_button = QPushButton("柱状图")
        self.bar_button.setCheckable(True)
        basic_layout.addWidget(self.bar_button, 0, 1)
        
        self.pie_button = QPushButton("饼图")
        self.pie_button.setCheckable(True)
        basic_layout.addWidget(self.pie_button, 0, 2)
        
        self.scatter_button = QPushButton("散点图")
        self.scatter_button.setCheckable(True)
        basic_layout.addWidget(self.scatter_button, 1, 0)
        
        self.area_button = QPushButton("面积图")
        self.area_button.setCheckable(True)
        basic_layout.addWidget(self.area_button, 1, 1)
        
        self.bubble_button = QPushButton("气泡图")
        self.bubble_button.setCheckable(True)
        basic_layout.addWidget(self.bubble_button, 1, 2)
        
        basic_tab.setLayout(basic_layout)
        
        # 高级图表选项卡
        advanced_tab = QWidget()
        advanced_layout = QGridLayout()
        
        self.box_button = QPushButton("箱线图")
        self.box_button.setCheckable(True)
        advanced_layout.addWidget(self.box_button, 0, 0)
        
        self.candlestick_button = QPushButton("K线图")
        self.candlestick_button.setCheckable(True)
        advanced_layout.addWidget(self.candlestick_button, 0, 1)
        
        self.heatmap_button = QPushButton("热力图")
        self.heatmap_button.setCheckable(True)
        advanced_layout.addWidget(self.heatmap_button, 0, 2)
        
        self.radar_button = QPushButton("雷达图")
        self.radar_button.setCheckable(True)
        advanced_layout.addWidget(self.radar_button, 1, 0)
        
        self.funnel_button = QPushButton("漏斗图")
        self.funnel_button.setCheckable(True)
        advanced_layout.addWidget(self.funnel_button, 1, 1)
        
        self.gauge_button = QPushButton("仪表盘")
        self.gauge_button.setCheckable(True)
        advanced_layout.addWidget(self.gauge_button, 1, 2)
        
        advanced_tab.setLayout(advanced_layout)
        
        # 自定义图表选项卡
        custom_tab = QWidget()
        custom_layout = QVBoxLayout()
        
        custom_layout.addWidget(QLabel("自定义图表配置将在此处显示"))
        
        custom_tab.setLayout(custom_layout)
        
        # 添加选项卡
        self.tabs.addTab(basic_tab, "基础图表")
        self.tabs.addTab(advanced_tab, "高级图表")
        self.tabs.addTab(custom_tab, "自定义图表")
        
        layout.addWidget(self.tabs)
        
        # 图表预览
        preview_group = QGroupBox("图表预览")
        preview_layout = QVBoxLayout()
        
        self.preview_chart = QChart()
        self.preview_chart.setTitle("预览")
        self.preview_view = QChartView(self.preview_chart)
        preview_layout.addWidget(self.preview_view)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # 按钮部分
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("应用")
        self.apply_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)


# 帮助窗口类
class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("帮助")
        self.setMinimumSize(700, 500)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # 创建选项卡
        self.tabs = QTabWidget()
        
        # 基本使用选项卡
        basic_tab = QWidget()
        basic_layout = QVBoxLayout()
        
        basic_text = QTextEdit()
        basic_text.setReadOnly(True)
        basic_text.setHtml("""
        <h2>基本使用指南</h2>
        <p>DataCharts是一款功能强大的数据图表分析工具，可以帮助您导入、分析和可视化数据。</p>
        
        <h3>主要功能</h3>
        <ul>
            <li><b>导入数据</b>：支持CSV、Excel、JSON等多种格式</li>
            <li><b>数据分析</b>：内置多种统计和机器学习算法</li>
            <li><b>图表可视化</b>：支持多种图表类型，包括折线图、柱状图、散点图等</li>
            <li><b>导出结果</b>：将分析结果和图表导出为多种格式</li>
        </ul>
        
        <h3>快速入门</h3>
        <ol>
            <li>点击"导入数据"按钮导入您的数据文件</li>
            <li>选择合适的分析算法进行数据分析</li>
            <li>选择图表类型展示分析结果</li>
            <li>根据需要调整图表参数</li>
            <li>导出分析结果或图表</li>
        </ol>
        """)
        
        basic_layout.addWidget(basic_text)
        basic_tab.setLayout(basic_layout)
        
        # 功能详解选项卡
        features_tab = QWidget()
        features_layout = QVBoxLayout()
        
        features_text = QTextEdit()
        features_text.setReadOnly(True)
        features_text.setHtml("""
        <h2>功能详解</h2>
        
        <h3>数据导入</h3>
        <p>支持多种数据格式，包括CSV、Excel、JSON和纯文本文件。导入时可以设置分隔符、表头等选项。</p>
        
        <h3>数据分析算法</h3>
        <p>内置多种分析算法：</p>
        <ul>
            <li><b>回归分析</b>：线性回归、多项式回归、岭回归等</li>
            <li><b>分类分析</b>：K近邻、支持向量机、决策树等</li>
            <li><b>聚类分析</b>：K-Means、层次聚类、DBSCAN等</li>
        </ul>
        
        <h3>图表类型</h3>
        <p>支持多种图表类型：</p>
        <ul>
            <li><b>基础图表</b>：折线图、柱状图、饼图、散点图等</li>
            <li><b>高级图表</b>：箱线图、热力图、雷达图等</li>
            <li><b>自定义图表</b>：可以自定义图表参数和样式</li>
        </ul>
        """)
        
        features_layout.addWidget(features_text)
        features_tab.setLayout(features_layout)
        
        # 常见问题选项卡
        faq_tab = QWidget()
        faq_layout = QVBoxLayout()
        
        faq_text = QTextEdit()
        faq_text.setReadOnly(True)
        faq_text.setHtml("""
        <h2>常见问题</h2>
        
        <h3>Q: 如何导入大型数据文件？</h3>
        <p>A: 对于大型数据文件，建议使用分块导入功能，或者先对数据进行预处理，减小文件大小。</p>
        
        <h3>Q: 如何选择合适的图表类型？</h3>
        <p>A: 不同的数据适合不同的图表类型：</p>
        <ul>
            <li>时间序列数据适合折线图</li>
            <li>分类比较适合柱状图或饼图</li>
            <li>相关性分析适合散点图</li>
            <li>多维数据适合雷达图或平行坐标图</li>
        </ul>
        
        <h3>Q: 如何保存我的分析项目？</h3>
        <p>A: 您可以使用"文件"菜单中的"保存项目"功能，将当前的数据、分析设置和图表配置保存为项目文件。</p>
        
        <h3>Q: 如何自定义图表样式？</h3>
        <p>A: 在图表类型选择对话框中，切换到"自定义图表"选项卡，可以设置颜色、字体、标签等样式。</p>
        """)
        
        faq_layout.addWidget(faq_text)
        faq_tab.setLayout(faq_layout)
        
        # 添加选项卡
        self.tabs.addTab(basic_tab, "基本使用")
        self.tabs.addTab(features_tab, "功能详解")
        self.tabs.addTab(faq_tab, "常见问题")
        
        layout.addWidget(self.tabs)
        
        # 按钮部分
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)


# 关于窗口类
class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于 DataCharts")
        self.setMinimumSize(400, 300)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # 应用信息
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setHtml("""
        <div style="text-align: center;">
            <h1>DataCharts</h1>
            <h3>数据图表分析工具</h3>
            <p>版本: 1.0.0</p>
            <p>© 2023 DataCharts Team. 保留所有权利。</p>
            <br>
            <p>DataCharts是一款功能强大的数据分析和可视化工具，支持多种数据格式、分析算法和图表类型。</p>
            <br>
            <p>技术支持: support@datacharts.example.com</p>
            <p>官方网站: <a href="https://www.datacharts.example.com">www.datacharts.example.com</a></p>
        </div>
        """)
        
        layout.addWidget(info_text)
        
        # 按钮部分
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)


# 数据分析结果窗口类
class AnalysisResultDialog(QDialog):
    def __init__(self, parent=None, result_data=None):
        super().__init__(parent)
        self.setWindowTitle("数据分析结果")
        self.setMinimumSize(800, 600)
        self.result_data = result_data
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # 创建选项卡
        self.tabs = QTabWidget()
        
        # 结果概览选项卡
        overview_tab = QWidget()
        overview_layout = QVBoxLayout()
        
        # 结果摘要
        summary_group = QGroupBox("分析摘要")
        summary_layout = QVBoxLayout()
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setHtml("""
        <h3>分析结果摘要</h3>
        <p><b>数据集大小:</b> 1000行 × 8列</p>
        <p><b>使用算法:</b> 线性回归</p>
        <p><b>模型性能:</b> R² = 0.85</p>
        <p><b>执行时间:</b> 0.45秒</p>
        <p><b>主要发现:</b> 变量X1和Y呈强正相关，变量X3对结果影响较小</p>
        """)
        
        summary_layout.addWidget(self.summary_text)
        summary_group.setLayout(summary_layout)
        overview_layout.addWidget(summary_group)
        
        # 关键指标
        metrics_group = QGroupBox("关键指标")
        metrics_layout = QGridLayout()
        
        metrics = [
            ("均方误差(MSE)", "0.245"),
            ("平均绝对误差(MAE)", "0.189"),
            ("R²值", "0.850"),
            ("调整后R²", "0.843"),
            ("F统计量", "245.32"),
            ("p值", "< 0.001")
        ]
        
        for i, (name, value) in enumerate(metrics):
            row = i // 3
            col = i % 3
            metrics_layout.addWidget(QLabel(f"<b>{name}:</b>"), row, col*2)
            metrics_layout.addWidget(QLabel(value), row, col*2+1)
        
        metrics_group.setLayout(metrics_layout)
        overview_layout.addWidget(metrics_group)
        
        overview_tab.setLayout(overview_layout)
        
        # 详细结果选项卡
        details_tab = QWidget()
        details_layout = QVBoxLayout()
        
        # 模型参数
        params_group = QGroupBox("模型参数")
        params_layout = QVBoxLayout()
        
        self.params_table = QTableWidget(5, 3)
        self.params_table.setHorizontalHeaderLabels(["参数", "值", "p值"])
        
        # 填充示例数据
        params_data = [
            ("截距", "1.234", "0.001"),
            ("X1", "0.567", "0.002"),
            ("X2", "0.890", "< 0.001"),
            ("X3", "0.123", "0.345"),
            ("X4", "0.456", "0.005")
        ]
        
        for i, (param, value, p) in enumerate(params_data):
            self.params_table.setItem(i, 0, QTableWidgetItem(param))
            self.params_table.setItem(i, 1, QTableWidgetItem(value))
            self.params_table.setItem(i, 2, QTableWidgetItem(p))
        
        params_layout.addWidget(self.params_table)
        params_group.setLayout(params_layout)
        details_layout.addWidget(params_group)
        
        # 残差分析
        residuals_group = QGroupBox("残差分析")
        residuals_layout = QVBoxLayout()
        
        self.residuals_chart = QChart()
        self.residuals_chart.setTitle("残差分布")
        self.residuals_view = QChartView(self.residuals_chart)
        
        # 这里可以添加残差图表的代码
        
        residuals_layout.addWidget(self.residuals_view)
        residuals_group.setLayout(residuals_layout)
        details_layout.addWidget(residuals_group)
        
        details_tab.setLayout(details_layout)
        
        # 可视化选项卡
        viz_tab = QWidget()
        viz_layout = QVBoxLayout()
        
        # 图表选择
        chart_select_layout = QHBoxLayout()
        chart_select_layout.addWidget(QLabel("选择图表类型:"))
        
        self.chart_combo = QComboBox()
        self.chart_combo.addItems(["散点图", "线性拟合", "残差图", "Q-Q图", "预测vs实际"])
        chart_select_layout.addWidget(self.chart_combo)
        
        viz_layout.addLayout(chart_select_layout)
        
        # 图表显示
        self.viz_chart = QChart()
        self.viz_chart.setTitle("数据可视化")
        self.viz_view = QChartView(self.viz_chart)
        
        # 这里可以添加可视化图表的代码
        
        viz_layout.addWidget(self.viz_view)
        viz_tab.setLayout(viz_layout)
        
        # 添加选项卡
        self.tabs.addTab(overview_tab, "结果概览")
        self.tabs.addTab(details_tab, "详细结果")
        self.tabs.addTab(viz_tab, "数据可视化")
        
        layout.addWidget(self.tabs)
        
        # 按钮部分
        button_layout = QHBoxLayout()
        
        self.export_button = QPushButton("导出结果")
        self.export_button.clicked.connect(self.export_results)
        
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.export_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def export_results(self):
        # 导出分析结果的功能
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出分析结果", "", 
            "PDF文件 (*.pdf);;Excel文件 (*.xlsx);;CSV文件 (*.csv);;HTML文件 (*.html)"
        )
        
        if file_path:
            # 这里添加导出功能的代码
            QMessageBox.information(self, "导出成功", f"分析结果已成功导出到:\n{file_path}")


# 设置窗口类
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("应用设置")
        self.setMinimumSize(600, 450)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # 创建选项卡
        self.tabs = QTabWidget()
        
        # 常规设置选项卡
        general_tab = QWidget()
        general_layout = QVBoxLayout()
        
        # 语言设置
        language_group = QGroupBox("语言设置")
        language_layout = QHBoxLayout()
        
        language_layout.addWidget(QLabel("界面语言:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(["简体中文", "English", "日本語", "Español"])
        language_layout.addWidget(self.language_combo)
        language_layout.addStretch()
        
        language_group.setLayout(language_layout)
        general_layout.addWidget(language_group)
        
        # 启动设置
        startup_group = QGroupBox("启动设置")
        startup_layout = QVBoxLayout()
        
        self.load_last_check = QCheckBox("启动时加载上次项目")
        self.load_last_check.setChecked(True)
        startup_layout.addWidget(self.load_last_check)
        
        self.show_welcome_check = QCheckBox("显示欢迎页面")
        self.show_welcome_check.setChecked(True)
        startup_layout.addWidget(self.show_welcome_check)
        
        self.check_update_check = QCheckBox("自动检查更新")
        self.check_update_check.setChecked(True)
        startup_layout.addWidget(self.check_update_check)
        
        startup_group.setLayout(startup_layout)
        general_layout.addWidget(startup_group)
        
        # 文件设置
        file_group = QGroupBox("文件设置")
        file_layout = QGridLayout()
        
        file_layout.addWidget(QLabel("默认保存位置:"), 0, 0)
        self.save_path_label = QLabel("用户文档目录")
        file_layout.addWidget(self.save_path_label, 0, 1)
        self.browse_save_button = QPushButton("浏览...")
        self.browse_save_button.clicked.connect(self.browse_save_path)
        file_layout.addWidget(self.browse_save_button, 0, 2)
        
        file_layout.addWidget(QLabel("自动保存间隔:"), 1, 0)
        self.autosave_combo = QComboBox()
        self.autosave_combo.addItems(["不自动保存", "5分钟", "10分钟", "15分钟", "30分钟"])
        file_layout.addWidget(self.autosave_combo, 1, 1, 1, 2)
        
        file_group.setLayout(file_layout)
        general_layout.addWidget(file_group)
        
        general_tab.setLayout(general_layout)
        
        # 外观设置选项卡
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout()
        
        # 主题设置
        theme_group = QGroupBox("主题设置")
        theme_layout = QVBoxLayout()
        
        theme_layout.addWidget(QLabel("选择主题:"))
        
        self.light_radio = QRadioButton("浅色主题")
        self.light_radio.setChecked(True)
        theme_layout.addWidget(self.light_radio)
        
        self.dark_radio = QRadioButton("深色主题")
        theme_layout.addWidget(self.dark_radio)
        
        self.system_radio = QRadioButton("跟随系统")
        theme_layout.addWidget(self.system_radio)
        
        theme_group.setLayout(theme_layout)
        appearance_layout.addWidget(theme_group)
        
        # 字体设置
        font_group = QGroupBox("字体设置")
        font_layout = QGridLayout()
        
        font_layout.addWidget(QLabel("界面字体:"), 0, 0)
        self.ui_font_combo = QComboBox()
        self.ui_font_combo.addItems(["系统默认", "微软雅黑", "宋体", "Arial", "Helvetica"])
        font_layout.addWidget(self.ui_font_combo, 0, 1)
        
        font_layout.addWidget(QLabel("图表字体:"), 0, 2)
        self.chart_font_combo = QComboBox()
        self.chart_font_combo.addItems(["系统默认", "微软雅黑", "宋体", "Arial", "Helvetica"])
        font_layout.addWidget(self.chart_font_combo, 0, 3)
        
        font_layout.addWidget(QLabel("字体大小:"), 1, 0)
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["小", "中", "大", "超大"])
        self.font_size_combo.setCurrentText("中")
        font_layout.addWidget(self.font_size_combo, 1, 1)
        
        font_group.setLayout(font_layout)
        appearance_layout.addWidget(font_group)
        
        appearance_tab.setLayout(appearance_layout)
        
        # 高级设置选项卡
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout()
        
        # 性能设置
        performance_group = QGroupBox("性能设置")
        performance_layout = QVBoxLayout()
        
        self.hardware_accel_check = QCheckBox("启用硬件加速")
        self.hardware_accel_check.setChecked(True)
        performance_layout.addWidget(self.hardware_accel_check)
        
        self.multithreading_check = QCheckBox("启用多线程计算")
        self.multithreading_check.setChecked(True)
        performance_layout.addWidget(self.multithreading_check)
        
        performance_layout.addWidget(QLabel("线程数:"))
        thread_layout = QHBoxLayout()
        self.thread_slider = QSlider(Qt.Horizontal)
        self.thread_slider.setMinimum(1)
        self.thread_slider.setMaximum(16)
        self.thread_slider.setValue(4)
        thread_layout.addWidget(self.thread_slider)
        self.thread_label = QLabel("4")
        thread_layout.addWidget(self.thread_label)
        performance_layout.addLayout(thread_layout)
        
        performance_group.setLayout(performance_layout)
        advanced_layout.addWidget(performance_group)
        
        # 数据设置
        data_group = QGroupBox("数据处理设置")
        data_layout = QVBoxLayout()
        
        self.missing_values_check = QCheckBox("自动处理缺失值")
        self.missing_values_check.setChecked(True)
        data_layout.addWidget(self.missing_values_check)
        
        self.outliers_check = QCheckBox("自动检测异常值")
        self.outliers_check.setChecked(True)
        data_layout.addWidget(self.outliers_check)
        
        data_layout.addWidget(QLabel("数据缓存大小:"))
        cache_layout = QHBoxLayout()
        self.cache_slider = QSlider(Qt.Horizontal)
        self.cache_slider.setMinimum(100)
        self.cache_slider.setMaximum(5000)
        self.cache_slider.setValue(1000)
        self.cache_slider.setTickInterval(500)
        self.cache_slider.setTickPosition(QSlider.TicksBelow)
        cache_layout.addWidget(self.cache_slider)
        self.cache_label = QLabel("1000 MB")
        cache_layout.addWidget(self.cache_label)
        data_layout.addLayout(cache_layout)
        
        data_group.setLayout(data_layout)
        advanced_layout.addWidget(data_group)
        
        advanced_tab.setLayout(advanced_layout)
        
        # 添加选项卡
        self.tabs.addTab(general_tab, "常规设置")
        self.tabs.addTab(appearance_tab, "外观设置")
        self.tabs.addTab(advanced_tab, "高级设置")
        
        layout.addWidget(self.tabs)
        
        # 按钮部分
        button_layout = QHBoxLayout()
        
        self.restore_defaults_button = QPushButton("恢复默认设置")
        self.restore_defaults_button.clicked.connect(self.restore_defaults)
        
        self.apply_button = QPushButton("应用")
        self.apply_button.clicked.connect(self.apply_settings)
        
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.restore_defaults_button)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def browse_save_path(self):
        folder_path = QFileDialog.getExistingDirectory(
            self, "选择默认保存位置", ""
        )
        
        if folder_path:
            self.save_path_label.setText(folder_path)
    
    def restore_defaults(self):
        # 恢复默认设置
        self.language_combo.setCurrentText("简体中文")
        self.load_last_check.setChecked(True)
        self.show_welcome_check.setChecked(True)
        self.check_update_check.setChecked(True)
        self.save_path_label.setText("用户文档目录")
        self.autosave_combo.setCurrentText("10分钟")
        
        self.light_radio.setChecked(True)
        self.ui_font_combo.setCurrentText("系统默认")
        self.font_size_combo.setCurrentText("中")
        
        self.hardware_accel_check.setChecked(True)
        self.multithreading_check.setChecked(True)
        self.thread_slider.setValue(4)
        self.thread_label.setText("4")
        
        self.missing_values_check.setChecked(True)
        self.outliers_check.setChecked(True)
        self.cache_slider.setValue(1000)
        self.cache_label.setText("1000 MB")
    
    def apply_settings(self):
        # 应用设置
        QMessageBox.information(self, "设置已应用", "您的设置已成功应用")


# 主题设置窗口类
class ThemeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("主题设置")
        self.setMinimumSize(700, 500)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # 主题预览
        preview_group = QGroupBox("主题预览")
        preview_layout = QVBoxLayout()
        
        self.preview_widget = QWidget()
        self.preview_widget.setMinimumHeight(200)
        self.preview_widget.setStyleSheet("""
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 8px;
        """)
        
        preview_layout.addWidget(self.preview_widget)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # 主题选择
        themes_group = QGroupBox("预设主题")
        themes_layout = QGridLayout()
        
        theme_buttons = [
            ("默认蓝", "#2196F3"),
            ("深邃黑", "#212121"),
            ("清新绿", "#4CAF50"),
            ("活力橙", "#FF9800"),
            ("典雅紫", "#9C27B0"),
            ("热情红", "#F44336")
        ]
        
        self.theme_button_group = QButtonGroup(self)
        
        for i, (name, color) in enumerate(theme_buttons):
            row = i // 3
            col = i % 3
            
            button = QPushButton(name)
            button.setCheckable(True)
            button.setMinimumHeight(40)
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                }}
                QPushButton:checked {{
                    border: 2px solid #FFC107;
                }}
            """)
            
            if i == 0:
                button.setChecked(True)
            
            self.theme_button_group.addButton(button, i)
            themes_layout.addWidget(button, row, col)
        
        themes_group.setLayout(themes_layout)
        layout.addWidget(themes_group)
        
        # 自定义颜色
        custom_group = QGroupBox("自定义颜色")
        custom_layout = QGridLayout()
        
        color_items = [
            ("主题色:", "#2196F3"),
            ("背景色:", "#FFFFFF"),
            ("文本色:", "#212121"),
            ("强调色:", "#FFC107"),
            ("成功色:", "#4CAF50"),
            ("错误色:", "#F44336")
        ]
        
        self.color_buttons = {}
        
        for i, (label_text, default_color) in enumerate(color_items):
            row = i // 3
            col = (i % 3) * 2
            
            custom_layout.addWidget(QLabel(label_text), row, col)
            
            color_button = QPushButton()
            color_button.setMinimumSize(80, 30)
            color_button.setStyleSheet(f"""
                background-color: {default_color};
                border: 1px solid #ddd;
                border-radius: 4px;
            """)
            color_button.clicked.connect(lambda _, btn=color_button: self.select_color(btn))
            
            self.color_buttons[label_text] = color_button
            custom_layout.addWidget(color_button, row, col + 1)
        
        custom_group.setLayout(custom_layout)
        layout.addWidget(custom_group)
        
        # 字体设置
        font_group = QGroupBox("字体设置")
        font_layout = QGridLayout()
        
        font_layout.addWidget(QLabel("界面字体:"), 0, 0)
        self.ui_font_combo = QComboBox()
        self.ui_font_combo.addItems(["系统默认", "微软雅黑", "宋体", "Arial", "Helvetica"])
        font_layout.addWidget(self.ui_font_combo, 0, 1)
        
        font_layout.addWidget(QLabel("图表字体:"), 0, 2)
        self.chart_font_combo = QComboBox()
        self.chart_font_combo.addItems(["系统默认", "微软雅黑", "宋体", "Arial", "Helvetica"])
        font_layout.addWidget(self.chart_font_combo, 0, 3)
        
        font_layout.addWidget(QLabel("字体大小:"), 1, 0)
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["小", "中", "大", "超大"])
        self.font_size_combo.setCurrentText("中")
        font_layout.addWidget(self.font_size_combo, 1, 1)
        
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)
        
        # 按钮部分
        button_layout = QHBoxLayout()
        
        self.save_theme_button = QPushButton("保存为自定义主题")
        self.save_theme_button.clicked.connect(self.save_custom_theme)
        
        self.apply_button = QPushButton("应用")
        self.apply_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_theme_button)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def select_color(self, button):
        current_color = button.palette().button().color()
        color = QColorDialog.getColor(current_color, self, "选择颜色")
        
        if color.isValid():
            button.setStyleSheet(f"""
                background-color: {color.name()};
                border: 1px solid #ddd;
                border-radius: 4px;
            """)
    
    def save_custom_theme(self):
        name, ok = QInputDialog.getText(self, "保存自定义主题", "请输入主题名称:")
        
        if ok and name:
            QMessageBox.information(self, "主题已保存", f"主题 \"{name}\" 已成功保存")


# 更新MainWindow类，添加设置菜单和相关功能
def update_MainWindow_menu():
    # 这些方法将添加到MainWindow类中
    
    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec_()
    
    def show_theme_settings(self):
        dialog = ThemeDialog(self)
        dialog.exec_()
    
    def show_analysis_result(self):
        dialog = AnalysisResultDialog(self)
        dialog.exec_()
    
    # 更新initMenu方法
    original_init_menu = MainWindow.initMenu
    
    def new_init_menu(self):
        original_init_menu(self)
        
        menubar = self.menuBar()
        
        # 添加设置菜单
        settings_menu = menubar.addMenu('设置')
        
        settings_action = QAction('应用设置', self)
        settings_action.triggered.connect(self.show_settings)
        settings_menu.addAction(settings_action)
        
        theme_action = QAction('主题设置', self)
        theme_action.triggered.connect(self.show_theme_settings)
        settings_menu.addAction(theme_action)
    
    # 添加新方法到MainWindow类
    MainWindow.show_settings = show_settings
    MainWindow.show_theme_settings = show_theme_settings
    MainWindow.show_analysis_result = show_analysis_result
    
    # 替换initMenu方法
    MainWindow.initMenu = new_init_menu

# 调用函数更新MainWindow类的菜单
update_MainWindow_menu()


# 更新MainWindow类中的select_algorithm方法，使其在算法应用后显示分析结果
def update_algorithm_handler():
    original_select_algorithm = MainWindow.select_algorithm
    
    def new_select_algorithm(self):
        dialog = AlgorithmDialog(self)
        if dialog.exec_():
            # 处理算法选择
            print("算法选择完成")
            
            # 模拟算法执行过程
            progress = QProgressDialog("正在执行分析...", "取消", 0, 100, self)
            progress.setWindowTitle("请稍候")
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            # 模拟进度
            for i in range(101):
                progress.setValue(i)
                QApplication.processEvents()
                time.sleep(0.02)  # 模拟计算时间
                
                if progress.wasCanceled():
                    break
            
            # 显示分析结果
            if not progress.wasCanceled():
                self.show_analysis_result()
    
    # 替换方法
    MainWindow.select_algorithm = new_select_algorithm

# 更新导入部分
from PyQt5.QtWidgets import (QMainWindow, QMenuBar, QVBoxLayout, QWidget, 
                             QPushButton, QHBoxLayout, QAction, QSplitter)
from PyQt5.QtWidgets import (QDialog, QFileDialog, QLabel, QComboBox, QGridLayout,
                            QTableWidget, QTableWidgetItem, QTabWidget, QTextEdit,
                            QMessageBox, QGroupBox, QRadioButton, QCheckBox,
                            QProgressDialog, QApplication, QSlider, QButtonGroup,
                            QColorDialog, QInputDialog)
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtChart import QChartView, QChart, QLineSeries
import time

# 调用函数更新算法处理方法
update_algorithm_handler()
