"""
文件服务层

提供文件上传、下载、管理等服务功能
"""

import os
import shutil
from typing import Dict, Any, List, Optional
from pathlib import Path
import tempfile
from datetime import datetime
import hashlib
import mimetypes


class FileService:
    """文件服务类"""
    
    def __init__(self, upload_dir: str = None):
        self.upload_dir = Path(upload_dir) if upload_dir else Path(tempfile.gettempdir()) / "datacharts_uploads"
        self.upload_dir.mkdir(exist_ok=True)
        
        # 支持的文件类型
        self.supported_types = {
            '.csv': 'text/csv',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.json': 'application/json',
            '.txt': 'text/plain'
        }
        
        # 最大文件大小 (100MB)
        self.max_file_size = 100 * 1024 * 1024
    
    async def save_uploaded_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        保存上传的文件
        
        Args:
            file_content: 文件内容
            filename: 文件名
            
        Returns:
            Dict[str, Any]: 保存结果
        """
        try:
            # 验证文件名
            if not filename or filename.strip() == "":
                return {
                    'success': False,
                    'error': '文件名不能为空',
                    'error_type': 'InvalidFileName'
                }
            
            # 验证文件扩展名
            file_extension = Path(filename).suffix.lower()
            if file_extension not in self.supported_types:
                return {
                    'success': False,
                    'error': f'不支持的文件类型: {file_extension}',
                    'error_type': 'UnsupportedFileType',
                    'supported_types': list(self.supported_types.keys())
                }
            
            # 验证文件大小
            if len(file_content) > self.max_file_size:
                return {
                    'success': False,
                    'error': f'文件大小超过限制 ({len(file_content)} bytes > {self.max_file_size} bytes)',
                    'error_type': 'FileSizeExceeded'
                }
            
            # 生成唯一文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_hash = hashlib.md5(file_content).hexdigest()[:8]
            safe_filename = self._sanitize_filename(filename)
            unique_filename = f"{timestamp}_{file_hash}_{safe_filename}"
            
            # 保存文件
            file_path = self.upload_dir / unique_filename
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # 获取文件信息
            file_info = {
                'original_filename': filename,
                'saved_filename': unique_filename,
                'file_path': str(file_path),
                'file_size': len(file_content),
                'file_type': file_extension,
                'mime_type': self.supported_types[file_extension],
                'upload_time': datetime.now().isoformat(),
                'file_hash': file_hash
            }
            
            return {
                'success': True,
                'file_info': file_info,
                'message': f'文件保存成功: {filename}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'文件保存失败: {str(e)}',
                'error_type': 'FileSaveError'
            }
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名，移除不安全字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            str: 清理后的文件名
        """
        # 移除路径分隔符和其他不安全字符
        unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        safe_filename = filename
        
        for char in unsafe_chars:
            safe_filename = safe_filename.replace(char, '_')
        
        # 移除连续的下划线和前后空格
        safe_filename = '_'.join(filter(None, safe_filename.split('_')))
        safe_filename = safe_filename.strip()
        
        # 确保文件名不为空
        if not safe_filename:
            safe_filename = "unnamed_file"
        
        return safe_filename
    
    async def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict[str, Any]: 文件信息
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return {
                    'success': False,
                    'error': '文件不存在',
                    'error_type': 'FileNotFound'
                }
            
            stat = path.stat()
            mime_type, _ = mimetypes.guess_type(str(path))
            
            file_info = {
                'filename': path.name,
                'file_path': str(path),
                'file_size': stat.st_size,
                'file_type': path.suffix.lower(),
                'mime_type': mime_type,
                'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'is_readable': os.access(path, os.R_OK),
                'is_writable': os.access(path, os.W_OK)
            }
            
            return {
                'success': True,
                'file_info': file_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'获取文件信息失败: {str(e)}',
                'error_type': 'FileInfoError'
            }
    
    async def delete_file(self, file_path: str) -> Dict[str, Any]:
        """
        删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict[str, Any]: 删除结果
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return {
                    'success': False,
                    'error': '文件不存在',
                    'error_type': 'FileNotFound'
                }
            
            # 检查文件是否在上传目录中（安全检查）
            if not str(path.resolve()).startswith(str(self.upload_dir.resolve())):
                return {
                    'success': False,
                    'error': '无权限删除此文件',
                    'error_type': 'PermissionDenied'
                }
            
            # 删除文件
            path.unlink()
            
            return {
                'success': True,
                'message': f'文件删除成功: {path.name}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'文件删除失败: {str(e)}',
                'error_type': 'FileDeletionError'
            }
    
    async def list_uploaded_files(self) -> Dict[str, Any]:
        """
        列出所有上传的文件
        
        Returns:
            Dict[str, Any]: 文件列表
        """
        try:
            files = []
            
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    file_info = {
                        'filename': file_path.name,
                        'file_path': str(file_path),
                        'file_size': stat.st_size,
                        'file_type': file_path.suffix.lower(),
                        'upload_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    }
                    files.append(file_info)
            
            # 按上传时间排序
            files.sort(key=lambda x: x['upload_time'], reverse=True)
            
            return {
                'success': True,
                'count': len(files),
                'files': files
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'获取文件列表失败: {str(e)}',
                'error_type': 'FileListError'
            }
    
    async def cleanup_old_files(self, days: int = 7) -> Dict[str, Any]:
        """
        清理旧文件
        
        Args:
            days: 保留天数
            
        Returns:
            Dict[str, Any]: 清理结果
        """
        try:
            import time
            cutoff_time = time.time() - (days * 24 * 60 * 60)
            
            deleted_files = []
            total_size_freed = 0
            
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    if stat.st_mtime < cutoff_time:
                        file_size = stat.st_size
                        file_path.unlink()
                        deleted_files.append({
                            'filename': file_path.name,
                            'size': file_size,
                            'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
                        total_size_freed += file_size
            
            return {
                'success': True,
                'deleted_count': len(deleted_files),
                'total_size_freed': total_size_freed,
                'deleted_files': deleted_files,
                'message': f'清理完成，删除了 {len(deleted_files)} 个文件，释放了 {total_size_freed} 字节空间'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'文件清理失败: {str(e)}',
                'error_type': 'FileCleanupError'
            }
    
    def get_upload_stats(self) -> Dict[str, Any]:
        """
        获取上传统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            total_files = 0
            total_size = 0
            type_stats = {}
            
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file():
                    total_files += 1
                    file_size = file_path.stat().st_size
                    total_size += file_size
                    
                    file_type = file_path.suffix.lower()
                    if file_type in type_stats:
                        type_stats[file_type]['count'] += 1
                        type_stats[file_type]['size'] += file_size
                    else:
                        type_stats[file_type] = {'count': 1, 'size': file_size}
            
            return {
                'total_files': total_files,
                'total_size': total_size,
                'type_statistics': type_stats,
                'upload_directory': str(self.upload_dir),
                'max_file_size': self.max_file_size,
                'supported_types': list(self.supported_types.keys())
            }
            
        except Exception as e:
            return {
                'error': f'获取统计信息失败: {str(e)}',
                'error_type': 'StatsError'
            }
    
    def set_max_file_size(self, size_in_bytes: int):
        """
        设置最大文件大小
        
        Args:
            size_in_bytes: 最大文件大小（字节）
        """
        self.max_file_size = size_in_bytes
    
    def get_supported_types(self) -> Dict[str, str]:
        """
        获取支持的文件类型
        
        Returns:
            Dict[str, str]: 支持的文件类型及MIME类型
        """
        return self.supported_types.copy()
