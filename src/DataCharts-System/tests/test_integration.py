# -*- coding: utf-8 -*-
"""
端到端集成测试

测试完整的数据可视化流程
"""

import pytest
import requests
import time
import os
import tempfile
import csv
from io import StringIO

# 测试配置
API_BASE_URL = "http://localhost:8000"
TEST_DATA_DIR = "test_data"


class TestEndToEndFlow:
    """端到端流程测试"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        cls.base_url = API_BASE_URL
        cls.session = requests.Session()
        
        # 创建测试数据
        cls.create_test_data()
        
        # 等待服务启动
        cls.wait_for_service()
    
    @classmethod
    def create_test_data(cls):
        """创建测试数据文件"""
        os.makedirs(TEST_DATA_DIR, exist_ok=True)
        
        # 创建CSV测试数据
        csv_data = [
            ['x', 'y', 'category'],
            [1, 2, 'A'],
            [2, 4, 'B'],
            [3, 6, 'A'],
            [4, 8, 'B'],
            [5, 10, 'A']
        ]
        
        with open(f"{TEST_DATA_DIR}/test_data.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(csv_data)
    
    @classmethod
    def wait_for_service(cls, timeout=30):
        """等待服务启动"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{cls.base_url}/health", timeout=5)
                if response.status_code == 200:
                    print("73 服务已启动")
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        
        raise Exception("74 服务启动超时")
    
    def test_health_check(self):
        """测试健康检查"""
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
    
    def test_system_info(self):
        """测试系统信息"""
        response = requests.get(f"{self.base_url}/api/system/info")
        assert response.status_code == 200
        
        data = response.json()
        assert "system" in data
        assert "application" in data
        assert data["application"]["name"] == "DataCharts System"
    
    def test_complete_data_visualization_flow(self):
        """测试完整的数据可视化流程"""
        
        # 1. 上传数据文件
        print("92 步骤1: 上传数据文件...")
        with open(f"{TEST_DATA_DIR}/test_data.csv", 'rb') as f:
            files = {'file': ('test_data.csv', f, 'text/csv')}
            upload_response = requests.post(
                f"{self.base_url}/api/data/upload",
                files=files
            )
        
        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        assert upload_data["status"] == "success"
        data_id = upload_data["data_id"]
        print(f"73 数据上传成功，ID: {data_id}")
        
        # 2. 获取数据预览
        print("98 步骤2: 获取数据预览...")
        preview_response = requests.get(f"{self.base_url}/api/data/{data_id}/preview")
        assert preview_response.status_code == 200
        
        preview_data = preview_response.json()
        assert preview_data["status"] == "success"
        assert "preview" in preview_data
        print("73 数据预览获取成功")
        
        # 3. 获取函数库
        print("92 步骤3: 获取函数库...")
        library_response = requests.get(f"{self.base_url}/api/function/library")
        assert library_response.status_code == 200
        
        library_data = library_response.json()
        assert library_data["status"] == "success"
        assert "supported_functions" in library_data
        print("73 函数库获取成功")
        
        # 4. 解析函数表达式
        print("93 步骤4: 解析函数表达式...")
        parse_response = requests.post(
            f"{self.base_url}/api/function/parse",
            json={"expression": "mean(x) + std(y)"}
        )
        assert parse_response.status_code == 200
        
        parse_data = parse_response.json()
        assert parse_data["status"] == "success"
        assert parse_data["is_valid"] == True
        print("73 函数表达式解析成功")
        
        # 5. 应用函数到数据
        print("73 步骤5: 应用函数到数据...")
        apply_response = requests.post(
            f"{self.base_url}/api/function/apply",
            json={
                "data_id": data_id,
                "expression": "mean(x)"
            }
        )
        assert apply_response.status_code == 200
        
        apply_data = apply_response.json()
        assert apply_data["status"] == "success"
        result_id = apply_data["result_id"]
        print(f"73 函数应用成功，结果ID: {result_id}")
        
        # 6. 获取支持的图表类型
        print("96 步骤6: 获取图表类型...")
        types_response = requests.get(f"{self.base_url}/api/chart/types")
        assert types_response.status_code == 200
        
        types_data = types_response.json()
        assert types_data["status"] == "success"
        assert "chart_types" in types_data
        print("73 图表类型获取成功")
        
        # 7. 创建图表
        print("96 步骤7: 创建图表...")
        chart_response = requests.post(
            f"{self.base_url}/api/chart/create",
            json={
                "data_id": data_id,
                "chart_type": "line",
                "config": {
                    "title": "集成测试图表",
                    "x_axis": "X轴",
                    "y_axis": "Y轴",
                    "width": 800,
                    "height": 600
                }
            }
        )
        assert chart_response.status_code == 200
        
        chart_data = chart_response.json()
        assert chart_data["status"] == "success"
        chart_id = chart_data["chart_id"]
        print(f"73 图表创建成功，ID: {chart_id}")
        
        # 8. 获取图表详情
        print("97 步骤8: 获取图表详情...")
        get_chart_response = requests.get(f"{self.base_url}/api/chart/{chart_id}")
        assert get_chart_response.status_code == 200
        
        get_chart_data = get_chart_response.json()
        assert get_chart_data["status"] == "success"
        assert get_chart_data["chart_id"] == chart_id
        print("73 图表详情获取成功")
        
        # 9. 导出图表
        print("97 步骤9: 导出图表...")
        export_response = requests.get(f"{self.base_url}/api/chart/{chart_id}/export?format=png")
        assert export_response.status_code == 200
        assert len(export_response.content) > 0
        print("73 图表导出成功")
        
        # 10. 列出所有数据
        print("95 步骤10: 列出所有数据...")
        list_data_response = requests.get(f"{self.base_url}/api/data/")
        assert list_data_response.status_code == 200
        
        list_data = list_data_response.json()
        assert "items" in list_data
        print("73 数据列表获取成功")
        
        # 11. 列出所有图表
        print("94 步骤11: 列出所有图表...")
        list_charts_response = requests.get(f"{self.base_url}/api/chart/")
        assert list_charts_response.status_code == 200
        
        list_charts = list_charts_response.json()
        assert "items" in list_charts
        print("73 图表列表获取成功")
        
        print("95 完整数据可视化流程测试通过！")
    
    def test_manual_data_upload(self):
        """测试手动数据上传"""
        manual_data = """x,y,z
1,2,3
4,5,6
7,8,9"""
        
        response = requests.post(
            f"{self.base_url}/api/data/manual",
            json={
                "content": manual_data,
                "format": "csv",
                "options": {}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data_id" in data
    
    def test_error_handling(self):
        """测试错误处理"""
        
        # 测试无效数据ID
        response = requests.get(f"{self.base_url}/api/data/invalid-id")
        assert response.status_code == 200  # 我们的API返回200但包含错误信息
        
        # 测试无效函数表达式
        response = requests.post(
            f"{self.base_url}/api/function/parse",
            json={"expression": "invalid_function((((("}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error" or data["is_valid"] == False
    
    def test_concurrent_requests(self):
        """测试并发请求"""
        import threading
        import concurrent.futures
        
        def make_health_request():
            response = requests.get(f"{self.base_url}/health")
            return response.status_code
        
        # 创建10个并发请求
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_health_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # 验证所有请求都成功
        assert all(status == 200 for status in results)
        assert len(results) == 10
    
    @classmethod
    def teardown_class(cls):
        """测试类清理"""
        # 清理测试数据
        import shutil
        if os.path.exists(TEST_DATA_DIR):
            shutil.rmtree(TEST_DATA_DIR)


class TestPerformance:
    """性能测试"""
    
    def test_api_response_time(self):
        """测试API响应时间"""
        start_time = time.time()
        response = requests.get(f"{API_BASE_URL}/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 2.0  # 应该在2秒内响应
        
        print(f"73 API响应时间: {response_time:.3f}秒")
    
    def test_function_library_performance(self):
        """测试函数库性能"""
        start_time = time.time()
        response = requests.get(f"{API_BASE_URL}/api/function/library")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 1.0  # 应该在1秒内响应
        
        print(f"73 函数库响应时间: {response_time:.3f}秒")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
