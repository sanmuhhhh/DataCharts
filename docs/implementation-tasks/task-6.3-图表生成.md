# 任务 6.3: 图表生成实现

## 任务概述

实现DataCharts数据可视化系统的图表生成和矩阵可视化功能，支持多种图表类型的创建、渲染、导出和动态更新。

## 设计文档参考

- **第4.3节**: 图表生成模块
- **第4.4节**: 矩阵可视化模块
- **第5.1节**: 用户界面设计 - 图表展示区域
- **第6.1节**: API接口设计 - 图表生成接口

## 功能需求分析

### 核心接口实现 (来自设计文档)
基于 `shared/interfaces.py` 中的相关类：

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

### 支持的图表类型 (设计文档第4.3节)
- **基础图表**: line, bar, scatter, pie
- **统计图表**: histogram, box_plot, violin_plot
- **多维图表**: heatmap, 3d_surface, contour
- **时间序列**: time_series, candlestick

## 实现要求

### 1. 图表创建功能 (`create_chart`)

#### 实现文件
- `shared/chart_templates/chart_factory.py` (新建)
- `shared/chart_templates/base_chart.py` (新建)
- `shared/chart_templates/chart_types/` (新建目录)
- `backend/app/core/chart_generator.py` (新建)

#### 图表工厂模式
```python
class ChartFactory:
    CHART_TYPES = {
        # 基础图表
        'line': LineChart,
        'bar': BarChart,
        'scatter': ScatterChart,
        'pie': PieChart,
        
        # 统计图表
        'histogram': HistogramChart,
        'box_plot': BoxPlotChart,
        'violin_plot': ViolinPlotChart,
        
        # 多维图表
        'heatmap': HeatmapChart,
        '3d_surface': Surface3DChart,
        'contour': ContourChart,
        
        # 时间序列
        'time_series': TimeSeriesChart,
        'candlestick': CandlestickChart
    }
    
    def create_chart(self, chart_type: str, data: DataSource, config: ChartConfig):
        if chart_type not in self.CHART_TYPES:
            raise ChartGenerationError(f"不支持的图表类型: {chart_type}")
        
        chart_class = self.CHART_TYPES[chart_type]
        return chart_class(data, config)
```

#### 基础图表类
```python
class BaseChart(ABC):
    def __init__(self, data: DataSource, config: ChartConfig):
        self.data = data
        self.config = config
        self.chart_id = self._generate_chart_id()
    
    @abstractmethod
    def render(self) -> Dict[str, Any]:
        """渲染图表数据"""
        pass
    
    @abstractmethod
    def export(self, format: str) -> bytes:
        """导出图表"""
        pass
    
    def update_data(self, new_data: DataSource) -> bool:
        """更新图表数据"""
        self.data = new_data
        return True
    
    def _generate_chart_id(self) -> str:
        return f"chart_{uuid.uuid4().hex[:8]}"
```

### 2. 具体图表类型实现

#### 折线图 (LineChart)
```python
class LineChart(BaseChart):
    def render(self) -> Dict[str, Any]:
        df = pd.DataFrame(self.data.content)
        
        return {
            "type": "line",
            "data": {
                "labels": df.index.tolist(),
                "datasets": [{
                    "label": self.config.title,
                    "data": df.values.tolist(),
                    "borderColor": self.config.options.get("color", "#409EFF"),
                    "tension": self.config.options.get("tension", 0.1)
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": self.config.title
                    }
                },
                "scales": {
                    "x": {"title": {"display": True, "text": self.config.x_axis}},
                    "y": {"title": {"display": True, "text": self.config.y_axis}}
                }
            }
        }
```

#### 柱状图 (BarChart)
```python
class BarChart(BaseChart):
    def render(self) -> Dict[str, Any]:
        df = pd.DataFrame(self.data.content)
        
        return {
            "type": "bar",
            "data": {
                "labels": df.index.tolist(),
                "datasets": [{
                    "label": self.config.title,
                    "data": df.values.tolist(),
                    "backgroundColor": self.config.options.get("colors", ["#409EFF"]),
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": self.config.title
                    }
                },
                "scales": {
                    "x": {"title": {"display": True, "text": self.config.x_axis}},
                    "y": {"title": {"display": True, "text": self.config.y_axis}}
                }
            }
        }
```

#### 散点图 (ScatterChart)
```python
class ScatterChart(BaseChart):
    def render(self) -> Dict[str, Any]:
        df = pd.DataFrame(self.data.content)
        
        scatter_data = []
        for i, row in df.iterrows():
            scatter_data.append({
                "x": row.iloc[0],
                "y": row.iloc[1] if len(row) > 1 else i
            })
        
        return {
            "type": "scatter",
            "data": {
                "datasets": [{
                    "label": self.config.title,
                    "data": scatter_data,
                    "backgroundColor": self.config.options.get("color", "#409EFF")
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": self.config.title
                    }
                },
                "scales": {
                    "x": {"title": {"display": True, "text": self.config.x_axis}},
                    "y": {"title": {"display": True, "text": self.config.y_axis}}
                }
            }
        }
```

