"""
数据可视化系统核心数据结构

此模块包含设计文档中定义的所有数据结构。
所有结构严格遵循设计规范。
"""

from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np


@dataclass
class ChartConfig:
    """图表配置结构，来自设计文档第4.3节"""
    chart_type: str          # 图表类型：line、bar、scatter、pie等
    title: str               # 图表标题
    x_axis: str             # X轴标签
    y_axis: str             # Y轴标签
    width: int              # 图表宽度
    height: int             # 图表高度
    options: Dict[str, Any] # 其他配置选项


@dataclass
class DataSource:
    """数据源结构，来自设计文档第4.1节"""
    id: str                  # 数据唯一标识
    format: str             # 数据格式：csv、excel、json、txt
    content: Any            # 数据内容
    metadata: Dict[str, Any] # 元数据信息


@dataclass
class FunctionExpression:
    """函数表达式结构，来自设计文档第4.2节"""
    expression: str          # 函数表达式字符串
    variables: List[str]     # 变量列表
    parameters: Dict[str, Any] # 参数字典


@dataclass
class ProcessingResult:
    """处理结果结构，来自设计文档第7节"""
    data: Any               # 处理后的数据
    processing_time: float  # 处理耗时
    status: str            # 处理状态：success、error
    error_message: Optional[str] # 错误信息


@dataclass
class MatrixData:
    """矩阵数据结构，来自设计文档第4.4节"""
    data: np.ndarray        # 矩阵数据
    dimensions: Tuple[int, ...] # 矩阵维度
    dtype: str             # 数据类型
    labels: Dict[str, List[str]] # 标签信息


class SystemError(Exception):
    """系统错误类型，来自设计文档第7节"""
    pass


class DataImportError(SystemError):
    """数据导入错误"""
    pass


class FunctionParseError(SystemError):
    """函数解析错误"""
    pass


class ChartGenerationError(SystemError):
    """图表生成错误"""
    pass


# 支持的数据格式
SUPPORTED_DATA_FORMATS = {
    'csv': '逗号分隔值文件',
    'excel': 'Excel工作表',
    'json': 'JSON数据文件',
    'txt': '文本数据文件',
    'manual': '手动输入数据'
}

# 支持的图表类型
SUPPORTED_CHART_TYPES = {
    '基础图表': ['line', 'bar', 'scatter', 'pie'],
    '统计图表': ['histogram', 'box_plot', 'violin_plot'],
    '多维图表': ['heatmap', '3d_surface', 'contour'],
    '时间序列': ['time_series', 'candlestick']
}

# 支持的函数类型
SUPPORTED_FUNCTIONS = {
    '数学函数': ['sin', 'cos', 'tan', 'log', 'exp', 'sqrt'],
    '统计函数': ['mean', 'std', 'var', 'median'],
    '数据变换': ['normalize', 'standardize', 'scale'],
    '滤波函数': ['moving_average', 'gaussian_filter']
}