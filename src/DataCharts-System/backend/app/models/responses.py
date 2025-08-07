# -*- coding: utf-8 -*-
"""
API响应模型

定义所有API响应的数据模型
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field
from datetime import datetime


class BaseResponse(BaseModel):
    """基础响应模型"""
    status: str = Field(..., description="响应状态")
    message: Optional[str] = Field(None, description="响应消息")


class DataResponse(BaseResponse):
    """数据相关响应"""
    data_id: str = Field(..., description="数据ID")
    format: str = Field(..., description="数据格式")
    validation_result: Optional[Dict[str, Any]] = Field(None, description="验证结果")
    preview: Optional[Any] = Field(None, description="预览数据")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


class DataListResponse(BaseModel):
    """数据列表响应"""
    items: List[DataResponse] = Field(..., description="数据列表")
    total: int = Field(..., description="总数量")
    skip: int = Field(..., description="跳过数量")
    limit: int = Field(..., description="限制数量")


class FunctionResponse(BaseResponse):
    """函数处理响应"""
    expression: str = Field(..., description="函数表达式")
    is_valid: bool = Field(..., description="是否有效")
    parsed_expression: Optional[Dict[str, Any]] = Field(None, description="解析结果")
    variables: Optional[List[str]] = Field(None, description="变量列表")
    functions_used: Optional[List[str]] = Field(None, description="使用的函数")
    complexity_score: Optional[float] = Field(None, description="复杂度分数")
    estimated_time: Optional[float] = Field(None, description="预估执行时间")
    error_message: Optional[str] = Field(None, description="错误消息")


class FunctionLibraryResponse(BaseModel):
    """函数库响应"""
    categories: Dict[str, List[str]] = Field(..., description="函数分类")
    functions: Dict[str, Dict[str, Any]] = Field(..., description="函数详情")
    total_functions: int = Field(..., description="函数总数")
    version: str = Field(..., description="库版本")


class ChartResponse(BaseResponse):
    """图表响应"""
    chart_id: str = Field(..., description="图表ID")
    chart_type: str = Field(..., description="图表类型")
    data_id: str = Field(..., description="数据ID")
    config: Dict[str, Any] = Field(..., description="图表配置")
    chart_data: Optional[Dict[str, Any]] = Field(None, description="图表数据")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class ChartListResponse(BaseModel):
    """图表列表响应"""
    items: List[ChartResponse] = Field(..., description="图表列表")
    total: int = Field(..., description="总数量")
    skip: int = Field(..., description="跳过数量")
    limit: int = Field(..., description="限制数量")


class ErrorResponse(BaseResponse):
    """错误响应"""
    error_code: str = Field(..., description="错误代码")
    error_detail: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误时间")
