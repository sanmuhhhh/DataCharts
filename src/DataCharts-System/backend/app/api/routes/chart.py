# -*- coding: utf-8 -*-
"""
图表相关API路由
"""

from fastapi import APIRouter, HTTPException, Response
from typing import Dict, Any, Optional
import os
import sys
import json

# 添加服务路径
current_dir = os.path.dirname(__file__)
backend_dir = os.path.join(current_dir, '..', '..', '..')
sys.path.insert(0, os.path.abspath(backend_dir))

try:
    from backend.app.models.requests import ChartCreateRequest, ChartUpdateRequest
    from backend.app.models.responses import ChartResponse
except ImportError:
    # 占位符模型
    from pydantic import BaseModel
    
    class ChartCreateRequest(BaseModel):
        data_id: str
        chart_type: str
        config: dict = {}
    
    class ChartUpdateRequest(BaseModel):
        data_id: str = None
        config: dict = None

router = APIRouter()


@router.post("/create")
async def create_chart(request: ChartCreateRequest):
    """
    创建图表
    
    基于数据和配置生成图表
    """
    try:
        if not request.data_id:
            raise HTTPException(400, "数据ID不能为空")
        
        if not request.chart_type:
            raise HTTPException(400, "图表类型不能为空")
        
        # 验证图表类型
        supported_types = ["line", "bar", "scatter", "pie", "heatmap", "histogram"]
        if request.chart_type not in supported_types:
            raise HTTPException(400, f"不支持的图表类型: {request.chart_type}")
        
        # 生成图表ID
        import uuid
        chart_id = str(uuid.uuid4())
        
        # 生成默认图表数据
        chart_data = generate_chart_data(request.chart_type, request.config)
        
        return {
            "status": "success",
            "chart_id": chart_id,
            "chart_type": request.chart_type,
            "data_id": request.data_id,
            "config": request.config,
            "chart_data": chart_data,
            "message": "图表创建成功",
            "created_at": "2024-01-01T00:00:00Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"图表创建失败: {str(e)}")


@router.get("/{chart_id}")
async def get_chart(chart_id: str):
    """获取图表详情"""
    try:
        # 这里应该从图表服务获取实际数据
        # 现在返回占位符响应
        return {
            "status": "success",
            "chart_id": chart_id,
            "chart_type": "line",
            "data_id": "sample_data",
            "config": {
                "title": "示例图表",
                "x_axis": "X轴",
                "y_axis": "Y轴"
            },
            "chart_data": generate_chart_data("line", {}),
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(500, f"获取图表失败: {str(e)}")


@router.put("/{chart_id}")
async def update_chart(chart_id: str, request: ChartUpdateRequest):
    """更新图表"""
    try:
        # 这里应该调用实际的图表更新服务
        # 现在返回占位符响应
        return {
            "status": "success",
            "chart_id": chart_id,
            "chart_type": "line",
            "data_id": request.data_id or "sample_data",
            "config": request.config or {},
            "chart_data": generate_chart_data("line", request.config or {}),
            "message": "图表更新成功",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"图表更新失败: {str(e)}")


@router.get("/{chart_id}/export")
async def export_chart(chart_id: str, format: str = "png"):
    """
    导出图表
    
    支持格式: png, jpg, svg, pdf, json
    """
    try:
        # 验证格式
        supported_formats = ["png", "jpg", "jpeg", "svg", "pdf", "json"]
        if format.lower() not in supported_formats:
            raise HTTPException(
                400, 
                f"不支持的格式: {format}. 支持的格式: {', '.join(supported_formats)}"
            )
        
        # 生成示例导出数据
        if format.lower() == "json":
            export_data = json.dumps({
                "chart_id": chart_id,
                "chart_data": generate_chart_data("line", {}),
                "export_time": "2024-01-01T00:00:00Z"
            }).encode()
            media_type = "application/json"
        else:
            # 对于图像格式，返回占位符
            export_data = b"placeholder image data"
            media_type = {
                "png": "image/png",
                "jpg": "image/jpeg",
                "jpeg": "image/jpeg",
                "svg": "image/svg+xml",
                "pdf": "application/pdf"
            }.get(format.lower(), "application/octet-stream")
        
        filename = f"chart_{chart_id}.{format}"
        
        return Response(
            content=export_data,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"图表导出失败: {str(e)}")


@router.delete("/{chart_id}")
async def delete_chart(chart_id: str):
    """删除图表"""
    try:
        # 这里应该调用实际的删除服务
        # 现在返回占位符响应
        return {
            "status": "success",
            "chart_id": chart_id,
            "message": "图表删除成功"
        }
        
    except Exception as e:
        raise HTTPException(500, f"删除图表失败: {str(e)}")


@router.get("/")
async def list_charts(
    skip: int = 0, 
    limit: int = 20, 
    chart_type: Optional[str] = None
):
    """获取图表列表"""
    try:
        # 这里应该从图表服务获取实际列表
        # 现在返回占位符响应
        sample_charts = [
            {
                "chart_id": f"chart_{i}",
                "chart_type": chart_type or "line",
                "data_id": f"data_{i}",
                "config": {"title": f"图表 {i}"},
                "created_at": "2024-01-01T00:00:00Z"
            }
            for i in range(skip, min(skip + limit, skip + 3))
        ]
        
        return {
            "items": sample_charts,
            "total": 3,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(500, f"获取图表列表失败: {str(e)}")


@router.get("/types")
async def get_chart_types():
    """获取支持的图表类型"""
    try:
        chart_types = {
            "basic": [
                {
                    "type": "line",
                    "name": "折线图",
                    "description": "用于显示数据随时间的变化趋势",
                    "icon": "94"
                },
                {
                    "type": "bar",
                    "name": "柱状图",
                    "description": "用于比较不同类别的数据",
                    "icon": "96"
                },
                {
                    "type": "scatter",
                    "name": "散点图",
                    "description": "用于显示两个变量之间的关系",
                    "icon": "74"
                },
                {
                    "type": "pie",
                    "name": "饼图",
                    "description": "用于显示各部分占整体的比例",
                    "icon": "07"
                }
            ],
            "advanced": [
                {
                    "type": "heatmap",
                    "name": "热力图",
                    "description": "用于显示数据矩阵的密度分布",
                    "icon": "9115"
                },
                {
                    "type": "histogram",
                    "name": "直方图",
                    "description": "用于显示数据的分布情况",
                    "icon": "90"
                }
            ]
        }
        
        return {
            "status": "success",
            "chart_types": chart_types,
            "total_types": len(chart_types["basic"]) + len(chart_types["advanced"])
        }
        
    except Exception as e:
        raise HTTPException(500, f"获取图表类型失败: {str(e)}")


def generate_chart_data(chart_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """生成图表数据"""
    title = config.get("title", f"{chart_type}图表")
    
    if chart_type == "line":
        return {
            "type": "line",
            "data": {
                "labels": ["1月", "2月", "3月", "4月", "5月", "6月"],
                "datasets": [{
                    "label": title,
                    "data": [12, 19, 3, 5, 2, 3],
                    "borderColor": "#409EFF",
                    "backgroundColor": "#409EFF20"
                }]
            },
            "options": {"responsive": True}
        }
    elif chart_type == "bar":
        return {
            "type": "bar",
            "data": {
                "labels": ["产品A", "产品B", "产品C", "产品D"],
                "datasets": [{
                    "label": title,
                    "data": [25, 45, 30, 35],
                    "backgroundColor": ["#409EFF", "#67C23A", "#E6A23C", "#F56C6C"]
                }]
            },
            "options": {"responsive": True}
        }
    elif chart_type == "scatter":
        return {
            "type": "scatter",
            "data": {
                "datasets": [{
                    "label": title,
                    "data": [{"x": 1, "y": 2}, {"x": 2, "y": 4}, {"x": 3, "y": 1}],
                    "backgroundColor": "#409EFF"
                }]
            },
            "options": {"responsive": True}
        }
    elif chart_type == "pie":
        return {
            "type": "pie",
            "data": {
                "labels": ["Chrome", "Firefox", "Safari", "Edge"],
                "datasets": [{
                    "data": [45, 25, 20, 10],
                    "backgroundColor": ["#409EFF", "#67C23A", "#E6A23C", "#F56C6C"]
                }]
            },
            "options": {"responsive": True}
        }
    else:
        return {
            "type": chart_type,
            "data": {},
            "options": {"responsive": True}
        }
