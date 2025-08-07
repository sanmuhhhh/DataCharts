"""
数据导入界面组件

提供数据文件导入和预览功能，集成后端API
"""

import sys
import os
import json
from typing import Optional, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QTableWidget, QTableWidgetItem, QTextEdit,
    QGroupBox, QComboBox, QProgressBar, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

# 添加共享模块路径
shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

try:
    from data_processing.data_importer import DataImporter
    from data_types import DataSource
    SHARED_MODULES_AVAILABLE = True
except ImportError as e:
    # 创建本地文件处理器
    print("警告: 共享模块未找到，使用本地文件处理器")
    import pandas as pd
    import numpy as np
    
    class FileHandler:
        def read_file(self, file_path: str) -> dict:
            """读取文件"""
            try:
                ext = os.path.splitext(file_path)[1].lower()
                
                if ext == '.csv':
                    df = pd.read_csv(file_path, encoding='utf-8')
                    return {
                        "status": "success",
                        "data": df.to_dict('records'),
                        "file_info": {"type": "csv", "rows": len(df), "columns": len(df.columns)}
                    }
                elif ext in ['.xlsx', '.xls']:
                    df = pd.read_excel(file_path)
                    return {
                        "status": "success",
                        "data": df.to_dict('records'),
                        "file_info": {"type": "excel", "rows": len(df), "columns": len(df.columns)}
                    }
                elif ext == '.json':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    return {
                        "status": "success",
                        "data": data if isinstance(data, list) else [data],
                        "file_info": {"type": "json", "size": len(str(data))}
                    }
                elif ext == '.txt':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = [line.strip() for line in f.readlines() if line.strip()]
                    # 尝试转换为数字
                    try:
                        data = [float(line) for line in lines]
                    except ValueError:
                        data = lines
                    return {
                        "status": "success",
                        "data": data,
                        "file_info": {"type": "txt", "lines": len(lines)}
                    }
                else:
                    return {"status": "error", "error": f"不支持的文件格式: {ext}"}
                    
            except Exception as e:
                return {"status": "error", "error": str(e)}
    
    class DataImporter:
        def __init__(self):
            self.file_handler = FileHandler()
        
        def import_data(self, file_path: str) -> dict:
            return self.file_handler.read_file(file_path)


