"""
图表导出器

负责将图表导出为不同格式
"""

import json
from typing import Dict, Any
import sys
import os

# 添加数据类型路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data_types import ChartGenerationError

from .base_chart import BaseChart


class ChartExporter:
    """图表导出器类"""
    
    SUPPORTED_FORMATS = ['png', 'jpg', 'jpeg', 'svg', 'pdf', 'json']
    
    def __init__(self):
        """初始化导出器"""
        pass
    
    def export_chart(self, chart: BaseChart, format: str) -> bytes:
        """
        导出图表
        
        Args:
            chart: 图表实例
            format: 导出格式
            
        Returns:
            bytes: 导出的数据
            
        Raises:
            ChartGenerationError: 导出失败时抛出
        """
        if format not in self.SUPPORTED_FORMATS:
            raise ChartGenerationError(
                f"不支持的导出格式: {format}. "
                f"支持的格式: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        try:
            if format == 'json':
                return self._export_json(chart)
            else:
                return chart.export(format)
                
        except Exception as e:
            raise ChartGenerationError(f"图表导出失败: {str(e)}")
    
    def _export_json(self, chart: BaseChart) -> bytes:
        """
        导出为JSON格式
        
        Args:
            chart: 图表实例
            
        Returns:
            bytes: JSON数据
        """
        try:
            chart_data = chart.render()
            
            # 添加额外的元数据
            export_data = {
                'chart_data': chart_data,
                'chart_info': chart.get_chart_info(),
                'export_format': 'json',
                'export_timestamp': __import__('time').time()
            }
            
            return json.dumps(export_data, ensure_ascii=False, indent=2).encode('utf-8')
            
        except Exception as e:
            raise ChartGenerationError(f"JSON导出失败: {str(e)}")
    
    def get_supported_formats(self) -> list:
        """
        获取支持的导出格式
        
        Returns:
            list: 支持的格式列表
        """
        return self.SUPPORTED_FORMATS.copy()
    
    def is_format_supported(self, format: str) -> bool:
        """
        检查格式是否支持
        
        Args:
            format: 格式名
            
        Returns:
            bool: 是否支持
        """
        return format.lower() in self.SUPPORTED_FORMATS
