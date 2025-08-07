# AI实现提示词 - 任务6.3: 图表生成

## 任务上下文

您正在实现DataCharts数据可视化系统的图表生成和矩阵可视化功能。这是系统的核心可视化模块，负责将处理后的数据转换为各种类型的图表。

### 前置条件
- 73 任务6.1 (数据导入处理) 已完成
- 73 任务6.2 (函数处理) 已完成
- 73 数据处理流水线可用

### 设计文档参考
- **第4.3节**: 图表生成模块规范
- **第4.4节**: 矩阵可视化模块规范
- **第6.1节**: RESTful API 图表生成接口

## 实现任务

### 主要目标
实现完整的图表生成系统，支持多种图表类型的创建、渲染、导出和动态更新。

### 核心功能要求

#### 1. 图表生成接口
实现 `ChartGenerator` 和 `MatrixVisualizer` 类：
```python
class ChartGenerator:
    def create_chart(self, data: DataSource, config: ChartConfig) -> str
    def export_chart(self, chart_id: str, format: str) -> bytes
    def update_chart(self, chart_id: str, new_data: DataSource) -> bool

class MatrixVisualizer:
    def visualize_2d_matrix(self, matrix: MatrixData) -> str
    def visualize_3d_matrix(self, matrix: MatrixData) -> str
    def create_heatmap(self, matrix: MatrixData) -> str
    def create_surface_plot(self, matrix: MatrixData) -> str
```

#### 2. 支持的图表类型 (严格按照设计文档)
- **基础图表**: line, bar, scatter, pie
- **统计图表**: histogram, box_plot, violin_plot
- **多维图表**: heatmap, 3d_surface, contour
- **时间序列**: time_series, candlestick

#### 3. 图表配置系统
- 标题和轴标签
- 颜色和样式配置
- 尺寸和布局设置
- 交互功能配置

## 技术实现要求

### 关键依赖
- **Matplotlib**: 后端图表生成
- **Plotly**: 交互式图表
- **Chart.js**: 前端图表库（配置生成）
- **ECharts**: 前端可视化库（配置生成）

### 文件结构
```
shared/chart_templates/
├── __init__.py
├── chart_factory.py         # 图表工厂
├── base_chart.py            # 基础图表类
├── chart_manager.py         # 图表管理器
├── chart_exporter.py        # 图表导出器
└── chart_types/             # 图表类型实现
    ├── __init__.py
    ├── basic_charts.py      # 基础图表
    ├── statistical_charts.py # 统计图表
    └── matrix_charts.py     # 矩阵图表

backend/app/core/
├── chart_generator.py       # 图表生成器核心

backend/app/api/
└── chart_routes.py          # 图表相关API路由

frontend/src/components/
├── ChartRenderer.vue        # Chart.js渲染器
└── EChartsRenderer.vue      # ECharts渲染器
```

## 具体实现指导

### 1. 图表工厂模式
```python
# shared/chart_templates/chart_factory.py
from typing import Dict, Type
from .base_chart import BaseChart
from .chart_types.basic_charts import LineChart, BarChart, ScatterChart, PieChart

class ChartFactory:
    """图表工厂类"""
    
    CHART_TYPES: Dict[str, Type[BaseChart]] = {
        # 基础图表
        'line': LineChart,
        'bar': BarChart,
        'scatter': ScatterChart,
        'pie': PieChart,
        
        # 统计图表
        'histogram': HistogramChart,
        'box_plot': BoxPlotChart,
        
        # 多维图表
        'heatmap': HeatmapChart,
        '3d_surface': Surface3DChart
    }
    
    def create_chart(self, chart_type: str, data: DataSource, config: ChartConfig) -> BaseChart:
        """
        创建图表实例
        
        Args:
            chart_type: 图表类型
            data: 数据源
            config: 图表配置
            
        Returns:
            BaseChart: 图表实例
            
        Raises:
            ChartGenerationError: 不支持的图表类型
        """
        if chart_type not in self.CHART_TYPES:
            raise ChartGenerationError(f"不支持的图表类型: {chart_type}")
        
        chart_class = self.CHART_TYPES[chart_type]
        return chart_class(data, config)
```

