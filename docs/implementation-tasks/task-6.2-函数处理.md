# 任务 6.2: 函数处理实现

## 任务概述

实现DataCharts数据可视化系统的函数解析和数学计算功能，支持多种数学函数、统计函数和数据变换函数的解析、验证和应用。

## 设计文档参考

- **第4.2节**: 函数处理模块
- **第5.2节**: 功能流程设计 - 数据处理流程
- **第6.1节**: API接口设计 - 函数处理接口
- **第7.1节**: 数据处理流程

## 功能需求分析

### 核心接口实现 (来自设计文档)
基于 `shared/interfaces.py` 中的 `FunctionProcessor` 类：

```python
class FunctionProcessor:
    def parse_expression(self, expression: str) -> FunctionExpression
    def validate_syntax(self, expression: str) -> bool
    def apply_function(self, data: DataSource, expression: FunctionExpression) -> ProcessingResult
    def get_supported_functions(self) -> List[str]
```

### 支持的函数类型 (设计文档第4.2节)
- **数学函数**: sin, cos, tan, log, exp, sqrt
- **统计函数**: mean, std, var, median
- **数据变换**: normalize, standardize, scale
- **滤波函数**: moving_average, gaussian_filter

## 实现要求

### 1. 表达式解析功能 (`parse_expression`)

#### 实现文件
- `shared/algorithms/function_parser.py` (新建)
- `shared/algorithms/expression_evaluator.py` (新建)
- `backend/app/core/function_processor.py` (新建)

#### 功能要求
- 使用SymPy进行数学表达式解析
- 支持复杂的数学表达式
- 变量替换和参数绑定
- 表达式语法树构建
- 安全的表达式执行环境

#### 实现步骤
1. **表达式词法分析**
   ```python
   class ExpressionLexer:
       def tokenize(self, expression: str) -> List[Token]:
           # 将表达式分解为令牌
   ```

2. **语法解析**
   ```python
   class ExpressionParser:
       def parse(self, tokens: List[Token]) -> AST:
           # 构建抽象语法树
   ```

3. **表达式验证**
   ```python
   def parse_expression(self, expression: str) -> FunctionExpression:
       try:
           # 使用SymPy解析表达式
           parsed_expr = sp.sympify(expression)
           variables = list(parsed_expr.free_symbols)
           return FunctionExpression(
               expression=expression,
               variables=[str(v) for v in variables],
               parameters={}
           )
       except Exception as e:
           raise FunctionParseError(f"表达式解析失败: {e}")
   ```

### 2. 语法验证功能 (`validate_syntax`)

#### 验证内容
- **语法正确性**: 符合数学表达式语法
- **函数支持性**: 使用的函数在支持列表中
- **变量有效性**: 变量名称符合规范
- **安全性检查**: 防止恶意代码执行
- **复杂度检查**: 避免过于复杂的表达式

#### 实现示例
```python
def validate_syntax(self, expression: str) -> bool:
    try:
        # 基础语法检查
        parsed = sp.sympify(expression)
        
        # 函数支持性检查
        functions_used = self._extract_functions(parsed)
        supported_functions = self.get_supported_functions()
        
        for func in functions_used:
            if func not in supported_functions:
                return False
        
        # 安全性检查
        if self._has_security_risks(parsed):
            return False
            
        return True
    except:
        return False
```

### 3. 函数应用功能 (`apply_function`)

#### 功能要求
- 将解析的函数应用到数据集
- 支持向量化操作
- 处理多维数据
- 计算结果验证
- 性能优化

#### 实现示例
```python
def apply_function(self, data: DataSource, expression: FunctionExpression) -> ProcessingResult:
    start_time = time.time()
    
    try:
        # 准备数据
        df = self._prepare_data(data)
        
        # 创建计算环境
        namespace = self._create_namespace(df, expression.variables)
        
        # 执行函数计算
        result = self._evaluate_expression(expression.expression, namespace)
        
        processing_time = time.time() - start_time
        
        return ProcessingResult(
            data=result,
            processing_time=processing_time,
            status="success",
            error_message=None
        )
    except Exception as e:
        return ProcessingResult(
            data=None,
            processing_time=time.time() - start_time,
            status="error",
            error_message=str(e)
        )
```

