"""
函数处理界面组件

提供数学函数输入、解析和应用功能，集成后端API
"""

import sys
import os
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QGroupBox, QComboBox, QListWidget, QListWidgetItem,
    QSplitter, QMessageBox, QLineEdit, QProgressBar, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor

# 添加共享模块路径
shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

try:
    from algorithms.function_parser import ExpressionParser
    from algorithms.safe_executor import SafeExecutionEnvironment
    from data_types import DataSource
except ImportError as e:
    # 创建本地函数处理器
    print(f"警告: 共享模块未找到，使用本地函数处理器 (错误: {e})")
    import numpy as np
    import pandas as pd
    import re
    
    class DataSource:
        def __init__(self, content):
            self.content = content
    
    class ExpressionParser:
        def parse_expression(self, expression: str) -> dict:
            """简化的表达式解析器"""
            try:
                # 简单的安全检查
                if any(danger in expression for danger in ['import', 'exec', 'eval', '__']):
                    return {"status": "error", "message": "表达式包含不安全的操作"}
                
                # 提取变量（简单实现）
                variables = list(set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', expression)))
                # 过滤掉函数名
                functions = ['sin', 'cos', 'tan', 'log', 'exp', 'sqrt', 'abs', 'mean', 'std', 'min', 'max', 'sum']
                variables = [v for v in variables if v not in functions and v not in ['np', 'x', 'pi', 'e']]
                
                return {
                    "status": "success",
                    "type": "numeric",
                    "variables": variables,
                    "functions": [f for f in functions if f in expression]
                }
            except Exception as e:
                return {"status": "error", "message": str(e)}
    
    class SafeExecutionEnvironment:
        def apply_function_to_data(self, data_source, expression: str, variables: list) -> dict:
            """简化的函数执行器"""
            try:
                data = data_source.content
                if isinstance(data, dict) and data.get("status") == "success":
                    dataset = data.get("data", [])
                else:
                    dataset = data
                
                if not isinstance(dataset, (list, pd.DataFrame)):
                    return {"status": "error", "message": "数据格式不支持"}
                
                # 转换为numpy数组进行计算
                if isinstance(dataset, list):
                    if len(dataset) > 0 and isinstance(dataset[0], dict):
                        # 字典列表转DataFrame
                        df = pd.DataFrame(dataset)
                        if len(df.columns) == 1:
                            x = df.iloc[:, 0].values
                        else:
                            x = df.values
                    else:
                        # 简单数组
                        x = np.array(dataset, dtype=float)
                elif isinstance(dataset, pd.DataFrame):
                    if len(dataset.columns) == 1:
                        x = dataset.iloc[:, 0].values
                    else:
                        x = dataset.values
                
                # 创建安全的命名空间
                namespace = {
                    'x': x,
                    'np': np,
                    'sin': np.sin,
                    'cos': np.cos,
                    'tan': np.tan,
                    'log': np.log,
                    'exp': np.exp,
                    'sqrt': np.sqrt,
                    'abs': np.abs,
                    'mean': np.mean,
                    'std': np.std,
                    'min': np.min,
                    'max': np.max,
                    'sum': np.sum,
                    'pi': np.pi,
                    'e': np.e
                }
                
                # 替换数据变量
                if hasattr(x, 'shape') and len(x.shape) > 1:
                    # 多列数据
                    for i, var in enumerate(variables):
                        if i < x.shape[1]:
                            namespace[var] = x[:, i]
                else:
                    # 单列数据
                    namespace['x'] = x
                
                # 执行表达式
                result = eval(expression, {"__builtins__": {}}, namespace)
                
                return {
                    "status": "success", 
                    "result": result.tolist() if hasattr(result, 'tolist') else result
                }
                
            except Exception as e:
                return {"status": "error", "message": f"计算失败: {str(e)}"}


class FunctionExecutorWorker(QThread):
    """函数执行工作线程"""
    
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, expression: str, data: Any, use_backend: bool = False, api_manager=None):
        super().__init__()
        self.expression = expression
        self.data = data
        self.use_backend = use_backend
        self.api_manager = api_manager
        self.parser = ExpressionParser()
        self.executor = SafeExecutionEnvironment()
    
    def run(self):
        """执行函数处理"""
        try:
            self.progress.emit(20)
            
            # 如果启用后端且后端可用，优先使用后端
            if (self.use_backend and 
                self.api_manager and 
                self.api_manager.is_backend_available()):
                
                try:
                    # 使用后端API解析函数
                    parse_result = self.api_manager.get_client().parse_function(self.expression)
                    
                    if parse_result.get("status") == "success":
                        self.progress.emit(60)
                        
                        # 使用后端API应用函数
                        apply_result = self.api_manager.get_client().apply_function(
                            self.expression, self.data, []
                        )
                        
                        if apply_result.get("status") == "success":
                            self.progress.emit(100)
                            result = apply_result.get("data", {})
                            result["backend_used"] = True
                            self.finished.emit(result)
                            return
                        else:
                            # 后端失败，降级到本地处理
                            print(f"后端函数应用失败，降级到本地处理: {apply_result.get('message')}")
                    else:
                        # 后端解析失败，降级到本地处理
                        print(f"后端函数解析失败，降级到本地处理: {parse_result.get('message')}")
                        
                except Exception as e:
                    print(f"后端API调用异常，降级到本地处理: {str(e)}")
            
            # 本地处理
            self.progress.emit(40)
            
            # 解析表达式
            parsed_result = self.parser.parse_expression(self.expression)
            if parsed_result.get("status") != "success":
                self.error.emit(f"表达式解析失败: {parsed_result.get('message', '未知错误')}")
                return
            
            self.progress.emit(70)
            
            # 创建数据源
            data_source = DataSource(self.data)
            variables = parsed_result.get("variables", [])
            
            # 执行函数
            exec_result = self.executor.apply_function_to_data(data_source, self.expression, variables)
            self.progress.emit(100)
            
            if exec_result.get("status") == "success":
                exec_result["backend_used"] = False
                self.finished.emit(exec_result)
            else:
                self.error.emit(f"函数执行失败: {exec_result.get('message', '未知错误')}")
                
        except Exception as e:
            self.error.emit(f"函数处理过程中发生错误: {str(e)}")


