"""
数据格式解析器

支持CSV、Excel、JSON、TXT等格式的数据解析
"""

import pandas as pd
import json
import chardet
from typing import Dict, Any, Optional
from pathlib import Path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data_types import DataSource, DataImportError


class BaseParser:
    """基础解析器类"""
    
    def __init__(self):
        self.supported_encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']
    
    def detect_encoding(self, file_path: str) -> str:
        """
        检测文件编码
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 检测到的编码格式
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # 读取前10KB进行检测
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                if encoding and result['confidence'] > 0.7:
                    return encoding.lower()
                else:
                    return 'utf-8'  # 默认使用UTF-8
        except Exception as e:
            raise DataImportError(f"编码检测失败: {str(e)}")
    
    def parse(self, file_path: str, options: Dict[str, Any]) -> pd.DataFrame:
        """
        解析文件，子类需要实现此方法
        
        Args:
            file_path: 文件路径
            options: 解析选项
            
        Returns:
            pd.DataFrame: 解析后的数据
        """
        raise NotImplementedError("子类必须实现parse方法")


class CSVParser(BaseParser):
    """CSV文件解析器"""
    
    def parse(self, file_path: str, options: Dict[str, Any]) -> pd.DataFrame:
        """
        解析CSV文件
        
        Args:
            file_path: CSV文件路径
            options: 解析选项，包含separator、header等
            
        Returns:
            pd.DataFrame: 解析后的数据
        """
        try:
            encoding = options.get('encoding') or self.detect_encoding(file_path)
            separator = options.get('separator', ',')
            header = options.get('header', 0)
            
            # 尝试解析CSV文件
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                sep=separator,
                header=header,
                on_bad_lines='skip'  # 跳过有问题的行
            )
            
            if df.empty:
                raise DataImportError("CSV文件为空或格式不正确")
            
            return df
            
        except UnicodeDecodeError:
            # 如果编码检测失败，尝试其他编码
            for encoding in self.supported_encodings:
                try:
                    df = pd.read_csv(
                        file_path,
                        encoding=encoding,
                        sep=separator,
                        header=header,
                        on_bad_lines='skip'
                    )
                    return df
                except UnicodeDecodeError:
                    continue
            raise DataImportError("无法确定CSV文件的正确编码格式")
            
        except Exception as e:
            raise DataImportError(f"CSV文件解析失败: {str(e)}")


class ExcelParser(BaseParser):
    """Excel文件解析器"""
    
    def parse(self, file_path: str, options: Dict[str, Any]) -> pd.DataFrame:
        """
        解析Excel文件
        
        Args:
            file_path: Excel文件路径
            options: 解析选项，包含sheet_name、header等
            
        Returns:
            pd.DataFrame: 解析后的数据
        """
        try:
            sheet_name = options.get('sheet_name', 0)  # 默认第一个工作表
            header = options.get('header', 0)
            
            # 检查文件扩展名
            file_extension = Path(file_path).suffix.lower()
            if file_extension not in ['.xlsx', '.xls']:
                raise DataImportError(f"不支持的Excel文件格式: {file_extension}")
            
            # 解析Excel文件
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                header=header,
                engine='openpyxl' if file_extension == '.xlsx' else 'xlrd'
            )
            
            if df.empty:
                raise DataImportError("Excel文件为空或指定的工作表不存在")
            
            return df
            
        except Exception as e:
            raise DataImportError(f"Excel文件解析失败: {str(e)}")


class JSONParser(BaseParser):
    """JSON文件解析器"""
    
    def parse(self, file_path: str, options: Dict[str, Any]) -> pd.DataFrame:
        """
        解析JSON文件
        
        Args:
            file_path: JSON文件路径
            options: 解析选项，包含orient等
            
        Returns:
            pd.DataFrame: 解析后的数据
        """
        try:
            encoding = options.get('encoding') or self.detect_encoding(file_path)
            orient = options.get('orient', 'records')  # 默认格式
            
            # 读取JSON文件
            with open(file_path, 'r', encoding=encoding) as f:
                json_data = json.load(f)
            
            # 根据JSON结构转换为DataFrame
            if isinstance(json_data, list):
                if orient == 'records':
                    df = pd.DataFrame(json_data)
                else:
                    df = pd.json_normalize(json_data)
            elif isinstance(json_data, dict):
                if orient == 'index':
                    df = pd.DataFrame.from_dict(json_data, orient='index')
                elif orient == 'columns':
                    df = pd.DataFrame.from_dict(json_data, orient='columns')
                else:
                    df = pd.json_normalize(json_data)
            else:
                raise DataImportError("不支持的JSON数据结构")
            
            if df.empty:
                raise DataImportError("JSON文件为空或数据结构不正确")
            
            return df
            
        except json.JSONDecodeError as e:
            raise DataImportError(f"JSON格式错误: {str(e)}")
        except Exception as e:
            raise DataImportError(f"JSON文件解析失败: {str(e)}")


class TXTParser(BaseParser):
    """文本文件解析器"""
    
    def parse(self, file_path: str, options: Dict[str, Any]) -> pd.DataFrame:
        """
        解析文本文件
        
        Args:
            file_path: 文本文件路径
            options: 解析选项，包含delimiter、header等
            
        Returns:
            pd.DataFrame: 解析后的数据
        """
        try:
            encoding = options.get('encoding') or self.detect_encoding(file_path)
            delimiter = options.get('delimiter', '\t')  # 默认制表符分隔
            header = options.get('header', None)
            
            # 尝试解析文本文件
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                sep=delimiter,
                header=header,
                on_bad_lines='skip'
            )
            
            # 如果没有指定header，使用数字列名
            if header is None:
                df.columns = [f'Column_{i+1}' for i in range(len(df.columns))]
            
            if df.empty:
                raise DataImportError("文本文件为空或格式不正确")
            
            return df
            
        except Exception as e:
            raise DataImportError(f"文本文件解析失败: {str(e)}")


class ManualParser:
    """手动输入数据解析器"""
    
    @staticmethod
    def parse_manual_data(data: Any, options: Dict[str, Any]) -> pd.DataFrame:
        """
        解析手动输入的数据
        
        Args:
            data: 手动输入的数据
            options: 解析选项
            
        Returns:
            pd.DataFrame: 解析后的数据
        """
        try:
            if isinstance(data, str):
                # 解析文本格式的数据
                lines = data.strip().split('\n')
                rows = []
                for line in lines:
                    if ',' in line:
                        rows.append(line.split(','))
                    elif '\t' in line:
                        rows.append(line.split('\t'))
                    else:
                        rows.append([line])
                
                df = pd.DataFrame(rows)
                
            elif isinstance(data, (list, tuple)):
                # 解析列表或元组数据
                df = pd.DataFrame(data)
                
            elif isinstance(data, dict):
                # 解析字典数据
                df = pd.DataFrame.from_dict(data)
                
            else:
                raise DataImportError("不支持的手动输入数据类型")
            
            if df.empty:
                raise DataImportError("手动输入的数据为空")
            
            return df
            
        except Exception as e:
            raise DataImportError(f"手动数据解析失败: {str(e)}")


def get_parser(format_type: str) -> BaseParser:
    """
    根据格式类型获取对应的解析器
    
    Args:
        format_type: 数据格式类型
        
    Returns:
        BaseParser: 对应的解析器实例
    """
    parsers = {
        'csv': CSVParser(),
        'excel': ExcelParser(),
        'json': JSONParser(),
        'txt': TXTParser()
    }
    
    parser = parsers.get(format_type.lower())
    if not parser:
        raise DataImportError(f"不支持的数据格式: {format_type}")
    
    return parser
