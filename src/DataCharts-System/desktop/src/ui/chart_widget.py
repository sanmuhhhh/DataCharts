"""
图表展示界面组件

提供各种类型图表的生成和显示功能，集成后端API
"""

import sys
import os
from typing import Optional, Dict, Any, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QComboBox, QTabWidget, QScrollArea, QSpinBox,
    QCheckBox, QSlider, QMessageBox, QSplitter, QLineEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPainter
from PyQt6.QtCharts import (
    QChart, QChartView, QLineSeries, QScatterSeries, QBarSeries,
    QBarSet, QPieSeries, QAreaSeries, QValueAxis, QCategoryAxis
)

# 添加共享模块路径
shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

try:
    from chart_templates.chart_factory import ChartFactory
    from chart_templates.chart_manager import ChartManager
    from data_types import DataSource
except ImportError as e:
    # 创建占位符
    print(f"警告: 共享模块未找到，使用占位符实现 (错误: {e})")
    class ChartFactory:
        def create_chart(self, chart_type: str, data: Any, config: dict) -> dict:
            return {"status": "placeholder", "chart": None}
    
    class ChartManager:
        def __init__(self):
            pass
        
        def get_chart_types(self) -> list:
            return ["line", "scatter", "bar", "pie", "area"]


class ChartGeneratorWorker(QThread):
    """图表生成工作线程"""
    
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, chart_type: str, data: Any, config: Dict, use_backend: bool = False, api_manager=None):
        super().__init__()
        self.chart_type = chart_type
        self.data = data
        self.config = config
        self.use_backend = use_backend
        self.api_manager = api_manager
        self.factory = ChartFactory()
    
    def run(self):
        """执行图表生成"""
        try:
            self.progress.emit(30)
            
            # 如果启用后端且后端可用，尝试使用后端生成图表
            if (self.use_backend and 
                self.api_manager and 
                self.api_manager.is_backend_available()):
                
                try:
                    chart_config = {
                        "type": self.chart_type,
                        "data": self.data,
                        "config": self.config
                    }
                    
                    result = self.api_manager.get_client().create_chart(chart_config)
                    
                    if result.get("status") == "success":
                        self.progress.emit(100)
                        chart_result = result.get("data", {})
                        chart_result["backend_used"] = True
                        self.finished.emit(chart_result)
                        return
                    else:
                        print(f"后端图表生成失败，降级到本地生成: {result.get('message')}")
                        
                except Exception as e:
                    print(f"后端API调用异常，降级到本地生成: {str(e)}")
            
            # 本地生成图表
            self.progress.emit(50)
            result = self.factory.create_chart(self.chart_type, self.data, self.config)
            self.progress.emit(80)
            
            if result.get("status") == "success":
                self.progress.emit(100)
                result["backend_used"] = False
                self.finished.emit(result)
            else:
                self.error.emit(f"图表生成失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            self.error.emit(f"图表生成过程中发生错误: {str(e)}")


class ChartWidget(QWidget):
    """图表展示界面组件"""
    
    # 信号定义
    chart_generated = pyqtSignal(object)  # 图表生成完成信号
    
    def __init__(self, api_manager=None):
        super().__init__()
        self.api_manager = api_manager
        self.current_data = None
        self.current_chart = None
        self.chart_manager = ChartManager()
        self.init_ui()
        self.create_sample_chart()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QHBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：图表配置
        config_widget = QWidget()
        config_widget.setMaximumWidth(350)
        config_layout = QVBoxLayout(config_widget)
        
        # 后端选项
        backend_group = QGroupBox("生成选项")
        backend_layout = QVBoxLayout(backend_group)
        
        self.use_backend_check = QCheckBox("使用后端API生成图表")
        self.use_backend_check.setChecked(True)
        backend_layout.addWidget(self.use_backend_check)
        
        self.backend_status_label = QLabel("")
        self.backend_status_label.setFont(QFont("Arial", 9))
        backend_layout.addWidget(self.backend_status_label)
        
        config_layout.addWidget(backend_group)
        
        # 图表类型选择
        type_group = QGroupBox("图表类型")
        type_layout = QVBoxLayout(type_group)
        
        self.chart_type_combo = QComboBox()
        chart_types = [
            ("折线图", "line"),
            ("散点图", "scatter"),
            ("柱状图", "bar"),
            ("饼图", "pie"),
            ("面积图", "area"),
            ("矩阵热力图", "heatmap"),
            ("3D表面图", "surface"),
            ("等高线图", "contour")
        ]
        
        for name, value in chart_types:
            self.chart_type_combo.addItem(name, value)
        
        self.chart_type_combo.currentTextChanged.connect(self.on_chart_type_changed)
        type_layout.addWidget(self.chart_type_combo)
        
        config_layout.addWidget(type_group)
        
        # 数据配置
        data_group = QGroupBox("数据配置")
        data_layout = QVBoxLayout(data_group)
        
        # X轴数据选择
        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel("X轴数据:"))
        self.x_axis_combo = QComboBox()
        self.x_axis_combo.addItem("自动索引")
        x_layout.addWidget(self.x_axis_combo)
        data_layout.addLayout(x_layout)
        
        # Y轴数据选择
        y_layout = QHBoxLayout()
        y_layout.addWidget(QLabel("Y轴数据:"))
        self.y_axis_combo = QComboBox()
        self.y_axis_combo.addItem("全部数据")
        y_layout.addWidget(self.y_axis_combo)
        data_layout.addLayout(y_layout)
        
        # 数据范围
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("显示范围:"))
        self.start_spin = QSpinBox()
        self.start_spin.setMinimum(0)
        self.start_spin.setValue(0)
        range_layout.addWidget(self.start_spin)
        
        range_layout.addWidget(QLabel("到"))
        self.end_spin = QSpinBox()
        self.end_spin.setMinimum(1)
        self.end_spin.setValue(100)
        range_layout.addWidget(self.end_spin)
        
        data_layout.addLayout(range_layout)
        
        config_layout.addWidget(data_group)
        
        # 样式配置
        style_group = QGroupBox("样式配置")
        style_layout = QVBoxLayout(style_group)
        
        # 标题
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("标题:"))
        self.title_edit = QLineEdit()
        self.title_edit.setText("数据可视化图表")
        title_layout.addWidget(self.title_edit)
        style_layout.addLayout(title_layout)
        
        # 显示选项
        self.show_legend_check = QCheckBox("显示图例")
        self.show_legend_check.setChecked(True)
        style_layout.addWidget(self.show_legend_check)
        
        self.show_grid_check = QCheckBox("显示网格")
        self.show_grid_check.setChecked(True)
        style_layout.addWidget(self.show_grid_check)
        
        self.animation_check = QCheckBox("启用动画")
        self.animation_check.setChecked(True)
        style_layout.addWidget(self.animation_check)
        
        config_layout.addWidget(style_group)
        
        # 操作按钮
        button_group = QGroupBox("操作")
        button_layout = QVBoxLayout(button_group)
        
        self.generate_button = QPushButton("生成图表")
        self.generate_button.clicked.connect(self.generate_chart)
        self.generate_button.setEnabled(False)
        button_layout.addWidget(self.generate_button)
        
        self.export_button = QPushButton("导出图表")
        self.export_button.clicked.connect(self.export_chart)
        self.export_button.setEnabled(False)
        button_layout.addWidget(self.export_button)
        
        self.clear_button = QPushButton("清空图表")
        self.clear_button.clicked.connect(self.clear_chart)
        button_layout.addWidget(self.clear_button)
        
        # 进度条
        from PyQt6.QtWidgets import QProgressBar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        button_layout.addWidget(self.progress_bar)
        
        config_layout.addWidget(button_group)
        
        # 添加伸缩空间
        config_layout.addStretch()
        
        # 右侧：图表显示
        chart_widget = QWidget()
        chart_layout = QVBoxLayout(chart_widget)
        
        # 图表信息
        info_layout = QHBoxLayout()
        self.chart_info = QLabel("暂无图表")
        self.chart_info.setFont(QFont("Arial", 12))
        self.chart_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.chart_info)
        
        # 图表生成状态
        self.generation_status_label = QLabel("")
        self.generation_status_label.setFont(QFont("Arial", 9))
        info_layout.addWidget(self.generation_status_label)
        info_layout.addStretch()
        
        chart_layout.addLayout(info_layout)
        
        # 图表视图
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setStyleSheet("""
            QChartView {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
            }
        """)
        chart_layout.addWidget(self.chart_view)
        
        # 添加到分割器
        splitter.addWidget(config_widget)
        splitter.addWidget(chart_widget)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
        
        # 检查后端状态
        self.update_backend_status()
    
    def on_chart_type_changed(self):
        """图表类型改变时的处理"""
        chart_type = self.chart_type_combo.currentData()
        
        # 根据图表类型调整配置选项
        if chart_type in ["pie"]:
            # 饼图只需要一个数据维度
            self.x_axis_combo.setEnabled(False)
            self.y_axis_combo.setEnabled(True)
        elif chart_type in ["heatmap", "surface", "contour"]:
            # 矩阵图需要二维数据
            self.x_axis_combo.setEnabled(True)
            self.y_axis_combo.setEnabled(True)
        else:
            # 其他图表需要X和Y轴数据
            self.x_axis_combo.setEnabled(True)
            self.y_axis_combo.setEnabled(True)
    
    def update_backend_status(self):
        """更新后端状态显示"""
        if self.api_manager and self.api_manager.is_backend_available():
            self.backend_status_label.setText("77 后端可用")
            self.backend_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.backend_status_label.setText("72 后端不可用")
            self.backend_status_label.setStyleSheet("color: orange; font-weight: bold;")
    
    def create_sample_chart(self):
        """创建示例图表"""
        # 创建简单的折线图示例
        chart = QChart()
        chart.setTitle("示例图表 - 请导入数据并生成图表")
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        
        # 创建示例数据
        series = QLineSeries()
        for i in range(10):
            series.append(i, i * i)
        
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.legend().setVisible(False)
        
        self.chart_view.setChart(chart)
        self.chart_info.setText("示例图表 - 请导入数据并生成图表")
    
    def set_data(self, data):
        """设置当前数据"""
        self.current_data = data
        
        if data and data.get("status") == "success":
            dataset = data.get("data", [])
            
            # 更新数据选择选项
            self.x_axis_combo.clear()
            self.y_axis_combo.clear()
            
            self.x_axis_combo.addItem("自动索引")
            self.y_axis_combo.addItem("全部数据")
            
            if dataset and isinstance(dataset, list) and len(dataset) > 0:
                if isinstance(dataset[0], dict):
                    # 字典格式数据
                    keys = list(dataset[0].keys())
                    for key in keys:
                        self.x_axis_combo.addItem(key)
                        self.y_axis_combo.addItem(key)
                elif isinstance(dataset[0], (list, tuple)):
                    # 列表格式数据
                    for i in range(len(dataset[0])):
                        column_name = f"列{i+1}"
                        self.x_axis_combo.addItem(column_name)
                        self.y_axis_combo.addItem(column_name)
                
                # 更新数据范围
                self.end_spin.setMaximum(len(dataset))
                self.end_spin.setValue(min(100, len(dataset)))
                
                self.generate_button.setEnabled(True)
            else:
                self.generate_button.setEnabled(False)
        else:
            self.generate_button.setEnabled(False)
    
    def generate_chart(self):
        """生成图表"""
        if not self.current_data:
            QMessageBox.warning(self, "警告", "请先导入数据")
            return
        
        self.update_backend_status()
        
        # 获取配置
        chart_type = self.chart_type_combo.currentData()
        config = {
            "title": self.title_edit.text(),
            "show_legend": self.show_legend_check.isChecked(),
            "show_grid": self.show_grid_check.isChecked(),
            "animation": self.animation_check.isChecked(),
            "x_axis": self.x_axis_combo.currentText(),
            "y_axis": self.y_axis_combo.currentText(),
            "start_index": self.start_spin.value(),
            "end_index": self.end_spin.value()
        }
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.generate_button.setEnabled(False)
        
        # 创建并启动工作线程
        use_backend = self.use_backend_check.isChecked()
        self.worker = ChartGeneratorWorker(chart_type, self.current_data, config, use_backend, self.api_manager)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_chart_finished)
        self.worker.error.connect(self.on_chart_error)
        self.worker.start()
    
    def on_chart_finished(self, result):
        """图表生成完成处理"""
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)
        
        # 如果是后端生成的图表，显示占位符
        if result.get("backend_used"):
            self.generation_status_label.setText("77 后端生成")
            self.generation_status_label.setStyleSheet("color: green; font-weight: bold;")
            
            # 创建占位符图表显示后端生成成功
            chart = QChart()
            chart.setTitle(f"后端生成图表成功 - {self.chart_type_combo.currentText()}")
            self.chart_view.setChart(chart)
            self.chart_info.setText("图表已在后端生成 - 集成完整后端渲染功能待实现")
        else:
            self.generation_status_label.setText("○ 本地生成")
            self.generation_status_label.setStyleSheet("color: #666; font-weight: normal;")
            
            # 本地生成Qt图表
            self.generate_qt_chart_local()
        
        self.current_chart = result
        self.export_button.setEnabled(True)
        
        # 发送信号
        self.chart_generated.emit(result)
        
        QMessageBox.information(self, "成功", "图表生成成功！")
    
    def on_chart_error(self, error_msg):
        """图表生成错误处理"""
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)
        self.generation_status_label.setText("")
        
        QMessageBox.critical(self, "错误", f"图表生成失败：\n{error_msg}")
    
    def generate_qt_chart_local(self):
        """生成本地Qt图表"""
        try:
            dataset = self.current_data.get("data", [])
            if not dataset:
                return
            
            chart_type = self.chart_type_combo.currentData()
            
            chart = QChart()
            chart.setTitle(self.title_edit.text())
            
            if self.animation_check.isChecked():
                chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
            
            # 准备数据
            start_idx = self.start_spin.value()
            end_idx = min(self.end_spin.value(), len(dataset))
            display_data = dataset[start_idx:end_idx]
            
            if chart_type == "line":
                series = QLineSeries()
                for i, item in enumerate(display_data):
                    if isinstance(item, (int, float)):
                        series.append(i, float(item))
                    elif isinstance(item, (list, tuple)) and len(item) >= 2:
                        series.append(float(item[0]), float(item[1]))
                    elif isinstance(item, dict) and len(item) >= 2:
                        values = list(item.values())
                        series.append(float(values[0]), float(values[1]))
                
                chart.addSeries(series)
                
            elif chart_type == "scatter":
                series = QScatterSeries()
                series.setMarkerSize(10)
                for i, item in enumerate(display_data):
                    if isinstance(item, (int, float)):
                        series.append(i, float(item))
                    elif isinstance(item, (list, tuple)) and len(item) >= 2:
                        series.append(float(item[0]), float(item[1]))
                    elif isinstance(item, dict) and len(item) >= 2:
                        values = list(item.values())
                        series.append(float(values[0]), float(values[1]))
                
                chart.addSeries(series)
                
            elif chart_type == "bar":
                series = QBarSeries()
                bar_set = QBarSet("数据")
                
                for item in display_data:
                    if isinstance(item, (int, float)):
                        bar_set.append(float(item))
                    elif isinstance(item, (list, tuple)) and len(item) >= 1:
                        bar_set.append(float(item[0]))
                    elif isinstance(item, dict) and len(item) >= 1:
                        value = list(item.values())[0]
                        bar_set.append(float(value))
                
                series.append(bar_set)
                chart.addSeries(series)
                
            elif chart_type == "pie":
                series = QPieSeries()
                
                for i, item in enumerate(display_data[:10]):  # 限制饼图片数
                    if isinstance(item, (int, float)):
                        series.append(f"项目{i+1}", float(item))
                    elif isinstance(item, (list, tuple)) and len(item) >= 1:
                        series.append(f"项目{i+1}", float(item[0]))
                    elif isinstance(item, dict):
                        for key, value in item.items():
                            series.append(str(key), float(value))
                            break
                
                chart.addSeries(series)
            
            # 创建默认坐标轴
            if chart_type != "pie":
                chart.createDefaultAxes()
            
            # 设置图例
            if self.show_legend_check.isChecked():
                chart.legend().setVisible(True)
                chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
            else:
                chart.legend().setVisible(False)
            
            # 设置图表
            self.chart_view.setChart(chart)
            
            # 更新信息
            self.chart_info.setText(f"{self.chart_type_combo.currentText()} - 数据点: {len(display_data)}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"本地图表生成失败：\n{str(e)}")
    
    def export_chart(self):
        """导出图表"""
        if not self.current_chart:
            QMessageBox.warning(self, "警告", "请先生成图表")
            return
        
        try:
            # 这里可以实现图表导出功能
            if self.current_chart.get("backend_used"):
                QMessageBox.information(self, "导出", "后端图表导出功能将在后续版本中实现\n可通过后端API获取图表文件")
            else:
                QMessageBox.information(self, "导出", "本地图表导出功能将在后续版本中实现\n可导出为PNG、SVG等格式")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"图表导出失败：\n{str(e)}")
    
    def clear_chart(self):
        """清空图表"""
        self.create_sample_chart()
        self.current_chart = None
        self.export_button.setEnabled(False)
        self.generation_status_label.setText("")
        self.chart_info.setText("图表已清空 - 请导入数据并生成图表")
    
    def get_current_chart(self):
        """获取当前图表"""
        return self.current_chart
