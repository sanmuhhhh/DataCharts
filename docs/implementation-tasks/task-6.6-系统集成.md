# 任务 6.6: 系统集成

## 任务概述

完成DataCharts数据可视化系统的最终集成，包括前后端集成、桌面客户端与后端通信、性能优化、端到端测试和系统部署准备。

## 设计文档参考

- **第7节**: 数据流设计
- **第7.2节**: 系统交互流程
- **第8节**: 文件组织结构
- **第9节**: 开发计划
- **第10节**: 风险评估和缓解策略

## 功能需求分析

### 系统交互流程 (设计文档第7.2节)
```
前端/客户端请求 → API网关 → 业务逻辑层 → 数据处理层 → 存储层
       ↑                                                    ↓
结果返回 ← 图表生成 ← 数据计算 ← 函数执行 ← 数据获取
```

### 集成目标
1. **前后端集成**: Vue.js前端与FastAPI后端的完整通信
2. **桌面客户端集成**: PyQt6客户端与后端API的通信
3. **数据流集成**: 完整的数据处理流水线
4. **性能优化**: 系统整体性能调优
5. **部署准备**: 生产环境部署配置

## 实现要求

### 1. 前后端集成

#### API客户端服务
```typescript
// frontend/src/services/apiClient.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

class ApiClient {
  private instance: AxiosInstance
  private baseURL: string

  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL
    this.instance = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        // 添加认证头等
        const token = localStorage.getItem('auth_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        return response
      },
      (error) => {
        this.handleError(error)
        return Promise.reject(error)
      }
    )
  }

  private handleError(error: any) {
    if (error.response) {
      const status = error.response.status
      const message = error.response.data?.error_message || error.response.data?.detail || '请求失败'
      
      switch (status) {
        case 400:
          ElMessage.error(`请求错误: ${message}`)
          break
        case 401:
          ElMessage.error('未授权访问')
          // 重定向到登录页
          break
        case 403:
          ElMessage.error('禁止访问')
          break
        case 404:
          ElMessage.error('资源不存在')
          break
        case 500:
          ElMessage.error(`服务器错误: ${message}`)
          break
        default:
          ElMessage.error(`网络错误: ${message}`)
      }
    } else if (error.request) {
      ElMessage.error('网络连接失败，请检查网络设置')
    } else {
      ElMessage.error('请求配置错误')
    }
  }

  // 数据相关API
  async uploadData(file: File, options?: any): Promise<any> {
    const formData = new FormData()
    formData.append('file', file)
    if (options) {
      formData.append('options', JSON.stringify(options))
    }

    return this.instance.post('/api/data/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        // 处理上传进度
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total!)
        console.log(`上传进度: ${percentCompleted}%`)
      }
    })
  }

  async uploadManualData(content: string, format: string): Promise<any> {
    return this.instance.post('/api/data/manual', {
      content,
      format,
      options: {}
    })
  }

  async getData(dataId: string): Promise<any> {
    return this.instance.get(`/api/data/${dataId}`)
  }

  async processData(dataId: string, options: any): Promise<any> {
    return this.instance.post('/api/data/process', {
      data_id: dataId,
      preprocess_options: options
    })
  }

  // 函数相关API
  async parseFunction(expression: string): Promise<any> {
    return this.instance.post('/api/function/parse', {
      expression
    })
  }

  async applyFunction(dataId: string, expression: string): Promise<any> {
    return this.instance.post('/api/function/apply', {
      data_id: dataId,
      expression
    })
  }

  async getFunctionLibrary(): Promise<any> {
    return this.instance.get('/api/function/library')
  }

  // 图表相关API
  async createChart(dataId: string, chartType: string, config: any): Promise<any> {
    return this.instance.post('/api/chart/create', {
      data_id: dataId,
      chart_type: chartType,
      config
    })
  }

  async getChart(chartId: string): Promise<any> {
    return this.instance.get(`/api/chart/${chartId}`)
  }

  async updateChart(chartId: string, dataId?: string, config?: any): Promise<any> {
    return this.instance.put(`/api/chart/${chartId}`, {
      data_id: dataId,
      config
    })
  }

  async exportChart(chartId: string, format: string = 'png'): Promise<Blob> {
    const response = await this.instance.get(`/api/chart/${chartId}/export`, {
      params: { format },
      responseType: 'blob'
    })
    return response.data
  }

  // 系统相关API
  async getSystemInfo(): Promise<any> {
    return this.instance.get('/api/system/info')
  }

  async healthCheck(): Promise<any> {
    return this.instance.get('/health')
  }
}

export const apiClient = new ApiClient()
export default ApiClient
```

