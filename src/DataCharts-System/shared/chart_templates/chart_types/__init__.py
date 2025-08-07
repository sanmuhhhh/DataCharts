"""
图表类型实现模块

包含各种具体图表类型的实现
"""

from .basic_charts import LineChart, BarChart, ScatterChart, PieChart

try:
    from .statistical_charts import HistogramChart, BoxPlotChart, ViolinPlotChart
except ImportError:
    # 占位符类
    class HistogramChart:
        pass
    class BoxPlotChart:
        pass  
    class ViolinPlotChart:
        pass

try:
    from .matrix_charts import HeatmapChart, Surface3DChart, ContourChart
except ImportError:
    # 占位符类
    class HeatmapChart:
        pass
    class Surface3DChart:
        pass
    class ContourChart:
        pass

__all__ = [
    # 基础图表
    'LineChart',
    'BarChart', 
    'ScatterChart',
    'PieChart',
    
    # 统计图表
    'HistogramChart',
    'BoxPlotChart',
    'ViolinPlotChart',
    
    # 矩阵图表
    'HeatmapChart',
    'Surface3DChart',
    'ContourChart'
]
