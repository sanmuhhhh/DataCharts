"""
DataCharts 数据可视化系统共享模块

此模块提供系统的核心数据结构和接口定义。
"""

from .data_types import (
    ChartConfig,
    DataSource,
    FunctionExpression,
    ProcessingResult,
    MatrixData,
    SystemError,
    DataImportError,
    FunctionParseError,
    ChartGenerationError,
    SUPPORTED_DATA_FORMATS,
    SUPPORTED_CHART_TYPES,
    SUPPORTED_FUNCTIONS
)

from .interfaces import (
    DataImporter,
    FunctionProcessor,
    ChartGenerator,
    MatrixVisualizer,
    initialize_system,
    shutdown_system,
    process_data_request
)

__version__ = "0.1.0"
__author__ = "DataCharts Team"

__all__ = [
    # 数据类型
    'ChartConfig',
    'DataSource',
    'FunctionExpression',
    'ProcessingResult',
    'MatrixData',
    
    # 异常类型
    'SystemError',
    'DataImportError',
    'FunctionParseError',
    'ChartGenerationError',
    
    # 常量
    'SUPPORTED_DATA_FORMATS',
    'SUPPORTED_CHART_TYPES',
    'SUPPORTED_FUNCTIONS',
    
    # 接口类
    'DataImporter',
    'FunctionProcessor',
    'ChartGenerator',
    'MatrixVisualizer',
    
    # API函数
    'initialize_system',
    'shutdown_system',
    'process_data_request'
]