#### 状态管理集成
```typescript
// frontend/src/store/dataStore.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/services/apiClient'
import type { DataSource, ProcessingResult } from '@/types'

export const useDataStore = defineStore('data', () => {
  // 状态
  const datasets = ref<Map<string, DataSource>>(new Map())
  const currentDataId = ref<string | null>(null)
  const processing = ref(false)
  const uploadProgress = ref(0)

  // 计算属性
  const currentData = computed(() => {
    return currentDataId.value ? datasets.value.get(currentDataId.value) : null
  })

  const dataList = computed(() => {
    return Array.from(datasets.value.values())
  })

  // 操作
  const uploadData = async (file: File, options?: any) => {
    processing.value = true
    uploadProgress.value = 0

    try {
      const response = await apiClient.uploadData(file, options)
      const dataSource: DataSource = response.data

      datasets.value.set(dataSource.data_id, dataSource)
      currentDataId.value = dataSource.data_id

      return dataSource
    } finally {
      processing.value = false
      uploadProgress.value = 0
    }
  }

  const uploadManualData = async (content: string, format: string) => {
    processing.value = true

    try {
      const response = await apiClient.uploadManualData(content, format)
      const dataSource: DataSource = response.data

      datasets.value.set(dataSource.data_id, dataSource)
      currentDataId.value = dataSource.data_id

      return dataSource
    } finally {
      processing.value = false
    }
  }

  const processData = async (dataId: string, options: any) => {
    processing.value = true

    try {
      const response = await apiClient.processData(dataId, options)
      const result: ProcessingResult = response.data

      // 更新处理后的数据
      if (result.status === 'success') {
        const processedData: DataSource = {
          data_id: result.result_id,
          format: 'processed',
          content: result.data,
          metadata: { processed_from: dataId, ...result }
        }

        datasets.value.set(processedData.data_id, processedData)
        return processedData
      }

      throw new Error(result.error_message || '数据处理失败')
    } finally {
      processing.value = false
    }
  }

  const setCurrentData = (dataId: string) => {
    if (datasets.value.has(dataId)) {
      currentDataId.value = dataId
    }
  }

  const removeData = (dataId: string) => {
    datasets.value.delete(dataId)
    if (currentDataId.value === dataId) {
      currentDataId.value = null
    }
  }

  return {
    // 状态
    datasets,
    currentDataId,
    processing,
    uploadProgress,

    // 计算属性
    currentData,
    dataList,

    // 操作
    uploadData,
    uploadManualData,
    processData,
    setCurrentData,
    removeData
  }
})
```

### 2. 桌面客户端与后端通信

