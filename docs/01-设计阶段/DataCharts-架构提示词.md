# DataCharts 数据可视化系统 - 架构提示词

## 项目概述

请基于数据可视化系统设计文档生成完整的项目架构、核心数据结构和外部接口定义。

## 核心数据结构要求

基于设计文档第4节核心功能模块和第8节文件组织结构，系统需要实现以下数据结构：

### 1. 图表配置结构 (来自设计文档第4.3节)
```python
@dataclass
class ChartConfig:
    chart_type: str          # 图表类型：line、bar、scatter、pie等
    title: str               # 图表标题
    x_axis: str             # X轴标签
    y_axis: str             # Y轴标签
    width: int              # 图表宽度
    height: int             # 图表高度
    options: Dict[str, Any] # 其他配置选项
```

### 2. 数据源结构 (来自设计文档第4.1节)
```python
@dataclass
class DataSource:
    id: str                  # 数据唯一标识
    format: str             # 数据格式：csv、excel、json、txt
    content: Any            # 数据内容
    metadata: Dict[str, Any] # 元数据信息
```

### 3. 函数表达式结构 (来自设计文档第4.2节)
```python
@dataclass
class FunctionExpression:
    expression: str          # 函数表达式字符串
    variables: List[str]     # 变量列表
    parameters: Dict[str, Any] # 参数字典
```

### 4. 处理结果结构 (来自设计文档第7节)
```python
@dataclass
class ProcessingResult:
    data: Any               # 处理后的数据
    processing_time: float  # 处理耗时
    status: str            # 处理状态：success、error
    error_message: str     # 错误信息
```

### 5. 系统错误类型 (来自设计文档第7节)
```python
class SystemError(Exception):
    pass

class DataImportError(SystemError):
    pass

class FunctionParseError(SystemError):
    pass

class ChartGenerationError(SystemError):
    pass
```

### 6. 矩阵数据结构 (来自设计文档第4.4节)
```python
@dataclass
class MatrixData:
    data: np.ndarray        # 矩阵数据
    dimensions: Tuple[int, ...] # 矩阵维度
    dtype: str             # 数据类型
    labels: Dict[str, List[str]] # 标签信息
```

## 外部接口定义要求

基于设计文档第6节API接口设计，系统需要实现以下外部接口：

### 1. 数据导入接口 (来自设计文档第4.1节)
```python
class DataImporter:
    def import_data(self, file_path: str, format: str, options: Dict[str, Any]) -> DataSource:
        """导入数据，支持多种格式"""
        pass
    
    def validate_data(self, data: DataSource) -> bool:
        """验证数据完整性和格式"""
        pass
    
    def preprocess_data(self, data: DataSource) -> DataSource:
        """预处理数据，清洗和标准化"""
        pass
    
    def detect_data_type(self, data: DataSource) -> str:
        """检测数据类型"""
        pass
```

### 2. 函数处理接口 (来自设计文档第4.2节)
```python
class FunctionProcessor:
    def parse_expression(self, expression: str) -> FunctionExpression:
        """解析函数表达式"""
        pass
    
    def validate_syntax(self, expression: str) -> bool:
        """验证表达式语法"""
        pass
    
    def apply_function(self, data: DataSource, expression: FunctionExpression) -> ProcessingResult:
        """应用函数到数据"""
        pass
    
    def get_supported_functions(self) -> List[str]:
        """获取支持的函数列表"""
        pass
```

### 3. 图表生成接口 (来自设计文档第4.3节)
```python
class ChartGenerator:
    def create_chart(self, data: DataSource, config: ChartConfig) -> str:
        """创建图表，返回图表ID"""
        pass
    
    def export_chart(self, chart_id: str, format: str) -> bytes:
        """导出图表为指定格式"""
        pass
    
    def update_chart(self, chart_id: str, new_data: DataSource) -> bool:
        """更新图表数据"""
        pass
```

### 4. 矩阵可视化接口 (来自设计文档第4.4节)
```python
class MatrixVisualizer:
    def visualize_2d_matrix(self, matrix: MatrixData) -> str:
        """可视化2D矩阵"""
        pass
    
    def visualize_3d_matrix(self, matrix: MatrixData) -> str:
        """可视化3D矩阵"""
        pass
    
    def create_heatmap(self, matrix: MatrixData) -> str:
        """创建热力图"""
        pass
    
    def create_surface_plot(self, matrix: MatrixData) -> str:
        """创建表面图"""
        pass
```

