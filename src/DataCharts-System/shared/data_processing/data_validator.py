"""
数据验证器

负责验证数据的完整性、一致性和有效性
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data_types import DataSource, DataImportError


class DataValidator:
    """数据验证器类"""
    
    def __init__(self):
        self.validation_rules = {
            'min_rows': 1,
            'max_rows': 1000000,
            'min_columns': 1,
            'max_columns': 1000,
            'max_null_ratio': 0.5  # 最大空值比例
        }
    
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
            # 获取数据内容
            df = data.content
            if not isinstance(df, pd.DataFrame):
                raise DataImportError("数据内容必须是pandas DataFrame格式")
            
            # 执行各项验证
            validation_results = [
                self._validate_structure(df),
                self._validate_data_types(df),
                self._validate_ranges(df),
                self._validate_completeness(df),
                self._validate_consistency(df)
            ]
            
            # 所有验证都必须通过
            if not all(validation_results):
                raise DataImportError("数据验证失败")
            
            return True
            
        except Exception as e:
            if isinstance(e, DataImportError):
                raise
            else:
                raise DataImportError(f"数据验证过程中发生错误: {str(e)}")
    
    def _validate_structure(self, df: pd.DataFrame) -> bool:
        """
        验证数据结构
        
        Args:
            df: 数据DataFrame
            
        Returns:
            bool: 结构验证是否通过
        """
        try:
            # 检查行数
            if len(df) < self.validation_rules['min_rows']:
                raise DataImportError(f"数据行数太少，至少需要{self.validation_rules['min_rows']}行")
            
            if len(df) > self.validation_rules['max_rows']:
                raise DataImportError(f"数据行数太多，最多支持{self.validation_rules['max_rows']}行")
            
            # 检查列数
            if len(df.columns) < self.validation_rules['min_columns']:
                raise DataImportError(f"数据列数太少，至少需要{self.validation_rules['min_columns']}列")
            
            if len(df.columns) > self.validation_rules['max_columns']:
                raise DataImportError(f"数据列数太多，最多支持{self.validation_rules['max_columns']}列")
            
            # 检查列名是否重复
            if len(df.columns) != len(set(df.columns)):
                duplicate_columns = df.columns[df.columns.duplicated()].tolist()
                raise DataImportError(f"发现重复的列名: {duplicate_columns}")
            
            return True
            
        except DataImportError:
            raise
        except Exception as e:
            raise DataImportError(f"结构验证失败: {str(e)}")
    
    def _validate_data_types(self, df: pd.DataFrame) -> bool:
        """
        验证数据类型
        
        Args:
            df: 数据DataFrame
            
        Returns:
            bool: 类型验证是否通过
        """
        try:
            # 检查每列的数据类型一致性
            for column in df.columns:
                series = df[column].dropna()  # 忽略空值
                if len(series) == 0:
                    continue
                
                # 检查是否存在混合类型
                if series.dtype == 'object':
                    # 尝试推断更具体的类型
                    inferred_type = pd.api.types.infer_dtype(series)
                    if inferred_type == 'mixed':
                        # 允许一定比例的混合类型，但要警告
                        print(f"警告: 列 '{column}' 包含混合数据类型")
            
            return True
            
        except Exception as e:
            raise DataImportError(f"数据类型验证失败: {str(e)}")
    
    def _validate_ranges(self, df: pd.DataFrame) -> bool:
        """
        验证数值范围
        
        Args:
            df: 数据DataFrame
            
        Returns:
            bool: 范围验证是否通过
        """
        try:
            # 检查数值列的范围
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            for column in numeric_columns:
                series = df[column].dropna()
                if len(series) == 0:
                    continue
                
                # 检查是否存在无穷大或NaN
                if np.isinf(series).any():
                    raise DataImportError(f"列 '{column}' 包含无穷大值")
                
                # 检查数值范围是否合理
                min_val = series.min()
                max_val = series.max()
                
                # 检查异常值（使用四分位数方法）
                q1 = series.quantile(0.25)
                q3 = series.quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                outliers = series[(series < lower_bound) | (series > upper_bound)]
                if len(outliers) > len(series) * 0.1:  # 异常值超过10%
                    print(f"警告: 列 '{column}' 包含大量异常值 ({len(outliers)} / {len(series)})")
            
            return True
            
        except DataImportError:
            raise
        except Exception as e:
            raise DataImportError(f"数值范围验证失败: {str(e)}")
    
    def _validate_completeness(self, df: pd.DataFrame) -> bool:
        """
        验证数据完整性
        
        Args:
            df: 数据DataFrame
            
        Returns:
            bool: 完整性验证是否通过
        """
        try:
            # 检查空值比例
            for column in df.columns:
                null_ratio = df[column].isnull().sum() / len(df)
                if null_ratio > self.validation_rules['max_null_ratio']:
                    raise DataImportError(
                        f"列 '{column}' 的空值比例过高 ({null_ratio:.2%}), "
                        f"超过了最大允许比例 ({self.validation_rules['max_null_ratio']:.2%})"
                    )
            
            # 检查是否有完全为空的行
            empty_rows = df.isnull().all(axis=1).sum()
            if empty_rows > 0:
                print(f"警告: 发现 {empty_rows} 行完全为空")
            
            return True
            
        except DataImportError:
            raise
        except Exception as e:
            raise DataImportError(f"完整性验证失败: {str(e)}")
    
    def _validate_consistency(self, df: pd.DataFrame) -> bool:
        """
        验证数据一致性
        
        Args:
            df: 数据DataFrame
            
        Returns:
            bool: 一致性验证是否通过
        """
        try:
            # 检查日期列的一致性
            for column in df.columns:
                if df[column].dtype == 'object':
                    # 尝试检测日期格式
                    sample_values = df[column].dropna().head(100)
                    if len(sample_values) > 0:
                        try:
                            pd.to_datetime(sample_values)
                            # 如果成功转换，检查日期范围是否合理
                            dates = pd.to_datetime(df[column], errors='coerce')
                            if dates.notna().any():
                                min_date = dates.min()
                                max_date = dates.max()
                                current_year = pd.Timestamp.now().year
                                
                                if min_date.year < 1900 or max_date.year > current_year + 10:
                                    print(f"警告: 列 '{column}' 的日期范围可能不合理 ({min_date} - {max_date})")
                        except:
                            pass
            
            return True
            
        except Exception as e:
            raise DataImportError(f"一致性验证失败: {str(e)}")
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        获取数据摘要信息
        
        Args:
            df: 数据DataFrame
            
        Returns:
            Dict[str, Any]: 数据摘要信息
        """
        try:
            summary = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'column_info': {},
                'missing_values': {},
                'data_types': {}
            }
            
            for column in df.columns:
                series = df[column]
                summary['column_info'][column] = {
                    'dtype': str(series.dtype),
                    'non_null_count': series.count(),
                    'null_count': series.isnull().sum(),
                    'unique_count': series.nunique()
                }
                
                if series.dtype in ['int64', 'float64']:
                    summary['column_info'][column].update({
                        'min': float(series.min()) if series.count() > 0 else None,
                        'max': float(series.max()) if series.count() > 0 else None,
                        'mean': float(series.mean()) if series.count() > 0 else None,
                        'std': float(series.std()) if series.count() > 0 else None
                    })
                
                summary['missing_values'][column] = series.isnull().sum()
                summary['data_types'][column] = str(series.dtype)
            
            return summary
            
        except Exception as e:
            raise DataImportError(f"生成数据摘要失败: {str(e)}")
    
    def validate_file_size(self, file_path: str, max_size_mb: int = 100) -> bool:
        """
        验证文件大小
        
        Args:
            file_path: 文件路径
            max_size_mb: 最大文件大小（MB）
            
        Returns:
            bool: 验证是否通过
        """
        try:
            import os
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            
            if file_size_mb > max_size_mb:
                raise DataImportError(f"文件大小 ({file_size_mb:.2f}MB) 超过限制 ({max_size_mb}MB)")
            
            return True
            
        except DataImportError:
            raise
        except Exception as e:
            raise DataImportError(f"文件大小验证失败: {str(e)}")
    
    def set_validation_rules(self, rules: Dict[str, Any]) -> None:
        """
        设置验证规则
        
        Args:
            rules: 验证规则字典
        """
        self.validation_rules.update(rules)
