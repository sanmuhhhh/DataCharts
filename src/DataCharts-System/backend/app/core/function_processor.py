"""
函数处理器核心实现

整合表达式解析、安全执行等功能，提供统一的函数处理接口
"""

import sys
import os
from typing import List, Dict, Any

# 添加共享模块路径
shared_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared')
sys.path.insert(0, os.path.abspath(shared_path))

from data_types import FunctionExpression, ProcessingResult, DataSource, FunctionParseError
from algorithms.function_parser import ExpressionParser
from algorithms.function_library import FunctionLibrary
from algorithms.safe_executor import SafeExecutionEnvironment


class FunctionProcessor:
    """函数处理器核心类"""
    
    def __init__(self):
        """初始化函数处理器"""
        self.parser = ExpressionParser()
        self.library = FunctionLibrary()
        self.executor = SafeExecutionEnvironment()
    
    def parse_expression(self, expression: str) -> FunctionExpression:
        """
        解析函数表达式
        
        Args:
            expression: 函数表达式字符串
            
        Returns:
            FunctionExpression: 解析后的表达式对象
            
        Raises:
            FunctionParseError: 解析失败时抛出
        """
        try:
            return self.parser.parse_expression(expression)
        except Exception as e:
            raise FunctionParseError(f"表达式解析失败: {str(e)}")
    
    def validate_syntax(self, expression: str) -> bool:
        """
        验证函数表达式语法
        
        Args:
            expression: 函数表达式字符串
            
        Returns:
            bool: 语法是否正确
        """
        try:
            self.parser.parse_expression(expression)
            return True
        except (FunctionParseError, Exception):
            return False
    
    def apply_function(self, data: DataSource, expression: FunctionExpression) -> ProcessingResult:
        """
        将函数应用到数据源
        
        Args:
            data: 数据源
            expression: 函数表达式
            
        Returns:
            ProcessingResult: 处理结果
        """
        try:
            return self.executor.apply_function_to_data(
                data, expression.expression, expression.variables
            )
        except Exception as e:
            return ProcessingResult(
                data=None,
                processing_time=0.0,
                status="error",
                error_message=f"函数应用失败: {str(e)}"
            )
    
    def get_supported_functions(self) -> List[str]:
        """
        获取支持的函数列表
        
        Returns:
            List[str]: 支持的函数名列表
        """
        return self.library.get_supported_function_names()
    
    def get_function_categories(self) -> Dict[str, List[str]]:
        """
        获取函数分类信息
        
        Returns:
            Dict[str, List[str]]: 函数分类字典
        """
        return self.library.get_function_categories()
    
    def get_function_info(self, func_name: str) -> Dict[str, Any]:
        """
        获取特定函数的信息
        
        Args:
            func_name: 函数名
            
        Returns:
            Dict[str, Any]: 函数信息
        """
        try:
            return self.library.get_function_info(func_name)
        except KeyError:
            return {
                'name': func_name,
                'category': None,
                'documentation': '函数不存在',
                'is_available': False
            }
    
    def analyze_expression(self, expression: str) -> Dict[str, Any]:
        """
        分析表达式的详细信息
        
        Args:
            expression: 表达式字符串
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        try:
            # 获取解析信息
            parse_info = self.parser.get_expression_info(expression)
            
            # 获取安全性验证信息
            safety_info = self.executor.validate_expression_safety(expression)
            
            # 合并信息
            analysis = {
                **parse_info,
                'safety': safety_info,
                'recommendations': self._get_optimization_recommendations(parse_info)
            }
            
            return analysis
            
        except Exception as e:
            return {
                'expression': expression,
                'is_valid': False,
                'error': str(e),
                'safety': {'is_safe': False, 'issues': ['解析失败']},
                'recommendations': []
            }
    
    def _get_optimization_recommendations(self, parse_info: Dict[str, Any]) -> List[str]:
        """
        获取优化建议
        
        Args:
            parse_info: 解析信息
            
        Returns:
            List[str]: 优化建议列表
        """
        recommendations = []
        
        if 'complexity' in parse_info:
            complexity = parse_info['complexity']
            
            # 基于复杂度给出建议
            if complexity.get('function_count', 0) > 5:
                recommendations.append("表达式包含多个函数，考虑分解为多个步骤")
            
            if complexity.get('nesting_depth', 0) > 5:
                recommendations.append("表达式嵌套过深，建议简化")
            
            if complexity.get('length', 0) > 200:
                recommendations.append("表达式过长，建议使用中间变量")
        
        return recommendations
    
    def validate_function_with_data(self, expression: str, data: DataSource) -> Dict[str, Any]:
        """
        验证函数表达式是否可以应用到指定数据
        
        Args:
            expression: 函数表达式
            data: 数据源
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        try:
            # 解析表达式
            parsed = self.parse_expression(expression)
            
            # 检查变量是否存在于数据中
            df = data.content
            missing_variables = []
            available_variables = []
            
            for var in parsed.variables:
                if var in df.columns:
                    available_variables.append(var)
                elif var in ['index', 'pi', 'e']:
                    available_variables.append(var)
                elif var.startswith('col_') and var[4:].isdigit():
                    col_idx = int(var[4:])
                    if 0 <= col_idx < len(df.columns):
                        available_variables.append(var)
                    else:
                        missing_variables.append(var)
                else:
                    missing_variables.append(var)
            
            return {
                'is_valid': len(missing_variables) == 0,
                'available_variables': available_variables,
                'missing_variables': missing_variables,
                'data_columns': list(df.columns),
                'suggestions': self._get_variable_suggestions(missing_variables, df.columns)
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'error': str(e),
                'available_variables': [],
                'missing_variables': [],
                'data_columns': [],
                'suggestions': []
            }
    
    def _get_variable_suggestions(self, missing_vars: List[str], 
                                available_cols: List[str]) -> List[str]:
        """
        为缺失变量提供建议
        
        Args:
            missing_vars: 缺失的变量列表
            available_cols: 可用的列名列表
            
        Returns:
            List[str]: 建议列表
        """
        suggestions = []
        
        for var in missing_vars:
            # 寻找相似的列名
            similar_cols = [col for col in available_cols 
                          if var.lower() in col.lower() or col.lower() in var.lower()]
            
            if similar_cols:
                suggestions.append(f"变量 '{var}' 不存在，您是否想使用 '{similar_cols[0]}'?")
            else:
                suggestions.append(f"变量 '{var}' 不存在，请检查列名或使用 'col_N' 格式按索引访问")
        
        return suggestions
    
    def get_execution_environment_info(self) -> Dict[str, Any]:
        """
        获取执行环境信息
        
        Returns:
            Dict[str, Any]: 执行环境信息
        """
        return {
            'parser_info': {
                'supported_syntax': ['数学表达式', '函数调用', '变量引用'],
                'max_expression_length': 1000,
                'max_nesting_depth': 10
            },
            'library_info': {
                'total_functions': len(self.library.get_supported_function_names()),
                'categories': self.library.get_function_categories()
            },
            'executor_info': self.executor.get_execution_stats()
        }
    
    def test_function_execution(self, expression: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        测试函数执行
        
        Args:
            expression: 表达式
            test_data: 测试数据
            
        Returns:
            Dict[str, Any]: 测试结果
        """
        try:
            # 创建测试数据源
            import pandas as pd
            test_df = pd.DataFrame(test_data)
            test_source = DataSource(
                id="test",
                format="manual",
                content=test_df,
                metadata={}
            )
            
            # 解析并执行
            parsed = self.parse_expression(expression)
            result = self.apply_function(test_source, parsed)
            
            return {
                'success': result.status == "success",
                'result': result.data,
                'processing_time': result.processing_time,
                'error_message': result.error_message
            }
            
        except Exception as e:
            return {
                'success': False,
                'result': None,
                'processing_time': 0.0,
                'error_message': str(e)
            }