class FunctionWidget(QWidget):
    """函数处理界面组件"""
    
    # 信号定义
    function_applied = pyqtSignal(object)  # 函数应用完成信号
    
    def __init__(self, api_manager=None):
        super().__init__()
        self.api_manager = api_manager
        self.current_data = None
        self.result_data = None
        self.init_ui()
        self.setup_function_templates()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：函数输入和模板
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 函数模板区域
        template_group = QGroupBox("函数模板")
        template_layout = QVBoxLayout(template_group)
        
        self.template_list = QListWidget()
        self.template_list.itemClicked.connect(self.on_template_selected)
        self.template_list.setStyleSheet("""
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
        """)
        template_layout.addWidget(self.template_list)
        
        left_layout.addWidget(template_group)
        
        # 函数输入区域
        input_group = QGroupBox("函数表达式")
        input_layout = QVBoxLayout(input_group)
        
        # 后端选项
        backend_layout = QHBoxLayout()
        self.use_backend_check = QCheckBox("使用后端API计算")
        self.use_backend_check.setChecked(True)
        backend_layout.addWidget(self.use_backend_check)
        
        self.backend_status_label = QLabel("")
        self.backend_status_label.setFont(QFont("Arial", 9))
        backend_layout.addWidget(self.backend_status_label)
        backend_layout.addStretch()
        
        input_layout.addLayout(backend_layout)
        
        # 表达式输入
        self.expression_edit = QTextEdit()
        self.expression_edit.setMaximumHeight(120)
        self.expression_edit.setPlaceholderText("输入数学表达式，例如: x**2 + np.sin(x)")
        self.expression_edit.setFont(QFont("Consolas", 11))
        self.expression_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        input_layout.addWidget(self.expression_edit)
        
        # 快速输入栏
        quick_layout = QHBoxLayout()
        quick_layout.addWidget(QLabel("快速输入:"))
        
        self.quick_input = QLineEdit()
        self.quick_input.setPlaceholderText("简单表达式")
        self.quick_input.returnPressed.connect(self.add_quick_input)
        quick_layout.addWidget(self.quick_input)
        
        add_button = QPushButton("添加")
        add_button.clicked.connect(self.add_quick_input)
        quick_layout.addWidget(add_button)
        
        input_layout.addLayout(quick_layout)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        self.parse_button = QPushButton("解析表达式")
        self.parse_button.clicked.connect(self.parse_expression)
        
        self.apply_button = QPushButton("应用到数据")
        self.apply_button.clicked.connect(self.apply_function)
        self.apply_button.setEnabled(False)
        
        self.clear_button = QPushButton("清除")
        self.clear_button.clicked.connect(self.clear_expression)
        
        button_layout.addWidget(self.parse_button)
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.clear_button)
        
        input_layout.addLayout(button_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        input_layout.addWidget(self.progress_bar)
        
        left_layout.addWidget(input_group)
        
        # 右侧：结果显示
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 解析结果区域
        parse_group = QGroupBox("解析结果")
        parse_layout = QVBoxLayout(parse_group)
        
        self.parse_result = QTextEdit()
        self.parse_result.setMaximumHeight(100)
        self.parse_result.setReadOnly(True)
        self.parse_result.setFont(QFont("Consolas", 10))
        self.parse_result.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        parse_layout.addWidget(self.parse_result)
        
        right_layout.addWidget(parse_group)
        
        # 计算结果区域
        result_group = QGroupBox("计算结果")
        result_layout = QVBoxLayout(result_group)
        
        # 结果信息
        result_info_layout = QHBoxLayout()
        self.result_info = QLabel("暂无结果")
        self.result_info.setFont(QFont("Arial", 10))
        result_info_layout.addWidget(self.result_info)
        
        # 后端使用状态
        self.execution_status_label = QLabel("")
        self.execution_status_label.setFont(QFont("Arial", 9))
        result_info_layout.addWidget(self.execution_status_label)
        result_info_layout.addStretch()
        
        result_layout.addLayout(result_info_layout)
        
        # 结果显示
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setFont(QFont("Consolas", 10))
        self.result_display.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        result_layout.addWidget(self.result_display)
        
        right_layout.addWidget(result_group)
        
        # 添加到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
        
        # 检查后端状态
        self.update_backend_status()
    
    def setup_function_templates(self):
        """设置函数模板"""
        templates = [
            ("线性函数", "a * x + b", "y = ax + b 的线性函数"),
            ("二次函数", "a * x**2 + b * x + c", "二次多项式函数"),
            ("指数函数", "a * np.exp(b * x)", "指数增长/衰减"),
            ("对数函数", "a * np.log(x) + b", "对数函数"),
            ("正弦函数", "a * np.sin(b * x + c)", "正弦波函数"),
            ("余弦函数", "a * np.cos(b * x + c)", "余弦波函数"),
            ("幂函数", "a * x**b", "幂次函数"),
            ("平方根", "np.sqrt(x)", "平方根函数"),
            ("绝对值", "np.abs(x)", "绝对值函数"),
            ("数据归一化", "(x - np.mean(x)) / np.std(x)", "标准化为均值0方差1"),
            ("数据标准化", "(x - np.min(x)) / (np.max(x) - np.min(x))", "缩放到0-1范围"),
            ("移动平均", "np.convolve(x, np.ones(5)/5, mode='same')", "5点移动平均"),
            ("差分", "np.diff(x)", "计算差分"),
            ("累积和", "np.cumsum(x)", "累积求和"),
            ("平滑处理", "np.convolve(x, np.ones(3)/3, mode='same')", "3点平滑")
        ]
        
        for name, expression, description in templates:
            item = QListWidgetItem(f"{name}: {expression}")
            item.setToolTip(description)
            item.setData(Qt.ItemDataRole.UserRole, expression)
            self.template_list.addItem(item)
    
    def on_template_selected(self, item):
        """选择函数模板"""
        expression = item.data(Qt.ItemDataRole.UserRole)
        if expression:
            self.expression_edit.setPlainText(expression)
    
    def add_quick_input(self):
        """添加快速输入"""
        text = self.quick_input.text().strip()
        if text:
            current_text = self.expression_edit.toPlainText()
            if current_text:
                # 在光标位置插入
                cursor = self.expression_edit.textCursor()
                cursor.insertText(f" {text} ")
            else:
                self.expression_edit.setPlainText(text)
            
            self.quick_input.clear()
    
    def update_backend_status(self):
        """更新后端状态显示"""
        if self.api_manager and self.api_manager.is_backend_available():
            self.backend_status_label.setText("77 后端可用")
            self.backend_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.backend_status_label.setText("72 后端不可用")
            self.backend_status_label.setStyleSheet("color: orange; font-weight: bold;")
    
    def parse_expression(self):
        """解析数学表达式"""
        expression = self.expression_edit.toPlainText().strip()
        if not expression:
            QMessageBox.warning(self, "警告", "请输入数学表达式")
            return
        
        self.update_backend_status()
        
        try:
            # 如果后端可用，尝试使用后端解析
            if (self.api_manager and 
                self.api_manager.is_backend_available() and 
                self.use_backend_check.isChecked()):
                
                result = self.api_manager.get_client().parse_function(expression)
                if result.get("status") == "success":
                    data = result.get("data", {})
                    self.parse_result.setPlainText(
                        f"后端解析成功！\n"
                        f"表达式类型: {data.get('type', '未知')}\n"
                        f"变量: {', '.join(data.get('variables', []))}\n"
                        f"函数: {', '.join(data.get('functions', []))}"
                    )
                    self.apply_button.setEnabled(self.current_data is not None)
                    return
            
            # 本地解析
            parser = ExpressionParser()
            result = parser.parse_expression(expression)
            
            if result.get("status") == "success":
                self.parse_result.setPlainText(
                    f"本地解析成功！\n"
                    f"表达式类型: {result.get('type', '未知')}\n"
                    f"变量: {', '.join(result.get('variables', []))}\n"
                    f"函数: {', '.join(result.get('functions', []))}"
                )
                self.apply_button.setEnabled(self.current_data is not None)
            else:
                self.parse_result.setPlainText(
                    f"解析失败！\n错误: {result.get('message', '未知错误')}"
                )
                self.apply_button.setEnabled(False)
                
        except Exception as e:
            self.parse_result.setPlainText(f"解析异常: {str(e)}")
            self.apply_button.setEnabled(False)
    
    def apply_function(self):
        """应用函数到数据"""
        if not self.current_data:
            QMessageBox.warning(self, "警告", "请先导入数据")
            return
        
        expression = self.expression_edit.toPlainText().strip()
        if not expression:
            QMessageBox.warning(self, "警告", "请输入数学表达式")
            return
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.apply_button.setEnabled(False)
        
        # 创建并启动工作线程
        use_backend = self.use_backend_check.isChecked()
        self.worker = FunctionExecutorWorker(expression, self.current_data, use_backend, self.api_manager)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_function_finished)
        self.worker.error.connect(self.on_function_error)
        self.worker.start()
    
    def on_function_finished(self, result):
        """函数应用完成处理"""
        self.progress_bar.setVisible(False)
        self.apply_button.setEnabled(True)
        
        # 保存结果
        self.result_data = result
        
        # 显示结果
        self.display_result(result)
        
        # 更新执行状态
        if result.get("backend_used"):
            self.execution_status_label.setText("77 后端计算")
            self.execution_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.execution_status_label.setText("○ 本地计算")
            self.execution_status_label.setStyleSheet("color: #666; font-weight: normal;")
        
        # 发送信号
        self.function_applied.emit(result)
        
        QMessageBox.information(self, "成功", "函数应用成功！")
    
    def on_function_error(self, error_msg):
        """函数应用错误处理"""
        self.progress_bar.setVisible(False)
        self.apply_button.setEnabled(True)
        self.execution_status_label.setText("")
        
        QMessageBox.critical(self, "错误", f"函数应用失败：\n{error_msg}")
    
    def display_result(self, result):
        """显示计算结果"""
        if not result or result.get("status") != "success":
            return
        
        result_data = result.get("result", [])
        
        # 更新结果信息
        if isinstance(result_data, list):
            count = len(result_data)
            self.result_info.setText(f"计算完成，共 {count} 个结果")
            
            # 显示部分结果（前100个）
            display_count = min(count, 100)
            display_text = "\n".join(str(result_data[i]) for i in range(display_count))
            
            if count > 100:
                display_text += f"\n... (共 {count} 个结果，显示前100个)"
            
            self.result_display.setPlainText(display_text)
        else:
            self.result_info.setText("计算完成")
            self.result_display.setPlainText(str(result_data))
    
    def clear_expression(self):
        """清除表达式和结果"""
        self.expression_edit.clear()
        self.quick_input.clear()
        self.parse_result.clear()
        self.result_display.clear()
        self.result_info.setText("暂无结果")
        self.execution_status_label.setText("")
        self.apply_button.setEnabled(False)
        self.result_data = None
    
    def set_data(self, data):
        """设置当前数据"""
        self.current_data = data
        # 如果已经解析了表达式，启用应用按钮
        if self.parse_result.toPlainText() and "解析成功" in self.parse_result.toPlainText():
            self.apply_button.setEnabled(True)
    
    def get_result_data(self):
        """获取计算结果数据"""
        return self.result_data
