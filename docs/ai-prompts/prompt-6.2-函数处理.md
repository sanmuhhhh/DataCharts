# AI实现提示词 - 任务6.2: 函数处理

## 任务上下文

您正在实现DataCharts数据可视化系统的函数解析和数学计算功能。此模块负责解析用户输入的数学表达式，并将其应用到数据集上进行计算。

### 前置条件
- 73 任务6.1 (数据导入处理) 已完成
- 73 数据导入功能正常工作
- 73 基础数据结构可用

### 设计文档参考
- **第4.2节**: 函数处理模块规范
- **第6.1节**: RESTful API 函数处理接口
- **安全要求**: 沙箱执行环境

## 实现任务

### 主要目标
实现安全、高效的函数解析和计算功能，支持多种数学函数、统计函数和数据变换函数。

### 核心功能要求

#### 1. 函数处理接口
实现 `FunctionProcessor` 类中的所有方法：
```python
class FunctionProcessor:
    def parse_expression(self, expression: str) -> FunctionExpression
    def validate_syntax(self, expression: str) -> bool
    def apply_function(self, data: DataSource, expression: FunctionExpression) -> ProcessingResult
    def get_supported_functions(self) -> List[str]
```

#### 2. 支持的函数类型 (严格按照设计文档)
- **数学函数**: sin, cos, tan, log, exp, sqrt
- **统计函数**: mean, std, var, median
- **数据变换**: normalize, standardize, scale
- **滤波函数**: moving_average, gaussian_filter

#### 3. 安全执行环境
- 沙箱机制防止恶意代码执行
- 限制可用函数和模块
- 表达式复杂度检查
- 执行时间限制

## 技术实现要求

### 关键依赖
- **SymPy**: 符号数学表达式解析
- **NumPy**: 数值计算和向量化操作
- **SciPy**: 高级数学函数
- **ast**: Python抽象语法树分析

### 文件结构
```
shared/algorithms/
├── __init__.py
├── function_parser.py        # 表达式解析器
├── expression_evaluator.py   # 表达式求值器
├── function_library.py       # 函数库定义
└── safe_executor.py          # 安全执行环境

backend/app/core/
├── function_processor.py     # 函数处理器核心

backend/app/api/
└── function_routes.py        # 函数相关API路由
```

### 安全要求
- 禁用危险的内置函数 (eval, exec, import等)
- 限制可访问的模块
- 表达式语法验证
- 执行时间监控

## 具体实现指导

### 1. 表达式解析器
```python
# shared/algorithms/function_parser.py
import sympy as sp
from typing import List, Dict, Any
from ..data_types import FunctionExpression, FunctionParseError

class ExpressionParser:
    """表达式解析器"""
    
    def parse(self, expression: str) -> FunctionExpression:
        """
        解析数学表达式
        
        Args:
            expression: 数学表达式字符串
            
        Returns:
            FunctionExpression: 解析后的表达式对象
            
        Raises:
            FunctionParseError: 解析失败时抛出
        """
        try:
            # 使用SymPy解析表达式
            parsed_expr = sp.sympify(expression)
            variables = [str(v) for v in parsed_expr.free_symbols]
            
            return FunctionExpression(
                expression=expression,
                variables=variables,
                parameters={}
            )
        except Exception as e:
            raise FunctionParseError(f"表达式解析失败: {e}")
```

### 2. 安全执行环境
```python
# shared/algorithms/safe_executor.py
class SafeExecutionEnvironment:
    """安全执行环境"""
    
    ALLOWED_MODULES = ['numpy', 'pandas', 'scipy.stats']
    FORBIDDEN_FUNCTIONS = ['eval', 'exec', 'open', 'import']
    
    def create_safe_namespace(self, data_vars: Dict) -> Dict:
        """创建安全的命名空间"""
        namespace = {
            '__builtins__': {},  # 禁用内置函数
            'np': np,
            'pd': pd,
            **self.get_allowed_functions(),
            **data_vars
        }
        return namespace
    
    def get_allowed_functions(self) -> Dict:
        """获取允许的函数"""
        return {
            # 数学函数
            'sin': np.sin,
            'cos': np.cos,
            'tan': np.tan,
            'log': np.log,
            'exp': np.exp,
            'sqrt': np.sqrt,
            
            # 统计函数
            'mean': np.mean,
            'std': np.std,
            'var': np.var,
            'median': np.median
        }
```

### 3. API接口实现
```python
# backend/app/api/function_routes.py
from fastapi import APIRouter, HTTPException
from services.function_service import FunctionService

router = APIRouter()

@router.post("/parse")
async def parse_function(request: dict):
    """
    解析函数表达式
    
    检查语法正确性并提取变量信息
    """
    expression = request.get("expression")
    if not expression:
        raise HTTPException(400, "缺少表达式参数")
    
    try:
        processor = FunctionService()
        result = processor.parse_expression(expression)
        
        return {
            "status": "success",
            "parsed_expression": result.__dict__,
            "is_valid": True
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
            "is_valid": False
        }

@router.post("/apply")
async def apply_function(request: dict):
    """应用函数到数据"""
    # 实现函数应用逻辑
    pass
```

## 性能优化要求

### 向量化计算
- 使用NumPy向量化操作
- 避免Python循环
- 内存效率优化

### 并行处理
- 大数据集分块处理
- 多线程/多进程支持
- 异步执行

## 测试要求

### 单元测试覆盖
- 表达式解析测试
- 函数执行测试
- 安全性验证测试
- 性能基准测试

### 测试用例示例
```python
# tests/test_function_processor.py
class TestFunctionProcessor:
    def test_parse_simple_expression(self):
        """测试简单表达式解析"""
        parser = ExpressionParser()
        result = parser.parse("sin(x) + cos(y)")
        
        assert result.expression == "sin(x) + cos(y)"
        assert set(result.variables) == {"x", "y"}
    
    def test_security_validation(self):
        """测试安全性验证"""
        parser = ExpressionParser()
        
        # 应该拒绝危险表达式
        with pytest.raises(FunctionParseError):
            parser.parse("__import__('os').system('rm -rf /')")
```

## 验证标准

### 功能验证
- [ ] 支持所有设计文档要求的函数类型
- [ ] 表达式解析准确率100%
- [ ] 安全性验证有效
- [ ] API接口响应正常

### 性能验证
- [ ] 简单表达式解析时间 <1ms
- [ ] 10万数据点函数应用时间 <1秒
- [ ] 内存使用合理

### 安全验证
- [ ] 恶意表达式被正确拒绝
- [ ] 沙箱环境有效
- [ ] 无代码注入风险

## 严格要求

### 安全第一原则
1. **表达式验证**: 严格验证所有输入表达式
2. **沙箱执行**: 在受限环境中执行代码
3. **时间限制**: 防止无限循环和长时间执行
4. **内存限制**: 防止内存耗尽攻击

### 代码质量要求
- 完整的类型注解
- 详细的中文文档
- 全面的错误处理
- 高测试覆盖率

## 交付要求

### 必须交付
1. 完整的函数处理器实现
2. 安全执行环境
3. API接口
4. 单元测试套件
5. 性能基准测试

### 测试验证
- 通过所有单元测试
- 安全性测试通过
- 性能测试达标
- API集成测试通过

## 成功标准

完成此任务后，应该能够：
1. 安全地解析和执行用户输入的数学表达式
2. 支持复杂的数学计算和数据变换
3. 为图表生成提供处理后的数据
4. 防止恶意代码执行和系统攻击

请确保实现的安全性和正确性，这是系统的核心计算模块。