class DataImportWorker(QThread):
    """数据导入工作线程"""
    
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, file_path: str, use_backend: bool = False, api_manager=None):
        super().__init__()
        self.file_path = file_path
        self.use_backend = use_backend
        self.api_manager = api_manager
        self.importer = DataImporter()
    
    def run(self):
        """执行数据导入"""
        try:
            self.progress.emit(10)
            
            # 本地导入数据
            result = self.importer.import_data(self.file_path)
            self.progress.emit(50)
            
            if result.get("status") == "success":
                # 如果启用后端且后端可用，尝试上传到后端
                if (self.use_backend and 
                    self.api_manager and 
                    self.api_manager.is_backend_available()):
                    
                    try:
                        file_info = {
                            "filename": os.path.basename(self.file_path),
                            "path": self.file_path,
                            **result.get("file_info", {})
                        }
                        
                        # 上传到后端
                        upload_result = self.api_manager.get_client().upload_data(
                            result.get("data"), file_info
                        )
                        
                        self.progress.emit(80)
                        
                        if upload_result.get("status") == "success":
                            # 合并本地和后端结果
                            result["backend_status"] = "uploaded"
                            result["backend_data"] = upload_result.get("data")
                        else:
                            result["backend_status"] = "failed"
                            result["backend_error"] = upload_result.get("message")
                    except Exception as e:
                        result["backend_status"] = "error"
                        result["backend_error"] = str(e)
                
                self.progress.emit(100)
                self.finished.emit(result)
            else:
                self.error.emit(f"导入失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            self.error.emit(f"导入过程中发生错误: {str(e)}")


class DataImportWidget(QWidget):
    """数据导入界面组件"""
    
    # 信号定义
    data_imported = pyqtSignal(object)  # 数据导入完成信号
    
    def __init__(self, api_manager=None):
        super().__init__()
        self.api_manager = api_manager
        self.current_data = None
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout(file_group)
        
        # 文件路径选择
        path_layout = QHBoxLayout()
        self.file_path_label = QLabel("未选择文件")
        self.file_path_label.setStyleSheet("color: #666; padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        
        self.browse_button = QPushButton("浏览文件")
        self.browse_button.clicked.connect(self.browse_file)
        
        path_layout.addWidget(QLabel("文件路径:"))
        path_layout.addWidget(self.file_path_label, 1)
        path_layout.addWidget(self.browse_button)
        
        file_layout.addLayout(path_layout)
        layout.addWidget(file_group)
        
        # 导入选项区域
        options_group = QGroupBox("导入选项")
        options_layout = QVBoxLayout(options_group)
        
        # 第一行：文件格式和后端选项
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("文件格式:"))
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["自动检测", "CSV", "Excel", "JSON", "TXT"])
        format_layout.addWidget(self.format_combo)
        
        # 后端集成选项
        self.use_backend_check = QCheckBox("使用后端API")
        self.use_backend_check.setChecked(True)
        format_layout.addWidget(self.use_backend_check)
        
        format_layout.addStretch()
        options_layout.addLayout(format_layout)
        
        # 第二行：操作按钮
        button_layout = QHBoxLayout()
        self.import_button = QPushButton("导入数据")
        self.import_button.clicked.connect(self.import_data)
        self.import_button.setEnabled(False)
        
        self.clear_button = QPushButton("清除数据")
        self.clear_button.clicked.connect(self.clear_data)
        self.clear_button.setEnabled(False)
        
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        
        options_layout.addLayout(button_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        options_layout.addWidget(self.progress_bar)
        
        layout.addWidget(options_group)
        
        # 数据预览区域
        preview_group = QGroupBox("数据预览")
        preview_layout = QVBoxLayout(preview_group)
        
        # 数据信息
        info_layout = QHBoxLayout()
        self.info_label = QLabel("暂无数据")
        self.info_label.setFont(QFont("Arial", 10))
        info_layout.addWidget(self.info_label)
        
        # 后端状态指示
        self.backend_status_label = QLabel("")
        self.backend_status_label.setFont(QFont("Arial", 9))
        info_layout.addWidget(self.backend_status_label)
        info_layout.addStretch()
        
        preview_layout.addLayout(info_layout)
        
        # 数据表格
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ddd;
                background-color: white;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        preview_layout.addWidget(self.data_table)
        
        layout.addWidget(preview_group)
        
        # 设置布局比例
        layout.setStretch(0, 0)  # 文件选择区域
        layout.setStretch(1, 0)  # 导入选项区域
        layout.setStretch(2, 1)  # 数据预览区域（可伸缩）
    
    def browse_file(self):
        """浏览并选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择数据文件",
            "",
            "数据文件 (*.csv *.xlsx *.xls *.json *.txt);;CSV文件 (*.csv);;Excel文件 (*.xlsx *.xls);;JSON文件 (*.json);;文本文件 (*.txt);;所有文件 (*.*)"
        )
        
        if file_path:
            self.file_path_label.setText(file_path)
            self.file_path_label.setStyleSheet("color: black; padding: 8px; border: 1px solid #3498db; border-radius: 4px; background-color: #f8f9fa;")
            self.import_button.setEnabled(True)
            
            # 自动检测文件格式
            if file_path.lower().endswith('.csv'):
                self.format_combo.setCurrentText("CSV")
            elif file_path.lower().endswith(('.xlsx', '.xls')):
                self.format_combo.setCurrentText("Excel")
            elif file_path.lower().endswith('.json'):
                self.format_combo.setCurrentText("JSON")
            elif file_path.lower().endswith('.txt'):
                self.format_combo.setCurrentText("TXT")
    
    def import_data(self):
        """导入数据"""
        file_path = self.file_path_label.text()
        if not file_path or file_path == "未选择文件":
            QMessageBox.warning(self, "警告", "请先选择要导入的文件")
            return
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "警告", "选择的文件不存在")
            return
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.import_button.setEnabled(False)
        
        # 检查后端可用性
        use_backend = self.use_backend_check.isChecked()
        if use_backend and not (self.api_manager and self.api_manager.is_backend_available()):
            reply = QMessageBox.question(
                self, 
                "后端不可用", 
                "后端API不可用，是否继续使用本地导入？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                self.progress_bar.setVisible(False)
                self.import_button.setEnabled(True)
                return
            use_backend = False
        
        # 创建并启动工作线程
        self.worker = DataImportWorker(file_path, use_backend, self.api_manager)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_import_finished)
        self.worker.error.connect(self.on_import_error)
        self.worker.start()
    
    def on_import_finished(self, result):
        """数据导入完成处理"""
        self.progress_bar.setVisible(False)
        self.import_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        
        # 保存数据
        self.current_data = result
        
        # 更新预览
        self.update_preview(result)
        
        # 更新后端状态显示
        self.update_backend_status(result)
        
        # 发送信号
        self.data_imported.emit(result)
        
        # 显示成功消息
        backend_msg = ""
        if result.get("backend_status") == "uploaded":
            backend_msg = "\n数据已同步到后端服务"
        elif result.get("backend_status") == "failed":
            backend_msg = f"\n后端同步失败: {result.get('backend_error', '未知错误')}"
        
        QMessageBox.information(self, "成功", f"数据导入成功！{backend_msg}")
    
    def on_import_error(self, error_msg):
        """数据导入错误处理"""
        self.progress_bar.setVisible(False)
        self.import_button.setEnabled(True)
        self.backend_status_label.setText("")
        
        QMessageBox.critical(self, "错误", f"数据导入失败：\n{error_msg}")
    
    def update_backend_status(self, result):
        """更新后端状态显示"""
        backend_status = result.get("backend_status")
        if backend_status == "uploaded":
            self.backend_status_label.setText("77 已同步到后端")
            self.backend_status_label.setStyleSheet("color: green; font-weight: bold;")
        elif backend_status == "failed":
            self.backend_status_label.setText("72 后端同步失败")
            self.backend_status_label.setStyleSheet("color: orange; font-weight: bold;")
        elif backend_status == "error":
            self.backend_status_label.setText("71 后端错误")
            self.backend_status_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.backend_status_label.setText("○ 本地数据")
            self.backend_status_label.setStyleSheet("color: #666; font-weight: normal;")
    
    def update_preview(self, data):
        """更新数据预览"""
        if not data or data.get("status") != "success":
            return
        
        dataset = data.get("data", [])
        if not dataset:
            self.info_label.setText("暂无数据")
            self.data_table.setRowCount(0)
            self.data_table.setColumnCount(0)
            return
        
        # 更新信息标签
        if isinstance(dataset, list) and len(dataset) > 0:
            if isinstance(dataset[0], dict):
                # 字典格式数据
                row_count = len(dataset)
                col_count = len(dataset[0].keys()) if dataset[0] else 0
                columns = list(dataset[0].keys()) if dataset[0] else []
            elif isinstance(dataset[0], (list, tuple)):
                # 列表/元组格式数据
                row_count = len(dataset)
                col_count = len(dataset[0]) if dataset[0] else 0
                columns = [f"列{i+1}" for i in range(col_count)]
            else:
                # 简单数据
                row_count = len(dataset)
                col_count = 1
                columns = ["数据"]
        else:
            row_count = 0
            col_count = 0
            columns = []
        
        # 显示文件信息
        file_info = data.get("file_info", {})
        file_type = file_info.get("type", "unknown").upper()
        
        self.info_label.setText(f"数据类型: {file_type} | 维度: {row_count} 行 × {col_count} 列")
        
        # 更新表格（只显示前100行）
        display_rows = min(row_count, 100)
        self.data_table.setRowCount(display_rows)
        self.data_table.setColumnCount(col_count)
        
        if columns:
            self.data_table.setHorizontalHeaderLabels(columns)
        
        # 填充数据
        for i in range(display_rows):
            if isinstance(dataset[i], dict):
                for j, key in enumerate(columns):
                    value = dataset[i].get(key, "")
                    item = QTableWidgetItem(str(value))
                    self.data_table.setItem(i, j, item)
            elif isinstance(dataset[i], (list, tuple)):
                for j in range(min(len(dataset[i]), col_count)):
                    item = QTableWidgetItem(str(dataset[i][j]))
                    self.data_table.setItem(i, j, item)
            else:
                item = QTableWidgetItem(str(dataset[i]))
                self.data_table.setItem(i, 0, item)
        
        # 自动调整列宽
        self.data_table.resizeColumnsToContents()
        
        if row_count > 100:
            self.info_label.setText(
                f"数据类型: {file_type} | 维度: {row_count} 行 × {col_count} 列 (显示前100行)"
            )
    
    def clear_data(self):
        """清除数据"""
        self.current_data = None
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)
        self.info_label.setText("暂无数据")
        self.backend_status_label.setText("")
        self.clear_button.setEnabled(False)
        
        QMessageBox.information(self, "完成", "数据已清除")
    
    def get_current_data(self):
        """获取当前导入的数据"""
        return self.current_data