### 3. 矩阵可视化实现

#### 热力图 (Heatmap)
```python
class HeatmapChart(BaseChart):
    def render(self) -> Dict[str, Any]:
        matrix = self.data.content
        if not isinstance(matrix, np.ndarray):
            matrix = np.array(matrix)
        
        # 生成热力图数据
        heatmap_data = []
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                heatmap_data.append({
                    "x": j,
                    "y": i,
                    "v": float(matrix[i, j])
                })
        
        return {
            "type": "heatmap",
            "data": heatmap_data,
            "options": {
                "title": self.config.title,
                "xAxis": {"title": self.config.x_axis},
                "yAxis": {"title": self.config.y_axis},
                "visualMap": {
                    "min": float(np.min(matrix)),
                    "max": float(np.max(matrix)),
                    "calculable": True,
                    "orient": "horizontal",
                    "left": "center",
                    "bottom": "15%"
                }
            }
        }
```

#### 3D表面图 (Surface3D)
```python
class Surface3DChart(BaseChart):
    def render(self) -> Dict[str, Any]:
        matrix = self.data.content
        if not isinstance(matrix, np.ndarray):
            matrix = np.array(matrix)
        
        # 生成3D表面数据
        surface_data = []
        for i in range(matrix.shape[0]):
            row_data = []
            for j in range(matrix.shape[1]):
                row_data.append(float(matrix[i, j]))
            surface_data.append(row_data)
        
        return {
            "type": "surface",
            "data": surface_data,
            "options": {
                "title": self.config.title,
                "grid3D": {
                    "boxWidth": 200,
                    "boxDepth": 80,
                    "boxHeight": 60
                },
                "xAxis3D": {"name": self.config.x_axis},
                "yAxis3D": {"name": self.config.y_axis},
                "zAxis3D": {"name": "值"}
            }
        }
```

### 4. 图表导出功能

#### 多格式导出支持
```python
class ChartExporter:
    SUPPORTED_FORMATS = ['png', 'jpg', 'svg', 'pdf', 'json']
    
    def export_chart(self, chart: BaseChart, format: str) -> bytes:
        if format not in self.SUPPORTED_FORMATS:
            raise ChartGenerationError(f"不支持的导出格式: {format}")
        
        if format == 'json':
            return self._export_json(chart)
        else:
            return self._export_image(chart, format)
    
    def _export_json(self, chart: BaseChart) -> bytes:
        chart_data = chart.render()
        return json.dumps(chart_data, ensure_ascii=False).encode('utf-8')
    
    def _export_image(self, chart: BaseChart, format: str) -> bytes:
        # 使用matplotlib或plotly生成图像
        fig = self._create_matplotlib_figure(chart)
        
        buffer = io.BytesIO()
        fig.savefig(buffer, format=format, dpi=300, bbox_inches='tight')
        buffer.seek(0)
        
        return buffer.getvalue()
```

### 5. 动态图表更新

#### 实时数据更新
```python
class ChartManager:
    def __init__(self):
        self.charts = {}  # chart_id -> chart_instance
    
    def create_chart(self, data: DataSource, config: ChartConfig) -> str:
        chart_type = config.chart_type
        chart = ChartFactory().create_chart(chart_type, data, config)
        
        self.charts[chart.chart_id] = chart
        return chart.chart_id
    
    def update_chart(self, chart_id: str, new_data: DataSource) -> bool:
        if chart_id not in self.charts:
            return False
        
        chart = self.charts[chart_id]
        return chart.update_data(new_data)
    
    def get_chart_data(self, chart_id: str) -> Dict[str, Any]:
        if chart_id not in self.charts:
            raise ChartGenerationError(f"图表不存在: {chart_id}")
        
        chart = self.charts[chart_id]
        return chart.render()
```

## API 接口实现

### 后端 API 端点 (设计文档第6.1节)

#### 图表创建接口
```python
@app.post("/api/chart/create")
async def create_chart(request: ChartCreateRequest):
    try:
        data_service = DataService()
        chart_manager = ChartManager()
        
        # 获取数据
        data = data_service.get_data(request.data_id)
        
        # 创建图表配置
        config = ChartConfig(
            chart_type=request.chart_type,
            title=request.config.get("title", ""),
            x_axis=request.config.get("x_axis", ""),
            y_axis=request.config.get("y_axis", ""),
            width=request.config.get("width", 800),
            height=request.config.get("height", 600),
            options=request.config.get("options", {})
        )
        
        # 创建图表
        chart_id = chart_manager.create_chart(data, config)
        chart_data = chart_manager.get_chart_data(chart_id)
        
        return {
            "status": "success",
            "chart_id": chart_id,
            "chart_data": chart_data
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }
```

