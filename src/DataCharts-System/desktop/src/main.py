"""
数据可视化系统桌面客户端主文件

使用PyQt6提供本地数据可视化功能，集成后端API服务
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QTabWidget, QMenuBar, QStatusBar, QToolBar, QMessageBox, QSplitter,
    QPushButton, QGroupBox, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QIcon, QFont

# 添加当前目录到路径
current_dir = os.path.dirname(__file__)
sys.path.insert(0, current_dir)

# 导入API客户端
try:
    from utils.api_client import APIManager
except ImportError as e:
    print(f"警告: API客户端导入失败 - {e}")
    class APIManager:
        def __init__(self, base_url=""):
            self.is_connected = False
        def test_connection_async(self):
            pass
        def is_backend_available(self):
            return False
        connection_tested = None

# 导入UI组件
try:
    from ui.data_import_widget import DataImportWidget
    from ui.function_widget import FunctionWidget
    from ui.chart_widget import ChartWidget
except ImportError as e:
    print(f"警告: UI组件导入失败 - {e}")
    # 创建占位符组件
    from PyQt6.QtWidgets import QLabel
    class DataImportWidget(QLabel):
        def __init__(self, api_manager=None):
            super().__init__("数据导入组件占位符")
            self.data_imported = None
    class FunctionWidget(QLabel):
        def __init__(self, api_manager=None):
            super().__init__("函数处理组件占位符")
            self.function_applied = None
    class ChartWidget(QLabel):
        def __init__(self, api_manager=None):
            super().__init__("图表显示组件占位符")
            self.chart_generated = None


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.current_data = None
        
        # 初始化API管理器
        self.api_manager = APIManager("http://localhost:8000")
        
        self.init_ui()
        self.setup_connections()
        self.setup_status_timer()
        self.test_backend_connection()
    
    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle("DataCharts System v0.1.0 - 数据可视化系统 (集成版)")
        self.setGeometry(100, 100, 1600, 1000)
        
        # 设置窗口最小大小，确保可以调整大小
        self.setMinimumSize(800, 600)
        
        # 确保窗口可以调整大小（默认情况下应该是可以的，但明确设置）
        self.setWindowFlags(self.windowFlags())
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_tool_bar()
        
        # 创建中心部件
        self.create_central_widget()
        
        # 创建状态栏
        self.create_status_bar()
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                top: -1px;
                background: white;
                border-radius: 5px;
            }
            QTabBar::tab {
                background: #e8e8e8;
                border: 1px solid #c0c0c0;
                padding: 10px 15px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 1px solid white;
                color: #2c3e50;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background: #ddd;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        
        # 导入数据动作
        import_action = QAction('导入数据(&I)', self)
        import_action.setShortcut('Ctrl+I')
        import_action.setStatusTip('导入数据文件')
        import_action.triggered.connect(self.trigger_import)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        # 退出动作
        exit_action = QAction('退出(&Q)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('退出应用程序')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu('工具(&T)')
        
        # 函数库动作
        functions_action = QAction('函数库(&F)', self)
        functions_action.setStatusTip('查看可用函数')
        functions_action.triggered.connect(self.show_functions)
        tools_menu.addAction(functions_action)
        
        # 连接测试动作
        connection_action = QAction('测试后端连接(&C)', self)
        connection_action.setStatusTip('测试与后端服务的连接')
        connection_action.triggered.connect(self.test_backend_connection)
        tools_menu.addAction(connection_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        
        # 关于动作
        about_action = QAction('关于(&A)', self)
        about_action.setStatusTip('关于DataCharts系统')
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_tool_bar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        self.addToolBar(toolbar)
        
        # 导入数据按钮
        import_action = QAction("导入数据", self)
        import_action.setStatusTip("导入数据文件")
        import_action.triggered.connect(self.trigger_import)
        toolbar.addAction(import_action)
        
        toolbar.addSeparator()
        
        # 生成图表按钮
        chart_action = QAction("生成图表", self)
        chart_action.setStatusTip("生成数据图表")
        chart_action.triggered.connect(self.trigger_chart_generation)
        toolbar.addAction(chart_action)
        
        toolbar.addSeparator()
        
        # 连接测试按钮
        connection_action = QAction("测试连接", self)
        connection_action.setStatusTip("测试后端连接")
        connection_action.triggered.connect(self.test_backend_connection)
        toolbar.addAction(connection_action)
    
    def create_central_widget(self):
        """创建中心部件"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建标题区域
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        
        title_label = QLabel("DataCharts - 数据可视化系统 (集成版)")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 15px; padding: 10px;")
        
        title_layout.addWidget(title_label)
        main_layout.addWidget(title_widget)
        
        # 创建连接状态区域
        self.create_connection_status_widget(main_layout)
        
        # 创建选项卡界面
        self.tab_widget = QTabWidget()
        
        # 数据导入选项卡
        self.data_import_widget = DataImportWidget(self.api_manager)
        self.tab_widget.addTab(self.data_import_widget, "数据导入")
        
        # 函数处理选项卡
        self.function_widget = FunctionWidget(self.api_manager)
        self.tab_widget.addTab(self.function_widget, "函数处理")
        
        # 图表展示选项卡
        self.chart_widget = ChartWidget(self.api_manager)
        self.tab_widget.addTab(self.chart_widget, "图表展示")
        
        main_layout.addWidget(self.tab_widget)
    
    def create_connection_status_widget(self, parent_layout):
        """创建连接状态显示区域"""
        status_group = QGroupBox("后端连接状态")
        status_layout = QHBoxLayout(status_group)
        
        self.connection_status_label = QLabel("正在检测连接...")
        self.connection_status_label.setFont(QFont("Arial", 12))
        status_layout.addWidget(self.connection_status_label)
        
        status_layout.addStretch()
        
        self.reconnect_button = QPushButton("重新连接")
        self.reconnect_button.clicked.connect(self.test_backend_connection)
        status_layout.addWidget(self.reconnect_button)
        
        self.connection_progress = QProgressBar()
        self.connection_progress.setVisible(False)
        status_layout.addWidget(self.connection_progress)
        
        status_group.setMaximumHeight(80)
        parent_layout.addWidget(status_group)
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 状态信息
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
        
        # 数据信息
        self.data_info_label = QLabel("无数据")
        self.status_bar.addPermanentWidget(self.data_info_label)
        
        # 后端连接状态
        self.backend_status_label = QLabel("后端: 检测中...")
        self.backend_status_label.setStyleSheet("color: orange;")
        self.status_bar.addPermanentWidget(self.backend_status_label)
        
        # 版本信息
        version_label = QLabel("v0.1.0")
        self.status_bar.addPermanentWidget(version_label)
    
    def setup_connections(self):
        """设置组件间的连接"""
        # 数据导入完成时的处理
        if hasattr(self.data_import_widget, 'data_imported'):
            self.data_import_widget.data_imported.connect(self.on_data_imported)
        
        # 函数应用完成时的处理
        if hasattr(self.function_widget, 'function_applied'):
            self.function_widget.function_applied.connect(self.on_function_applied)
        
        # 图表生成完成时的处理
        if hasattr(self.chart_widget, 'chart_generated'):
            self.chart_widget.chart_generated.connect(self.on_chart_generated)
        
        # 选项卡切换时的处理
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # API连接状态变化处理
        if hasattr(self.api_manager, 'connection_tested'):
            self.api_manager.connection_tested.connect(self.on_backend_connection_tested)
    
    def setup_status_timer(self):
        """设置状态更新定时器"""
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(30000)  # 每30秒检查一次状态
    
    def on_data_imported(self, data):
        """数据导入完成处理"""
        self.current_data = data
        
        # 更新状态
        if data and data.get("status") == "success":
            dataset = data.get("data", [])
            count = len(dataset) if isinstance(dataset, list) else 0
            self.data_info_label.setText(f"数据: {count} 条记录")
            self.status_label.setText("数据导入成功")
            
            # 将数据传递给其他组件
            if hasattr(self.function_widget, 'set_data'):
                self.function_widget.set_data(data)
            if hasattr(self.chart_widget, 'set_data'):
                self.chart_widget.set_data(data)
        else:
            self.status_label.setText("数据导入失败")
    
    def on_function_applied(self, result):
        """函数应用完成处理"""
        if result and result.get("status") == "success":
            self.status_label.setText("函数应用成功")
            
            # 将结果数据传递给图表组件
            if hasattr(self.chart_widget, 'set_data'):
                self.chart_widget.set_data(result)
        else:
            self.status_label.setText("函数应用失败")
    
    def on_chart_generated(self, chart_data):
        """图表生成完成处理"""
        if chart_data and chart_data.get("status") == "success":
            self.status_label.setText("图表生成成功")
        else:
            self.status_label.setText("图表生成失败")
    
    def on_tab_changed(self, index):
        """选项卡切换处理"""
        tab_names = ["数据导入", "函数处理", "图表展示"]
        if 0 <= index < len(tab_names):
            self.status_label.setText(f"当前: {tab_names[index]}")
    
    def update_status(self):
        """更新状态信息"""
        # 定期检查后端连接状态
        if hasattr(self, 'api_manager'):
            if not self.api_manager.is_backend_available():
                # 如果当前显示已连接但实际未连接，更新状态
                if "已连接" in self.backend_status_label.text():
                    self.backend_status_label.setText("后端: 连接中断")
                    self.backend_status_label.setStyleSheet("color: red;")
                    self.connection_status_label.setText("连接已中断，请检查后端服务")
                    self.connection_status_label.setStyleSheet("color: red;")
    
    def trigger_import(self):
        """触发数据导入"""
        self.tab_widget.setCurrentIndex(0)  # 切换到数据导入选项卡
        if hasattr(self.data_import_widget, 'browse_file'):
            self.data_import_widget.browse_file()
    
    def trigger_chart_generation(self):
        """触发图表生成"""
        self.tab_widget.setCurrentIndex(2)  # 切换到图表展示选项卡
        if hasattr(self.chart_widget, 'generate_chart'):
            self.chart_widget.generate_chart()
    
    def test_backend_connection(self):
        """测试后端连接"""
        self.connection_progress.setVisible(True)
        self.connection_progress.setRange(0, 0)  # 显示为无限进度条
        self.connection_status_label.setText("正在测试连接...")
        self.connection_status_label.setStyleSheet("color: orange;")
        self.backend_status_label.setText("后端: 测试中...")
        self.backend_status_label.setStyleSheet("color: orange;")
        
        if hasattr(self, 'api_manager'):
            self.api_manager.test_connection_async()
    
    def on_backend_connection_tested(self, result):
        """后端连接测试结果处理"""
        self.connection_progress.setVisible(False)
        
        if result.get("status") == "success":
            self.backend_status_label.setText("后端: 已连接")
            self.backend_status_label.setStyleSheet("color: green; font-weight: bold;")
            self.connection_status_label.setText("后端服务连接成功 77")
            self.connection_status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText("后端服务连接成功")
        else:
            self.backend_status_label.setText("后端: 未连接")
            self.backend_status_label.setStyleSheet("color: red; font-weight: bold;")
            error_msg = result.get("message", "连接失败")
            self.connection_status_label.setText(f"连接失败: {error_msg}")
            self.connection_status_label.setStyleSheet("color: red; font-weight: bold;")
            self.status_label.setText(f"后端连接失败: {error_msg}")
    
    def show_functions(self):
        """显示函数库"""
        functions_info = """
可用函数库：

数学函数：
61 np.sin, np.cos, np.tan - 三角函数
61 np.exp, np.log, np.sqrt - 指数和对数函数
61 np.abs, np.sign - 绝对值和符号函数

统计函数：
61 np.mean, np.median, np.std - 平均值、中位数、标准差
61 np.min, np.max, np.sum - 最小值、最大值、求和
61 np.cumsum, np.diff - 累积和、差分

数据处理：
61 数据归一化: (x - np.mean(x)) / np.std(x)
61 数据标准化: (x - np.min(x)) / (np.max(x) - np.min(x))
61 移动平均: np.convolve(x, np.ones(n)/n, mode='same')

变量：
61 x: 输入数据
61 支持numpy数组操作

注意：所有函数运算都通过后端API执行，确保安全性。
        """
        
        QMessageBox.information(self, "函数库", functions_info)
    
    def show_about(self):
        """显示关于信息"""
        about_text = """
DataCharts 数据可视化系统 v0.1.0 (集成版)

一个强大的数据可视化和分析工具，特色功能：
61 多种数据格式导入（CSV、Excel、JSON、TXT）
61 灵活的数学函数处理
61 丰富的图表类型
61 实时数据处理和可视化
61 与后端API服务集成
61 分布式架构支持

技术架构：
61 前端：PyQt6 桌面应用
61 后端：FastAPI + Python
61 数据处理：NumPy + Pandas + SymPy
61 图表引擎：Qt Charts + Matplotlib

开发团队：DataCharts Team
版本：v0.1.0 集成版
        """
        
        QMessageBox.about(self, "关于 DataCharts", about_text)


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("DataCharts System")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("DataCharts Team")
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    print("DataCharts System Desktop v0.1.0 (集成版) 已启动")
    print("正在测试后端连接...")
    
    # 检查是否为测试模式
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("测试模式: 应用启动成功")
        return 0
    
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
