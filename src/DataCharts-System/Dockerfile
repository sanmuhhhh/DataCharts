# DataCharts System Dockerfile
FROM python:3.11-slim

# 设置工作目录
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

# 复制前端构建文件（如果存在）
COPY frontend/dist/ ./frontend/dist/ 2>/dev/null || echo "Frontend dist not found, skipping..."

# 创建必要的目录
RUN mkdir -p /app/data /app/logs /app/uploads

# 设置环境变量
ENV PYTHONPATH=/app:/app/shared:/app/backend
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DEBUG=false

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# 启动命令
CMD ["python", "backend/app/main.py"]