#### 图表导出接口
```python
@app.get("/api/chart/{chart_id}/export")
async def export_chart(chart_id: str, format: str = "png"):
    try:
        chart_manager = ChartManager()
        exporter = ChartExporter()
        
        if chart_id not in chart_manager.charts:
            raise HTTPException(404, "图表不存在")
        
        chart = chart_manager.charts[chart_id]
        exported_data = exporter.export_chart(chart, format)
        
        return Response(
            content=exported_data,
            media_type=f"image/{format}" if format != "json" else "application/json",
            headers={"Content-Disposition": f"attachment; filename=chart.{format}"}
        )
        
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
```

#### 图表更新接口
```python
@app.put("/api/chart/{chart_id}")
async def update_chart(chart_id: str, request: ChartUpdateRequest):
    try:
        chart_manager = ChartManager()
        data_service = DataService()
        
        # 获取新数据
        new_data = data_service.get_data(request.data_id)
        
        # 更新图表
        success = chart_manager.update_chart(chart_id, new_data)
        
        if success:
            chart_data = chart_manager.get_chart_data(chart_id)
            return {
                "status": "success",
                "chart_data": chart_data
            }
        else:
            return {
                "status": "error",
                "error_message": "图表更新失败"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }
```

## 前端集成

### Chart.js 集成
```typescript
// frontend/src/components/ChartRenderer.vue
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

### ECharts 集成
```typescript
// frontend/src/components/EChartsRenderer.vue
<template>
  <div ref="chartContainer" class="echarts-container" :style="{ width: width + 'px', height: height + 'px' }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

interface Props {
  chartData: any
  width?: number
  height?: number
}

const props = withDefaults(defineProps<Props>(), {
  width: 800,
  height: 600
})

const chartContainer = ref<HTMLDivElement>()
let chartInstance: echarts.ECharts | null = null

const renderChart = () => {
  if (chartContainer.value && props.chartData) {
    if (!chartInstance) {
      chartInstance = echarts.init(chartContainer.value)
    }
    
    chartInstance.setOption(props.chartData)
  }
}

onMounted(() => {
  renderChart()
})

watch(() => props.chartData, () => {
  renderChart()
}, { deep: true })

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
})
</script>
```

## 测试要求

### 单元测试
```python
class TestChartGenerator:
    def test_create_line_chart(self):
        # 测试折线图创建
        
    def test_create_bar_chart(self):
        # 测试柱状图创建
        
    def test_create_heatmap(self):
        # 测试热力图创建
        
    def test_export_chart_png(self):
        # 测试PNG格式导出
        
    def test_update_chart_data(self):
        # 测试图表数据更新
        
    def test_chart_validation(self):
        # 测试图表配置验证
```

### 集成测试
- **API接口测试**: 所有图表相关API
- **前端渲染测试**: 图表在浏览器中的渲染
- **导出功能测试**: 各种格式的导出
- **性能测试**: 大数据集图表渲染

## 实现文件清单

### 新建文件
1. `shared/chart_templates/__init__.py`
2. `shared/chart_templates/chart_factory.py`
3. `shared/chart_templates/base_chart.py`
4. `shared/chart_templates/chart_manager.py`
5. `shared/chart_templates/chart_exporter.py`
6. `shared/chart_templates/chart_types/__init__.py`
7. `shared/chart_templates/chart_types/basic_charts.py`
8. `shared/chart_templates/chart_types/statistical_charts.py`
9. `shared/chart_templates/chart_types/matrix_charts.py`
10. `backend/app/core/chart_generator.py`
11. `backend/app/api/chart_routes.py`
12. `frontend/src/components/ChartRenderer.vue`
13. `frontend/src/components/EChartsRenderer.vue`
14. `tests/test_chart_generator.py`

## 成功标准

### 功能标准
- 73 支持所有设计文档要求的图表类型
- 73 图表渲染质量高
- 73 导出功能正常工作
- 73 动态更新功能正常
- 73 前端集成无问题

### 质量标准
- 73 单元测试覆盖率 ≥90%
- 73 图表渲染性能良好
- 73 内存使用合理
- 73 代码质量高

### 性能标准
- 73 1万数据点图表渲染时间 <3秒
- 73 图表导出时间 <5秒
- 73 动态更新响应时间 <1秒

## 依赖关系

### 前置依赖
- 73 任务6.1 (数据导入处理) 已完成
- 73 任务6.2 (函数处理) 已完成

### 后续依赖
- 为任务6.4 (用户界面) 提供图表展示功能
- 为任务6.5 (API服务) 提供图表生成服务

## 估时和里程碑

### 总工期: 3天

#### 第1天
- **上午**: 实现基础图表类型
- **下午**: 实现统计图表类型

#### 第2天
- **上午**: 实现矩阵可视化功能
- **下午**: 实现图表导出和更新功能

#### 第3天
- **上午**: 前端集成和API接口
- **下午**: 测试和优化

### 关键里程碑
- **M1**: 基础图表功能完成 (1天)
- **M2**: 高级图表功能完成 (2天)
- **M3**: 完整功能实现和测试 (3天)