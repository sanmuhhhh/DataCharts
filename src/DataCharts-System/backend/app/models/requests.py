# -*- coding: utf-8 -*-
"""
API请求模型

定义所有API请求的数据模型
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class DataUploadRequest(BaseModel):
    """手动数据上传请求"""
    content: str = Field(..., description="数据内容")
    format: str = Field(..., description="数据格式", example="csv")
    options: Optional[Dict[str, Any]] = Field(default={}, description="导入选项")


class DataProcessRequest(BaseModel):
    """数据处理请求"""
    data_id: str = Field(..., description="数据ID")
    preprocess_options: Dict[str, Any] = Field(default={}, description="预处理选项")


class FunctionParseRequest(BaseModel):
    """函数解析请求"""
    expression: str = Field(..., description="函数表达式", example="sin(x) + cos(y)")


class FunctionApplyRequest(BaseModel):
    """函数应用请求"""
    data_id: str = Field(..., description="数据ID")
    expression: str = Field(..., description="函数表达式")
    options: Optional[Dict[str, Any]] = Field(default={}, description="执行选项")


class ChartCreateRequest(BaseModel):
    """图表创建请求"""
    data_id: str = Field(..., description="数据ID")
    chart_type: str = Field(..., description="图表类型", example="line")
    config: Dict[str, Any] = Field(default={}, description="图表配置")


class ChartUpdateRequest(BaseModel):
    """图表更新请求"""
    data_id: Optional[str] = Field(None, description="新数据ID")
    config: Optional[Dict[str, Any]] = Field(None, description="新配置")
