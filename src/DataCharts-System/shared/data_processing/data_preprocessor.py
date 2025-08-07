"""
数据预处理器

负责数据清洗、标准化、转换等预处理操作
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data_types import DataSource, DataImportError


class DataPreprocessor:
    """数据预处理器类"""
    
    def __init__(self):
        self.scalers = {
            'standard': StandardScaler(),
            'minmax': MinMaxScaler(),
        }
        self.encoders = {}
    
    def preprocess_data(self, data: DataSource, options: Dict[str, Any] = None) -> DataSource:
        """
        预处理数据，清洗和标准化
        
        Args:
            data: 输入数据源
            options: 预处理选项
            
        Returns:
            DataSource: 预处理后的数据源
        """
        if options is None:
            options = {}
        
        try:
            df = data.content.copy()
            
            # 按照指定顺序执行预处理步骤
            if options.get('clean_data', True):
                df = self._clean_data(df, options.get('clean_options', {}))
            
            if options.get('standardize_format', True):
                df = self._standardize_format(df, options.get('format_options', {}))
            
            if options.get('handle_missing', True):
                df = self._handle_missing_values(df, options.get('missing_options', {}))
            
            if options.get('transform_data', False):
                df = self._transform_data(df, options.get('transform_options', {}))
            
            # 创建新的数据源对象
            processed_data = DataSource(
                id=f"{data.id}_processed",
                format=data.format,
                content=df,
                metadata={
                    **data.metadata,
                    'preprocessing': {
                        'timestamp': pd.Timestamp.now().isoformat(),
                        'options': options,
                        'original_shape': data.content.shape,
                        'processed_shape': df.shape
                    }
                }
            )
            
            return processed_data
            
        except Exception as e:
            raise DataImportError(f"数据预处理失败: {str(e)}")
    
    def _clean_data(self, df: pd.DataFrame, options: Dict[str, Any]) -> pd.DataFrame:
        """
        数据清洗
        
        Args:
            df: 输入DataFrame
            options: 清洗选项
            
        Returns:
            pd.DataFrame: 清洗后的DataFrame
        """
        try:
            # 去除重复行
            if options.get('remove_duplicates', True):
                original_len = len(df)
                df = df.drop_duplicates()
                removed_count = original_len - len(df)
                if removed_count > 0:
                    print(f"已移除 {removed_count} 行重复数据")
            
            # 去除完全为空的行
            if options.get('remove_empty_rows', True):
                original_len = len(df)
                df = df.dropna(how='all')
                removed_count = original_len - len(df)
                if removed_count > 0:
                    print(f"已移除 {removed_count} 行完全为空的数据")
            
            # 去除完全为空的列
            if options.get('remove_empty_columns', True):
                original_cols = len(df.columns)
                df = df.dropna(axis=1, how='all')
                removed_count = original_cols - len(df.columns)
                if removed_count > 0:
                    print(f"已移除 {removed_count} 列完全为空的数据")
            
            # 去除异常值
            if options.get('remove_outliers', False):
                df = self._remove_outliers(df, options.get('outlier_method', 'iqr'))
            
            # 清理文本数据
            if options.get('clean_text', True):
                df = self._clean_text_data(df)
            
            return df
            
        except Exception as e:
            raise DataImportError(f"数据清洗失败: {str(e)}")
    
    def _remove_outliers(self, df: pd.DataFrame, method: str = 'iqr') -> pd.DataFrame:
        """
        移除异常值
        
        Args:
            df: 输入DataFrame
            method: 异常值检测方法 ('iqr', 'zscore')
            
        Returns:
            pd.DataFrame: 移除异常值后的DataFrame
        """
        try:
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            for column in numeric_columns:
                if method == 'iqr':
                    Q1 = df[column].quantile(0.25)
                    Q3 = df[column].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outlier_mask = (df[column] < lower_bound) | (df[column] > upper_bound)
                    
                elif method == 'zscore':
                    z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
                    outlier_mask = z_scores > 3
                
                # 记录移除的异常值数量
                outlier_count = outlier_mask.sum()
                if outlier_count > 0:
                    print(f"列 '{column}' 移除了 {outlier_count} 个异常值")
                    # 将异常值设为NaN而不是直接删除行
                    df.loc[outlier_mask, column] = np.nan
            
            return df
            
        except Exception as e:
            raise DataImportError(f"异常值移除失败: {str(e)}")
    
    def _clean_text_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清理文本数据
        
        Args:
            df: 输入DataFrame
            
        Returns:
            pd.DataFrame: 清理后的DataFrame
        """
        try:
            text_columns = df.select_dtypes(include=['object']).columns
            
            for column in text_columns:
                # 去除前后空格
                df[column] = df[column].astype(str).str.strip()
                
                # 将空字符串和'nan'字符串设为NaN
                df[column] = df[column].replace(['', 'nan', 'NaN', 'NULL', 'null'], np.nan)
                
                # 统一大小写（可选）
                # df[column] = df[column].str.lower()
            
            return df
            
        except Exception as e:
            raise DataImportError(f"文本数据清理失败: {str(e)}")
    
    def _standardize_format(self, df: pd.DataFrame, options: Dict[str, Any]) -> pd.DataFrame:
        """
        格式标准化
        
        Args:
            df: 输入DataFrame
            options: 格式化选项
            
        Returns:
            pd.DataFrame: 标准化后的DataFrame
        """
        try:
            # 标准化日期格式
            if options.get('standardize_dates', True):
                df = self._standardize_dates(df)
            
            # 标准化数值格式
            if options.get('standardize_numbers', True):
                df = self._standardize_numbers(df)
            
            # 标准化列名
            if options.get('standardize_columns', True):
                df = self._standardize_column_names(df)
            
            return df
            
        except Exception as e:
            raise DataImportError(f"格式标准化失败: {str(e)}")
    
    def _standardize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化日期格式
        
        Args:
            df: 输入DataFrame
            
        Returns:
            pd.DataFrame: 日期标准化后的DataFrame
        """
        try:
            for column in df.columns:
                if df[column].dtype == 'object':
                    # 尝试转换为日期时间
                    try:
                        sample = df[column].dropna().head(100)
                        if len(sample) > 0:
                            # 检测是否为日期格式
                            converted = pd.to_datetime(sample, errors='coerce')
                            if converted.notna().sum() / len(sample) > 0.8:  # 80%以上可以转换
                                df[column] = pd.to_datetime(df[column], errors='coerce')
                                print(f"列 '{column}' 已转换为日期时间格式")
                    except:
                        pass
            
            return df
            
        except Exception as e:
            raise DataImportError(f"日期格式标准化失败: {str(e)}")
    
    def _standardize_numbers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化数值格式
        
        Args:
            df: 输入DataFrame
            
        Returns:
            pd.DataFrame: 数值标准化后的DataFrame
        """
        try:
            for column in df.columns:
                if df[column].dtype == 'object':
                    # 尝试转换为数值
                    try:
                        # 移除常见的非数值字符
                        cleaned = df[column].astype(str).str.replace(',', '')
                        cleaned = cleaned.str.replace('$', '')
                        cleaned = cleaned.str.replace('%', '')
                        
                        # 尝试转换为数值
                        numeric = pd.to_numeric(cleaned, errors='coerce')
                        
                        # 如果转换成功率高，则替换原列
                        success_rate = numeric.notna().sum() / df[column].notna().sum()
                        if success_rate > 0.8:  # 80%以上可以转换
                            df[column] = numeric
                            print(f"列 '{column}' 已转换为数值格式")
                    except:
                        pass
            
            return df
            
        except Exception as e:
            raise DataImportError(f"数值格式标准化失败: {str(e)}")
    
    def _standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化列名
        
        Args:
            df: 输入DataFrame
            
        Returns:
            pd.DataFrame: 列名标准化后的DataFrame
        """
        try:
            # 清理列名
            new_columns = []
            for col in df.columns:
                # 转换为字符串并去除前后空格
                clean_col = str(col).strip()
                
                # 替换特殊字符
                clean_col = clean_col.replace(' ', '_')
                clean_col = clean_col.replace('-', '_')
                clean_col = clean_col.replace('.', '_')
                
                # 移除重复的下划线
                clean_col = '_'.join(filter(None, clean_col.split('_')))
                
                new_columns.append(clean_col)
            
            df.columns = new_columns
            
            return df
            
        except Exception as e:
            raise DataImportError(f"列名标准化失败: {str(e)}")
    
    def _handle_missing_values(self, df: pd.DataFrame, options: Dict[str, Any]) -> pd.DataFrame:
        """
        处理缺失值
        
        Args:
            df: 输入DataFrame
            options: 缺失值处理选项
            
        Returns:
            pd.DataFrame: 处理缺失值后的DataFrame
        """
        try:
            strategy = options.get('strategy', 'auto')
            
            for column in df.columns:
                null_count = df[column].isnull().sum()
                if null_count == 0:
                    continue
                
                null_ratio = null_count / len(df)
                print(f"列 '{column}' 缺失值比例: {null_ratio:.2%}")
                
                if strategy == 'auto':
                    # 自动选择策略
                    if null_ratio > 0.5:
                        # 缺失值过多，删除列
                        print(f"删除缺失值过多的列: {column}")
                        df = df.drop(columns=[column])
                        continue
                    elif df[column].dtype in ['int64', 'float64']:
                        # 数值列用均值填充
                        df[column] = df[column].fillna(df[column].mean())
                    else:
                        # 分类列用众数填充
                        mode_value = df[column].mode()
                        if len(mode_value) > 0:
                            df[column] = df[column].fillna(mode_value[0])
                        else:
                            df[column] = df[column].fillna('Unknown')
                
                elif strategy == 'drop':
                    # 删除含有缺失值的行
                    df = df.dropna(subset=[column])
                
                elif strategy == 'fill':
                    # 使用指定值填充
                    fill_value = options.get('fill_value', 0)
                    df[column] = df[column].fillna(fill_value)
                
                elif strategy == 'interpolate':
                    # 插值填充（仅适用于数值列）
                    if df[column].dtype in ['int64', 'float64']:
                        df[column] = df[column].interpolate()
            
            return df
            
        except Exception as e:
            raise DataImportError(f"缺失值处理失败: {str(e)}")
    
    def _transform_data(self, df: pd.DataFrame, options: Dict[str, Any]) -> pd.DataFrame:
        """
        数据转换
        
        Args:
            df: 输入DataFrame
            options: 转换选项
            
        Returns:
            pd.DataFrame: 转换后的DataFrame
        """
        try:
            # 数值标准化
            if options.get('normalize', False):
                scaler_type = options.get('scaler', 'standard')
                df = self._normalize_data(df, scaler_type)
            
            # 分类编码
            if options.get('encode_categorical', False):
                df = self._encode_categorical(df)
            
            # 数据类型转换
            if options.get('convert_types', True):
                df = self._convert_data_types(df)
            
            return df
            
        except Exception as e:
            raise DataImportError(f"数据转换失败: {str(e)}")
    
    def _normalize_data(self, df: pd.DataFrame, scaler_type: str) -> pd.DataFrame:
        """
        数值标准化
        
        Args:
            df: 输入DataFrame
            scaler_type: 标准化类型 ('standard', 'minmax')
            
        Returns:
            pd.DataFrame: 标准化后的DataFrame
        """
        try:
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_columns) == 0:
                return df
            
            scaler = self.scalers.get(scaler_type, StandardScaler())
            df[numeric_columns] = scaler.fit_transform(df[numeric_columns])
            
            print(f"已对 {len(numeric_columns)} 列数值进行 {scaler_type} 标准化")
            
            return df
            
        except Exception as e:
            raise DataImportError(f"数值标准化失败: {str(e)}")
    
    def _encode_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        分类数据编码
        
        Args:
            df: 输入DataFrame
            
        Returns:
            pd.DataFrame: 编码后的DataFrame
        """
        try:
            categorical_columns = df.select_dtypes(include=['object']).columns
            
            for column in categorical_columns:
                if df[column].nunique() <= 50:  # 只对类别数量不超过50的列进行编码
                    encoder = LabelEncoder()
                    df[column + '_encoded'] = encoder.fit_transform(df[column].astype(str))
                    self.encoders[column] = encoder
                    print(f"列 '{column}' 已进行标签编码")
            
            return df
            
        except Exception as e:
            raise DataImportError(f"分类编码失败: {str(e)}")
    
    def _convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        数据类型转换优化
        
        Args:
            df: 输入DataFrame
            
        Returns:
            pd.DataFrame: 类型优化后的DataFrame
        """
        try:
            # 优化整数类型
            int_columns = df.select_dtypes(include=['int64']).columns
            for column in int_columns:
                max_val = df[column].max()
                min_val = df[column].min()
                
                if min_val >= 0:
                    if max_val <= 255:
                        df[column] = df[column].astype('uint8')
                    elif max_val <= 65535:
                        df[column] = df[column].astype('uint16')
                    elif max_val <= 4294967295:
                        df[column] = df[column].astype('uint32')
                else:
                    if min_val >= -128 and max_val <= 127:
                        df[column] = df[column].astype('int8')
                    elif min_val >= -32768 and max_val <= 32767:
                        df[column] = df[column].astype('int16')
                    elif min_val >= -2147483648 and max_val <= 2147483647:
                        df[column] = df[column].astype('int32')
            
            # 优化浮点类型
            float_columns = df.select_dtypes(include=['float64']).columns
            for column in float_columns:
                df[column] = pd.to_numeric(df[column], downcast='float')
            
            return df
            
        except Exception as e:
            raise DataImportError(f"数据类型转换失败: {str(e)}")
    
    def get_preprocessing_report(self, original_data: DataSource, processed_data: DataSource) -> Dict[str, Any]:
        """
        生成预处理报告
        
        Args:
            original_data: 原始数据源
            processed_data: 处理后数据源
            
        Returns:
            Dict[str, Any]: 预处理报告
        """
        try:
            original_df = original_data.content
            processed_df = processed_data.content
            
            report = {
                'original_shape': original_df.shape,
                'processed_shape': processed_df.shape,
                'changes': {
                    'rows_removed': original_df.shape[0] - processed_df.shape[0],
                    'columns_removed': original_df.shape[1] - processed_df.shape[1]
                },
                'data_quality': {
                    'original_missing_ratio': original_df.isnull().sum().sum() / original_df.size,
                    'processed_missing_ratio': processed_df.isnull().sum().sum() / processed_df.size
                }
            }
            
            return report
            
        except Exception as e:
            raise DataImportError(f"生成预处理报告失败: {str(e)}")
