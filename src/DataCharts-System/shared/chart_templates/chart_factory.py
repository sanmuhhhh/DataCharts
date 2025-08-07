"""
图表工厂

负责创建不同类型的图表实例
"""

from typing import Dict, Type
import sys
import os

# 添加数据类型路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data_types import DataSource, ChartConfig, ChartGenerationError

from .base_chart import BaseChart
from .chart_types.basic_charts import LineChart, BarChart, ScatterChart, PieChart


class ChartFactory:
    """图表工厂类"""
    
    # 支持的图表类型映射
    CHART_TYPES: Dict[str, Type[BaseChart]] = {
        # 基础图表
        'line': LineChart,
        'bar': BarChart,
        'scatter': ScatterChart,
        'pie': PieChart,
        
        # 别名
        'column': BarChart,  # 柱状图别名
        'area': LineChart,   # 面积图使用折线图实现
    }
    
    @classmethod
    def create_chart(cls, chart_type: str, data: DataSource, config: ChartConfig) -> BaseChart:
        """
        创建图表实例
        
        Args:
            chart_type: 图表类型
            data: 数据源
            config: 图表配置
            
        Returns:
            BaseChart: 图表实例
            
        Raises:
            ChartGenerationError: 不支持的图表类型或创建失败
        """
        try:
            # 检查图表类型是否支持
            if chart_type not in cls.CHART_TYPES:
                supported_types = ', '.join(cls.CHART_TYPES.keys())
                raise ChartGenerationError(
                    f"不支持的图表类型: {chart_type}. "
                    f"支持的类型: {supported_types}"
                )
            
            # 获取图表类
            chart_class = cls.CHART_TYPES[chart_type]
            
            # 创建图表实例
            chart = chart_class(data, config)
            
            return chart
            
        except ChartGenerationError:
            raise
        except Exception as e:
            raise ChartGenerationError(f"创建图表失败: {str(e)}")
    
    @classmethod
    def get_supported_chart_types(cls) -> list:
        """
        获取支持的图表类型列表
        
        Returns:
            list: 支持的图表类型
        """
        return list(cls.CHART_TYPES.keys())
    
    @classmethod
    def is_chart_type_supported(cls, chart_type: str) -> bool:
        """
        检查图表类型是否支持
        
        Args:
            chart_type: 图表类型
            
        Returns:
            bool: 是否支持
        """
        return chart_type in cls.CHART_TYPES
    
    @classmethod
    def get_chart_type_info(cls, chart_type: str) -> Dict[str, any]:
        """
        获取图表类型信息
        
        Args:
            chart_type: 图表类型
            
        Returns:
            Dict: 图表类型信息
        """
        if chart_type not in cls.CHART_TYPES:
            return {
                'type': chart_type,
                'supported': False,
                'description': '不支持的图表类型'
            }
        
        chart_class = cls.CHART_TYPES[chart_type]
        
        return {
            'type': chart_type,
            'supported': True,
            'class_name': chart_class.__name__,
            'description': chart_class.__doc__ or '无描述',
            'category': cls._get_chart_category(chart_type)
        }
    
    @classmethod
    def _get_chart_category(cls, chart_type: str) -> str:
        """
        获取图表分类
        
        Args:
            chart_type: 图表类型
            
        Returns:
            str: 图表分类
        """
        basic_charts = ['line', 'bar', 'scatter', 'pie', 'column', 'area']
        
        if chart_type in basic_charts:
            return '基础图表'
        else:
            return '其他图表'
