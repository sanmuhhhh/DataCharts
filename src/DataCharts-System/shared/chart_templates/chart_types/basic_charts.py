"""
基础图表类型实现

实现折线图、柱状图、散点图、饼图等基础图表类型
"""

import pandas as pd
import numpy as np
import io
import json
from typing import Dict, Any, List
import sys
import os

# 添加父目录路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from base_chart import BaseChart

# 添加数据类型路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from data_types import ChartGenerationError


class LineChart(BaseChart):
    """折线图实现"""
    
    def _validate_data_specific(self) -> None:
        """验证折线图数据"""
        df = self._prepare_data_for_rendering()
        if df.empty:
            raise ChartGenerationError("折线图需要非空数据")
    
    def render(self) -> Dict[str, Any]:
        """渲染折线图"""
        try:
            df = self._prepare_data_for_rendering()
            
            # 准备数据集
            datasets = []
            colors = self._get_default_colors()
            
            if len(df.columns) == 1:
                # 单列数据
                datasets.append({
                    "label": df.columns[0],
                    "data": df.iloc[:, 0].tolist(),
                    "borderColor": colors[0],
                    "backgroundColor": colors[0] + "20",  # 添加透明度
                    "tension": self._safe_get_config_option("line_tension", 0.1),
                    "fill": self._safe_get_config_option("fill_area", False),
                    "pointRadius": self._safe_get_config_option("point_radius", 3)
                })
            else:
                # 多列数据
                for i, col in enumerate(df.columns):
                    color_idx = i % len(colors)
                    datasets.append({
                        "label": str(col),
                        "data": df[col].tolist(),
                        "borderColor": colors[color_idx],
                        "backgroundColor": colors[color_idx] + "20",
                        "tension": self._safe_get_config_option("line_tension", 0.1),
                        "fill": False,
                        "pointRadius": self._safe_get_config_option("point_radius", 3)
                    })
            
            # 构建Chart.js配置
            chart_config = {
                "type": "line",
                "data": {
                    "labels": [str(x) for x in df.index.tolist()],
                    "datasets": datasets
                },
                "options": {
                    **self._create_common_chart_options(),
                    "scales": self._create_common_scales(),
                    "elements": {
                        "line": {
                            "tension": self._safe_get_config_option("line_tension", 0.1)
                        }
                    }
                }
            }
            
            return chart_config
            
        except Exception as e:
            raise ChartGenerationError(f"折线图渲染失败: {str(e)}")
    
    def export(self, format: str) -> bytes:
        """导出折线图"""
        try:
            if format == "json":
                return json.dumps(self.render(), ensure_ascii=False).encode('utf-8')
            
            # 使用matplotlib导出图像
            import matplotlib.pyplot as plt
            
            df = self._prepare_data_for_rendering()
            
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            
            fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))
            
            # 绘制线条
            for col in df.columns:
                ax.plot(df.index, df[col], label=str(col), 
                       linewidth=self._safe_get_config_option("line_width", 2))
            
            # 设置标题和标签
            if self.config.title:
                ax.set_title(self.config.title, fontsize=16)
            if self.config.x_axis:
                ax.set_xlabel(self.config.x_axis)
            if self.config.y_axis:
                ax.set_ylabel(self.config.y_axis)
            
            # 设置图例
            if len(df.columns) > 1:
                ax.legend()
            
            # 设置网格
            if self._safe_get_config_option("show_grid", True):
                ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # 导出到字节流
            buffer = io.BytesIO()
            fig.savefig(buffer, format=format, dpi=300, bbox_inches='tight')
            buffer.seek(0)
            
            plt.close(fig)
            return buffer.getvalue()
            
        except Exception as e:
            raise ChartGenerationError(f"折线图导出失败: {str(e)}")


