"""
安全执行环境

提供沙箱环境来安全地执行数学表达式计算
"""

import numpy as np
import pandas as pd
import time
import signal
from typing import Dict, Any, List, Optional
import sys
import os
from contextlib import contextmanager

# 添加数据类型路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data_types import ProcessingResult, DataSource, FunctionParseError

from .function_library import FunctionLibrary


class ExecutionTimeoutError(Exception):
    """执行超时异常"""
    pass


class SafeExecutionEnvironment:
    """安全执行环境类"""
    
    def __init__(self, max_execution_time: int = 30, max_memory_mb: int = 256):
        """
        初始化安全执行环境
        
        Args:
            max_execution_time: 最大执行时间（秒）
            max_memory_mb: 最大内存使用（MB）
        """
        self.max_execution_time = max_execution_time
        self.max_memory_mb = max_memory_mb
        self.function_library = FunctionLibrary()
        
        # 禁用的内置函数和模块
        self.forbidden_builtins = [
            'eval', 'exec', 'compile', '__import__',
            'open', 'file', 'input', 'raw_input',
            'reload', 'vars', 'globals', 'locals',
            'dir', 'hasattr', 'getattr', 'setattr',
            'delattr', 'callable'
        ]
        
        # 允许的内置函数
        self.allowed_builtins = {
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'sum': sum,
            'len': len,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'bool': bool,
            'int': int,
            'float': float,
            'str': str,
            'list': list,
            'tuple': tuple,
            'dict': dict,
            'set': set
        }
    
    def create_safe_namespace(self, data_vars: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建安全的命名空间
        
        Args:
            data_vars: 数据变量字典
            
        Returns:
            Dict[str, Any]: 安全的命名空间
        """
        # 基础命名空间
        namespace = {
            '__builtins__': self.allowed_builtins,
            'np': np,
            'pd': pd,
        }
        
        # 添加函数库中的所有函数
        namespace.update(self.function_library.get_all_functions())
        
        # 添加数据变量
        namespace.update(data_vars)
        
        # 添加常用数学常数
        namespace.update({
            'pi': np.pi,
            'e': np.e,
            'inf': np.inf,
            'nan': np.nan
        })
        
        return namespace
    
    @contextmanager
    def timeout_handler(self, seconds: int):
        """
        超时处理上下文管理器
        
        Args:
            seconds: 超时秒数
        """
        def timeout_callback(signum, frame):
            raise ExecutionTimeoutError(f"执行超时 ({seconds}秒)")
        
        # 设置信号处理器（仅在Unix系统上）
        if hasattr(signal, 'SIGALRM'):
            old_handler = signal.signal(signal.SIGALRM, timeout_callback)
            signal.alarm(seconds)
            try:
                yield
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        else:
            # Windows系统使用简单的时间检查
            start_time = time.time()
            try:
                yield
            finally:
                if time.time() - start_time > seconds:
                    raise ExecutionTimeoutError(f"执行超时 ({seconds}秒)")
    
    def execute_expression(self, expression: str, namespace: Dict[str, Any]) -> Any:
        """
        安全执行表达式
        
        Args:
            expression: 要执行的表达式
            namespace: 命名空间
            
        Returns:
            Any: 执行结果
            
        Raises:
            ExecutionTimeoutError: 执行超时
            FunctionParseError: 执行失败
        """
        try:
            with self.timeout_handler(self.max_execution_time):
                # 使用eval在受限环境中执行表达式
                result = eval(expression, {"__builtins__": {}}, namespace)
                return result
                
        except ExecutionTimeoutError:
            raise
        except Exception as e:
            raise FunctionParseError(f"表达式执行失败: {str(e)}")
    
    def apply_function_to_data(self, data: DataSource, expression: str, 
                             variables: List[str]) -> ProcessingResult:
        """
        将函数应用到数据上
        
        Args:
            data: 数据源
            expression: 函数表达式
            variables: 变量列表
            
        Returns:
            ProcessingResult: 处理结果
        """
        start_time = time.time()
        
        try:
            # 准备数据
            df = data.content
            if not isinstance(df, pd.DataFrame):
                raise FunctionParseError("数据必须是pandas DataFrame格式")
            
            # 创建数据变量映射
            data_vars = self._prepare_data_variables(df, variables)
            
            # 创建安全命名空间
            namespace = self.create_safe_namespace(data_vars)
            
            # 执行表达式
            result = self.execute_expression(expression, namespace)
            
            # 处理结果
            processed_result = self._process_result(result, df)
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                data=processed_result,
                processing_time=processing_time,
                status="success",
                error_message=None
            )
            
        except (ExecutionTimeoutError, FunctionParseError) as e:
            return ProcessingResult(
                data=None,
                processing_time=time.time() - start_time,
                status="error",
                error_message=str(e)
            )
        except Exception as e:
            return ProcessingResult(
                data=None,
                processing_time=time.time() - start_time,
                status="error",
                error_message=f"执行过程中发生未知错误: {str(e)}"
            )
    
    def _prepare_data_variables(self, df: pd.DataFrame, variables: List[str]) -> Dict[str, Any]:
        """
        准备数据变量
        
        Args:
            df: 数据DataFrame
            variables: 变量列表
            
        Returns:
            Dict[str, Any]: 数据变量字典
        """
        data_vars = {}
        
        for var in variables:
            if var in df.columns:
                # 列数据
                data_vars[var] = df[var].values
            elif var == 'index':
                # 行索引
                data_vars[var] = df.index.values
            elif var.startswith('col_') and var[4:].isdigit():
                # 按列号访问
                col_idx = int(var[4:])
                if 0 <= col_idx < len(df.columns):
                    data_vars[var] = df.iloc[:, col_idx].values
            else:
                # 创建默认变量（索引数组）
                data_vars[var] = np.arange(len(df))
        
        return data_vars
    
    def _process_result(self, result: Any, original_df: pd.DataFrame) -> Any:
        """
        处理执行结果
        
        Args:
            result: 原始结果
            original_df: 原始数据框
            
        Returns:
            Any: 处理后的结果
        """
        if isinstance(result, np.ndarray):
            # 如果结果是数组，转换为列表或单值
            if result.ndim == 0:
                return float(result)
            elif result.ndim == 1:
                if len(result) == len(original_df):
                    # 如果长度匹配，创建新的DataFrame列
                    return pd.Series(result, index=original_df.index)
                else:
                    return result.tolist()
            else:
                return result.tolist()
        elif isinstance(result, pd.Series):
            return result
        elif isinstance(result, (int, float, complex)):
            return result
        elif isinstance(result, (list, tuple)):
            return list(result)
        else:
            # 尝试转换为数值
            try:
                return float(result)
            except (ValueError, TypeError):
                return str(result)
    
    def validate_expression_safety(self, expression: str) -> Dict[str, Any]:
        """
        验证表达式安全性
        
        Args:
            expression: 表达式字符串
            
        Returns:
            Dict[str, Any]: 安全性验证结果
        """
        issues = []
        warnings = []
        
        # 检查禁用的内置函数
        for forbidden in self.forbidden_builtins:
            if forbidden in expression:
                issues.append(f"包含禁用的函数: {forbidden}")
        
        # 检查危险模式
        dangerous_patterns = [
            ('__', "包含双下划线方法调用"),
            ('import', "包含import语句"),
            ('while', "包含while循环"),
            ('for', "包含for循环"),
        ]
        
        for pattern, message in dangerous_patterns:
            if pattern in expression:
                issues.append(message)
        
        # 检查复杂度
        if len(expression) > 500:
            warnings.append("表达式过长，可能影响执行性能")
        
        if expression.count('(') > 20:
            warnings.append("表达式嵌套过深，可能影响执行性能")
        
        return {
            'is_safe': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'risk_level': 'high' if issues else ('medium' if warnings else 'low')
        }
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """
        获取执行环境统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        return {
            'max_execution_time': self.max_execution_time,
            'max_memory_mb': self.max_memory_mb,
            'available_functions': len(self.function_library.get_supported_function_names()),
            'function_categories': list(self.function_library.get_function_categories().keys()),
            'security_level': 'high'
        }
