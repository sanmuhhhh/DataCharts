"""
数据服务层

提供数据导入、处理、验证等服务功能
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import tempfile
import shutil

import sys
import os

# 添加共享模块路径
current_dir = os.path.dirname(os.path.abspath(__file__))
shared_dir = os.path.join(current_dir, '..', '..', '..', 'shared')
sys.path.insert(0, os.path.abspath(shared_dir))

try:
    from interfaces import DataImporter
    from data_types import DataSource, DataImportError
except ImportError as e:
    raise ImportError(f"无法导入共享模块: {e}. 请确保shared目录存在且包含正确的模块。")


class DataService:
    """数据服务类"""
    
    def __init__(self):
        self.data_importer = DataImporter()
        self.data_storage: Dict[str, DataSource] = {}
        self.temp_dir = Path(tempfile.gettempdir()) / "datacharts_temp"
        self.temp_dir.mkdir(exist_ok=True)
    
    async def import_file_data(self, file_path: str, format: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        导入文件数据
        
        Args:
            file_path: 文件路径
            format: 数据格式
            options: 导入选项
            
        Returns:
            Dict[str, Any]: 导入结果
        """
        try:
            if options is None:
                options = {}
            
            # 导入数据
            data_source = self.data_importer.import_data(file_path, format, options)
            
            # 验证数据
            validation_passed = self.data_importer.validate_data(data_source)
            
            # 存储数据
            self.data_storage[data_source.id] = data_source
            
            # 获取导入摘要
            summary = self.data_importer.get_import_summary(data_source)
            
            return {
                'success': True,
                'data_id': data_source.id,
                'validation_passed': validation_passed,
                'summary': summary,
                'message': f"成功导入数据文件: {Path(file_path).name}"
            }
            
        except DataImportError as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'DataImportError'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"导入过程中发生未知错误: {str(e)}",
                'error_type': 'UnknownError'
            }
    
    async def import_manual_data(self, data: Any, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        导入手动输入数据
        
        Args:
            data: 手动输入的数据
            options: 导入选项
            
        Returns:
            Dict[str, Any]: 导入结果
        """
        try:
            if options is None:
                options = {}
            
            # 设置手动数据选项
            options['data'] = data
            
            # 导入数据
            data_source = self.data_importer.import_data("", "manual", options)
            
            # 验证数据
            validation_passed = self.data_importer.validate_data(data_source)
            
            # 存储数据
            self.data_storage[data_source.id] = data_source
            
            # 获取导入摘要
            summary = self.data_importer.get_import_summary(data_source)
            
            return {
                'success': True,
                'data_id': data_source.id,
                'validation_passed': validation_passed,
                'summary': summary,
                'message': "成功导入手动输入数据"
            }
            
        except DataImportError as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'DataImportError'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"导入过程中发生未知错误: {str(e)}",
                'error_type': 'UnknownError'
            }
    
    async def process_data(self, data_id: str, process_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        预处理数据
        
        Args:
            data_id: 数据ID
            process_options: 处理选项
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        try:
            if data_id not in self.data_storage:
                return {
                    'success': False,
                    'error': f"数据ID不存在: {data_id}",
                    'error_type': 'DataNotFoundError'
                }
            
            if process_options is None:
                process_options = {}
            
            # 获取原始数据
            original_data = self.data_storage[data_id]
            
            # 预处理数据
            processed_data = self.data_importer.preprocess_data(original_data, process_options)
            
            # 存储处理后的数据
            self.data_storage[processed_data.id] = processed_data
            
            # 生成处理报告
            try:
                from data_processing.data_preprocessor import DataPreprocessor
            except ImportError:
                # 如果无法导入，使用占位符
                class DataPreprocessor:
                    def get_preprocessing_report(self, original_data, processed_data):
                        return {"message": "预处理报告功能暂不可用"}
            preprocessor = DataPreprocessor()
            report = preprocessor.get_preprocessing_report(original_data, processed_data)
            
            return {
                'success': True,
                'original_data_id': data_id,
                'processed_data_id': processed_data.id,
                'report': report,
                'message': "数据预处理完成"
            }
            
        except DataImportError as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'DataImportError'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"处理过程中发生未知错误: {str(e)}",
                'error_type': 'UnknownError'
            }
    
    async def validate_data(self, data_id: str) -> Dict[str, Any]:
        """
        验证数据
        
        Args:
            data_id: 数据ID
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        try:
            if data_id not in self.data_storage:
                return {
                    'success': False,
                    'error': f"数据ID不存在: {data_id}",
                    'error_type': 'DataNotFoundError'
                }
            
            data_source = self.data_storage[data_id]
            
            # 执行验证
            validation_passed = self.data_importer.validate_data(data_source)
            
            # 获取数据摘要
            try:
                from data_processing.data_validator import DataValidator
            except ImportError:
                # 如果无法导入，使用占位符
                class DataValidator:
                    def get_data_summary(self, df):
                        return {"message": "数据摘要功能暂不可用"}
            validator = DataValidator()
            summary = validator.get_data_summary(data_source.content)
            
            return {
                'success': True,
                'validation_passed': validation_passed,
                'data_id': data_id,
                'summary': summary,
                'message': "数据验证完成"
            }
            
        except DataImportError as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'DataImportError'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"验证过程中发生未知错误: {str(e)}",
                'error_type': 'UnknownError'
            }
    
    async def get_data_info(self, data_id: str) -> Dict[str, Any]:
        """
        获取数据信息
        
        Args:
            data_id: 数据ID
            
        Returns:
            Dict[str, Any]: 数据信息
        """
        try:
            if data_id not in self.data_storage:
                return {
                    'success': False,
                    'error': f"数据ID不存在: {data_id}",
                    'error_type': 'DataNotFoundError'
                }
            
            data_source = self.data_storage[data_id]
            
            # 获取数据类型
            detected_type = self.data_importer.detect_data_type(data_source)
            
            # 获取详细摘要
            summary = self.data_importer.get_import_summary(data_source)
            
            return {
                'success': True,
                'data_id': data_id,
                'detected_type': detected_type,
                'summary': summary,
                'metadata': data_source.metadata
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"获取数据信息失败: {str(e)}",
                'error_type': 'UnknownError'
            }
    
    async def get_data_preview(self, data_id: str, rows: int = 10) -> Dict[str, Any]:
        """
        获取数据预览
        
        Args:
            data_id: 数据ID
            rows: 预览行数
            
        Returns:
            Dict[str, Any]: 数据预览
        """
        try:
            if data_id not in self.data_storage:
                return {
                    'success': False,
                    'error': f"数据ID不存在: {data_id}",
                    'error_type': 'DataNotFoundError'
                }
            
            data_source = self.data_storage[data_id]
            df = data_source.content
            
            # 获取预览数据
            preview_data = {
                'head': df.head(rows).to_dict('records'),
                'tail': df.tail(rows).to_dict('records'),
                'columns': list(df.columns),
                'shape': df.shape,
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
            }
            
            return {
                'success': True,
                'data_id': data_id,
                'preview': preview_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"获取数据预览失败: {str(e)}",
                'error_type': 'UnknownError'
            }
    
    async def list_data_sources(self) -> Dict[str, Any]:
        """
        列出所有数据源
        
        Returns:
            Dict[str, Any]: 数据源列表
        """
        try:
            data_list = []
            
            for data_id, data_source in self.data_storage.items():
                data_info = {
                    'data_id': data_id,
                    'format': data_source.format,
                    'shape': data_source.content.shape,
                    'columns': list(data_source.content.columns),
                    'import_time': data_source.metadata.get('import_time'),
                    'detected_type': self.data_importer.detect_data_type(data_source)
                }
                data_list.append(data_info)
            
            return {
                'success': True,
                'count': len(data_list),
                'data_sources': data_list
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"获取数据源列表失败: {str(e)}",
                'error_type': 'UnknownError'
            }
    
    async def delete_data_source(self, data_id: str) -> Dict[str, Any]:
        """
        删除数据源
        
        Args:
            data_id: 数据ID
            
        Returns:
            Dict[str, Any]: 删除结果
        """
        try:
            if data_id not in self.data_storage:
                return {
                    'success': False,
                    'error': f"数据ID不存在: {data_id}",
                    'error_type': 'DataNotFoundError'
                }
            
            # 删除数据
            del self.data_storage[data_id]
            
            return {
                'success': True,
                'data_id': data_id,
                'message': "数据源已删除"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"删除数据源失败: {str(e)}",
                'error_type': 'UnknownError'
            }
    
    def get_data_source(self, data_id: str) -> Optional[DataSource]:
        """
        获取数据源对象
        
        Args:
            data_id: 数据ID
            
        Returns:
            Optional[DataSource]: 数据源对象，如果不存在则返回None
        """
        return self.data_storage.get(data_id)
    
    def save_temp_file(self, file_content: bytes, filename: str) -> str:
        """
        保存临时文件
        
        Args:
            file_content: 文件内容
            filename: 文件名
            
        Returns:
            str: 临时文件路径
        """
        temp_file_path = self.temp_dir / filename
        
        with open(temp_file_path, 'wb') as f:
            f.write(file_content)
        
        return str(temp_file_path)
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                self.temp_dir.mkdir(exist_ok=True)
        except Exception as e:
            print(f"清理临时文件失败: {str(e)}")
    
    def get_supported_formats(self) -> Dict[str, str]:
        """
        获取支持的数据格式
        
        Returns:
            Dict[str, str]: 支持的格式列表
        """
        return self.data_importer.get_supported_formats()
