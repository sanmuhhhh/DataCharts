#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据导入功能测试脚本
"""

import sys
import os
sys.path.append('shared')

from shared.interfaces import DataImporter
from shared.data_types import DataImportError

def test_data_import():
    """测试数据导入功能"""
    print("开始测试数据导入功能...")
    
    try:
        # 创建数据导入器
        importer = DataImporter()
        
        # 测试CSV文件导入
        print("\n1. 测试CSV文件导入")
        csv_data = importer.import_data(
            file_path="test_data/test_data.csv",
            format="csv",
            options={'separator': ',', 'header': 0}
        )
        print(f"77 CSV导入成功: {csv_data.content.shape[0]} 行, {csv_data.content.shape[1]} 列")
        print(f"  列名: {list(csv_data.content.columns)}")
        print(f"  数据类型: {importer.detect_data_type(csv_data)}")
        
        # 测试数据验证
        print("\n2. 测试数据验证")
        is_valid = importer.validate_data(csv_data)
        print(f"77 数据验证通过: {is_valid}")
        
        # 测试数据预处理
        print("\n3. 测试数据预处理")
        processed_data = importer.preprocess_data(csv_data)
        print(f"77 数据预处理成功: {processed_data.content.shape[0]} 行, {processed_data.content.shape[1]} 列")
        
        # 测试手动数据输入
        print("\n4. 测试手动数据输入")
        manual_data = importer.import_data(
            file_path="",
            format="manual",
            options={'data': [[1, 2, 'A'], [3, 4, 'B'], [5, 6, 'C']]}
        )
        print(f"77 手动数据导入成功: {manual_data.content.shape[0]} 行, {manual_data.content.shape[1]} 列")
        
        # 获取导入摘要
        print("\n5. 获取导入摘要")
        summary = importer._impl.get_import_summary(csv_data)
        print(f"77 导入摘要生成成功")
        print(f"  数据ID: {summary['data_id']}")
        print(f"  数据形状: {summary['shape']}")
        print(f"  检测类型: {summary['detected_type']}")
        
        print("\n73 所有数据导入测试通过！")
        return True
        
    except DataImportError as e:
        print(f"74 数据导入错误: {e}")
        return False
    except Exception as e:
        print(f"74 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_data_import()
    sys.exit(0 if success else 1)
