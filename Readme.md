# DataCharts - 数据前处理与可视化工具

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt](https://img.shields.io/badge/PyQt-5%2F6-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

一个基于Python和PyQt开发的强大数据前处理与可视化工具，为用户提供直观的数据导入、处理、分析和可视化功能。

## 📋 项目简介

DataCharts是一个专业的数据前处理工具，旨在简化数据分析流程。通过友好的图形用户界面，用户可以轻松导入各种格式的数据文件，进行数据清洗和处理，并生成精美的可视化图表。该工具特别适合数据分析师、研究人员和学生使用。

## ✨ 主要功能

### 🔄 数据导入与处理
- **多格式支持**: 支持CSV、Excel、JSON、TXT等常见数据格式
- **批量导入**: 一次性导入多个数据文件
- **拖拽操作**: 便捷的文件拖拽导入方式
- **数据清洗**: 自动检测和处理缺失值、异常值
- **数据转换**: 灵活的数据类型转换和格式化

### 📊 可视化功能
- **多种图表**: 支持折线图、柱状图、散点图、饼图、热力图等
- **实时更新**: 数据变化时图表自动更新
- **样式自定义**: 丰富的图表样式和主题选择
- **多图表联动**: 支持多个图表之间的交互联动
- **高质量导出**: 支持多种格式的图表导出

### 🎛️ 动态交互
- **实时筛选**: 交互式数据筛选和过滤
- **参数调整**: 实时调整图表参数并查看效果
- **操作历史**: 完整的操作历史记录和撤销功能
- **快速恢复**: 一键恢复到任意历史状态

## 🛠️ 技术栈

- **编程语言**: Python 3.8+
- **GUI框架**: PyQt5/PyQt6
- **图表库**: PyQtChart
- **数据处理**: NumPy, Pandas
- **可视化**: Matplotlib (辅助)
- **文件处理**: OpenPyXL, XlsxWriter

## 📦 安装说明

### 环境要求
- Python 3.8 或更高版本
- 操作系统: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/sanmuhhhh/DataCharts.git
cd DataCharts
```

2. **创建虚拟环境** (推荐)
```bash
python -m venv venv
```

3. **激活虚拟环境**
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

4. **安装依赖**
```bash
pip install -r requirements.txt
```

5. **运行程序**
```bash
python main.py
```

### 依赖包清单 (requirements.txt)
```
# DataCharts 数据前处理工具依赖包

# GUI框架
PyQt5>=5.15.0
PyQtChart>=5.15.0

# 数据处理
numpy>=1.21.0
pandas>=1.3.0

# 文件处理
openpyxl>=3.0.0
chardet>=4.0.0

# 可视化支持 (备用)
matplotlib>=3.4.0 
```

## 🚀 快速开始

### 1. 启动应用
运行 `python main.py` 启动应用程序

### 2. 导入数据
- 点击"文件" -> "导入数据"
- 或直接拖拽文件到应用窗口
- 支持单个或批量导入

### 3. 数据预览
- 在左侧文件列表中选择数据文件
- 在数据预览区域查看数据内容
- 检查数据类型和统计信息

### 4. 创建图表
- 在控制面板选择图表类型
- 设置X轴和Y轴数据列
- 调整图表样式和参数
- 在主显示区域查看生成的图表

### 5. 动态交互
- 使用筛选器过滤数据
- 调整参数观察图表变化
- 使用缩放和平移功能详细查看

## 📖 使用指南

### 数据导入技巧
- **CSV文件**: 自动检测分隔符和编码格式
- **Excel文件**: 支持多工作表选择
- **大文件**: 采用分块加载，避免内存溢出
- **编码问题**: 自动检测文件编码，支持UTF-8、GBK等

### 图表创建指南
1. **选择合适的图表类型**
   - 时间序列数据 → 折线图
   - 分类数据比较 → 柱状图
   - 相关性分析 → 散点图
   - 比例展示 → 饼图
   - 数据分布 → 热力图

2. **优化图表显示**
   - 合理设置坐标轴范围
   - 选择合适的颜色主题
   - 添加标题和标签
   - 调整图例位置

### 性能优化建议
- 大数据集建议先进行数据采样
- 避免同时显示过多图表
- 定期清理不需要的数据文件
- 使用筛选功能减少显示数据量

## 🏗️ 项目结构

```
DataCharts/
├── main.py              # 应用程序入口文件
├── ui.py                # 用户界面模块
├── core.py              # 核心业务逻辑模块
├── requirements.txt     # 依赖包列表
├── README.md           # 项目说明文档
├── 基础设计方案.md      # 项目设计方案
└── LICENSE             # 许可证文件
```

### 文件说明

- **main.py**: 应用程序启动入口，负责初始化和启动主窗口
- **ui.py**: 包含所有用户界面相关的类和组件
  - MainWindow: 主窗口类
  - 数据导入、预览、图表显示等界面组件
  - 事件处理和界面交互逻辑
- **core.py**: 核心业务逻辑模块
  - DataProcessor: 数据处理和分析
  - ChartGenerator: 图表生成和管理
  - FileHandler: 文件读取和解析
  - DataValidator: 数据验证
  - DynamicController: 动态交互控制

## 🤝 贡献指南

我们欢迎任何形式的贡献！

### 如何贡献
1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

### 开发环境设置
```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
python -m pytest tests/

# 代码格式化
black src/
flake8 src/
```

## 📝 更新日志

### v1.0.0 (开发中)
- ✅ 基础GUI框架
- ✅ 数据导入功能
- ✅ 基本图表显示
- 🔄 数据处理功能 (进行中)
- ⏳ 动态交互功能 (计划中)

## 🐛 问题反馈

如果您在使用过程中遇到问题，请通过以下方式反馈：

- [GitHub Issues](https://github.com/your-username/DataCharts/issues)
- 邮箱: your-email@example.com

## 📄 许可证

本项目采用 MIT 许可证。详情请查看 [LICENSE](LICENSE) 文件。

## 🙏 致谢

感谢以下开源项目为本项目提供的支持：
- [PyQt](https://www.riverbankcomputing.com/software/pyqt/)
- [NumPy](https://numpy.org/)
- [Pandas](https://pandas.pydata.org/)
- [Matplotlib](https://matplotlib.org/)

## 📞 联系我们

- 项目主页: https://github.com/sanmuhhhh/DataCharts
- 讨论群组: [加入我们的QQ群/微信群]

---

**⭐ 如果这个项目对您有帮助，请给我们一个Star！**
