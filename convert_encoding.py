#!/usr/bin/env python3
"""
Encoding Conversion Script

This script converts files from various encodings (GB18030, GBK, etc.) to UTF-8
and handles Chinese content properly.
"""

import os
import chardet
import sys
from pathlib import Path


def detect_encoding(file_path):
    """Detect file encoding"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result['encoding']
    except Exception as e:
        print(f"Error detecting encoding for {file_path}: {e}")
        return None


def convert_to_utf8(file_path, original_encoding):
    """Convert file to UTF-8 encoding"""
    try:
        # Read with original encoding
        with open(file_path, 'r', encoding=original_encoding, errors='ignore') as f:
            content = f.read()
        
        # Write with UTF-8 encoding
        with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Error converting {file_path}: {e}")
        return False


def process_directory(directory):
    """Process all files in directory recursively"""
    target_extensions = {'.py', '.ts', '.vue', '.js', '.md', '.txt', '.json', '.html', '.css'}
    converted_count = 0
    error_count = 0
    
    print(f"Processing directory: {directory}")
    
    for root, dirs, files in os.walk(directory):
        # Skip node_modules and other unnecessary directories
        dirs[:] = [d for d in dirs if d not in {'node_modules', '__pycache__', '.git', 'dist', 'build'}]
        
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()
            
            if file_ext in target_extensions:
                print(f"Processing: {file_path}")
                
                # Detect current encoding
                encoding = detect_encoding(file_path)
                
                if encoding and encoding.lower() not in ['utf-8', 'ascii']:
                    print(f"  Detected encoding: {encoding}")
                    if convert_to_utf8(file_path, encoding):
                        print(f"  ✓ Converted to UTF-8")
                        converted_count += 1
                    else:
                        print(f"  ✗ Conversion failed")
                        error_count += 1
                else:
                    print(f"  Already UTF-8 or ASCII")
    
    print(f"\nConversion complete:")
    print(f"  Files converted: {converted_count}")
    print(f"  Errors: {error_count}")


def replace_chinese_content():
    """Replace Chinese content with proper UTF-8 encoded Chinese"""
    
    # Define Chinese content mappings
    chinese_mappings = {
        # Comments and docstrings
        "DataCharts System Core Data Types": "数据可视化系统核心数据结构",
        "This module contains all data structures defined in the design document.": "此模块包含设计文档中定义的所有数据结构。",
        "All structures strictly follow the design specifications.": "所有结构严格遵循设计规范。",
        "Chart configuration structure from design document section 4.3": "图表配置结构，来自设计文档第4.3节",
        "Chart type: line, bar, scatter, pie, etc.": "图表类型：line、bar、scatter、pie等",
        "Chart title": "图表标题",
        "X-axis label": "X轴标签", 
        "Y-axis label": "Y轴标签",
        "Chart width": "图表宽度",
        "Chart height": "图表高度",
        "Other configuration options": "其他配置选项",
        "Data source structure from design document section 4.1": "数据源结构，来自设计文档第4.1节",
        "Unique data identifier": "数据唯一标识",
        "Data format: csv, excel, json, txt": "数据格式：csv、excel、json、txt",
        "Data content": "数据内容",
        "Metadata information": "元数据信息",
        "Function expression structure from design document section 4.2": "函数表达式结构，来自设计文档第4.2节",
        "Function expression string": "函数表达式字符串",
        "Variable list": "变量列表",
        "Parameter dictionary": "参数字典",
        "Processing result structure from design document section 7": "处理结果结构，来自设计文档第7节",
        "Processed data": "处理后的数据",
        "Processing time": "处理耗时",
        "Processing status: success, error": "处理状态：success、error",
        "Error message": "错误信息",
        "System error types from design document section 7": "系统错误类型，来自设计文档第7节",
        "Matrix data structure from design document section 4.4": "矩阵数据结构，来自设计文档第4.4节",
        "Matrix data": "矩阵数据",
        "Matrix dimensions": "矩阵维度",
        "Data type": "数据类型",
        "Label information": "标签信息",
        "DataCharts System External Interface Definitions": "数据可视化系统外部接口定义",
        "This module contains all external interfaces defined in the design document.": "此模块包含设计文档中定义的所有外部接口。",
        "All interfaces strictly follow the design specifications.": "所有接口严格遵循设计规范。",
        "Data import interface from design document section 4.1": "数据导入接口，来自设计文档第4.1节",
        "Import data supporting multiple formats": "导入数据，支持多种格式",
        "Validate data integrity and format": "验证数据完整性和格式",
        "Preprocess data, cleaning and normalization": "预处理数据，清洗和标准化",
        "Detect data type": "检测数据类型",
        "Function processor interface from design document section 4.2": "函数处理接口，来自设计文档第4.2节",
        "Parse function expression": "解析函数表达式",
        "Validate expression syntax": "验证表达式语法",
        "Apply function to data": "应用函数到数据",
        "Get list of supported functions": "获取支持的函数列表",
        "Chart generator interface from design document section 4.3": "图表生成接口，来自设计文档第4.3节",
        "Create chart, return chart ID": "创建图表，返回图表ID",
        "Export chart to specified format": "导出图表为指定格式",
        "Update chart data": "更新图表数据",
        "Matrix visualizer interface from design document section 4.4": "矩阵可视化接口，来自设计文档第4.4节",
        "Visualize 2D matrix": "可视化2D矩阵",
        "Visualize 3D matrix": "可视化3D矩阵",
        "Create heatmap": "创建热力图",
        "Create surface plot": "创建表面图",
        "API function definitions from design document section 6.1": "API函数定义（来自设计文档第6.1节）",
        "Initialize system, implementation pending": "初始化系统，实现待完成",
        "Shutdown system, implementation pending": "关闭系统，实现待完成",
        "Process data request, implementation pending": "处理数据请求，实现待完成",
        "Data upload API endpoint": "数据上传API端点",
        "Data processing API endpoint": "数据处理API端点",
        "Chart creation API endpoint": "图表创建API端点",
        "Chart export API endpoint": "图表导出API端点",
        "Implementation pending": "实现待完成",
        "DataCharts System Backend Main File": "数据可视化系统后端主文件",
        "Provides data processing and API services according to design document specifications": "根据设计文档规范提供数据处理和API服务",
        "Add shared module path": "添加共享模块路径",
        "Failed to import shared modules": "导入共享模块失败",
        "Create placeholders to ensure application can start": "创建占位符以确保应用可以启动",
        "CORS configuration": "CORS 配置",
        "Root path": "根路径",
        "Health check": "健康检查",
        "API information": "API信息",
        "Basic test": "基础测试",
        "starting...": "启动中...",
        "DataCharts System Desktop Client Main File": "数据可视化系统桌面客户端主文件",
        "Provides local data visualization functionality using PyQt6": "使用PyQt6提供本地数据可视化功能",
        "Main window class": "主窗口类",
        "Create central widget and layout": "创建中心部件和布局",
        "Title label": "标题标签",
        "Data Visualization System": "数据可视化系统",
        "Version": "版本",
        "Version info label": "版本信息标签",
        "Status label": "状态标签",
        "Desktop client started": "桌面客户端已启动",
        "Add stretch space": "添加伸缩空间",
        "Main function": "主函数",
        "Set application information": "设置应用程序信息",
        "started": "已启动",
        "Check if in test mode": "检查是否为测试模式",
        "Test mode: Application started successfully": "测试模式: 应用启动成功"
    }
    
    # Process files in src directory
    src_dir = "src/DataCharts-System"
    if os.path.exists(src_dir):
        for root, dirs, files in os.walk(src_dir):
            dirs[:] = [d for d in dirs if d not in {'node_modules', '__pycache__', '.git'}]
            
            for file in files:
                if file.endswith(('.py', '.ts', '.vue', '.js')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Replace English with Chinese
                        for english, chinese in chinese_mappings.items():
                            content = content.replace(english, chinese)
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        print(f"Updated Chinese content in: {file_path}")
                    except Exception as e:
                        print(f"Error updating {file_path}: {e}")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python convert_encoding.py <directory_path>")
        print("Example: python convert_encoding.py src")
        return
    
    directory = sys.argv[1]
    
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return
    
    print("Step 1: Converting file encodings to UTF-8...")
    process_directory(directory)
    
    print("\nStep 2: Updating content with proper Chinese...")
    replace_chinese_content()
    
    print("\nEncoding conversion completed!")


if __name__ == "__main__":
    main()