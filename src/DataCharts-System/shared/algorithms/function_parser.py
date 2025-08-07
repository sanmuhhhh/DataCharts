"""
函数表达式解析器

负责解析用户输入的数学表达式，提取变量和函数信息
"""

import re
import ast
import sympy as sp
from typing import List, Dict, Any, Set
import sys
import os

# 添加数据类型路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data_types import FunctionExpression, FunctionParseError

from .function_library import FunctionLibrary


class ExpressionParser:
    """表达式解析器类"""
    
    def __init__(self):
        self.function_library = FunctionLibrary()
        # 安全的函数名模式
        self.safe_function_pattern = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
        # 危险操作模式
        self.dangerous_patterns = [
            r'__\w+__',  # 双下划线方法
            r'import\s+',  # import语句
            r'exec\s*\(',  # exec函数
            r'eval\s*\(',  # eval函数
            r'open\s*\(',  # open函数
            r'file\s*\(',  # file函数
            r'input\s*\(',  # input函数
            r'raw_input\s*\(',  # raw_input函数
        ]
    
    def parse_expression(self, expression: str) -> FunctionExpression:
        """
        解析数学表达式
        
        Args:
            expression: 数学表达式字符串
            
        Returns:
            FunctionExpression: 解析后的表达式对象
            
        Raises:
            FunctionParseError: 解析失败时抛出
        """
        try:
            # 基础安全检查
            if not self._is_expression_safe(expression):
                raise FunctionParseError("表达式包含不安全的操作")
            
            # 使用SymPy解析表达式
            try:
                parsed_expr = sp.sympify(expression)
            except Exception as e:
                raise FunctionParseError(f"表达式语法错误: {str(e)}")
            
            # 提取变量
            variables = self._extract_variables(parsed_expr)
            
            # 提取函数
            functions_used = self._extract_functions(parsed_expr)
            
            # 验证函数支持
            self._validate_functions(functions_used)
            
            # 创建参数字典
            parameters = self._extract_parameters(expression)
            
            return FunctionExpression(
                expression=expression,
                variables=variables,
                parameters=parameters
            )
            
        except FunctionParseError:
            raise
        except Exception as e:
            raise FunctionParseError(f"表达式解析失败: {str(e)}")
    
    def validate_syntax(self, expression: str) -> bool:
        """
        验证表达式语法
        
        Args:
            expression: 数学表达式字符串
            
        Returns:
            bool: 语法是否正确
        """
        try:
            self.parse_expression(expression)
            return True
        except FunctionParseError:
            return False
    
    def _is_expression_safe(self, expression: str) -> bool:
        """
        检查表达式是否安全
        
        Args:
            expression: 表达式字符串
            
        Returns:
            bool: 是否安全
        """
        # 检查危险模式
        for pattern in self.dangerous_patterns:
            if re.search(pattern, expression, re.IGNORECASE):
                return False
        
        # 检查字符长度限制
        if len(expression) > 1000:
            return False
        
        # 检查嵌套层次
        if self._get_nesting_depth(expression) > 10:
            return False
        
        return True
    
    def _get_nesting_depth(self, expression: str) -> int:
        """
        计算表达式的嵌套深度
        
        Args:
            expression: 表达式字符串
            
        Returns:
            int: 嵌套深度
        """
        depth = 0
        max_depth = 0
        
        for char in expression:
            if char == '(':
                depth += 1
                max_depth = max(max_depth, depth)
            elif char == ')':
                depth -= 1
        
        return max_depth
    
    def _extract_variables(self, parsed_expr) -> List[str]:
        """
        从解析的表达式中提取变量
        
        Args:
            parsed_expr: SymPy解析的表达式
            
        Returns:
            List[str]: 变量名列表
        """
        try:
            variables = [str(symbol) for symbol in parsed_expr.free_symbols]
            # 过滤掉常数和函数名
            filtered_variables = []
            for var in variables:
                if var not in ['pi', 'e', 'I'] and not self.function_library.is_function_supported(var):
                    filtered_variables.append(var)
            return sorted(filtered_variables)
        except Exception:
            return []
    
    def _extract_functions(self, parsed_expr) -> Set[str]:
        """
        从解析的表达式中提取函数
        
        Args:
            parsed_expr: SymPy解析的表达式
            
        Returns:
            Set[str]: 使用的函数名集合
        """
        try:
            functions = set()
            
            # 遍历表达式树
            for node in sp.preorder_traversal(parsed_expr):
                if hasattr(node, 'func') and hasattr(node.func, '__name__'):
                    func_name = str(node.func.__name__)
                    # 映射SymPy函数名到我们的函数名
                    if func_name in ['sin', 'cos', 'tan', 'log', 'exp', 'sqrt', 'Abs']:
                        if func_name == 'Abs':
                            functions.add('abs')
                        else:
                            functions.add(func_name)
                elif isinstance(node, sp.Function):
                    func_name = str(type(node).__name__).lower()
                    if func_name in self.function_library.get_supported_function_names():
                        functions.add(func_name)
            
            return functions
        except Exception:
            return set()
    
    def _validate_functions(self, functions_used: Set[str]) -> None:
        """
        验证使用的函数是否都被支持
        
        Args:
            functions_used: 使用的函数名集合
            
        Raises:
            FunctionParseError: 如果有不支持的函数
        """
        unsupported_functions = []
        
        for func_name in functions_used:
            if not self.function_library.is_function_supported(func_name):
                unsupported_functions.append(func_name)
        
        if unsupported_functions:
            raise FunctionParseError(
                f"不支持的函数: {', '.join(unsupported_functions)}. "
                f"支持的函数列表: {', '.join(self.function_library.get_supported_function_names())}"
            )
    
    def _extract_parameters(self, expression: str) -> Dict[str, Any]:
        """
        提取表达式中的参数
        
        Args:
            expression: 表达式字符串
            
        Returns:
            Dict[str, Any]: 参数字典
        """
        parameters = {}
        
        # 提取数值常数
        numbers = re.findall(r'\b\d+\.?\d*\b', expression)
        for i, num in enumerate(numbers):
            try:
                if '.' in num:
                    parameters[f'const_{i}'] = float(num)
                else:
                    parameters[f'const_{i}'] = int(num)
            except ValueError:
                continue
        
        return parameters
    
    def get_expression_info(self, expression: str) -> Dict[str, Any]:
        """
        获取表达式的详细信息
        
        Args:
            expression: 表达式字符串
            
        Returns:
            Dict[str, Any]: 表达式信息
        """
        try:
            parsed = self.parse_expression(expression)
            
            # 分析复杂度
            complexity = self._analyze_complexity(expression)
            
            return {
                'expression': expression,
                'variables': parsed.variables,
                'parameters': parsed.parameters,
                'complexity': complexity,
                'is_valid': True,
                'estimated_execution_time': self._estimate_execution_time(complexity),
                'memory_usage': self._estimate_memory_usage(complexity)
            }
        except FunctionParseError as e:
            return {
                'expression': expression,
                'is_valid': False,
                'error': str(e),
                'variables': [],
                'parameters': {}
            }
    
    def _analyze_complexity(self, expression: str) -> Dict[str, Any]:
        """
        分析表达式复杂度
        
        Args:
            expression: 表达式字符串
            
        Returns:
            Dict[str, Any]: 复杂度信息
        """
        return {
            'length': len(expression),
            'function_count': len(re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*\s*\(', expression)),
            'operator_count': len(re.findall(r'[+\-*/^%]', expression)),
            'nesting_depth': self._get_nesting_depth(expression),
            'variable_count': len(set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', expression)))
        }
    
    def _estimate_execution_time(self, complexity: Dict[str, Any]) -> str:
        """
        估算执行时间
        
        Args:
            complexity: 复杂度信息
            
        Returns:
            str: 预估执行时间描述
        """
        score = (
            complexity['function_count'] * 2 +
            complexity['operator_count'] * 1 +
            complexity['nesting_depth'] * 3 +
            complexity['variable_count'] * 1
        )
        
        if score < 5:
            return "很快 (<1ms)"
        elif score < 20:
            return "快速 (1-10ms)"
        elif score < 50:
            return "中等 (10-100ms)"
        else:
            return "较慢 (>100ms)"
    
    def _estimate_memory_usage(self, complexity: Dict[str, Any]) -> str:
        """
        估算内存使用
        
        Args:
            complexity: 复杂度信息
            
        Returns:
            str: 预估内存使用描述
        """
        score = complexity['variable_count'] + complexity['function_count']
        
        if score < 3:
            return "低内存使用"
        elif score < 8:
            return "中等内存使用"
        else:
            return "高内存使用"
