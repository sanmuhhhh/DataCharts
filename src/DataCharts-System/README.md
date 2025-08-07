# DataCharts 数据可视化系统

## 项目概述

DataCharts 是一个智能数据可视化系统，支持多端交互，用户可以通过导入数据、输入函数或矩阵，自动生成相应的图表展示。

## 系统架构

```
DataCharts-System/
├── frontend/           # Vue.js 前端应用
├── backend/            # Python FastAPI 后端服务
├── desktop/            # PyQt6 桌面客户端
├── shared/             # 共享代码模块
├── tests/              # 测试文件
└── docs/               # 项目文档
```

## 技术栈

### 前端 (Vue.js)
- Vue 3 + TypeScript
- Element Plus UI 组件库
- ECharts / Chart.js 图表库
- Pinia 状态管理
- Vite 构建工具

### 后端 (Python)
- FastAPI 框架
- NumPy, Pandas 数据处理
- SymPy 函数解析
- Matplotlib, Plotly 图表生成
- SQLite 数据存储

### 桌面客户端 (PyQt6)
- PyQt6 GUI 框架
- PyQt-Charts 图表组件
- NumPy, Pandas 数据处理

## 快速开始

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

### 后端开发

```bash
cd backend
pip install -r requirements.txt
python app/main.py
```

### 桌面客户端

```bash
cd desktop
pip install -r requirements.txt
python src/main.py
```

## 核心功能

- 73 数据导入（CSV、Excel、JSON等格式）
- 73 函数表达式解析和处理
- 73 多种图表类型生成
- 73 矩阵数据可视化
- 73 跨平台支持

## 开发状态

当前版本：v0.1.0

- [x] 项目架构设计
- [x] 基础框架代码生成
- [ ] 核心功能实现
- [ ] 用户界面完善
- [ ] 测试和优化

## 贡献指南

1. Fork 本仓库
2. 创建特性分支
3. 提交更改
4. 发起 Pull Request

## 许可证

MIT License

## 联系我们

DataCharts Team