### 5. RESTful API接口 (来自设计文档第6.1节)
```python
# 数据操作接口
@app.post("/api/data/upload")
async def upload_data():
    """数据上传API端点"""
    pass

@app.post("/api/data/process")
async def process_data():
    """数据处理API端点"""
    pass

@app.post("/api/chart/create")
async def create_chart():
    """图表创建API端点"""
    pass

@app.get("/api/chart/{chart_id}/export")
async def export_chart():
    """图表导出API端点"""
    pass
```

## 技术要求

基于设计文档第3节技术栈选择：

### 前端技术栈
- **框架**: Vue 3 + TypeScript
- **图表库**: Chart.js / ECharts
- **UI组件**: Element Plus / Vuetify
- **状态管理**: Pinia
- **构建工具**: Vite

### 后端技术栈
- **框架**: FastAPI
- **数据处理**: NumPy, Pandas, SciPy
- **函数解析**: SymPy
- **图表生成**: Matplotlib, Plotly
- **数据库**: SQLite (开发) / PostgreSQL (生产)

### 客户端技术栈
- **GUI框架**: PyQt6
- **图表组件**: PyQt-Charts
- **数据处理**: NumPy, Pandas
- **本地存储**: SQLite

## 项目结构要求

基于设计文档第8节文件组织结构：

```
src/DataCharts-System/
├── frontend/                    # Vue.js 前端
│   ├── src/
│   │   ├── components/         # 组件
│   │   ├── views/             # 页面
│   │   ├── store/             # 状态管理
│   │   └── utils/             # 工具函数
│   ├── public/
│   └── package.json
├── backend/                     # Python 后端
│   ├── app/
│   │   ├── api/               # API 路由
│   │   ├── core/              # 核心功能
│   │   ├── models/            # 数据模型
│   │   └── services/          # 业务服务
│   ├── tests/
│   └── requirements.txt
├── desktop/                     # PyQt 客户端
│   ├── src/
│   │   ├── ui/                # 界面文件
│   │   ├── core/              # 核心逻辑
│   │   └── utils/             # 工具模块
│   ├── resources/             # 资源文件
│   └── requirements.txt
├── shared/                      # 共享代码
│   ├── algorithms/            # 算法实现
│   ├── data_processing/       # 数据处理
│   └── chart_templates/       # 图表模板
├── tests/                       # 测试文件
└── README.md
```

## 输出要求

1. **文档要求**：
   - 每个模块包含完整的中文文档注释
   - 严格遵循设计文档中的数据结构定义
   - 严格遵循设计文档中的接口规范
   - 不允许增减设计文档中定义的结构和接口

2. **代码要求**：
   - 代码目录放置在 src/DataCharts-System/ 目录
   - 生成相应的 .gitignore 文件
   - 实现必要的类型定义和接口
   - 包含基本的使用示例

3. **质量要求**：
   - 遵循 PEP 8 (Python) 和 ESLint (TypeScript) 代码规范
   - 实现基本的错误处理机制
   - 包含必要的配置文件（requirements.txt, package.json等）

## 支持的功能范围

基于设计文档第4节核心功能模块：

### 数据格式支持
- CSV文件
- Excel工作表
- JSON数据文件
- 文本数据文件
- 手动输入数据

### 函数类型支持
- 数学函数：sin, cos, tan, log, exp, sqrt
- 统计函数：mean, std, var, median
- 数据变换：normalize, standardize, scale
- 滤波函数：moving_average, gaussian_filter

### 图表类型支持
- 基础图表：line, bar, scatter, pie
- 统计图表：histogram, box_plot, violin_plot
- 多维图表：heatmap, 3d_surface, contour
- 时间序列：time_series, candlestick

## 使用示例要求

每个主要接口都需要包含基本的使用示例，展示如何：
1. 导入和处理数据
2. 解析和应用函数
3. 生成和导出图表
4. 处理矩阵数据
5. 使用API接口

## 验证要求

生成的架构必须：
- 涵盖设计文档中的所有核心数据结构
- 涵盖设计文档中的所有外部接口
- 支持设计文档中规定的所有功能
- 遵循设计文档中的技术栈选择
- 符合设计文档中的架构设计原则