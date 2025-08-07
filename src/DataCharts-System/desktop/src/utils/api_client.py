"""
API客户端模块

提供与后端服务通信的功能
"""

import requests
import json
from typing import Optional, Dict, Any, List
from PyQt6.QtCore import QObject, pyqtSignal, QThread


class APIClient(QObject):
    """API客户端类"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        super().__init__()
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def test_connection(self) -> Dict[str, Any]:
        """测试与后端的连接"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "连接成功",
                    "data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "message": f"服务器响应错误: {response.status_code}"
                }
        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "message": "无法连接到后端服务，请确保服务已启动"
            }
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": "连接超时"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"连接失败: {str(e)}"
            }
    
    def get_api_info(self) -> Dict[str, Any]:
        """获取API信息"""
        try:
            response = self.session.get(f"{self.base_url}/api/info", timeout=5)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "message": f"获取API信息失败: {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"获取API信息失败: {str(e)}"
            }
    
    def upload_data(self, data: Any, file_info: Dict = None) -> Dict[str, Any]:
        """上传数据到后端"""
        try:
            payload = {
                "data": data,
                "file_info": file_info or {},
                "timestamp": str(self.get_current_timestamp())
            }
            
            response = self.session.post(
                f"{self.base_url}/api/data/upload",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "message": f"数据上传失败: {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"数据上传失败: {str(e)}"
            }
    
    def process_data(self, data: Any, processing_config: Dict) -> Dict[str, Any]:
        """处理数据"""
        try:
            payload = {
                "data": data,
                "config": processing_config
            }
            
            response = self.session.post(
                f"{self.base_url}/api/data/process",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "message": f"数据处理失败: {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"数据处理失败: {str(e)}"
            }
    
    def parse_function(self, expression: str) -> Dict[str, Any]:
        """解析函数表达式"""
        try:
            payload = {
                "expression": expression
            }
            
            response = self.session.post(
                f"{self.base_url}/api/function/parse",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "message": f"函数解析失败: {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"函数解析失败: {str(e)}"
            }
    
    def apply_function(self, expression: str, data: Any, variables: List = None) -> Dict[str, Any]:
        """应用函数到数据"""
        try:
            payload = {
                "expression": expression,
                "data": data,
                "variables": variables or []
            }
            
            response = self.session.post(
                f"{self.base_url}/api/function/apply",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "message": f"函数应用失败: {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"函数应用失败: {str(e)}"
            }
    
    def create_chart(self, chart_config: Dict) -> Dict[str, Any]:
        """创建图表"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/chart/create",
                json=chart_config,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "message": f"图表创建失败: {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"图表创建失败: {str(e)}"
            }
    
    def export_chart(self, chart_id: str, export_format: str = "png") -> Dict[str, Any]:
        """导出图表"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/chart/{chart_id}/export",
                params={"format": export_format},
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "data": response.content if export_format in ["png", "jpg", "svg"] else response.json()
                }
            else:
                return {
                    "status": "error",
                    "message": f"图表导出失败: {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"图表导出失败: {str(e)}"
            }
    
    def get_current_timestamp(self):
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


class APIWorker(QThread):
    """API调用工作线程"""
    
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, api_client: APIClient, method: str, *args, **kwargs):
        super().__init__()
        self.api_client = api_client
        self.method = method
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        """执行API调用"""
        try:
            self.progress.emit(10)
            
            # 获取API客户端方法
            api_method = getattr(self.api_client, self.method)
            if not api_method:
                self.error.emit(f"未找到API方法: {self.method}")
                return
            
            self.progress.emit(50)
            
            # 调用API方法
            result = api_method(*self.args, **self.kwargs)
            self.progress.emit(100)
            
            if result.get("status") == "success":
                self.finished.emit(result)
            else:
                self.error.emit(result.get("message", "API调用失败"))
                
        except Exception as e:
            self.error.emit(f"API调用异常: {str(e)}")


class APIManager(QObject):
    """API管理器"""
    
    connection_tested = pyqtSignal(object)
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        super().__init__()
        self.api_client = APIClient(base_url)
        self.is_connected = False
    
    def test_connection_async(self):
        """异步测试连接"""
        self.worker = APIWorker(self.api_client, "test_connection")
        self.worker.finished.connect(self._on_connection_tested)
        self.worker.error.connect(self._on_connection_error)
        self.worker.start()
    
    def _on_connection_tested(self, result):
        """连接测试完成"""
        self.is_connected = result.get("status") == "success"
        self.connection_tested.emit(result)
    
    def _on_connection_error(self, error_msg):
        """连接测试失败"""
        self.is_connected = False
        self.connection_tested.emit({
            "status": "error",
            "message": error_msg
        })
    
    def get_client(self) -> APIClient:
        """获取API客户端"""
        return self.api_client
    
    def is_backend_available(self) -> bool:
        """检查后端是否可用"""
        return self.is_connected
