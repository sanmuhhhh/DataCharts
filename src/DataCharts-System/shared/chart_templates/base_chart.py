"""
基础图表类

定义所有图表类型的公共接口和基础功能
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import uuid
import sys
import os

# 添加数据类型路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data_types import DataSource, ChartConfig, ChartGenerationError


class BaseChart(ABC):
    """基础图表类，所有图表类型的父类"""
    
    def __init__(self, data: DataSource, config: ChartConfig):
        """
        初始化图表
        
        Args:
            data: 数据源
            config: 图表配置
        """
        self.data = data
        self.config = config
        self.chart_id = self._generate_chart_id()
        self._validate_data()
        self._validate_config()
    
    @abstractmethod
    def render(self) -> Dict[str, Any]:
        """
        渲染图表数据
        
        Returns:
            Dict[str, Any]: 图表配置和数据字典
        """
        pass
    
    @abstractmethod
    def export(self, format: str) -> bytes:
        """
        导出图表
        
        Args:
            format: 导出格式 (png, jpg, svg, pdf, json)
            
        Returns:
            bytes: 导出的图表数据
        """
        pass
    
    def update_data(self, new_data: DataSource) -> bool:
        """
        更新图表数据
        
        Args:
            new_data: 新的数据源
            
        Returns:
            bool: 更新是否成功
        """
        try:
            self.data = new_data
            self._validate_data()
            return True
        except Exception:
            return False
    
    def update_config(self, new_config: ChartConfig) -> bool:
        """
        更新图表配置
        
        Args:
            new_config: 新的图表配置
            
        Returns:
            bool: 更新是否成功
        """
        try:
            self.config = new_config
            self._validate_config()
            return True
        except Exception:
            return False
    
    def get_chart_info(self) -> Dict[str, Any]:
        """
        获取图表信息
        
        Returns:
            Dict[str, Any]: 图表信息
        """
        return {
            'chart_id': self.chart_id,
            'chart_type': self.__class__.__name__.replace('Chart', '').lower(),
            'title': self.config.title,
            'width': self.config.width,
            'height': self.config.height,
            'data_size': len(self.data.content) if hasattr(self.data.content, '__len__') else 0,
            'created_time': getattr(self, '_created_time', None)
        }
    
    def _generate_chart_id(self) -> str:
        """
        生成唯一图表ID
        
        Returns:
            str: 唯一ID
        """
        return f"chart_{uuid.uuid4().hex[:8]}"
    
    def _validate_data(self) -> None:
        """
        验证数据源
        
        Raises:
            ChartGenerationError: 数据无效时抛出
        """
        if not self.data:
            raise ChartGenerationError("数据源不能为空")
        
        if not hasattr(self.data, 'content') or self.data.content is None:
            raise ChartGenerationError("数据内容不能为空")
        
        # 子类可以重写此方法进行更具体的验证
        self._validate_data_specific()
    
    def _validate_config(self) -> None:
        """
        验证图表配置
        
        Raises:
            ChartGenerationError: 配置无效时抛出
        """
        if not self.config:
            raise ChartGenerationError("图表配置不能为空")
        
        if self.config.width <= 0 or self.config.height <= 0:
            raise ChartGenerationError("图表尺寸必须大于0")
        
        # 子类可以重写此方法进行更具体的验证
        self._validate_config_specific()
    
    def _validate_data_specific(self) -> None:
        """
        子类特定的数据验证
        
        子类可以重写此方法实现特定的数据验证逻辑
        """
        pass
    
    def _validate_config_specific(self) -> None:
        """
        子类特定的配置验证
        
        子类可以重写此方法实现特定的配置验证逻辑
        """
        pass
    
    def _prepare_data_for_rendering(self) -> Any:
        """
        为渲染准备数据
        
        Returns:
            Any: 准备好的数据
        """
        import pandas as pd
        
        # 确保数据是DataFrame格式
        if isinstance(self.data.content, pd.DataFrame):
            return self.data.content
        elif isinstance(self.data.content, (list, tuple)):
            return pd.DataFrame(self.data.content)
        elif isinstance(self.data.content, dict):
            return pd.DataFrame([self.data.content])
        else:
            # 尝试转换为DataFrame
            try:
                return pd.DataFrame(self.data.content)
            except Exception:
                raise ChartGenerationError("无法将数据转换为DataFrame格式")
    
    def _get_default_colors(self) -> list:
        """
        获取默认颜色方案
        
        Returns:
            list: 颜色列表
        """
        return [
            '#409EFF',  # 蓝色
            '#67C23A',  # 绿色
            '#E6A23C',  # 橙色
            '#F56C6C',  # 红色
            '#909399',  # 灰色
            '#C71585',  # 深粉色
            '#20B2AA',  # 浅海洋绿
            '#FF69B4',  # 热粉色
            '#8A2BE2',  # 蓝紫色
            '#00CED1'   # 深青色
        ]
    
    def _format_number(self, value: float, precision: int = 2) -> str:
        """
        格式化数字显示
        
        Args:
            value: 数值
            precision: 精度
            
        Returns:
            str: 格式化后的字符串
        """
        if isinstance(value, (int, float)):
            if abs(value) >= 1e6:
                return f"{value/1e6:.{precision}f}M"
            elif abs(value) >= 1e3:
                return f"{value/1e3:.{precision}f}K"
            else:
                return f"{value:.{precision}f}"
        return str(value)
    
    def _safe_get_config_option(self, key: str, default: Any = None) -> Any:
        """
        安全获取配置选项
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        if hasattr(self.config, 'options') and self.config.options:
            return self.config.options.get(key, default)
        return default
    
    def _create_common_chart_options(self) -> Dict[str, Any]:
        """
        创建通用图表选项
        
        Returns:
            Dict[str, Any]: 通用选项
        """
        return {
            "responsive": True,
            "maintainAspectRatio": False,
            "plugins": {
                "title": {
                    "display": bool(self.config.title),
                    "text": self.config.title or "",
                    "font": {
                        "size": self._safe_get_config_option("title_font_size", 16)
                    }
                },
                "legend": {
                    "display": self._safe_get_config_option("show_legend", True),
                    "position": self._safe_get_config_option("legend_position", "top")
                },
                "tooltip": {
                    "enabled": self._safe_get_config_option("show_tooltip", True)
                }
            },
            "animation": {
                "duration": self._safe_get_config_option("animation_duration", 1000)
            }
        }
    
    def _create_common_scales(self) -> Dict[str, Any]:
        """
        创建通用坐标轴配置
        
        Returns:
            Dict[str, Any]: 坐标轴配置
        """
        return {
            "x": {
                "title": {
                    "display": bool(self.config.x_axis),
                    "text": self.config.x_axis or ""
                },
                "grid": {
                    "display": self._safe_get_config_option("show_grid", True)
                }
            },
            "y": {
                "title": {
                    "display": bool(self.config.y_axis),
                    "text": self.config.y_axis or ""
                },
                "grid": {
                    "display": self._safe_get_config_option("show_grid", True)
                }
            }
        }