#### API通信模块
```python
# desktop/src/core/api_client.py
import requests
import json
from typing import Dict, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal, QThread
import logging

class ApiClient(QObject):
    """API客户端，负责与后端通信"""
    
    # 信号定义
    request_started = pyqtSignal(str)  # 请求开始
    request_finished = pyqtSignal(str, dict)  # 请求完成
    request_error = pyqtSignal(str, str)  # 请求错误
    upload_progress = pyqtSignal(int)  # 上传进度

    def __init__(self, base_url: str = "http://localhost:8000"):
        super().__init__()
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'DataCharts-Desktop/0.1.0'
        })
        
        # 设置超时
        self.timeout = 30
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """发起HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            self.request_started.emit(f"{method} {endpoint}")
            
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            response.raise_for_status()
            result = response.json() if response.content else {}
            
            self.request_finished.emit(f"{method} {endpoint}", result)
            return result
            
        except requests.exceptions.Timeout:
            error_msg = "请求超时"
            self.request_error.emit(f"{method} {endpoint}", error_msg)
            return None
            
        except requests.exceptions.ConnectionError:
            error_msg = "连接失败，请检查后端服务是否启动"
            self.request_error.emit(f"{method} {endpoint}", error_msg)
            return None
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP错误: {e.response.status_code}"
            try:
                error_detail = e.response.json().get('detail', str(e))
                error_msg += f" - {error_detail}"
            except:
                pass
            self.request_error.emit(f"{method} {endpoint}", error_msg)
            return None
            
        except Exception as e:
            error_msg = f"请求失败: {str(e)}"
            self.request_error.emit(f"{method} {endpoint}", error_msg)
            return None

    # 数据相关API
    def upload_file(self, file_path: str, file_format: str = None) -> Optional[Dict[str, Any]]:
        """上传文件"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.split('/')[-1], f, 'application/octet-stream')}
                
                # 临时移除Content-Type头以支持multipart/form-data
                original_headers = self.session.headers.copy()
                del self.session.headers['Content-Type']
                
                response = self.session.post(
                    f"{self.base_url}/api/data/upload",
                    files=files,
                    timeout=self.timeout
                )
                
                # 恢复原始头
                self.session.headers = original_headers
                
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            self.request_error.emit("POST /api/data/upload", str(e))
            return None

    def upload_manual_data(self, content: str, format: str) -> Optional[Dict[str, Any]]:
        """上传手动输入的数据"""
        return self._make_request(
            'POST',
            '/api/data/manual',
            json={
                'content': content,
                'format': format,
                'options': {}
            }
        )

    def get_data(self, data_id: str) -> Optional[Dict[str, Any]]:
        """获取数据"""
        return self._make_request('GET', f'/api/data/{data_id}')

    def process_data(self, data_id: str, options: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """处理数据"""
        return self._make_request(
            'POST',
            '/api/data/process',
            json={
                'data_id': data_id,
                'preprocess_options': options
            }
        )

    # 函数相关API
    def parse_function(self, expression: str) -> Optional[Dict[str, Any]]:
        """解析函数表达式"""
        return self._make_request(
            'POST',
            '/api/function/parse',
            json={'expression': expression}
        )

    def apply_function(self, data_id: str, expression: str) -> Optional[Dict[str, Any]]:
        """应用函数"""
        return self._make_request(
            'POST',
            '/api/function/apply',
            json={
                'data_id': data_id,
                'expression': expression
            }
        )

    def get_function_library(self) -> Optional[Dict[str, Any]]:
        """获取函数库"""
        return self._make_request('GET', '/api/function/library')

    # 图表相关API
    def create_chart(self, data_id: str, chart_type: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建图表"""
        return self._make_request(
            'POST',
            '/api/chart/create',
            json={
                'data_id': data_id,
                'chart_type': chart_type,
                'config': config
            }
        )

    def get_chart(self, chart_id: str) -> Optional[Dict[str, Any]]:
        """获取图表"""
        return self._make_request('GET', f'/api/chart/{chart_id}')

    def export_chart(self, chart_id: str, format: str = 'png') -> Optional[bytes]:
        """导出图表"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/chart/{chart_id}/export",
                params={'format': format},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.content
        except Exception as e:
            self.request_error.emit(f"GET /api/chart/{chart_id}/export", str(e))
            return None

    # 系统相关API
    def health_check(self) -> Optional[Dict[str, Any]]:
        """健康检查"""
        return self._make_request('GET', '/health')

    def get_system_info(self) -> Optional[Dict[str, Any]]:
        """获取系统信息"""
        return self._make_request('GET', '/api/system/info')


class AsyncApiWorker(QThread):
    """异步API调用工作线程"""
    
    result_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)

    def __init__(self, api_client: ApiClient, method_name: str, *args, **kwargs):
        super().__init__()
        self.api_client = api_client
        self.method_name = method_name
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """执行API调用"""
        try:
            method = getattr(self.api_client, self.method_name)
            result = method(*self.args, **self.kwargs)
            self.result_ready.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))
```

### 3. 数据流集成和优化

