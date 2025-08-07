"""
数据可视化系统后端主文件

根据设计文档规范提供数据处理和API服务
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from typing import Dict, Any

# 添加共享模块路径
shared_path = os.path.join(os.path.dirname(__file__), '..', '..', 'shared')
sys.path.insert(0, shared_path)

try:
    import interfaces
    import data_types
    from interfaces import *
    from data_types import *
except ImportError as e:
    # 导入共享模块失败时创建占位符以确保应用可以启动
    print(f"警告: 导入共享模块失败: {e}")
    pass

app = FastAPI(
    title="DataCharts System API",
    description="数据可视化系统API接口",
    version="0.1.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "DataCharts System API",
        "version": "0.1.0",
        "description": "数据可视化系统API服务"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "DataCharts Backend"}


@app.get("/api/info")
async def api_info():
    """API信息"""
    return {
        "name": "DataCharts System API",
        "version": "0.1.0",
        "endpoints": [
            "/api/data/upload",
            "/api/data/process",
            "/api/chart/create",
            "/api/chart/export"
        ]
    }


# 包含API路由
try:
    # 添加当前目录到路径
    current_dir = os.path.dirname(__file__)
    sys.path.insert(0, current_dir)
    
    from api.routes.data import router as data_router
    from api.routes.function import router as function_router
    from api.routes.chart import router as chart_router
    from api.routes.system import router as system_router
    
    app.include_router(data_router, prefix="/api/data", tags=["数据管理"])
    app.include_router(function_router, prefix="/api/function", tags=["函数处理"])
    app.include_router(chart_router, prefix="/api/chart", tags=["图表生成"])
    app.include_router(system_router, prefix="/api/system", tags=["系统管理"])
    
    print("所有API路由已加载")
except ImportError as e:
    print(f"警告: API路由加载失败: {e}")
    
    # 提供占位符API端点
    @app.post("/api/data/upload")
    async def upload_data():
        """数据上传API端点（占位符）"""
        return {"message": "数据上传接口", "status": "实现待完成"}

    @app.post("/api/data/process")
    async def process_data():
        """数据处理API端点（占位符）"""
        return {"message": "数据处理接口", "status": "实现待完成"}


@app.post("/api/function/parse")
async def parse_function():
    """函数解析API端点"""
    # 实现待完成
    return {"message": "函数解析接口", "status": "实现待完成"}


@app.post("/api/function/apply")
async def apply_function():
    """函数应用API端点"""
    # 实现待完成
    return {"message": "函数应用接口", "status": "实现待完成"}


@app.post("/api/chart/create")
async def create_chart():
    """图表创建API端点"""
    # 实现待完成
    return {"message": "图表创建接口", "status": "实现待完成"}


@app.get("/api/chart/{chart_id}/export")
async def export_chart(chart_id: str):
    """图表导出API端点"""
    # 实现待完成
    return {"message": f"图表导出接口 - ID: {chart_id}", "status": "实现待完成"}


# 基础测试
if __name__ == "__main__":
    import uvicorn
    print("DataCharts System Backend v0.1.0 启动中...")
    uvicorn.run(app, host="0.0.0.0", port=8000)