class BarChart(BaseChart):
    """柱状图实现"""
    
    def _validate_data_specific(self) -> None:
        """验证柱状图数据"""
        df = self._prepare_data_for_rendering()
        if df.empty:
            raise ChartGenerationError("柱状图需要非空数据")
    
    def render(self) -> Dict[str, Any]:
        """渲染柱状图"""
        try:
            df = self._prepare_data_for_rendering()
            
            # 准备数据集
            datasets = []
            colors = self._get_default_colors()
            
            if len(df.columns) == 1:
                # 单列数据
                datasets.append({
                    "label": df.columns[0],
                    "data": df.iloc[:, 0].tolist(),
                    "backgroundColor": colors[0],
                    "borderColor": colors[0],
                    "borderWidth": self._safe_get_config_option("border_width", 1)
                })
            else:
                # 多列数据
                for i, col in enumerate(df.columns):
                    color_idx = i % len(colors)
                    datasets.append({
                        "label": str(col),
                        "data": df[col].tolist(),
                        "backgroundColor": colors[color_idx],
                        "borderColor": colors[color_idx],
                        "borderWidth": self._safe_get_config_option("border_width", 1)
                    })
            
            # 构建Chart.js配置
            chart_config = {
                "type": "bar",
                "data": {
                    "labels": [str(x) for x in df.index.tolist()],
                    "datasets": datasets
                },
                "options": {
                    **self._create_common_chart_options(),
                    "scales": self._create_common_scales(),
                    "plugins": {
                        **self._create_common_chart_options()["plugins"],
                        "datalabels": {
                            "display": self._safe_get_config_option("show_data_labels", False)
                        }
                    }
                }
            }
            
            return chart_config
            
        except Exception as e:
            raise ChartGenerationError(f"柱状图渲染失败: {str(e)}")
    
    def export(self, format: str) -> bytes:
        """导出柱状图"""
        try:
            if format == "json":
                return json.dumps(self.render(), ensure_ascii=False).encode('utf-8')
            
            # 使用matplotlib导出图像
            import matplotlib.pyplot as plt
            
            df = self._prepare_data_for_rendering()
            
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            
            fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))
            
            # 绘制柱状图
            x_pos = np.arange(len(df.index))
            
            if len(df.columns) == 1:
                ax.bar(x_pos, df.iloc[:, 0], color=self._get_default_colors()[0])
            else:
                width = 0.8 / len(df.columns)
                colors = self._get_default_colors()
                
                for i, col in enumerate(df.columns):
                    offset = (i - len(df.columns)/2 + 0.5) * width
                    ax.bar(x_pos + offset, df[col], width, 
                          label=str(col), color=colors[i % len(colors)])
            
            # 设置标题和标签
            if self.config.title:
                ax.set_title(self.config.title, fontsize=16)
            if self.config.x_axis:
                ax.set_xlabel(self.config.x_axis)
            if self.config.y_axis:
                ax.set_ylabel(self.config.y_axis)
            
            # 设置x轴标签
            ax.set_xticks(x_pos)
            ax.set_xticklabels([str(x) for x in df.index])
            
            # 设置图例
            if len(df.columns) > 1:
                ax.legend()
            
            # 设置网格
            if self._safe_get_config_option("show_grid", True):
                ax.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            
            # 导出到字节流
            buffer = io.BytesIO()
            fig.savefig(buffer, format=format, dpi=300, bbox_inches='tight')
            buffer.seek(0)
            
            plt.close(fig)
            return buffer.getvalue()
            
        except Exception as e:
            raise ChartGenerationError(f"柱状图导出失败: {str(e)}")


class ScatterChart(BaseChart):
    """散点图实现"""
    
    def _validate_data_specific(self) -> None:
        """验证散点图数据"""
        df = self._prepare_data_for_rendering()
        if df.empty:
            raise ChartGenerationError("散点图需要非空数据")
        if len(df.columns) < 2:
            raise ChartGenerationError("散点图至少需要两列数据")
    
    def render(self) -> Dict[str, Any]:
        """渲染散点图"""
        try:
            df = self._prepare_data_for_rendering()
            
            # 准备散点数据
            scatter_data = []
            for i, (idx, row) in enumerate(df.iterrows()):
                scatter_data.append({
                    "x": row.iloc[0] if len(row) > 0 else i,
                    "y": row.iloc[1] if len(row) > 1 else 0
                })
            
            # 构建Chart.js配置
            chart_config = {
                "type": "scatter",
                "data": {
                    "datasets": [{
                        "label": self.config.title or "散点数据",
                        "data": scatter_data,
                        "backgroundColor": self._safe_get_config_option("point_color", self._get_default_colors()[0]),
                        "borderColor": self._safe_get_config_option("point_border_color", self._get_default_colors()[0]),
                        "pointRadius": self._safe_get_config_option("point_radius", 5),
                        "pointHoverRadius": self._safe_get_config_option("point_hover_radius", 8)
                    }]
                },
                "options": {
                    **self._create_common_chart_options(),
                    "scales": self._create_common_scales()
                }
            }
            
            return chart_config
            
        except Exception as e:
            raise ChartGenerationError(f"散点图渲染失败: {str(e)}")
    
    def export(self, format: str) -> bytes:
        """导出散点图"""
        try:
            if format == "json":
                return json.dumps(self.render(), ensure_ascii=False).encode('utf-8')
            
            # 使用matplotlib导出图像
            import matplotlib.pyplot as plt
            
            df = self._prepare_data_for_rendering()
            
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            
            fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))
            
            # 绘制散点图
            x_data = df.iloc[:, 0] if len(df.columns) > 0 else range(len(df))
            y_data = df.iloc[:, 1] if len(df.columns) > 1 else [0] * len(df)
            
            ax.scatter(x_data, y_data, 
                      c=self._safe_get_config_option("point_color", self._get_default_colors()[0]),
                      s=self._safe_get_config_option("point_size", 50),
                      alpha=self._safe_get_config_option("point_alpha", 0.7))
            
            # 设置标题和标签
            if self.config.title:
                ax.set_title(self.config.title, fontsize=16)
            if self.config.x_axis:
                ax.set_xlabel(self.config.x_axis)
            if self.config.y_axis:
                ax.set_ylabel(self.config.y_axis)
            
            # 设置网格
            if self._safe_get_config_option("show_grid", True):
                ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # 导出到字节流
            buffer = io.BytesIO()
            fig.savefig(buffer, format=format, dpi=300, bbox_inches='tight')
            buffer.seek(0)
            
            plt.close(fig)
            return buffer.getvalue()
            
        except Exception as e:
            raise ChartGenerationError(f"散点图导出失败: {str(e)}")


