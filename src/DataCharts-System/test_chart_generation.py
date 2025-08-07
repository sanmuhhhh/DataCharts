#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图表生成功能测试脚本
"""

import sys
import os
sys.path.append('shared')

from shared.interfaces import ChartGenerator
from shared.data_types import DataSource, ChartConfig, ChartGenerationError
import pandas as pd

def test_chart_generation():
    """测试图表生成功能"""
    print("开始测试图表生成功能...")
    
    try:
        # 创建图表生成器
        generator = ChartGenerator()
        
        # 创建测试数据
        test_data = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [2, 4, 6, 8, 10],
            'z': [1, 4, 9, 16, 25]
        })
        
        test_source = DataSource(
            id="test_chart",
            format="manual", 
            content=test_data,
            metadata={}
        )
        
        # 测试1：折线图生成
        print("\n1. 测试折线图生成")
        line_config = ChartConfig(
            chart_type="line",
            title="测试折线图",
            x_axis="X轴",
            y_axis="Y轴",
            width=800,
            height=600,
            options={"show_grid": True, "line_tension": 0.3}
        )
        
        line_chart_id = generator.create_chart(test_source, line_config)
        print(f"77 折线图创建成功，ID: {line_chart_id}")
        
        # 测试2：柱状图生成
        print("\n2. 测试柱状图生成")
        bar_config = ChartConfig(
            chart_type="bar",
            title="测试柱状图",
            x_axis="类别",
            y_axis="数值",
            width=800,
            height=600,
            options={"show_data_labels": True}
        )
        
        bar_chart_id = generator.create_chart(test_source, bar_config)
        print(f"77 柱状图创建成功，ID: {bar_chart_id}")
        
        # 测试3：散点图生成
        print("\n3. 测试散点图生成")
        scatter_config = ChartConfig(
            chart_type="scatter",
            title="测试散点图",
            x_axis="X数据",
            y_axis="Y数据",
            width=800,
            height=600,
            options={"point_radius": 6}
        )
        
        scatter_chart_id = generator.create_chart(test_source, scatter_config)
        print(f"77 散点图创建成功，ID: {scatter_chart_id}")
        
        # 测试4：饼图生成
        print("\n4. 测试饼图生成")
        pie_data = pd.DataFrame({
            'category': ['A', 'B', 'C', 'D'],
            'value': [30, 25, 20, 25]
        })
        
        pie_source = DataSource(
            id="test_pie",
            format="manual",
            content=pie_data,
            metadata={}
        )
        
        pie_config = ChartConfig(
            chart_type="pie",
            title="测试饼图",
            x_axis="",
            y_axis="",
            width=600,
            height=600,
            options={"legend_position": "right"}
        )
        
        pie_chart_id = generator.create_chart(pie_source, pie_config)
        print(f"77 饼图创建成功，ID: {pie_chart_id}")
        
        # 测试5：图表导出
        print("\n5. 测试图表导出")
        exported_data = generator.export_chart(line_chart_id, "json")
        print(f"77 图表导出成功，数据大小: {len(exported_data)} 字节")
        
        # 测试6：图表更新
        print("\n6. 测试图表更新")
        new_data = pd.DataFrame({
            'x': [6, 7, 8, 9, 10],
            'y': [12, 14, 16, 18, 20],
            'z': [36, 49, 64, 81, 100]
        })
        
        new_source = DataSource(
            id="updated_data",
            format="manual",
            content=new_data,
            metadata={}
        )
        
        update_success = generator.update_chart(line_chart_id, new_source)
        print(f"77 图表更新结果: {update_success}")
        
        # 测试7：获取图表管理统计信息
        print("\n7. 测试图表管理器状态")
        if hasattr(generator, '_manager'):
            stats = generator._manager.get_statistics()
            print(f"77 图表统计信息:")
            print(f"  总图表数: {stats['total_charts']}")
            print(f"  图表类型: {stats['chart_types']}")
            print(f"  支持的类型: {stats['supported_types']}")
        
        print("\n73 所有图表生成测试通过！")
        return True
        
    except Exception as e:
        print(f"74 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chart_generation()
    sys.exit(0 if success else 1)
