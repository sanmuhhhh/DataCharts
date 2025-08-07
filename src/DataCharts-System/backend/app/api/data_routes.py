"""
数据相关API路由

提供数据上传、导入、处理、验证等API端点
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Dict, Any, Optional, List
import json

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from services.data_service import DataService
from services.file_service import FileService


# 创建路由器
router = APIRouter(prefix="/api/data", tags=["data"])

# 服务实例
data_service = DataService()
file_service = FileService()


@router.post("/upload")
async def upload_data_file(
    file: UploadFile = File(...),
    format: Optional[str] = None,
    options: Optional[str] = None
):
    """
    上传数据文件
    
    Args:
        file: 上传的文件
        format: 数据格式 (可选，自动检测)
        options: 导入选项 (JSON字符串)
    
    Returns:
        Dict: 上传和导入结果
    """
    try:
        # 读取文件内容
        file_content = await file.read()
        
        # 保存文件
        save_result = await file_service.save_uploaded_file(file_content, file.filename)
        if not save_result['success']:
            raise HTTPException(status_code=400, detail=save_result['error'])
        
        # 确定格式
        if not format:
            file_extension = save_result['file_info']['file_type']
            format_mapping = {
                '.csv': 'csv',
                '.xlsx': 'excel',
                '.xls': 'excel',
                '.json': 'json',
                '.txt': 'txt'
            }
            format = format_mapping.get(file_extension, 'csv')
        
        # 解析导入选项
        import_options = {}
        if options:
            try:
                import_options = json.loads(options)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="导入选项格式错误")
        
        # 导入数据
        file_path = save_result['file_info']['file_path']
        import_result = await data_service.import_file_data(file_path, format, import_options)
        
        if not import_result['success']:
            raise HTTPException(status_code=400, detail=import_result['error'])
        
        return {
            'success': True,
            'file_info': save_result['file_info'],
            'import_result': import_result,
            'message': '文件上传和数据导入成功'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.post("/import/manual")
async def import_manual_data(
    data: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None
):
    """
    导入手动输入数据
    
    Args:
        data: 手动输入的数据
        options: 导入选项
    
    Returns:
        Dict: 导入结果
    """
    try:
        if options is None:
            options = {}
        
        # 提取数据内容
        data_content = data.get('content')
        if data_content is None:
            raise HTTPException(status_code=400, detail="数据内容不能为空")
        
        # 导入数据
        import_result = await data_service.import_manual_data(data_content, options)
        
        if not import_result['success']:
            raise HTTPException(status_code=400, detail=import_result['error'])
        
        return import_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"手动数据导入失败: {str(e)}")


@router.post("/process/{data_id}")
async def process_data(
    data_id: str,
    process_options: Optional[Dict[str, Any]] = None
):
    """
    预处理数据
    
    Args:
        data_id: 数据ID
        process_options: 处理选项
    
    Returns:
        Dict: 处理结果
    """
    try:
        if process_options is None:
            process_options = {}
        
        result = await data_service.process_data(data_id, process_options)
        
        if not result['success']:
            if result.get('error_type') == 'DataNotFoundError':
                raise HTTPException(status_code=404, detail=result['error'])
            else:
                raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据处理失败: {str(e)}")


@router.post("/validate/{data_id}")
async def validate_data(data_id: str):
    """
    验证数据
    
    Args:
        data_id: 数据ID
    
    Returns:
        Dict: 验证结果
    """
    try:
        result = await data_service.validate_data(data_id)
        
        if not result['success']:
            if result.get('error_type') == 'DataNotFoundError':
                raise HTTPException(status_code=404, detail=result['error'])
            else:
                raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据验证失败: {str(e)}")


@router.get("/info/{data_id}")
async def get_data_info(data_id: str):
    """
    获取数据信息
    
    Args:
        data_id: 数据ID
    
    Returns:
        Dict: 数据信息
    """
    try:
        result = await data_service.get_data_info(data_id)
        
        if not result['success']:
            if result.get('error_type') == 'DataNotFoundError':
                raise HTTPException(status_code=404, detail=result['error'])
            else:
                raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据信息失败: {str(e)}")


@router.get("/preview/{data_id}")
async def get_data_preview(
    data_id: str,
    rows: Optional[int] = 10
):
    """
    获取数据预览
    
    Args:
        data_id: 数据ID
        rows: 预览行数
    
    Returns:
        Dict: 数据预览
    """
    try:
        result = await data_service.get_data_preview(data_id, rows)
        
        if not result['success']:
            if result.get('error_type') == 'DataNotFoundError':
                raise HTTPException(status_code=404, detail=result['error'])
            else:
                raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据预览失败: {str(e)}")


@router.get("/list")
async def list_data_sources():
    """
    列出所有数据源
    
    Returns:
        Dict: 数据源列表
    """
    try:
        result = await data_service.list_data_sources()
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据源列表失败: {str(e)}")


@router.delete("/{data_id}")
async def delete_data_source(data_id: str):
    """
    删除数据源
    
    Args:
        data_id: 数据ID
    
    Returns:
        Dict: 删除结果
    """
    try:
        result = await data_service.delete_data_source(data_id)
        
        if not result['success']:
            if result.get('error_type') == 'DataNotFoundError':
                raise HTTPException(status_code=404, detail=result['error'])
            else:
                raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除数据源失败: {str(e)}")


@router.get("/formats")
async def get_supported_formats():
    """
    获取支持的数据格式
    
    Returns:
        Dict: 支持的格式列表
    """
    try:
        formats = data_service.get_supported_formats()
        return {
            'success': True,
            'supported_formats': formats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取支持格式失败: {str(e)}")


# 文件管理相关API
@router.get("/files/list")
async def list_uploaded_files():
    """
    列出所有上传的文件
    
    Returns:
        Dict: 文件列表
    """
    try:
        result = await file_service.list_uploaded_files()
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")


@router.get("/files/info")
async def get_file_info(file_path: str):
    """
    获取文件信息
    
    Args:
        file_path: 文件路径
    
    Returns:
        Dict: 文件信息
    """
    try:
        result = await file_service.get_file_info(file_path)
        
        if not result['success']:
            if result.get('error_type') == 'FileNotFound':
                raise HTTPException(status_code=404, detail=result['error'])
            else:
                raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件信息失败: {str(e)}")


@router.delete("/files")
async def delete_file(file_path: str):
    """
    删除文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        Dict: 删除结果
    """
    try:
        result = await file_service.delete_file(file_path)
        
        if not result['success']:
            if result.get('error_type') == 'FileNotFound':
                raise HTTPException(status_code=404, detail=result['error'])
            elif result.get('error_type') == 'PermissionDenied':
                raise HTTPException(status_code=403, detail=result['error'])
            else:
                raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文件失败: {str(e)}")


@router.post("/files/cleanup")
async def cleanup_old_files(days: Optional[int] = 7):
    """
    清理旧文件
    
    Args:
        days: 保留天数
    
    Returns:
        Dict: 清理结果
    """
    try:
        result = await file_service.cleanup_old_files(days)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件清理失败: {str(e)}")


@router.get("/files/stats")
async def get_upload_stats():
    """
    获取上传统计信息
    
    Returns:
        Dict: 统计信息
    """
    try:
        stats = file_service.get_upload_stats()
        
        if 'error' in stats:
            raise HTTPException(status_code=400, detail=stats['error'])
        
        return {
            'success': True,
            'stats': stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")
