from fastapi import APIRouter, HTTPException
import platform
import sys
import os
import time

router = APIRouter()

@router.get("/info")
async def get_system_info():
    try:
        return {
            "system": {
                "platform": platform.system(),
                "python_version": platform.python_version(),
                "architecture": platform.architecture()[0]
            },
            "application": {
                "name": "DataCharts System",
                "version": "0.1.0",
                "status": "running"
            }
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to get system info: {str(e)}")

@router.get("/health")
async def health_check():
    try:
        return {
            "status": "healthy",
            "service": "DataCharts Backend",
            "version": "0.1.0",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    except Exception as e:
        raise HTTPException(500, f"健康检查 failed: {str(e)}")

@router.get("/version")
async def get_version():
    try:
        return {
            "application": {
                "name": "DataCharts System",
                "version": "0.1.0"
            },
            "api": {
                "version": "v1",
                "documentation": "/docs"
            }
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to get version: {str(e)}")