### 2. 基础图表类
```python
# shared/chart_templates/base_chart.py
from abc import ABC, abstractmethod
from typing import Dict, Any
import uuid

class BaseChart(ABC):
    """基础图表类"""
    
    def __init__(self, data: DataSource, config: ChartConfig):
        self.data = data
        self.config = config
        self.chart_id = self._generate_chart_id()
    
    @abstractmethod
    def render(self) -> Dict[str, Any]:
        """
        渲染图表数据
        
        Returns:
            Dict: 图表配置和数据
        """
        pass
    
    @abstractmethod
    def export(self, format: str) -> bytes:
        """
        导出图表
        
        Args:
            format: 导出格式 (png, jpg, svg, pdf)
            
        Returns:
            bytes: 导出的图表数据
        """
        pass
    
    def update_data(self, new_data: DataSource) -> bool:
        """更新图表数据"""
        self.data = new_data
        return True
    
    def _generate_chart_id(self) -> str:
        """生成唯一图表ID"""
        return f"chart_{uuid.uuid4().hex[:8]}"
```

### 3. 具体图表实现
```python
# shared/chart_templates/chart_types/basic_charts.py
import pandas as pd
import numpy as np
from ..base_chart import BaseChart

class LineChart(BaseChart):
    """折线图实现"""
    
    def render(self) -> Dict[str, Any]:
        """渲染折线图"""
        df = pd.DataFrame(self.data.content)
        
        return {
            "type": "line",
            "data": {
                "labels": df.index.tolist(),
                "datasets": [{
                    "label": self.config.title,
                    "data": df.values.tolist(),
                    "borderColor": self.config.options.get("color", "#409EFF"),
                    "tension": self.config.options.get("tension", 0.1),
                    "fill": False
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": self.config.title
                    },
                    "legend": {
                        "display": True
                    }
                },
                "scales": {
                    "x": {
                        "title": {
                            "display": True,
                            "text": self.config.x_axis
                        }
                    },
                    "y": {
                        "title": {
                            "display": True,
                            "text": self.config.y_axis
                        }
                    }
                }
            }
        }
    
    def export(self, format: str) -> bytes:
        """导出折线图"""
        import matplotlib.pyplot as plt
        
        df = pd.DataFrame(self.data.content)
        
        fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))
        ax.plot(df.index, df.values)
        ax.set_title(self.config.title)
        ax.set_xlabel(self.config.x_axis)
        ax.set_ylabel(self.config.y_axis)
        
        # 导出到字节流
        import io
        buffer = io.BytesIO()
        fig.savefig(buffer, format=format, dpi=300, bbox_inches='tight')
        buffer.seek(0)
        
        plt.close(fig)
        return buffer.getvalue()

class HeatmapChart(BaseChart):
    """热力图实现"""
    
    def render(self) -> Dict[str, Any]:
        """渲染热力图"""
        matrix = self.data.content
        if not isinstance(matrix, np.ndarray):
            matrix = np.array(matrix)
        
        # 生成ECharts热力图配置
        heatmap_data = []
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                heatmap_data.append([j, i, float(matrix[i, j])])
        
        return {
            "type": "heatmap",
            "tooltip": {
                "position": "top"
            },
            "grid": {
                "height": "50%",
                "top": "10%"
            },
            "xAxis": {
                "type": "category",
                "splitArea": {
                    "show": True
                }
            },
            "yAxis": {
                "type": "category",
                "splitArea": {
                    "show": True
                }
            },
            "visualMap": {
                "min": float(np.min(matrix)),
                "max": float(np.max(matrix)),
                "calculable": True,
                "orient": "horizontal",
                "left": "center",
                "bottom": "15%"
            },
            "series": [{
                "name": self.config.title,
                "type": "heatmap",
                "data": heatmap_data,
                "label": {
                    "show": True
                },
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowColor": "rgba(0, 0, 0, 0.5)"
                    }
                }
            }]
        }
```

