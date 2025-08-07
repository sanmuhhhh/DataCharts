"""
数据导入器

实现数据导入、验证、预处理和类型检测功能
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from pathlib import Path
import uuid
from datetime import datetime

from .format_parsers import get_parser, ManualParser
from .data_validator import DataValidator
from .data_preprocessor import DataPreprocessor
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data_types import DataSource, DataImportError, SUPPORTED_DATA_FORMATS


class DataImporter:
    """数据导入器实现类"""
    
    def __init__(self):
        self.validator = DataValidator()
        self.preprocessor = DataPreprocessor()
        self.supported_formats = list(SUPPORTED_DATA_FORMATS.keys())
    
    def import_data(self, file_path: str, format: str, options: Dict[str, Any]) -> DataSource:
        """
        导入数据，支持多种格式
        
        Args:
            file_path: 文件路径
            format: 数据格式 (csv, excel, json, txt, manual)
            options: 导入选项
            
        Returns:
            DataSource: 导入的数据源对象
            
        Raises:
            DataImportError: 导入失败时抛出
        """
        try:
            # 验证格式支持
            if format.lower() not in self.supported_formats:
                raise DataImportError(f"不支持的数据格式: {format}")
            
            # 处理手动输入数据
            if format.lower() == 'manual':
                return self._import_manual_data(options.get('data'), options)
            
            # 验证文件存在
            if not Path(file_path).exists():
                raise DataImportError(f"文件不存在: {file_path}")
            
            # 验证文件大小
            max_size_mb = options.get('max_file_size_mb', 100)
            self.validator.validate_file_size(file_path, max_size_mb)
            
            # 获取解析器并解析文件
            parser = get_parser(format.lower())
            df = parser.parse(file_path, options)
            
            # 创建数据源对象
            data_source = DataSource(
                id=self._generate_data_id(),
                format=format.lower(),
                content=df,
                metadata={
                    'file_path': file_path,
                    'file_size': Path(file_path).stat().st_size,
                    'import_time': datetime.now().isoformat(),
                    'import_options': options,
                    'original_shape': df.shape,
                    'columns': list(df.columns),
                    'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
                }
            )
            
            print(f"成功导入数据: {df.shape[0]} 行, {df.shape[1]} 列")
            return data_source
            
        except DataImportError:
            raise
        except Exception as e:
            raise DataImportError(f"数据导入失败: {str(e)}")
    
    def _import_manual_data(self, data: Any, options: Dict[str, Any]) -> DataSource:
        """
        导入手动输入的数据
        
        Args:
            data: 手动输入的数据
            options: 导入选项
            
        Returns:
            DataSource: 数据源对象
        """
        try:
            if data is None:
                raise DataImportError("手动输入数据不能为空")
            
            # 使用手动数据解析器
            df = ManualParser.parse_manual_data(data, options)
            
            # 创建数据源对象
            data_source = DataSource(
                id=self._generate_data_id(),
                format='manual',
                content=df,
                metadata={
                    'data_type': 'manual_input',
                    'import_time': datetime.now().isoformat(),
                    'import_options': options,
                    'original_shape': df.shape,
                    'columns': list(df.columns),
                    'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
                }
            )
            
            print(f"成功导入手动数据: {df.shape[0]} 行, {df.shape[1]} 列")
            return data_source
            
        except Exception as e:
            raise DataImportError(f"手动数据导入失败: {str(e)}")
    
    def validate_data(self, data: DataSource) -> bool:
        """
        验证数据完整性和格式
        
        Args:
            data: 数据源对象
            
        Returns:
            bool: 验证是否通过
            
        Raises:
            DataImportError: 验证失败时抛出
        """
        try:
            return self.validator.validate_data(data)
        except Exception as e:
            raise DataImportError(f"数据验证失败: {str(e)}")
    
    def preprocess_data(self, data: DataSource, options: Dict[str, Any] = None) -> DataSource:
        """
        预处理数据，清洗和标准化
        
        Args:
            data: 输入数据源
            options: 预处理选项
            
        Returns:
            DataSource: 预处理后的数据源
            
        Raises:
            DataImportError: 预处理失败时抛出
        """
        try:
            return self.preprocessor.preprocess_data(data, options)
        except Exception as e:
            raise DataImportError(f"数据预处理失败: {str(e)}")
    
    def detect_data_type(self, data: DataSource) -> str:
        """
        检测数据类型
        
        Args:
            data: 数据源对象
            
        Returns:
            str: 检测到的主要数据类型
        """
        try:
            df = data.content
            if not isinstance(df, pd.DataFrame):
                return 'unknown'
            
            # 分析各列的数据类型
            type_counts = {
                'numeric': 0,
                'datetime': 0,
                'categorical': 0,
                'boolean': 0,
                'text': 0
            }
            
            for column in df.columns:
                series = df[column].dropna()
                if len(series) == 0:
                    continue
                
                detected_type = self._detect_column_type(series)
                type_counts[detected_type] += 1
            
            # 返回主要的数据类型
            if type_counts['numeric'] > 0:
                if type_counts['datetime'] > 0:
                    return 'time_series'
                else:
                    return 'numeric'
            elif type_counts['datetime'] > 0:
                return 'temporal'
            elif type_counts['categorical'] > 0:
                return 'categorical'
            elif type_counts['text'] > 0:
                return 'text'
            else:
                return 'mixed'
                
        except Exception as e:
            print(f"数据类型检测失败: {str(e)}")
            return 'unknown'
    
    def _detect_column_type(self, series: pd.Series) -> str:
        """
        检测单列的数据类型
        
        Args:
            series: 数据列
            
        Returns:
            str: 检测到的数据类型
        """
        try:
            # 检查数值类型
            if self._is_numeric_type(series):
                return 'numeric'
            
            # 检查日期时间类型
            if self._is_datetime_type(series):
                return 'datetime'
            
            # 检查布尔类型
            if self._is_boolean_type(series):
                return 'boolean'
            
            # 检查分类类型
            if self._is_categorical_type(series):
                return 'categorical'
            
            # 默认为文本类型
            return 'text'
            
        except Exception:
            return 'text'
    
    def _is_numeric_type(self, series: pd.Series) -> bool:
        """检查是否为数值类型"""
        try:
            if series.dtype in ['int64', 'float64', 'int32', 'float32']:
                return True
            
            # 尝试转换为数值
            numeric_series = pd.to_numeric(series, errors='coerce')
            success_rate = numeric_series.notna().sum() / len(series)
            return success_rate > 0.8  # 80%以上可以转换
        except:
            return False
    
    def _is_datetime_type(self, series: pd.Series) -> bool:
        """检查是否为日期时间类型"""
        try:
            if series.dtype in ['datetime64[ns]', 'datetime64']:
                return True
            
            # 尝试转换为日期时间
            datetime_series = pd.to_datetime(series, errors='coerce')
            success_rate = datetime_series.notna().sum() / len(series)
            return success_rate > 0.8  # 80%以上可以转换
        except:
            return False
    
    def _is_boolean_type(self, series: pd.Series) -> bool:
        """检查是否为布尔类型"""
        try:
            if series.dtype == 'bool':
                return True
            
            # 检查是否只包含布尔值
            unique_values = set(series.astype(str).str.lower().unique())
            boolean_values = {'true', 'false', '1', '0', 'yes', 'no', '是', '否'}
            
            return unique_values.issubset(boolean_values)
        except:
            return False
    
    def _is_categorical_type(self, series: pd.Series) -> bool:
        """检查是否为分类类型"""
        try:
            # 唯一值数量相对较少
            unique_ratio = series.nunique() / len(series)
            return unique_ratio < 0.1 and series.nunique() <= 50
        except:
            return False
    
    def _is_text_type(self, series: pd.Series) -> bool:
        """检查是否为文本类型"""
        try:
            return series.dtype == 'object'
        except:
            return True
    
    def _generate_data_id(self) -> str:
        """生成唯一的数据ID"""
        return f"data_{uuid.uuid4().hex[:8]}"
    
    def get_import_summary(self, data: DataSource) -> Dict[str, Any]:
        """
        获取导入摘要信息
        
        Args:
            data: 数据源对象
            
        Returns:
            Dict[str, Any]: 导入摘要信息
        """
        try:
            df = data.content
            summary = {
                'data_id': data.id,
                'format': data.format,
                'shape': df.shape,
                'columns': list(df.columns),
                'data_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'missing_values': df.isnull().sum().to_dict(),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'detected_type': self.detect_data_type(data)
            }
            
            # 添加数值列的统计信息
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 0:
                summary['numeric_summary'] = df[numeric_columns].describe().to_dict()
            
            return summary
            
        except Exception as e:
            raise DataImportError(f"生成导入摘要失败: {str(e)}")
    
    def set_validation_rules(self, rules: Dict[str, Any]) -> None:
        """
        设置数据验证规则
        
        Args:
            rules: 验证规则字典
        """
        self.validator.set_validation_rules(rules)
    
    def get_supported_formats(self) -> Dict[str, str]:
        """
        获取支持的数据格式列表
        
        Returns:
            Dict[str, str]: 支持的格式及其描述
        """
        return SUPPORTED_DATA_FORMATS.copy()
