# 任务 6.1: 数据导入处理实现

## 任务概述

实现DataCharts数据可视化系统的数据导入和处理功能，支持多种数据格式的导入、验证、清洗和预处理。

## 设计文档参考

- **第4.1节**: 数据导入模块
- **第5.1节**: 用户界面设计 - 数据操作面板
- **第6.1节**: API接口设计 - 数据操作接口
- **第7.1节**: 数据处理流程

## 功能需求分析

### 核心接口实现 (来自设计文档)
基于 `shared/interfaces.py` 中的 `DataImporter` 类：

```python
class DataImporter:
    def import_data(self, file_path: str, format: str, options: Dict[str, Any]) -> DataSource
    def validate_data(self, data: DataSource) -> bool
    def preprocess_data(self, data: DataSource) -> DataSource
    def detect_data_type(self, data: DataSource) -> str
```

### 支持的数据格式 (设计文档第4.1节)
- **CSV**: 逗号分隔值文件
- **Excel**: Excel工作表 (.xlsx, .xls)
- **JSON**: JSON数据文件
- **TXT**: 文本数据文件
- **Manual**: 手动输入数据

## 实现要求

### 1. 数据导入功能 (`import_data`)

#### 实现文件
- `shared/data_processing/data_importer.py` (新建)
- `backend/app/services/data_service.py` (新建)

#### 功能要求
- 自动检测文件格式
- 支持不同编码格式 (UTF-8, GBK, GB2312)
- 处理大文件分块读取
- 提供导入进度反馈
- 错误处理和用户友好的错误信息

#### 实现步骤
1. **文件格式检测**
   ```python
   def detect_file_format(file_path: str) -> str:
       # 基于文件扩展名和内容特征检测格式
   ```

2. **格式特定解析器**
   ```python
   class CSVParser:
       def parse(self, file_path: str, options: Dict) -> pd.DataFrame
   
   class ExcelParser:
       def parse(self, file_path: str, options: Dict) -> pd.DataFrame
   
   class JSONParser:
       def parse(self, file_path: str, options: Dict) -> pd.DataFrame
   ```

3. **统一导入接口**
   ```python
   def import_data(self, file_path: str, format: str, options: Dict[str, Any]) -> DataSource:
       # 调用相应的解析器，返回标准化的DataSource对象
   ```

### 2. 数据验证功能 (`validate_data`)

#### 验证内容
- **格式验证**: 数据结构完整性
- **类型验证**: 数据类型一致性
- **范围验证**: 数值范围合理性
- **完整性验证**: 必填字段检查
- **一致性验证**: 数据逻辑一致性

#### 实现示例
```python
def validate_data(self, data: DataSource) -> bool:
    validators = [
        self._validate_structure,
        self._validate_data_types,
        self._validate_ranges,
        self._validate_completeness
    ]
    return all(validator(data) for validator in validators)
```

### 3. 数据预处理功能 (`preprocess_data`)

#### 预处理操作
- **数据清洗**: 去除异常值、重复值
- **格式标准化**: 统一日期格式、数值格式
- **缺失值处理**: 填充或删除缺失数据
- **数据转换**: 类型转换、编码转换
- **数据归一化**: 数值范围标准化

#### 实现示例
```python
def preprocess_data(self, data: DataSource) -> DataSource:
    # 1. 数据清洗
    cleaned_data = self._clean_data(data)
    # 2. 格式标准化
    standardized_data = self._standardize_format(cleaned_data)
    # 3. 缺失值处理
    complete_data = self._handle_missing_values(standardized_data)
    # 4. 数据转换
    transformed_data = self._transform_data(complete_data)
    return transformed_data
```

### 4. 数据类型检测 (`detect_data_type`)

#### 检测类型
- **数值型**: 整数、浮点数
- **文本型**: 字符串、分类数据
- **日期型**: 日期、时间、时间戳
- **布尔型**: 真/假值
- **复合型**: 列表、对象

#### 实现策略
```python
def detect_data_type(self, data: DataSource) -> str:
    type_detectors = {
        'numeric': self._is_numeric_type,
        'datetime': self._is_datetime_type,
        'categorical': self._is_categorical_type,
        'boolean': self._is_boolean_type,
        'text': self._is_text_type
    }
    # 返回检测到的主要数据类型
```

## API 接口实现

### 后端 API 端点 (设计文档第6.1节)

#### 文件上传接口
```python
@app.post("/api/data/upload")
async def upload_data(file: UploadFile, options: str = None):
    # 实现文件上传和初步处理
    # 返回数据ID和基本信息
```

#### 数据处理接口
```python
@app.post("/api/data/process")
async def process_data(data_id: str, process_options: Dict):
    # 实现数据预处理
    # 返回处理结果和统计信息
```

