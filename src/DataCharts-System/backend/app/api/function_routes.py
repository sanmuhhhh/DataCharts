"""
函数处理相关API路由

提供函数解析、验证、应用等API端点
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional, List
import json
import sys
import os

# 添加共享模块路径
shared_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared')
sys.path.insert(0, os.path.abspath(shared_path))

from interfaces import FunctionProcessor
from data_types import FunctionExpression, DataSource

# 添加服务路径
services_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(services_path))

try:
    from services.data_service import DataService
except ImportError:
    # 如果无法导入，使用占位符
    class DataService:
        def get_data_source(self, data_id: str):
            return None


# 创建路由器
router = APIRouter(prefix="/api/function", tags=["function"])

# 服务实例
function_processor = FunctionProcessor()
data_service = DataService()


@router.post("/parse")
async def parse_function_expression(request: Dict[str, Any]):
    """
    解析函数表达式
    
    Args:
        request: 请求数据，包含expression字段
    
    Returns:
        Dict: 解析结果
    """
    try:
        expression = request.get("expression")
        if not expression:
            raise HTTPException(status_code=400, detail="缺少表达式参数")
        
        # 解析表达式
        parsed = function_processor.parse_expression(expression)
        
        return {
            "status": "success",
            "parsed_expression": {
                "expression": parsed.expression,
                "variables": parsed.variables,
                "parameters": parsed.parameters
            },
            "is_valid": True,
            "message": "表达式解析成功"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
            "is_valid": False,
            "parsed_expression": None
        }


@router.post("/validate")
async def validate_function_syntax(request: Dict[str, Any]):
    """
    验证函数表达式语法
    
    Args:
        request: 请求数据，包含expression字段
    
    Returns:
        Dict: 验证结果
    """
    try:
        expression = request.get("expression")
        if not expression:
            raise HTTPException(status_code=400, detail="缺少表达式参数")
        
        # 验证语法
        is_valid = function_processor.validate_syntax(expression)
        
        # 如果有具体实现，获取详细分析
        if hasattr(function_processor, '_impl') and function_processor._impl:
            analysis = function_processor._impl.analyze_expression(expression)
        else:
            analysis = {"is_valid": is_valid}
        
        return {
            "status": "success",
            "is_valid": is_valid,
            "analysis": analysis,
            "message": "语法验证完成"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
            "is_valid": False,
            "analysis": None
        }


@router.post("/apply")
async def apply_function_to_data(request: Dict[str, Any]):
    """
    将函数应用到数据
    
    Args:
        request: 请求数据，包含data_id、expression、options字段
    
    Returns:
        Dict: 应用结果
    """
    try:
        data_id = request.get("data_id")
        expression = request.get("expression")
        options = request.get("options", {})
        
        if not data_id:
            raise HTTPException(status_code=400, detail="缺少数据ID参数")
        if not expression:
            raise HTTPException(status_code=400, detail="缺少表达式参数")
        
        # 获取数据源
        data_source = data_service.get_data_source(data_id)
        if not data_source:
            raise HTTPException(status_code=404, detail=f"数据ID不存在: {data_id}")
        
        # 解析表达式
        parsed_expression = function_processor.parse_expression(expression)
        
        # 应用函数
        result = function_processor.apply_function(data_source, parsed_expression)
        
        # 处理结果
        if result.status == "success":
            # 将结果转换为可序列化的格式
            processed_data = _serialize_result(result.data)
            
            return {
                "status": "success",
                "result_data": processed_data,
                "processing_time": result.processing_time,
                "data_type": type(result.data).__name__,
                "message": "函数应用成功"
            }
        else:
            return {
                "status": "error",
                "error_message": result.error_message,
                "processing_time": result.processing_time,
                "result_data": None
            }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"函数应用失败: {str(e)}",
            "processing_time": 0.0,
            "result_data": None
        }


@router.get("/library")
async def get_function_library():
    """
    获取函数库信息
    
    Returns:
        Dict: 函数库信息
    """
    try:
        # 获取支持的函数列表
        supported_functions = function_processor.get_supported_functions()
        
        # 如果有具体实现，获取分类信息
        if hasattr(function_processor, '_impl') and function_processor._impl:
            categories = function_processor._impl.get_function_categories()
            execution_info = function_processor._impl.get_execution_environment_info()
        else:
            # 占位符分类
            categories = {
                "数学函数": ["sin", "cos", "tan", "log", "exp", "sqrt"],
                "统计函数": ["mean", "std", "var", "median"],
                "数据变换": ["normalize", "standardize", "scale"],
                "滤波函数": ["moving_average", "gaussian_filter"]
            }
            execution_info = {"message": "详细信息暂不可用"}
        
        return {
            "status": "success",
            "supported_functions": supported_functions,
            "function_categories": categories,
            "total_functions": len(supported_functions),
            "execution_environment": execution_info
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"获取函数库信息失败: {str(e)}",
            "supported_functions": [],
            "function_categories": {}
        }


@router.get("/info/{function_name}")
async def get_function_info(function_name: str):
    """
    获取特定函数的信息
    
    Args:
        function_name: 函数名
    
    Returns:
        Dict: 函数信息
    """
    try:
        # 检查函数是否支持
        supported_functions = function_processor.get_supported_functions()
        
        if function_name not in supported_functions:
            raise HTTPException(status_code=404, detail=f"函数不存在: {function_name}")
        
        # 如果有具体实现，获取详细信息
        if hasattr(function_processor, '_impl') and function_processor._impl:
            func_info = function_processor._impl.get_function_info(function_name)
        else:
            # 占位符信息
            func_info = {
                "name": function_name,
                "category": "unknown",
                "documentation": "暂无文档",
                "is_available": True
            }
        
        return {
            "status": "success",
            "function_info": func_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"获取函数信息失败: {str(e)}",
            "function_info": None
        }


@router.post("/test")
async def test_function_execution(request: Dict[str, Any]):
    """
    测试函数执行
    
    Args:
        request: 测试请求，包含expression和test_data字段
    
    Returns:
        Dict: 测试结果
    """
    try:
        expression = request.get("expression")
        test_data = request.get("test_data", {})
        
        if not expression:
            raise HTTPException(status_code=400, detail="缺少表达式参数")
        
        # 如果没有测试数据，使用默认数据
        if not test_data:
            test_data = {
                "x": [1, 2, 3, 4, 5],
                "y": [2, 4, 6, 8, 10]
            }
        
        # 如果有具体实现，执行测试
        if hasattr(function_processor, '_impl') and function_processor._impl:
            test_result = function_processor._impl.test_function_execution(expression, test_data)
        else:
            # 占位符测试
            test_result = {
                "success": True,
                "result": "测试功能暂不可用",
                "processing_time": 0.0,
                "error_message": None
            }
        
        return {
            "status": "success",
            "test_result": test_result,
            "test_data_used": test_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"函数测试失败: {str(e)}",
            "test_result": None
        }


@router.post("/validate-with-data")
async def validate_function_with_data(request: Dict[str, Any]):
    """
    验证函数是否可以应用到指定数据
    
    Args:
        request: 验证请求，包含expression和data_id字段
    
    Returns:
        Dict: 验证结果
    """
    try:
        expression = request.get("expression")
        data_id = request.get("data_id")
        
        if not expression:
            raise HTTPException(status_code=400, detail="缺少表达式参数")
        if not data_id:
            raise HTTPException(status_code=400, detail="缺少数据ID参数")
        
        # 获取数据源
        data_source = data_service.get_data_source(data_id)
        if not data_source:
            raise HTTPException(status_code=404, detail=f"数据ID不存在: {data_id}")
        
        # 如果有具体实现，执行验证
        if hasattr(function_processor, '_impl') and function_processor._impl:
            validation_result = function_processor._impl.validate_function_with_data(expression, data_source)
        else:
            # 占位符验证
            validation_result = {
                "is_valid": True,
                "available_variables": [],
                "missing_variables": [],
                "suggestions": ["详细验证功能暂不可用"]
            }
        
        return {
            "status": "success",
            "validation": validation_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"数据验证失败: {str(e)}",
            "validation": None
        }


def _serialize_result(data: Any) -> Any:
    """
    将结果序列化为JSON可兼容格式
    
    Args:
        data: 原始数据
    
    Returns:
        Any: 序列化后的数据
    """
    import pandas as pd
    import numpy as np
    
    if isinstance(data, pd.Series):
        return {
            "type": "series",
            "data": data.tolist(),
            "index": data.index.tolist()
        }
    elif isinstance(data, pd.DataFrame):
        return {
            "type": "dataframe",
            "data": data.to_dict('records'),
            "columns": list(data.columns)
        }
    elif isinstance(data, np.ndarray):
        return {
            "type": "array",
            "data": data.tolist(),
            "shape": data.shape
        }
    elif isinstance(data, (list, tuple)):
        return {
            "type": "list",
            "data": list(data)
        }
    elif isinstance(data, (int, float, complex)):
        return {
            "type": "scalar",
            "data": float(data) if not isinstance(data, complex) else str(data)
        }
    else:
        return {
            "type": "other",
            "data": str(data)
        }