### 4. 支持函数库管理 (`get_supported_functions`)

#### 函数库组织
```python
class FunctionLibrary:
    MATH_FUNCTIONS = {
        'sin': np.sin,
        'cos': np.cos,
        'tan': np.tan,
        'log': np.log,
        'exp': np.exp,
        'sqrt': np.sqrt,
        'abs': np.abs,
        'floor': np.floor,
        'ceil': np.ceil
    }
    
    STATISTICAL_FUNCTIONS = {
        'mean': np.mean,
        'std': np.std,
        'var': np.var,
        'median': np.median,
        'min': np.min,
        'max': np.max,
        'sum': np.sum
    }
    
    TRANSFORM_FUNCTIONS = {
        'normalize': lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)),
        'standardize': lambda x: (x - np.mean(x)) / np.std(x),
        'scale': lambda x, factor: x * factor
    }
    
    FILTER_FUNCTIONS = {
        'moving_average': lambda x, window: pd.Series(x).rolling(window).mean(),
        'gaussian_filter': lambda x, sigma: scipy.ndimage.gaussian_filter1d(x, sigma)
    }
```

## 高级功能实现

### 1. 复杂表达式支持

#### 多变量函数
```python
# 支持如下表达式:
# "sin(x) + cos(y)"
# "mean(x) * std(y)"
# "normalize(x) + standardize(y)"
```

#### 嵌套函数
```python
# 支持如下表达式:
# "sin(log(x))"
# "mean(normalize(x))"
# "moving_average(sin(x), 5)"
```

### 2. 安全执行环境

#### 沙箱机制
```python
class SafeExecutionEnvironment:
    ALLOWED_MODULES = ['numpy', 'pandas', 'scipy.stats']
    FORBIDDEN_FUNCTIONS = ['eval', 'exec', 'open', 'import']
    
    def create_safe_namespace(self, data_vars: Dict) -> Dict:
        namespace = {
            '__builtins__': {},  # 禁用内置函数
            'np': np,
            'pd': pd,
            **self.MATH_FUNCTIONS,
            **self.STATISTICAL_FUNCTIONS,
            **data_vars
        }
        return namespace
```

### 3. 性能优化

#### 向量化计算
```python
def vectorized_apply(self, data: np.ndarray, func: callable) -> np.ndarray:
    # 使用NumPy向量化操作
    return np.vectorize(func)(data)
```

#### 并行计算
```python
def parallel_apply(self, data: np.ndarray, func: callable, n_jobs: int = -1) -> np.ndarray:
    # 对大数据集使用并行计算
    from joblib import Parallel, delayed
    return Parallel(n_jobs=n_jobs)(delayed(func)(chunk) for chunk in np.array_split(data, cpu_count()))
```

## API 接口实现

### 后端 API 端点 (设计文档第6.1节)

#### 函数解析接口
```python
@app.post("/api/function/parse")
async def parse_function(request: FunctionParseRequest):
    processor = FunctionProcessor()
    try:
        result = processor.parse_expression(request.expression)
        return {
            "status": "success",
            "parsed_expression": result,
            "variables": result.variables,
            "is_valid": True
        }
    except FunctionParseError as e:
        return {
            "status": "error",
            "error_message": str(e),
            "is_valid": False
        }
```

#### 函数应用接口
```python
@app.post("/api/function/apply")
async def apply_function(request: FunctionApplyRequest):
    processor = FunctionProcessor()
    data_service = DataService()
    
    # 获取数据
    data = data_service.get_data(request.data_id)
    
    # 解析函数
    expression = processor.parse_expression(request.expression)
    
    # 应用函数
    result = processor.apply_function(data, expression)
    
    return {
        "status": result.status,
        "processing_time": result.processing_time,
        "result_data": result.data,
        "error_message": result.error_message
    }
```