#### 数据流管理器
```python
# shared/data_processing/flow_manager.py
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import asyncio
import time
import logging

@dataclass
class FlowStep:
    """数据流步骤"""
    step_id: str
    step_type: str  # 'import', 'process', 'function', 'chart'
    input_data: Any
    parameters: Dict[str, Any]
    status: str = 'pending'  # 'pending', 'running', 'completed', 'failed'
    result: Any = None
    error_message: str = None
    execution_time: float = 0.0

class DataFlowManager:
    """数据流管理器"""
    
    def __init__(self):
        self.flows = {}  # flow_id -> List[FlowStep]
        self.processors = {
            'import': self._process_import,
            'process': self._process_data,
            'function': self._process_function,
            'chart': self._process_chart
        }
        
    async def create_flow(self, flow_id: str, steps: List[FlowStep]) -> bool:
        """创建数据流"""
        try:
            # 验证步骤依赖关系
            if not self._validate_flow(steps):
                return False
                
            self.flows[flow_id] = steps
            return True
            
        except Exception as e:
            logging.error(f"创建数据流失败: {e}")
            return False
            
    async def execute_flow(self, flow_id: str) -> Dict[str, Any]:
        """执行数据流"""
        if flow_id not in self.flows:
            return {"status": "error", "message": "数据流不存在"}
            
        steps = self.flows[flow_id]
        results = []
        total_time = 0
        
        try:
            for step in steps:
                start_time = time.time()
                step.status = 'running'
                
                # 执行步骤
                processor = self.processors.get(step.step_type)
                if not processor:
                    step.status = 'failed'
                    step.error_message = f"不支持的步骤类型: {step.step_type}"
                    continue
                
                try:
                    step.result = await processor(step.input_data, step.parameters)
                    step.status = 'completed'
                except Exception as e:
                    step.status = 'failed'
                    step.error_message = str(e)
                
                step.execution_time = time.time() - start_time
                total_time += step.execution_time
                
                results.append({
                    "step_id": step.step_id,
                    "status": step.status,
                    "execution_time": step.execution_time,
                    "error_message": step.error_message
                })
                
                # 如果步骤失败且不允许继续，停止执行
                if step.status == 'failed':
                    break
            
            # 检查整体执行状态
            failed_steps = [r for r in results if r["status"] == "failed"]
            overall_status = "failed" if failed_steps else "completed"
            
            return {
                "status": overall_status,
                "total_time": total_time,
                "steps": results,
                "failed_steps": len(failed_steps)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "total_time": total_time
            }
    
    def _validate_flow(self, steps: List[FlowStep]) -> bool:
        """验证数据流的有效性"""
        # 检查步骤顺序和依赖关系
        step_types = [step.step_type for step in steps]
        
        # 基本验证：数据导入应该在最前面
        if step_types and step_types[0] != 'import':
            return False
            
        # 其他验证逻辑...
        return True
        
    async def _process_import(self, input_data: Any, parameters: Dict[str, Any]) -> Any:
        """处理数据导入步骤"""
        from ..interfaces import DataImporter
        
        importer = DataImporter()
        return await importer.import_data(
            input_data,
            parameters.get('format'),
            parameters.get('options', {})
        )
        
    async def _process_data(self, input_data: Any, parameters: Dict[str, Any]) -> Any:
        """处理数据预处理步骤"""
        from ..interfaces import DataImporter
        
        importer = DataImporter()
        return await importer.preprocess_data(input_data)
        
    async def _process_function(self, input_data: Any, parameters: Dict[str, Any]) -> Any:
        """处理函数应用步骤"""
        from ..interfaces import FunctionProcessor
        
        processor = FunctionProcessor()
        expression = processor.parse_expression(parameters.get('expression'))
        return await processor.apply_function(input_data, expression)
        
    async def _process_chart(self, input_data: Any, parameters: Dict[str, Any]) -> Any:
        """处理图表生成步骤"""
        from ..interfaces import ChartGenerator
        from ..data_types import ChartConfig
        
        generator = ChartGenerator()
        config = ChartConfig(**parameters.get('config', {}))
        return await generator.create_chart(input_data, config)
```

### 4. 性能优化

