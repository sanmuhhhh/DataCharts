# AI实现提示词 - 任务6.1: 数据导入处理

## 任务上下文

您正在实现DataCharts数据可视化系统的数据导入和处理功能。这是系统的核心基础功能，所有后续功能都依赖于此模块。

### 项目状态
- 73 基础框架代码已完成 (src/DataCharts-System/)
- 73 共享数据结构已定义 (shared/data_types.py)
- 73 接口定义已完成 (shared/interfaces.py)
- 73 编译检查已通过

### 设计文档参考
- **第4.1节**: 数据导入模块规范
- **第6.1节**: RESTful API 数据操作接口
- **第7.1节**: 数据处理流程

## 实现任务

### 主要目标
实现完整的数据导入和处理功能，支持多种数据格式的导入、验证、清洗和预处理。

### 核心功能要求

#### 1. 数据导入功能
实现 `DataImporter` 类中的所有方法：
```python
class DataImporter:
    def import_data(self, file_path: str, format: str, options: Dict[str, Any]) -> DataSource
    def validate_data(self, data: DataSource) -> bool  
    def preprocess_data(self, data: DataSource) -> DataSource
    def detect_data_type(self, data: DataSource) -> str
```

#### 2. 支持的数据格式 (严格按照设计文档)
- **CSV**: 逗号分隔值文件
- **Excel**: Excel工作表 (.xlsx, .xls)
- **JSON**: JSON数据文件
- **TXT**: 文本数据文件
- **Manual**: 手动输入数据

#### 3. 数据验证要求
- 格式验证：数据结构完整性
- 类型验证：数据类型一致性
- 范围验证：数值范围合理性
- 完整性验证：必填字段检查

#### 4. 数据预处理功能
- 数据清洗：去除异常值、重复值
- 格式标准化：统一日期格式、数值格式
- 缺失值处理：填充或删除缺失数据
- 数据转换：类型转换、编码转换

## 技术实现要求

### 文件结构
创建以下新文件：
```
shared/data_processing/
├── __init__.py
├── data_importer.py          # 主要实现类
├── data_validator.py         # 数据验证逻辑
├── data_preprocessor.py      # 数据预处理逻辑
└── format_parsers.py         # 各格式解析器

backend/app/services/
├── __init__.py
├── data_service.py           # 数据服务层
└── file_service.py           # 文件处理服务

backend/app/api/
└── data_routes.py            # 数据相关API路由
```

### 依赖库使用
- **pandas**: 数据处理和分析
- **numpy**: 数值计算
- **openpyxl**: Excel文件处理
- **chardet**: 编码检测
- **fastapi**: API框架

### 代码质量要求
- **类型注解**: 所有函数都必须有完整的类型注解
- **中文文档**: 所有公共方法都必须有中文文档字符串
- **错误处理**: 实现完整的异常处理机制
- **单元测试**: 测试覆盖率 ≥90%

## 具体实现指导

### 1. 主实现类
```python
# shared/data_processing/data_importer.py
from typing import Dict, Any
import pandas as pd
from ..data_types import DataSource, SystemError, DataImportError

class DataImporter:
    """数据导入器实现"""
    
    def __init__(self):
        self.supported_formats = ['csv', 'excel', 'json', 'txt', 'manual']
        self.format_parsers = {
            'csv': self._parse_csv,
            'excel': self._parse_excel,
            'json': self._parse_json,
            'txt': self._parse_txt
        }
    
    def import_data(self, file_path: str, format: str, options: Dict[str, Any]) -> DataSource:
        """
        导入数据，支持多种格式
        
        Args:
            file_path: 文件路径
            format: 数据格式
            options: 导入选项
            
        Returns:
            DataSource: 导入的数据源对象
            
        Raises:
            DataImportError: 导入失败时抛出
        """
        # 实现导入逻辑
        pass
    
    # 实现其他方法...
```

### 2. API接口实现
```python
# backend/app/api/data_routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.data_service import DataService

router = APIRouter()

@router.post("/upload")
async def upload_data(file: UploadFile = File(...)):
    """
    上传数据文件
    
    支持的格式: CSV, Excel, JSON, TXT
    """
    # 实现文件上传逻辑
    pass

@router.post("/process")
async def process_data(data_id: str, process_options: dict):
    """数据预处理"""
    # 实现数据处理逻辑
    pass
```

### 3. 单元测试
```python
# tests/test_data_importer.py
import pytest
from shared.data_processing.data_importer import DataImporter

class TestDataImporter:
    def test_import_csv_file(self):
        """测试CSV文件导入"""
        # 实现测试逻辑
        pass
    
    def test_validate_data_structure(self):
        """测试数据结构验证"""
        # 实现测试逻辑
        pass
```

## 验证标准

### 功能验证
- [ ] 成功导入所有支持的数据格式
- [ ] 数据验证功能正常工作
- [ ] 数据预处理功能完整
- [ ] API接口响应正常

### 质量验证
- [ ] 单元测试覆盖率 ≥90%
- [ ] 所有测试用例通过
- [ ] 代码符合PEP 8规范
- [ ] 完整的中文文档注释

### 性能验证
- [ ] 100MB文件导入时间 <30秒
- [ ] 内存使用合理
- [ ] 支持并发处理

## 严格要求

### 必须遵循的规范
1. **严格按照设计文档**: 不能增加或删除设计文档中定义的功能
2. **类型安全**: 必须使用完整的类型注解
3. **错误处理**: 使用定义好的异常类型
4. **编码规范**: 遵循PEP 8标准
5. **测试驱动**: 每个功能都必须有对应的测试

### 禁止的操作
- 74 修改已定义的数据结构
- 74 添加设计文档中未定义的功能
- 74 使用不安全的文件操作
- 74 忽略错误处理

## 交付要求

### 代码文件
- 实现所有新建文件
- 更新shared/interfaces.py中的DataImporter类
- 更新backend/app/main.py添加路由

### 测试文件
- 完整的单元测试套件
- 集成测试用例
- 测试数据文件

### 文档
- 更新API文档
- 使用说明和示例
- 错误代码说明

## 成功标准

完成此任务后，应该能够：
1. 通过API成功上传各种格式的数据文件
2. 自动验证和预处理数据
3. 为后续的函数处理和图表生成提供数据基础
4. 处理各种异常情况并给出友好的错误提示

请严格按照上述要求实现数据导入功能，确保代码质量和系统稳定性。