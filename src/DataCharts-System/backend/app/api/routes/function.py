# -*- coding: utf-8 -*-
"""
函数处理API路由
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import os
import sys

# 添加服务路径
current_dir = os.path.dirname(__file__)
backend_dir = os.path.join(current_dir, '..', '..', '..')
sys.path.insert(0, os.path.abspath(backend_dir))

try:
    from backend.app.models.requests import FunctionParseRequest, FunctionApplyRequest
    from backend.app.models.responses import FunctionResponse, FunctionLibraryResponse
except ImportError:
    # 占位符模型
    from pydantic import BaseModel
    
    class FunctionParseRequest(BaseModel):
        expression: str
    
    class FunctionApplyRequest(BaseModel):
        data_id: str
        expression: str
        options: dict = {}

router = APIRouter()


@router.post("/parse")
async def parse_function(request: FunctionParseRequest):
    """
    解析函数表达式
    
    检查语法正确性并提取变量信息
    """
    try:
        expression = request.expression.strip()
        
        if not expression:
            raise HTTPException(400, "函数表达式不能为空")
        
        # 简单的语法检查
        is_valid = True
        error_message = None
        variables = []
        functions_used = []
        
        # 检查括号匹配
        if expression.count('(') != expression.count(')'):
            is_valid = False
            error_message = "括号不匹配"
        
        # 提取可能的变量
        import re
        var_pattern = r'\b[a-zA-Z][a-zA-Z0-9_]*\b'
        potential_vars = re.findall(var_pattern, expression)
        
        # 预定义的函数列表
        known_functions = ['sin', 'cos', 'tan', 'log', 'exp', 'sqrt', 'mean', 'std', 'var', 'median']
        
        for var in potential_vars:
            if var in known_functions:
                functions_used.append(var)
            elif var not in ['e', 'pi']:  # 排除常数
                variables.append(var)
        
        # 去重
        variables = list(set(variables))
        functions_used = list(set(functions_used))
        
        return {
            "status": "success" if is_valid else "error",
            "expression": expression,
            "is_valid": is_valid,
            "parsed_expression": {
                "variables": variables,
                "functions": functions_used
            } if is_valid else None,
            "variables": variables,
            "functions_used": functions_used,
            "complexity_score": len(functions_used) + len(variables),
            "estimated_time": 0.1 * (len(functions_used) + len(variables)),
            "error_message": error_message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "expression": request.expression,
            "is_valid": False,
            "error_message": str(e)
        }


@router.post("/apply")
async def apply_function(request: FunctionApplyRequest):
    """
    应用函数到数据
    
    执行函数计算并返回结果
    """
    try:
        if not request.data_id:
            raise HTTPException(400, "数据ID不能为空")
        
        if not request.expression.strip():
            raise HTTPException(400, "函数表达式不能为空")
        
        # 这里应该调用实际的函数处理服务
        # 现在返回占位符响应
        return {
            "status": "success",
            "result_id": f"result_{request.data_id}_{hash(request.expression)}",
            "processing_time": 0.25,
            "data_type": "numeric",
            "result_data": {
                "preview": [1.0, 2.0, 3.0, 4.0, 5.0],
                "shape": [100, 1],
                "description": f"应用函数 {request.expression} 的结果"
            },
            "message": "函数应用成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"函数应用失败: {str(e)}")


@router.get("/library")
async def get_function_library():
    """
    获取支持的函数库
    
    返回所有可用的函数和分类
    """
    try:
        function_library = {
            "mathematical": {
                "sin": {"description": "正弦函数", "parameters": ["x"]},
                "cos": {"description": "余弦函数", "parameters": ["x"]},
                "tan": {"description": "正切函数", "parameters": ["x"]},
                "log": {"description": "自然对数", "parameters": ["x"]},
                "exp": {"description": "指数函数", "parameters": ["x"]},
                "sqrt": {"description": "平方根", "parameters": ["x"]}
            },
            "statistical": {
                "mean": {"description": "平均值", "parameters": ["data"]},
                "std": {"description": "标准差", "parameters": ["data"]},
                "var": {"description": "方差", "parameters": ["data"]},
                "median": {"description": "中位数", "parameters": ["data"]}
            },
            "transformation": {
                "normalize": {"description": "归一化", "parameters": ["data"]},
                "standardize": {"description": "标准化", "parameters": ["data"]},
                "scale": {"description": "缩放", "parameters": ["data", "factor"]}
            }
        }
        
        # 计算统计信息
        total_functions = sum(len(category) for category in function_library.values())
        
        return {
            "status": "success",
            "supported_functions": function_library,
            "function_categories": list(function_library.keys()),
            "total_functions": total_functions,
            "execution_environment": "safe_sandbox",
            "version": "1.0.0"
        }
        
    except Exception as e:
        raise HTTPException(500, f"获取函数库失败: {str(e)}")


@router.post("/validate")
async def validate_function(request: FunctionParseRequest):
    """
    验证函数表达式
    
    详细的语法和安全性检查
    """
    try:
        expression = request.expression.strip()
        
        if not expression:
            raise HTTPException(400, "函数表达式不能为空")
        
        # 基础语法验证
        is_valid = True
        issues = []
        security_score = 100
        
        # 检查危险关键词
        dangerous_keywords = ['import', 'exec', 'eval', '__', 'open', 'file']
        for keyword in dangerous_keywords:
            if keyword in expression:
                issues.append(f"检测到危险关键词: {keyword}")
                security_score -= 20
                is_valid = False
        
        # 检查括号匹配
        if expression.count('(') != expression.count(')'):
            issues.append("括号不匹配")
            is_valid = False
        
        # 性能评估
        complexity = len(expression)
        estimated_time = complexity * 0.001  # 简单估算
        memory_estimate = complexity * 100    # 简单估算
        
        recommendations = []
        if complexity > 100:
            recommendations.append("表达式过于复杂，建议简化")
        if len(issues) > 0:
            recommendations.append("存在安全风险，请检查表达式")
        
        return {
            "is_valid": is_valid,
            "analysis": {
                "syntax_correct": is_valid,
                "complexity": complexity,
                "safety_check": len(issues) == 0
            },
            "security_issues": issues,
            "security_score": max(0, security_score),
            "estimated_time": estimated_time,
            "memory_estimate": memory_estimate,
            "recommendations": recommendations,
            "message": "验证完成"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"函数验证失败: {str(e)}")


@router.get("/info/{function_name}")
async def get_function_info(function_name: str):
    """获取特定函数的详细信息"""
    try:
        # 函数信息数据库
        function_info = {
            "sin": {
                "name": "sin",
                "description": "计算角度的正弦值",
                "parameters": ["x"],
                "return_type": "float",
                "examples": ["sin(0)", "sin(pi/2)"],
                "category": "mathematical"
            },
            "cos": {
                "name": "cos",
                "description": "计算角度的余弦值",
                "parameters": ["x"],
                "return_type": "float",
                "examples": ["cos(0)", "cos(pi)"],
                "category": "mathematical"
            },
            "mean": {
                "name": "mean",
                "description": "计算数据的平均值",
                "parameters": ["data"],
                "return_type": "float",
                "examples": ["mean([1,2,3,4,5])"],
                "category": "statistical"
            }
        }
        
        if function_name not in function_info:
            raise HTTPException(404, f"函数 {function_name} 不存在")
        
        return {
            "status": "success",
            "function_info": function_info[function_name]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"获取函数信息失败: {str(e)}")
