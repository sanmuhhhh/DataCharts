"""
图表管理器

负责图表的创建、存储、更新和删除管理
"""

from typing import Dict, Any, Optional
import time
import sys
import os

# 添加数据类型路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data_types import DataSource, ChartConfig, ChartGenerationError

from .base_chart import BaseChart
from .chart_factory import ChartFactory


class ChartManager:
    """图表管理器类"""
    
    def __init__(self):
        """初始化图表管理器"""
        self.charts: Dict[str, BaseChart] = {}  # chart_id -> chart实例
        self.chart_metadata: Dict[str, Dict[str, Any]] = {}  # chart_id -> 元数据
        self.factory = ChartFactory()
    
    def create_chart(self, data: DataSource, config: ChartConfig) -> str:
        """
        创建新图表
        
        Args:
            data: 数据源
            config: 图表配置
            
        Returns:
            str: 图表ID
            
        Raises:
            ChartGenerationError: 创建失败时抛出
        """
        try:
            # 创建图表实例
            chart = self.factory.create_chart(config.chart_type, data, config)
            
            # 存储图表
            chart_id = chart.chart_id
            self.charts[chart_id] = chart
            
            # 记录元数据
            self.chart_metadata[chart_id] = {
                'created_time': time.time(),
                'last_updated': time.time(),
                'chart_type': config.chart_type,
                'data_size': len(data.content) if hasattr(data.content, '__len__') else 0,
                'access_count': 0
            }
            
            return chart_id
            
        except Exception as e:
            raise ChartGenerationError(f"创建图表失败: {str(e)}")
    
    def get_chart(self, chart_id: str) -> Optional[BaseChart]:
        """
        获取图表实例
        
        Args:
            chart_id: 图表ID
            
        Returns:
            Optional[BaseChart]: 图表实例，不存在时返回None
        """
        chart = self.charts.get(chart_id)
        if chart:
            # 更新访问计数
            if chart_id in self.chart_metadata:
                self.chart_metadata[chart_id]['access_count'] += 1
        return chart
    
    def get_chart_data(self, chart_id: str) -> Dict[str, Any]:
        """
        获取图表渲染数据
        
        Args:
            chart_id: 图表ID
            
        Returns:
            Dict[str, Any]: 图表数据
            
        Raises:
            ChartGenerationError: 图表不存在或渲染失败
        """
        chart = self.get_chart(chart_id)
        if not chart:
            raise ChartGenerationError(f"图表不存在: {chart_id}")
        
        try:
            return chart.render()
        except Exception as e:
            raise ChartGenerationError(f"获取图表数据失败: {str(e)}")
    
    def update_chart(self, chart_id: str, new_data: DataSource) -> bool:
        """
        更新图表数据
        
        Args:
            chart_id: 图表ID
            new_data: 新数据源
            
        Returns:
            bool: 更新是否成功
        """
        chart = self.get_chart(chart_id)
        if not chart:
            return False
        
        try:
            success = chart.update_data(new_data)
            if success and chart_id in self.chart_metadata:
                self.chart_metadata[chart_id]['last_updated'] = time.time()
                self.chart_metadata[chart_id]['data_size'] = len(new_data.content) if hasattr(new_data.content, '__len__') else 0
            return success
        except Exception:
            return False
    
    def update_chart_config(self, chart_id: str, new_config: ChartConfig) -> bool:
        """
        更新图表配置
        
        Args:
            chart_id: 图表ID
            new_config: 新配置
            
        Returns:
            bool: 更新是否成功
        """
        chart = self.get_chart(chart_id)
        if not chart:
            return False
        
        try:
            success = chart.update_config(new_config)
            if success and chart_id in self.chart_metadata:
                self.chart_metadata[chart_id]['last_updated'] = time.time()
            return success
        except Exception:
            return False
    
    def delete_chart(self, chart_id: str) -> bool:
        """
        删除图表
        
        Args:
            chart_id: 图表ID
            
        Returns:
            bool: 删除是否成功
        """
        if chart_id in self.charts:
            del self.charts[chart_id]
            if chart_id in self.chart_metadata:
                del self.chart_metadata[chart_id]
            return True
        return False
    
    def list_charts(self) -> Dict[str, Dict[str, Any]]:
        """
        列出所有图表
        
        Returns:
            Dict[str, Dict[str, Any]]: 图表列表和信息
        """
        result = {}
        
        for chart_id, chart in self.charts.items():
            metadata = self.chart_metadata.get(chart_id, {})
            chart_info = chart.get_chart_info()
            
            result[chart_id] = {
                **chart_info,
                **metadata
            }
        
        return result
    
    def get_chart_count(self) -> int:
        """
        获取图表总数
        
        Returns:
            int: 图表数量
        """
        return len(self.charts)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取图表管理器统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        total_charts = len(self.charts)
        chart_types = {}
        total_access = 0
        
        for chart_id, metadata in self.chart_metadata.items():
            chart_type = metadata.get('chart_type', 'unknown')
            chart_types[chart_type] = chart_types.get(chart_type, 0) + 1
            total_access += metadata.get('access_count', 0)
        
        return {
            'total_charts': total_charts,
            'chart_types': chart_types,
            'total_access_count': total_access,
            'supported_types': self.factory.get_supported_chart_types()
        }
    
    def cleanup_old_charts(self, max_age_hours: int = 24) -> int:
        """
        清理旧图表
        
        Args:
            max_age_hours: 最大保留时间（小时）
            
        Returns:
            int: 清理的图表数量
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        charts_to_delete = []
        
        for chart_id, metadata in self.chart_metadata.items():
            created_time = metadata.get('created_time', current_time)
            age = current_time - created_time
            
            if age > max_age_seconds:
                charts_to_delete.append(chart_id)
        
        # 删除旧图表
        for chart_id in charts_to_delete:
            self.delete_chart(chart_id)
        
        return len(charts_to_delete)