#### 函数库查询接口
```python
@app.get("/api/function/library")
async def get_function_library():
    processor = FunctionProcessor()
    return {
        "supported_functions": processor.get_supported_functions(),
        "function_categories": {
            "数学函数": list(FunctionLibrary.MATH_FUNCTIONS.keys()),
            "统计函数": list(FunctionLibrary.STATISTICAL_FUNCTIONS.keys()),
            "数据变换": list(FunctionLibrary.TRANSFORM_FUNCTIONS.keys()),
            "滤波函数": list(FunctionLibrary.FILTER_FUNCTIONS.keys())
        }
    }
```

## 错误处理策略

### 异常类型定义
```python
class FunctionParseError(SystemError):
    """函数解析异常"""
    pass

class FunctionExecutionError(SystemError):
    """函数执行异常"""
    pass

class UnsupportedFunctionError(SystemError):
    """不支持的函数异常"""
    pass
```

### 错误处理原则
- **详细错误信息**: 指出具体的语法错误位置
- **建议修复**: 提供可能的修复建议
- **安全防护**: 防止恶意表达式执行
- **优雅降级**: 部分函数失败时的处理

## 测试要求

### 单元测试
- **测试覆盖率**: ≥95%
- **表达式解析测试**: 各种复杂表达式
- **函数执行测试**: 所有支持的函数
- **错误处理测试**: 异常表达式处理
- **性能测试**: 大数据集处理性能

### 测试用例
```python
class TestFunctionProcessor:
    def test_parse_simple_expression(self):
        # 测试简单数学表达式解析
        
    def test_parse_complex_expression(self):
        # 测试复杂嵌套表达式解析
        
    def test_validate_syntax(self):
        # 测试语法验证功能
        
    def test_apply_math_functions(self):
        # 测试数学函数应用
        
    def test_apply_statistical_functions(self):
        # 测试统计函数应用
        
    def test_security_validation(self):
        # 测试安全性验证
        
    def test_performance_large_dataset(self):
        # 测试大数据集性能
```

## 实现文件清单

### 新建文件
1. `shared/algorithms/__init__.py`
2. `shared/algorithms/function_parser.py`
3. `shared/algorithms/expression_evaluator.py`
4. `shared/algorithms/function_library.py`
5. `shared/algorithms/safe_executor.py`
6. `backend/app/core/__init__.py`
7. `backend/app/core/function_processor.py`
8. `backend/app/api/function_routes.py`
9. `tests/test_function_parser.py`
10. `tests/test_function_processor.py`

### 更新文件
1. `shared/interfaces.py` - 实现FunctionProcessor类
2. `backend/app/main.py` - 添加函数处理路由
3. `shared/data_types.py` - 添加函数相关错误类型

## 成功标准

### 功能标准
- 73 支持所有设计文档要求的函数类型
- 73 表达式解析准确率100%
- 73 函数执行结果正确
- 73 安全性验证有效
- 73 API接口响应正常

### 质量标准
- 73 单元测试覆盖率 ≥95%
- 73 所有测试用例通过
- 73 代码符合编码规范
- 73 完整的中文文档注释
- 73 安全机制完善

### 性能标准
- 73 简单表达式解析时间 <1ms
- 73 复杂表达式解析时间 <10ms
- 73 10万数据点函数应用时间 <1秒
- 73 内存使用合理

## 依赖关系

### 前置依赖
- 73 任务6.1 (数据导入处理) 已完成
- 73 基础框架代码已完成
- 73 共享数据结构已定义

### 后续依赖
- 为任务6.3 (图表生成) 提供数据处理能力
- 为任务6.4 (用户界面) 提供函数计算功能
- 为任务6.5 (API服务) 提供函数处理接口

## 估时和里程碑

### 总工期: 2天

#### 第1天
- **上午**: 实现表达式解析和验证功能
- **下午**: 实现函数库和基础应用功能

#### 第2天
- **上午**: 实现高级功能和安全机制
- **下午**: API接口实现和测试

### 关键里程碑
- **M1**: 基础解析功能完成 (1天)
- **M2**: 完整功能实现和测试 (2天)

## 注意事项

1. **安全性**: 严格的表达式验证，防止代码注入
2. **性能**: 大数据集处理时的内存和时间控制
3. **准确性**: 数学计算的精度和正确性
4. **扩展性**: 预留新函数添加的扩展机制
5. **用户友好**: 清晰的错误提示和使用说明