#### 数据验证接口
```python
@app.post("/api/data/validate")
async def validate_data(data_id: str):
    # 实现数据验证
    # 返回验证结果和问题列表
```

## 错误处理策略

### 异常类型定义
```python
class DataImportError(SystemError):
    """数据导入异常"""
    pass

class DataValidationError(SystemError):
    """数据验证异常"""
    pass

class DataProcessingError(SystemError):
    """数据处理异常"""
    pass
```

### 错误处理原则
- **用户友好**: 提供清晰的错误信息
- **可恢复**: 支持错误恢复和重试
- **日志记录**: 详细的错误日志
- **状态保持**: 错误时保持系统稳定

## 性能优化要求

### 大文件处理
- **分块读取**: 避免内存溢出
- **异步处理**: 不阻塞用户界面
- **进度反馈**: 实时处理进度
- **缓存机制**: 重复访问优化

### 内存管理
- **及时释放**: 处理完成后释放内存
- **流式处理**: 边读边处理
- **压缩存储**: 临时数据压缩

## 测试要求

### 单元测试
- **测试覆盖率**: ≥90%
- **边界测试**: 各种边界条件
- **异常测试**: 错误处理逻辑
- **性能测试**: 大文件处理性能

### 测试用例
```python
class TestDataImporter:
    def test_import_csv_file(self):
        # 测试CSV文件导入
    
    def test_import_excel_file(self):
        # 测试Excel文件导入
    
    def test_validate_data_structure(self):
        # 测试数据结构验证
    
    def test_preprocess_missing_values(self):
        # 测试缺失值处理
    
    def test_detect_numeric_type(self):
        # 测试数值类型检测
```

### 集成测试
- **API接口测试**: 所有数据相关API
- **文件处理测试**: 各种格式文件
- **错误处理测试**: 异常情况处理

## 实现文件清单

### 新建文件
1. `shared/data_processing/__init__.py`
2. `shared/data_processing/data_importer.py`
3. `shared/data_processing/data_validator.py`
4. `shared/data_processing/data_preprocessor.py`
5. `shared/data_processing/format_parsers.py`
6. `backend/app/services/__init__.py`
7. `backend/app/services/data_service.py`
8. `backend/app/api/data_routes.py`
9. `tests/test_data_importer.py`
10. `tests/test_data_validator.py`

### 更新文件
1. `shared/interfaces.py` - 实现DataImporter类
2. `backend/app/main.py` - 添加数据路由
3. `shared/data_types.py` - 添加错误类型定义

## 成功标准

### 功能标准
- 73 成功导入所有支持的数据格式
- 73 数据验证功能正常工作
- 73 数据预处理功能完整
- 73 数据类型检测准确
- 73 API接口响应正常

### 质量标准
- 73 单元测试覆盖率 ≥90%
- 73 所有测试用例通过
- 73 代码符合编码规范
- 73 完整的中文文档注释
- 73 错误处理机制完善

### 性能标准
- 73 100MB文件导入时间 <30秒
- 73 内存使用合理 (不超过文件大小的2倍)
- 73 支持并发处理
- 73 用户界面响应流畅

## 验证方法

### 功能验证
1. **格式兼容性测试**: 导入各种格式的测试文件
2. **大文件测试**: 测试100MB+文件处理
3. **异常数据测试**: 测试格式错误、编码错误等情况
4. **API集成测试**: 测试前后端数据传输

### 性能验证
1. **处理时间测试**: 记录不同大小文件的处理时间
2. **内存使用测试**: 监控内存使用峰值
3. **并发测试**: 测试多用户同时上传处理

## 依赖关系

### 前置依赖
- 73 基础框架代码已完成
- 73 共享数据结构已定义
- 73 基础接口已定义

### 后续依赖
- 为任务6.2 (函数处理) 提供数据源
- 为任务6.3 (图表生成) 提供数据基础
- 为任务6.4 (用户界面) 提供数据操作功能
- 为任务6.5 (API服务) 提供数据处理能力

## 估时和里程碑

### 总工期: 2天

#### 第1天
- **上午**: 实现基础数据导入功能
- **下午**: 实现数据验证和预处理

#### 第2天
- **上午**: 实现API接口和错误处理
- **下午**: 单元测试和集成测试

### 关键里程碑
- **M1**: 基础导入功能完成 (1天)
- **M2**: 完整功能实现和测试 (2天)

## 注意事项

1. **安全性**: 文件上传需要安全验证，防止恶意文件
2. **兼容性**: 确保跨平台兼容性
3. **扩展性**: 预留新格式支持的扩展接口
4. **用户体验**: 提供清晰的进度提示和错误信息
5. **性能**: 大文件处理时注意内存和时间控制