### 4. API接口实现
```python
# backend/app/api/chart_routes.py
from fastapi import APIRouter, HTTPException, Response
from services.chart_service import ChartService
from services.data_service import DataService

router = APIRouter()

@router.post("/create")
async def create_chart(request: dict):
    """
    创建图表
    
    基于数据和配置生成图表
    """
    try:
        data_service = DataService()
        chart_service = ChartService()
        
        # 获取数据
        data = data_service.get_data(request["data_id"])
        if not data:
            raise HTTPException(404, "数据不存在")
        
        # 创建图表
        chart_result = chart_service.create_chart(
            data=data,
            chart_type=request["chart_type"],
            config=request["config"]
        )
        
        return {
            "status": "success",
            "chart_id": chart_result.chart_id,
            "chart_data": chart_result.chart_data
        }
        
    except Exception as e:
        raise HTTPException(500, f"图表创建失败: {str(e)}")

@router.get("/{chart_id}/export")
async def export_chart(chart_id: str, format: str = "png"):
    """导出图表"""
    try:
        chart_service = ChartService()
        
        # 获取图表
        chart = chart_service.get_chart(chart_id)
        if not chart:
            raise HTTPException(404, "图表不存在")
        
        # 导出图表
        exported_data = chart_service.export_chart(chart, format)
        
        # 设置响应头
        media_type = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "svg": "image/svg+xml",
            "pdf": "application/pdf"
        }.get(format, "application/octet-stream")
        
        return Response(
            content=exported_data,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename=chart.{format}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"图表导出失败: {str(e)}")
```

### 5. 前端集成
```vue
<!-- frontend/src/components/ChartRenderer.vue -->
<template>
  <div class="chart-container">
    <canvas ref="chartCanvas" :width="width" :height="height"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

interface Props {
  chartData: any
  width?: number
  height?: number
}

const props = withDefaults(defineProps<Props>(), {
  width: 800,
  height: 600
})

const chartCanvas = ref<HTMLCanvasElement>()
let chartInstance: Chart | null = null

const renderChart = () => {
  if (chartCanvas.value && props.chartData) {
    if (chartInstance) {
      chartInstance.destroy()
    }
    
    chartInstance = new Chart(chartCanvas.value, props.chartData)
  }
}

onMounted(() => {
  renderChart()
})

watch(() => props.chartData, () => {
  renderChart()
}, { deep: true })
</script>
```

## 测试要求

### 单元测试
```python
# tests/test_chart_generator.py
class TestChartGenerator:
    def test_create_line_chart(self):
        """测试折线图创建"""
        factory = ChartFactory()
        config = ChartConfig(
            chart_type="line",
            title="测试折线图",
            x_axis="X轴",
            y_axis="Y轴",
            width=800,
            height=600,
            options={}
        )
        
        chart = factory.create_chart("line", test_data, config)
        result = chart.render()
        
        assert result["type"] == "line"
        assert result["data"]["datasets"][0]["label"] == "测试折线图"
    
    def test_export_chart_png(self):
        """测试PNG格式导出"""
        # 实现导出测试
        pass
```

## 性能要求

### 渲染性能
- 1万数据点图表渲染时间 <3秒
- 图表交互响应时间 <500ms
- 内存使用合理

### 导出性能
- 图表导出时间 <5秒
- 支持高分辨率导出
- 多格式支持

## 验证标准

### 功能验证
- [ ] 支持所有设计文档要求的图表类型
- [ ] 图表渲染质量高
- [ ] 导出功能正常工作
- [ ] 前端集成无问题

### 质量验证
- [ ] 单元测试覆盖率 ≥90%
- [ ] 图表配置灵活
- [ ] 错误处理完善

## 交付要求

### 必须交付
1. 完整的图表生成系统
2. 所有支持的图表类型实现
3. 图表导出功能
4. 前端渲染组件
5. API接口
6. 单元测试套件

### 质量要求
- 代码质量符合规范
- 完整的中文文档
- 高测试覆盖率

## 成功标准

完成此任务后，应该能够：
1. 根据数据和配置生成各种类型的图表
2. 支持图表的实时更新和交互
3. 导出高质量的图表文件
4. 为用户界面提供完整的图表展示功能

请确保图表的美观性和交互性，这是用户直接感受到的核心功能。