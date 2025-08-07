#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
函数处理功能测试脚本
"""

import sys
import os
sys.path.append('shared')

from shared.interfaces import FunctionProcessor
from shared.data_types import DataImportError, FunctionParseError, DataSource
import pandas as pd

def test_function_processor():
    """测试函数处理功能"""
    print("开始测试函数处理功能...")
    
    try:
        # 创建函数处理器
        processor = FunctionProcessor()
        
        # 创建测试数据
        test_data = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [2, 4, 6, 8, 10],
            'z': [1, 4, 9, 16, 25]
        })
        
        test_source = DataSource(
            id="test_func",
            format="manual",
            content=test_data,
            metadata={}
        )
        
        # 测试1：基础数学表达式解析
        print("\n1. 测试基础数学表达式解析")
        expression1 = "x + y"
        parsed1 = processor.parse_expression(expression1)
        print(f"77 表达式解析成功: {expression1}")
        print(f"  变量: {parsed1.variables}")
        print(f"  参数: {parsed1.parameters}")
        
        # 测试2：复杂函数表达式解析
        print("\n2. 测试复杂函数表达式解析")
        expression2 = "sin(x) + cos(y) * 2"
        parsed2 = processor.parse_expression(expression2)
        print(f"77 复杂表达式解析成功: {expression2}")
        print(f"  变量: {parsed2.variables}")
        
        # 测试3：语法验证
        print("\n3. 测试语法验证")
        valid_expr = "sqrt(x**2 + y**2)"
        invalid_expr = "x + y +"
        
        is_valid1 = processor.validate_syntax(valid_expr)
        is_valid2 = processor.validate_syntax(invalid_expr)
        print(f"77 语法验证 '{valid_expr}': {is_valid1}")
        print(f"77 语法验证 '{invalid_expr}': {is_valid2}")
        
        # 测试4：函数应用
        print("\n4. 测试函数应用")
        result = processor.apply_function(test_source, parsed1)
        print(f"77 函数应用结果: {result.status}")
        if result.status == "success":
            print(f"  处理时间: {result.processing_time:.4f}秒")
            print(f"  结果类型: {type(result.data)}")
        else:
            print(f"  错误信息: {result.error_message}")
        
        # 测试5：获取支持的函数列表
        print("\n5. 测试获取支持的函数列表")
        functions = processor.get_supported_functions()
        print(f"77 支持的函数数量: {len(functions)}")
        print(f"  前10个函数: {functions[:10]}")
        
        # 测试6：表达式分析
        print("\n6. 测试表达式分析")
        analysis = processor.analyze_expression("sin(x) + cos(y)**2 + log(z)")
        print(f"77 表达式分析成功")
        print(f"  是否有效: {analysis.get('is_valid', False)}")
        print(f"  复杂度: {analysis.get('complexity', {})}")
        
        # 测试7：与数据验证
        print("\n7. 测试函数与数据验证")
        validation = processor.validate_function_with_data("x + y", test_source)
        print(f"77 函数验证结果: {validation['is_valid']}")
        print(f"  可用变量: {validation['available_variables']}")
        print(f"  缺失变量: {validation['missing_variables']}")
        
        print("\n73 所有函数处理测试通过！")
        return True
        
    except Exception as e:
        print(f"74 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_function_processor()
    sys.exit(0 if success else 1)