#### 缓存机制
```python
# backend/app/core/cache.py
import redis
import json
import pickle
from typing import Any, Optional
import hashlib
from core.config import get_settings

settings = get_settings()

class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=False
        ) if settings.USE_REDIS else None
        
        self.local_cache = {}  # 本地缓存
        self.max_local_cache_size = 1000
        
    def _generate_key(self, prefix: str, *args) -> str:
        """生成缓存键"""
        key_data = f"{prefix}:{':'.join(map(str, args))}"
        return hashlib.md5(key_data.encode()).hexdigest()
        
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            if self.redis_client:
                data = self.redis_client.get(key)
                return pickle.loads(data) if data else None
            else:
                return self.local_cache.get(key)
        except Exception:
            return None
            
    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """设置缓存"""
        try:
            if self.redis_client:
                serialized = pickle.dumps(value)
                return self.redis_client.setex(key, expire, serialized)
            else:
                # 本地缓存大小限制
                if len(self.local_cache) >= self.max_local_cache_size:
                    # 移除最旧的缓存项
                    oldest_key = next(iter(self.local_cache))
                    del self.local_cache[oldest_key]
                    
                self.local_cache[key] = value
                return True
        except Exception:
            return False
            
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            if self.redis_client:
                return bool(self.redis_client.delete(key))
            else:
                return self.local_cache.pop(key, None) is not None
        except Exception:
            return False

# 缓存装饰器
def cached(prefix: str = "default", expire: int = 3600):
    """缓存装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            cache = CacheManager()
            
            # 生成缓存键
            cache_key = cache._generate_key(prefix, func.__name__, *args, **kwargs)
            
            # 尝试从缓存获取
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result
                
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 保存到缓存
            await cache.set(cache_key, result, expire)
            
            return result
        return wrapper
    return decorator
```

#### 异步处理优化
```python
# backend/app/core/async_processor.py
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Callable, Any, List
import multiprocessing

class AsyncProcessor:
    """异步处理器"""
    
    def __init__(self):
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.process_pool = ProcessPoolExecutor(max_workers=multiprocessing.cpu_count())
        
    async def run_in_thread(self, func: Callable, *args, **kwargs) -> Any:
        """在线程池中执行函数"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.thread_pool, func, *args, **kwargs)
        
    async def run_in_process(self, func: Callable, *args, **kwargs) -> Any:
        """在进程池中执行函数"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.process_pool, func, *args, **kwargs)
        
    async def batch_process(self, func: Callable, items: List[Any], batch_size: int = 10) -> List[Any]:
        """批量处理"""
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            # 创建任务
            tasks = [self.run_in_thread(func, item) for item in batch]
            
            # 等待批量完成
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            results.extend(batch_results)
            
        return results
        
    def cleanup(self):
        """清理资源"""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
```

### 5. 部署配置

#### Docker配置
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制后端代码
COPY backend/ ./backend/
COPY shared/ ./shared/

# 安装Python依赖
RUN pip install --no-cache-dir -r backend/requirements.txt

# 复制前端构建文件
COPY frontend/dist/ ./frontend/dist/

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "backend/app/main.py"]
```

#### Docker Compose配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  datacharts-backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - REDIS_HOST=redis
      - DATABASE_URL=postgresql://user:password@postgres:5432/datacharts
    depends_on:
      - redis
      - postgres
    volumes:
      - ./data:/app/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=datacharts
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./frontend/dist:/usr/share/nginx/html
    depends_on:
      - datacharts-backend

volumes:
  redis_data:
  postgres_data:
```

### 6. 端到端测试

#### 集成测试套件
```python
# tests/test_integration.py
import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestEndToEndFlow:
    """端到端流程测试"""
    
    def test_complete_data_visualization_flow(self):
        """测试完整的数据可视化流程"""
        
        # 1. 上传数据
        with open("test_data.csv", "rb") as f:
            upload_response = client.post(
                "/api/data/upload",
                files={"file": ("test_data.csv", f, "text/csv")}
            )
        
        assert upload_response.status_code == 200
        data_info = upload_response.json()
        data_id = data_info["data_id"]
        
        # 2. 应用函数处理
        function_response = client.post(
            "/api/function/apply",
            json={
                "data_id": data_id,
                "expression": "mean(x)"
            }
        )
        
        assert function_response.status_code == 200
        function_result = function_response.json()
        processed_data_id = function_result["result_id"]
        
        # 3. 创建图表
        chart_response = client.post(
            "/api/chart/create",
            json={
                "data_id": processed_data_id,
                "chart_type": "line",
                "config": {
                    "title": "测试图表",
                    "x_axis": "X轴",
                    "y_axis": "Y轴"
                }
            }
        )
        
        assert chart_response.status_code == 200
        chart_info = chart_response.json()
        chart_id = chart_info["chart_id"]
        
        # 4. 导出图表
        export_response = client.get(f"/api/chart/{chart_id}/export?format=png")
        assert export_response.status_code == 200
        assert export_response.headers["content-type"] == "image/png"
        
    def test_error_handling_flow(self):
        """测试错误处理流程"""
        
        # 测试无效数据ID
        response = client.post(
            "/api/function/apply",
            json={
                "data_id": "invalid-id",
                "expression": "mean(x)"
            }
        )
        assert response.status_code == 404
        
        # 测试无效函数表达式
        response = client.post(
            "/api/function/parse",
            json={"expression": "invalid_function(x)"}
        )
        assert response.status_code == 200
        result = response.json()
        assert result["is_valid"] == False

class TestPerformance:
    """性能测试"""
    
    def test_large_file_upload(self):
        """测试大文件上传"""
        # 创建测试大文件
        import pandas as pd
        large_data = pd.DataFrame({
            'x': range(100000),
            'y': range(100000)
        })
        large_data.to_csv("large_test_data.csv", index=False)
        
        # 上传测试
        with open("large_test_data.csv", "rb") as f:
            response = client.post(
                "/api/data/upload",
                files={"file": ("large_test_data.csv", f, "text/csv")}
            )
        
        assert response.status_code == 200
        
    def test_concurrent_requests(self):
        """测试并发请求"""
        import threading
        results = []
        
        def make_request():
            response = client.get("/health")
            results.append(response.status_code)
        
        # 创建多个并发线程
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有请求都成功
        assert all(status == 200 for status in results)
        assert len(results) == 10
```

