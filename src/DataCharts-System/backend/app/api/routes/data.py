# -*- coding: utf-8 -*-
"""
数据相关API路由
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import os
import sys

# 添加服务路径
current_dir = os.path.dirname(__file__)
backend_dir = os.path.join(current_dir, '..', '..', '..')
sys.path.insert(0, os.path.abspath(backend_dir))

try:
    from backend.app.models.requests import DataUploadRequest, DataProcessRequest
    from backend.app.models.responses import DataResponse
except ImportError:
    # 占位符模型
    from pydantic import BaseModel
    
    class DataUploadRequest(BaseModel):
        content: str
        format: str
        options: dict = {}
    
    class DataProcessRequest(BaseModel):
        data_id: str
        preprocess_options: dict = {}
    
    class DataResponse(BaseModel):
        data_id: str
        format: str
        status: str
        message: str = ""

router = APIRouter()


@router.post("/upload")
async def upload_data(file: UploadFile = File(...)):
    """
    上传数据文件
    
    支持的格式: CSV, Excel, JSON, TXT
    """
    try:
        # 验证文件类型
        allowed_extensions = ['.csv', '.xlsx', '.xls', '.json', '.txt']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(400, f"不支持的文件格式: {file_ext}")
        
        # 读取文件内容
        content = await file.read()
        
        # 这里应该调用实际的数据导入服务
        # 现在返回占位符响应
        return {
            "status": "success",
            "data_id": f"data_{file.filename}_{len(content)}",
            "format": file_ext[1:],  # 去掉点号
            "message": f"文件 {file.filename} 上传成功",
            "preview": {
                "size": len(content),
                "filename": file.filename
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"文件上传失败: {str(e)}")


@router.post("/manual")
async def upload_manual_data(request: DataUploadRequest):
    """
    手动输入数据
    
    支持CSV格式的文本数据
    """
    try:
        if not request.content.strip():
            raise HTTPException(400, "数据内容不能为空")
        
        # 这里应该调用实际的数据处理服务
        # 现在返回占位符响应
        return {
            "status": "success",
            "data_id": f"manual_{hash(request.content)}",
            "format": request.format,
            "message": "手动数据导入成功",
            "preview": {
                "content_length": len(request.content),
                "lines": len(request.content.split('\n'))
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"数据处理失败: {str(e)}")


@router.get("/{data_id}")
async def get_data(data_id: str):
    """获取数据详情"""
    try:
        # 这里应该从数据服务获取实际数据
        # 现在返回占位符响应
        return {
            "status": "success",
            "data_id": data_id,
            "format": "csv",
            "message": "数据获取成功",
            "metadata": {
                "created_at": "2024-01-01T00:00:00Z",
                "size": "1024 bytes"
            }
        }
        
    except Exception as e:
        raise HTTPException(500, f"获取数据失败: {str(e)}")


@router.post("/process")
async def process_data(request: DataProcessRequest):
    """数据预处理"""
    try:
        if not request.data_id:
            raise HTTPException(400, "数据ID不能为空")
        
        # 这里应该调用实际的数据预处理服务
        # 现在返回占位符响应
        return {
            "status": "success",
            "original_data_id": request.data_id,
            "processed_data_id": f"processed_{request.data_id}",
            "message": "数据预处理成功",
            "processing_options": request.preprocess_options
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"数据处理失败: {str(e)}")


@router.get("/")
async def list_data(skip: int = 0, limit: int = 20):
    """获取数据列表"""
    try:
        # 这里应该从数据服务获取实际列表
        # 现在返回占位符响应
        sample_data = [
            {
                "data_id": f"data_{i}",
                "format": "csv",
                "status": "success",
                "created_at": "2024-01-01T00:00:00Z"
            }
            for i in range(skip, min(skip + limit, skip + 5))
        ]
        
        return {
            "items": sample_data,
            "total": 5,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(500, f"获取数据列表失败: {str(e)}")


@router.delete("/{data_id}")
async def delete_data(data_id: str):
    """删除数据"""
    try:
        # 这里应该调用实际的删除服务
        # 现在返回占位符响应
        return {
            "status": "success",
            "data_id": data_id,
            "message": "数据删除成功"
        }
        
    except Exception as e:
        raise HTTPException(500, f"删除数据失败: {str(e)}")


@router.get("/{data_id}/preview")
async def get_data_preview(data_id: str, rows: int = 10):
    """获取数据预览"""
    try:
        # 这里应该从数据服务获取预览数据
        # 现在返回占位符响应
        return {
            "status": "success",
            "data_id": data_id,
            "preview": {
                "columns": ["col1", "col2", "col3"],
                "data": [
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]
                ],
                "shape": [3, 3],
                "rows_shown": min(rows, 3)
            }
        }
        
    except Exception as e:
        raise HTTPException(500, f"获取数据预览失败: {str(e)}")
