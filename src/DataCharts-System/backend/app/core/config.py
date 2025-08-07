# -*- coding: utf-8 -*-
"""
应用配置管理

提供系统配置和环境变量管理
"""

import os
from typing import List

class Settings:
    """应用设置类"""
    
    # API配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # API文档配置
    API_TITLE: str = "DataCharts System API"
    API_DESCRIPTION: str = "数据可视化系统RESTful API服务"
    API_VERSION: str = "0.1.0"
    
    # CORS配置
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ]
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "uploads"
    ALLOWED_EXTENSIONS: List[str] = [".csv", ".xlsx", ".xls", ".json", ".txt"]
    
    # 安全配置
    SECRET_KEY: str = "datacharts-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 数据库配置 (可选)
    DATABASE_URL: str = "sqlite:///./datacharts.db"
    
    def __init__(self):
        """初始化配置，支持环境变量覆盖"""
        # 从环境变量读取配置
        self.HOST = os.getenv("HOST", self.HOST)
        self.PORT = int(os.getenv("PORT", self.PORT))
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"
        
        # 安全相关
        self.SECRET_KEY = os.getenv("SECRET_KEY", self.SECRET_KEY)
        
        # 文件上传相关
        self.MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", self.MAX_FILE_SIZE))
        self.UPLOAD_DIR = os.getenv("UPLOAD_DIR", self.UPLOAD_DIR)
        
        # 确保上传目录存在
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)


# 全局设置实例
_settings = None

def get_settings() -> Settings:
    """获取应用设置单例"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
