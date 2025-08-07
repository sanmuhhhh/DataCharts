"""
数据可视化系统外部接口定义

此模块包含设计文档中定义的所有外部接口。
所有接口严格遵循设计规范。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
import sys
import os
sys.path.append(os.path.dirname(__file__))
from data_types import (
    DataSource, FunctionExpression, ProcessingResult, 
    ChartConfig, MatrixData
)
import numpy as np


class DataImporter:
    """数据导入接口，来自设计文档第4.1节"""
    
    def __init__(self):
        """初始化数据导入器"""
        from data_processing.data_importer import DataImporter as DataImporterImpl
        self._impl = DataImporterImpl()
    
    def import_data(self, file_path: str, format: str, options: Dict[str, Any]) -> DataSource:
        """导入数据，支持多种格式"""
        return self._impl.import_data(file_path, format, options)
    
    def validate_data(self, data: DataSource) -> bool:
        """验证数据完整性和格式"""
        return self._impl.validate_data(data)
    
    def preprocess_data(self, data: DataSource) -> DataSource:
        """预处理数据，清洗和标准化"""
        return self._impl.preprocess_data(data)
    
    def detect_data_type(self, data: DataSource) -> str:
        """检测数据类型"""
        return self._impl.detect_data_type(data)


class FunctionProcessor:
    """函数处理接口，来自设计文档第4.2节"""
    
    def __init__(self):
        """初始化函数处理器"""
        # 延迟导入以避免循环依赖
        import importlib.util
        import os
        
        # 构建模块路径
        core_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'app', 'core', 'function_processor.py')
        core_path = os.path.abspath(core_path)
        
        if os.path.exists(core_path):
            spec = importlib.util.spec_from_file_location("function_processor_core", core_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self._impl = module.FunctionProcessor()
        else:
            # 如果核心模块不存在，使用占位符
            self._impl = None
    
    def parse_expression(self, expression: str) -> FunctionExpression:
        """解析函数表达式"""
        if self._impl:
            return self._impl.parse_expression(expression)
        else:
            # 占位符实现
            return FunctionExpression(expression=expression, variables=[], parameters={})
    
    def validate_syntax(self, expression: str) -> bool:
        """验证表达式语法"""
        if self._impl:
            return self._impl.validate_syntax(expression)
        else:
            return True  # 占位符总是返回True
    
    def apply_function(self, data: DataSource, expression: FunctionExpression) -> ProcessingResult:
        """应用函数到数据"""
        if self._impl:
            return self._impl.apply_function(data, expression)
        else:
            # 占位符实现
            return ProcessingResult(
                data=None,
                processing_time=0.0,
                status="error",
                error_message="函数处理器未初始化"
            )
    
    def get_supported_functions(self) -> List[str]:
        """获取支持的函数列表"""
        if self._impl:
            return self._impl.get_supported_functions()
        else:
            return ['sin', 'cos', 'tan', 'log', 'exp', 'sqrt', 'mean', 'std']  # 占位符列表


class ChartGenerator:
    """图表生成接口，来自设计文档第4.3节"""
    
    def __init__(self):
        """初始化图表生成器"""
        try:
            from chart_templates.chart_manager import ChartManager
            from chart_templates.chart_exporter import ChartExporter
            self._manager = ChartManager()
            self._exporter = ChartExporter()
        except ImportError:
            self._manager = None
            self._exporter = None
    
    def create_chart(self, data: DataSource, config: ChartConfig) -> str:
        """创建图表，返回图表ID"""
        if self._manager:
            return self._manager.create_chart(data, config)
        else:
            # 占位符实现
            return "chart_placeholder"
    
    def export_chart(self, chart_id: str, format: str) -> bytes:
        """导出图表为指定格式"""
        if self._manager and self._exporter:
            chart = self._manager.get_chart(chart_id)
            if chart:
                return self._exporter.export_chart(chart, format)
        # 占位符实现
        return b"chart export placeholder"
    
    def update_chart(self, chart_id: str, new_data: DataSource) -> bool:
        """更新图表数据"""
        if self._manager:
            return self._manager.update_chart(chart_id, new_data)
        else:
            return True  # 占位符总是返回True


class MatrixVisualizer:
    """矩阵可视化接口，来自设计文档第4.4节"""
    
    def visualize_2d_matrix(self, matrix: MatrixData) -> str:
        """可视化2D矩阵"""
        # 实现待完成
        pass
    
    def visualize_3d_matrix(self, matrix: MatrixData) -> str:
        """可视化3D矩阵"""
        # 实现待完成
        pass
    
    def create_heatmap(self, matrix: MatrixData) -> str:
        """创建热力图"""
        # 实现待完成
        pass
    
    def create_surface_plot(self, matrix: MatrixData) -> str:
        """创建表面图"""
        # 实现待完成
        pass


# API函数定义（来自设计文档第6.1节）
def initialize_system(config: Dict[str, Any]) -> ProcessingResult:
    """初始化系统，实现待完成"""
    # 实现待完成
    pass


def shutdown_system() -> ProcessingResult:
    """关闭系统，实现待完成"""
    # 实现待完成
    pass


def process_data_request(
    data_source: DataSource, 
    function_expr: FunctionExpression, 
    chart_config: ChartConfig
) -> ProcessingResult:
    """处理数据请求，实现待完成"""
    # 实现待完成
    pass