class PieChart(BaseChart):
    """饼图实现"""
    
    def _validate_data_specific(self) -> None:
        """验证饼图数据"""
        df = self._prepare_data_for_rendering()
        if df.empty:
            raise ChartGenerationError("饼图需要非空数据")
    
    def render(self) -> Dict[str, Any]:
        """渲染饼图"""
        try:
            df = self._prepare_data_for_rendering()
            
            # 处理数据
            if len(df.columns) == 1:
                # 单列数据，使用索引作为标签
                labels = [str(x) for x in df.index.tolist()]
                data = df.iloc[:, 0].tolist()
            else:
                # 多列数据，使用列名作为标签
                labels = [str(col) for col in df.columns]
                data = df.sum().tolist()
            
            # 过滤负值
            filtered_data = []
            filtered_labels = []
            for i, value in enumerate(data):
                if value > 0:
                    filtered_data.append(value)
                    filtered_labels.append(labels[i])
            
            colors = self._get_default_colors()
            
            # 构建Chart.js配置
            chart_config = {
                "type": "pie",
                "data": {
                    "labels": filtered_labels,
                    "datasets": [{
                        "data": filtered_data,
                        "backgroundColor": colors[:len(filtered_data)],
                        "borderColor": "#ffffff",
                        "borderWidth": self._safe_get_config_option("border_width", 2)
                    }]
                },
                "options": {
                    **self._create_common_chart_options(),
                    "plugins": {
                        **self._create_common_chart_options()["plugins"],
                        "legend": {
                            "display": True,
                            "position": self._safe_get_config_option("legend_position", "right")
                        },
                        "tooltip": {
                            "callbacks": {
                                "label": "function(context) { return context.label + ': ' + context.parsed + ' (' + Math.round(context.parsed / context.dataset.data.reduce((a, b) => a + b, 0) * 100) + '%)'; }"
                            }
                        }
                    }
                }
            }
            
            return chart_config
            
        except Exception as e:
            raise ChartGenerationError(f"饼图渲染失败: {str(e)}")
    
    def export(self, format: str) -> bytes:
        """导出饼图"""
        try:
            if format == "json":
                return json.dumps(self.render(), ensure_ascii=False).encode('utf-8')
            
            # 使用matplotlib导出图像
            import matplotlib.pyplot as plt
            
            df = self._prepare_data_for_rendering()
            
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            
            fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))
            
            # 处理数据
            if len(df.columns) == 1:
                labels = [str(x) for x in df.index.tolist()]
                data = df.iloc[:, 0].tolist()
            else:
                labels = [str(col) for col in df.columns]
                data = df.sum().tolist()
            
            # 过滤负值
            filtered_data = []
            filtered_labels = []
            for i, value in enumerate(data):
                if value > 0:
                    filtered_data.append(value)
                    filtered_labels.append(labels[i])
            
            colors = self._get_default_colors()[:len(filtered_data)]
            
            # 绘制饼图
            wedges, texts, autotexts = ax.pie(filtered_data, labels=filtered_labels,
                                            colors=colors, autopct='%1.1f%%',
                                            startangle=90)
            
            # 设置标题
            if self.config.title:
                ax.set_title(self.config.title, fontsize=16)
            
            # 确保饼图是圆形
            ax.axis('equal')
            
            plt.tight_layout()
            
            # 导出到字节流
            buffer = io.BytesIO()
            fig.savefig(buffer, format=format, dpi=300, bbox_inches='tight')
            buffer.seek(0)
            
            plt.close(fig)
            return buffer.getvalue()
            
        except Exception as e:
            raise ChartGenerationError(f"饼图导出失败: {str(e)}")