## 实现文件清单

### 新建文件
1. `frontend/src/services/apiClient.ts`
2. `frontend/src/store/dataStore.ts`
3. `frontend/src/store/chartStore.ts`
4. `desktop/src/core/api_client.py`
5. `desktop/src/core/async_worker.py`
6. `shared/data_processing/flow_manager.py`
7. `backend/app/core/cache.py`
8. `backend/app/core/async_processor.py`
9. `backend/app/core/performance.py`
10. `tests/test_integration.py`
11. `tests/test_performance.py`
12. `Dockerfile`
13. `docker-compose.yml`
14. `nginx.conf`
15. `deploy/production.env`

### 更新文件
1. `backend/app/main.py` - 添加性能中间件
2. `frontend/src/main.ts` - 集成API客户端
3. `desktop/src/main.py` - 集成API通信

## 成功标准

### 功能集成标准
- 73 前后端完全集成，数据流畅通
- 73 桌面客户端与后端正常通信
- 73 完整的用户操作流程可用
- 73 错误处理机制完善
- 73 数据持久化正常工作

### 性能标准
- 73 API响应时间 <500ms (简单请求)
- 73 大文件处理时间 <5分钟 (100MB)
- 73 并发用户支持 >50人
- 73 内存使用稳定 <2GB
- 73 CPU使用率正常 <80%

### 部署标准
- 73 Docker容器化成功
- 73 生产环境配置完整
- 73 监控和日志系统正常
- 73 自动化部署流程

### 测试标准
- 73 端到端测试通过率 100%
- 73 集成测试覆盖率 >90%
- 73 性能测试达标
- 73 压力测试通过

## 依赖关系

### 前置依赖
- 73 任务6.1-6.5 全部完成
- 73 所有核心功能实现完毕
- 73 单元测试全部通过

### 交付成果
- 73 完整可部署的系统
- 73 完整的用户文档
- 73 部署和运维指南
- 73 测试报告

## 估时和里程碑

### 总工期: 2天

#### 第1天
- **上午**: 前后端集成和API通信
- **下午**: 桌面客户端集成和数据流优化

#### 第2天
- **上午**: 性能优化和缓存机制
- **下午**: 部署配置和端到端测试

### 关键里程碑
- **M1**: 基础集成完成 (1天)
- **M2**: 完整系统集成和部署就绪 (2天)

## 风险管控

### 集成风险
- **风险**: 前后端接口不匹配
- **缓解**: 严格按照API文档开发，早期集成测试

### 性能风险
- **风险**: 大数据处理性能不达标
- **缓解**: 分块处理，异步优化，缓存机制

### 部署风险
- **风险**: 生产环境配置问题
- **缓解**: 使用Docker统一环境，完整的部署文档

## 总结

任务6.6完成系统的最终集成，确保DataCharts数据可视化系统作为一个完整的产品可以正常运行、部署和维护。这个任务是整个项目的收官之作，需要确保所有组件协调工作，用户体验流畅，系统性能稳定。