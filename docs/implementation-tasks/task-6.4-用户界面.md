# 任务 6.4: 用户界面实现

## 任务概述

实现DataCharts数据可视化系统的用户界面，包括Vue.js前端Web应用和PyQt6桌面客户端，提供完整的用户交互体验。

## 设计文档参考

- **第5节**: 用户界面设计
- **第5.1节**: 主界面布局
- **第5.2节**: 功能流程设计
- **第3.1节**: 前端技术栈 (Vue.js)
- **第3.3节**: 客户端技术栈 (PyQt)

## 功能需求分析

### 主界面布局 (设计文档第5.1节)
```
┌─────────────────────────────────────────────────────────┐
│  DataCharts - 数据可视化系统                           │
├─────────────────────────────────────────────────────────┤
│ [数据导入] [函数处理] [图表配置] [导出] [帮助]          │
├─────────────────┬───────────────────────────────────────┤
│                 │                                       │
│   数据操作面板   │           图表展示区域                │
│                 │                                       │
│ □ 导入数据      │     ┌─────────────────────────┐       │
│ □ 数据预览      │     │                         │       │
│ □ 函数输入      │     │      生成的图表         │       │
│ □ 参数设置      │     │                         │       │
│ □ 算法选择      │     └─────────────────────────┘       │
│                 │                                       │
├─────────────────┼───────────────────────────────────────┤
│   控制台日志    │           状态栏                      │
└─────────────────┴───────────────────────────────────────┘
```

### 用户操作流程 (设计文档第5.2节)
1. 启动应用 → 选择工作模式（在线/离线）
2. 数据导入 → 选择数据源 → 数据验证 → 数据预览
3. 数据处理 → 输入函数表达式 → 参数配置 → 处理执行
4. 图表生成 → 选择图表类型 → 样式配置 → 生成图表
5. 结果导出 → 选择导出格式 → 保存文件

## Vue.js 前端实现

### 1. 项目结构优化

#### 更新的目录结构
```
frontend/src/
├── components/          # 组件
│   ├── common/         # 通用组件
│   ├── data/          # 数据相关组件
│   ├── chart/         # 图表相关组件
│   ├── function/      # 函数相关组件
│   └── layout/        # 布局组件
├── views/             # 页面视图
├── store/             # 状态管理
├── services/          # API服务
├── utils/             # 工具函数
├── styles/            # 样式文件
└── types/             # TypeScript类型定义
```

### 2. 主要组件实现

#### 主布局组件 (Layout)
```vue
<!-- src/components/layout/MainLayout.vue -->
<template>
  <el-container class="main-container">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-content">
        <h1 class="title">DataCharts - 数据可视化系统</h1>
        <div class="nav-buttons">
          <el-button-group>
            <el-button @click="activeTab = 'data'" :type="activeTab === 'data' ? 'primary' : 'default'">
              数据导入
            </el-button>
            <el-button @click="activeTab = 'function'" :type="activeTab === 'function' ? 'primary' : 'default'">
              函数处理
            </el-button>
            <el-button @click="activeTab = 'chart'" :type="activeTab === 'chart' ? 'primary' : 'default'">
              图表配置
            </el-button>
            <el-button @click="showExportDialog = true">导出</el-button>
            <el-button @click="showHelpDialog = true">帮助</el-button>
          </el-button-group>
        </div>
      </div>
    </el-header>

    <!-- 主内容区 -->
    <el-container class="main-content">
      <!-- 左侧操作面板 -->
      <el-aside width="350px" class="sidebar">
        <el-card class="operation-panel">
          <template #header>
            <span>数据操作面板</span>
          </template>
          
          <!-- 数据导入面板 -->
          <DataImportPanel v-if="activeTab === 'data'" @data-imported="handleDataImported" />
          
          <!-- 函数处理面板 -->
          <FunctionPanel v-if="activeTab === 'function'" :data="currentData" @function-applied="handleFunctionApplied" />
          
          <!-- 图表配置面板 -->
          <ChartConfigPanel v-if="activeTab === 'chart'" :data="processedData" @chart-created="handleChartCreated" />
        </el-card>
      </el-aside>

      <!-- 主显示区域 -->
      <el-main class="main-display">
        <el-card class="chart-area">
          <template #header>
            <span>图表展示区域</span>
          </template>
          
          <!-- 图表显示 -->
          <ChartRenderer v-if="currentChart" :chart-data="currentChart" />
          
          <!-- 欢迎页面 -->
          <WelcomePage v-else />
        </el-card>
      </el-main>
    </el-container>

    <!-- 底部状态栏 -->
    <el-footer height="60px" class="footer">
      <div class="footer-content">
        <div class="console-log">
          <el-tag v-for="log in logs" :key="log.id" :type="log.type" class="log-item">
            {{ log.message }}
          </el-tag>
        </div>
        <div class="status-bar">
          <span>状态: {{ systemStatus }}</span>
          <span>版本: v0.1.0</span>
        </div>
      </div>
    </el-footer>
  </el-container>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import DataImportPanel from '@/components/data/DataImportPanel.vue'
import FunctionPanel from '@/components/function/FunctionPanel.vue'
import ChartConfigPanel from '@/components/chart/ChartConfigPanel.vue'
import ChartRenderer from '@/components/chart/ChartRenderer.vue'
import WelcomePage from '@/components/common/WelcomePage.vue'

const activeTab = ref('data')
const currentData = ref(null)
const processedData = ref(null)
const currentChart = ref(null)
const systemStatus = ref('就绪')
const logs = reactive([])

const handleDataImported = (data) => {
  currentData.value = data
  systemStatus.value = '数据已导入'
  logs.push({ id: Date.now(), type: 'success', message: '数据导入成功' })
}

const handleFunctionApplied = (result) => {
  processedData.value = result
  systemStatus.value = '数据处理完成'
  logs.push({ id: Date.now(), type: 'info', message: '函数处理完成' })
}

const handleChartCreated = (chart) => {
  currentChart.value = chart
  systemStatus.value = '图表生成完成'
  logs.push({ id: Date.now(), type: 'success', message: '图表生成成功' })
}
</script>
```

#### 数据导入面板
```vue
<!-- src/components/data/DataImportPanel.vue -->
<template>
  <div class="data-import-panel">
    <el-steps :active="currentStep" direction="vertical" class="import-steps">
      <el-step title="选择数据源" />
      <el-step title="上传文件" />
      <el-step title="数据预览" />
      <el-step title="数据验证" />
    </el-steps>

    <!-- 步骤1: 选择数据源 -->
    <div v-if="currentStep === 0" class="step-content">
      <h4>选择数据格式</h4>
      <el-radio-group v-model="selectedFormat" class="format-options">
        <el-radio label="csv">CSV文件</el-radio>
        <el-radio label="excel">Excel文件</el-radio>
        <el-radio label="json">JSON文件</el-radio>
        <el-radio label="txt">文本文件</el-radio>
        <el-radio label="manual">手动输入</el-radio>
      </el-radio-group>
      
      <el-button type="primary" @click="nextStep" :disabled="!selectedFormat" class="next-btn">
        下一步
      </el-button>
    </div>

    <!-- 步骤2: 上传文件 -->
    <div v-if="currentStep === 1" class="step-content">
      <h4>上传数据文件</h4>
      
      <el-upload
        v-if="selectedFormat !== 'manual'"
        drag
        :auto-upload="false"
        :on-change="handleFileSelect"
        :accept="getAcceptedTypes()"
        class="upload-area"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 {{ getFormatDescription() }} 格式文件
          </div>
        </template>
      </el-upload>

      <!-- 手动输入模式 -->
      <div v-else class="manual-input">
        <el-input
          v-model="manualData"
          type="textarea"
          :rows="10"
          placeholder="请输入数据，支持CSV格式..."
        />
      </div>

      <div class="step-buttons">
        <el-button @click="prevStep">上一步</el-button>
        <el-button type="primary" @click="uploadData" :disabled="!canUpload" :loading="uploading">
          上传数据
        </el-button>
      </div>
    </div>

    <!-- 步骤3: 数据预览 -->
    <div v-if="currentStep === 2" class="step-content">
      <h4>数据预览</h4>
      
      <el-table :data="previewData" max-height="300" class="preview-table">
        <el-table-column
          v-for="(column, index) in dataColumns"
          :key="index"
          :prop="column"
          :label="column"
          width="120"
        />
      </el-table>

      <div class="data-info">
        <el-descriptions :column="2" size="small">
          <el-descriptions-item label="数据行数">{{ dataRows }}</el-descriptions-item>
          <el-descriptions-item label="数据列数">{{ dataColumns.length }}</el-descriptions-item>
          <el-descriptions-item label="文件大小">{{ fileSize }}</el-descriptions-item>
          <el-descriptions-item label="数据格式">{{ selectedFormat.toUpperCase() }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <div class="step-buttons">
        <el-button @click="prevStep">上一步</el-button>
        <el-button type="primary" @click="nextStep">下一步</el-button>
      </div>
    </div>

    <!-- 步骤4: 数据验证 -->
    <div v-if="currentStep === 3" class="step-content">
      <h4>数据验证</h4>
      
      <el-result
        :icon="validationResult.status === 'success' ? 'success' : 'warning'"
        :title="validationResult.title"
        :sub-title="validationResult.message"
      >
        <template #extra>
          <div v-if="validationResult.issues.length > 0" class="validation-issues">
            <h5>发现的问题：</h5>
            <el-alert
              v-for="issue in validationResult.issues"
              :key="issue.id"
              :title="issue.message"
              :type="issue.type"
              show-icon
              class="issue-alert"
            />
          </div>
          
          <div class="step-buttons">
            <el-button @click="prevStep">返回修改</el-button>
            <el-button type="primary" @click="finishImport" :disabled="!canFinishImport">
              完成导入
            </el-button>
          </div>
        </template>
      </el-result>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { dataService } from '@/services/dataService'

const emit = defineEmits(['data-imported'])

const currentStep = ref(0)
const selectedFormat = ref('')
const selectedFile = ref(null)
const manualData = ref('')
const uploading = ref(false)
const previewData = ref([])
const dataColumns = ref([])
const dataRows = ref(0)
const fileSize = ref('')
const validationResult = ref({
  status: 'success',
  title: '数据验证通过',
  message: '数据格式正确，可以进行后续处理',
  issues: []
})

// 计算属性
const canUpload = computed(() => {
  return selectedFormat.value === 'manual' ? manualData.value.trim() !== '' : selectedFile.value !== null
})

const canFinishImport = computed(() => {
  return validationResult.value.status === 'success' || validationResult.value.issues.every(issue => issue.type !== 'error')
})

// 方法
const nextStep = () => {
  if (currentStep.value < 3) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const getAcceptedTypes = () => {
  const types = {
    csv: '.csv',
    excel: '.xlsx,.xls',
    json: '.json',
    txt: '.txt'
  }
  return types[selectedFormat.value] || ''
}

const getFormatDescription = () => {
  const descriptions = {
    csv: 'CSV',
    excel: 'Excel (xlsx/xls)',
    json: 'JSON',
    txt: '文本'
  }
  return descriptions[selectedFormat.value] || ''
}

const handleFileSelect = (file) => {
  selectedFile.value = file
}

const uploadData = async () => {
  uploading.value = true
  try {
    let result
    if (selectedFormat.value === 'manual') {
      result = await dataService.uploadManualData(manualData.value, selectedFormat.value)
    } else {
      result = await dataService.uploadFile(selectedFile.value.raw, selectedFormat.value)
    }
    
    // 设置预览数据
    previewData.value = result.preview
    dataColumns.value = result.columns
    dataRows.value = result.rows
    fileSize.value = result.size
    
    nextStep()
  } catch (error) {
    ElMessage.error('数据上传失败: ' + error.message)
  } finally {
    uploading.value = false
  }
}

const finishImport = () => {
  emit('data-imported', {
    format: selectedFormat.value,
    data: previewData.value,
    columns: dataColumns.value,
    rows: dataRows.value
  })
  
  ElMessage.success('数据导入成功！')
  currentStep.value = 0 // 重置步骤
}
</script>
```

### 3. 状态管理 (Pinia Store)

#### 主应用状态
```typescript
// src/store/appStore.ts
import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 状态
  const systemStatus = ref('就绪')
  const currentTab = ref('data')
  const logs = reactive([])
  
  // 数据状态
  const currentData = ref(null)
  const processedData = ref(null)
  const currentChart = ref(null)
  
  // 操作
  const setSystemStatus = (status: string) => {
    systemStatus.value = status
  }
  
  const addLog = (message: string, type: 'success' | 'info' | 'warning' | 'error' = 'info') => {
    logs.push({
      id: Date.now(),
      message,
      type,
      timestamp: new Date().toLocaleTimeString()
    })
    
    // 保留最近50条日志
    if (logs.length > 50) {
      logs.splice(0, logs.length - 50)
    }
  }
  
  const setCurrentData = (data: any) => {
    currentData.value = data
    addLog('数据已更新', 'success')
  }
  
  const setProcessedData = (data: any) => {
    processedData.value = data
    addLog('数据处理完成', 'info')
  }
  
  const setCurrentChart = (chart: any) => {
    currentChart.value = chart
    addLog('图表已生成', 'success')
  }
  
  return {
    // 状态
    systemStatus,
    currentTab,
    logs,
    currentData,
    processedData,
    currentChart,
    
    // 操作
    setSystemStatus,
    addLog,
    setCurrentData,
    setProcessedData,
    setCurrentChart
  }
})
```

## PyQt6 桌面客户端实现

### 1. 主窗口重构

#### 更新主窗口类
```python
# desktop/src/main.py (更新)
import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTabWidget, QTextEdit, QStatusBar, QMenuBar, QToolBar,
    QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QAction

# 添加共享模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

try:
    from interfaces import *
    from data_types import *
except ImportError:
    print("警告: 导入共享模块失败")
    pass

from ui.data_import_widget import DataImportWidget
from ui.function_widget import FunctionWidget
from ui.chart_widget import ChartWidget
from ui.chart_display_widget import ChartDisplayWidget

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.current_data = None
        self.processed_data = None
        self.current_chart = None
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("DataCharts System v0.1.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_tool_bar()
        
        # 创建主界面布局
        self.create_main_layout()
        
        # 创建状态栏
        self.create_status_bar()
        
        # 设置样式
        self.set_style()
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        import_action = QAction('导入数据', self)
        import_action.setShortcut('Ctrl+O')
        import_action.triggered.connect(self.import_data)
        file_menu.addAction(import_action)
        
        export_action = QAction('导出图表', self)
        export_action.setShortcut('Ctrl+S')
        export_action.triggered.connect(self.export_chart)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu('工具')
        
        function_action = QAction('函数处理', self)
        function_action.triggered.connect(self.show_function_tab)
        tools_menu.addAction(function_action)
        
        chart_action = QAction('图表配置', self)
        chart_action.triggered.connect(self.show_chart_tab)
        tools_menu.addAction(chart_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_tool_bar(self):
        """创建工具栏"""
        toolbar = QToolBar(self)
        self.addToolBar(toolbar)
        
        # 导入数据按钮
        import_btn = QPushButton('导入数据')
        import_btn.clicked.connect(self.import_data)
        toolbar.addWidget(import_btn)
        
        toolbar.addSeparator()
        
        # 函数处理按钮
        function_btn = QPushButton('函数处理')
        function_btn.clicked.connect(self.show_function_tab)
        toolbar.addWidget(function_btn)
        
        # 图表配置按钮
        chart_btn = QPushButton('图表配置')
        chart_btn.clicked.connect(self.show_chart_tab)
        toolbar.addWidget(chart_btn)
        
        toolbar.addSeparator()
        
        # 导出按钮
        export_btn = QPushButton('导出图表')
        export_btn.clicked.connect(self.export_chart)
        toolbar.addWidget(export_btn)
    
    def create_main_layout(self):
        """创建主界面布局"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主分割器
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧操作面板
        self.create_operation_panel(main_splitter)
        
        # 右侧显示区域
        self.create_display_area(main_splitter)
        
        # 底部日志区域
        self.create_log_area()
        
        # 设置分割器比例
        main_splitter.setSizes([350, 850])
        
        # 主布局
        layout = QVBoxLayout()
        layout.addWidget(main_splitter)
        layout.addWidget(self.log_area)
        
        central_widget.setLayout(layout)
    
    def create_operation_panel(self, parent):
        """创建操作面板"""
        # 创建选项卡
        self.operation_tabs = QTabWidget()
        
        # 数据导入选项卡
        self.data_import_widget = DataImportWidget()
        self.data_import_widget.data_imported.connect(self.handle_data_imported)
        self.operation_tabs.addTab(self.data_import_widget, "数据导入")
        
        # 函数处理选项卡
        self.function_widget = FunctionWidget()
        self.function_widget.function_applied.connect(self.handle_function_applied)
        self.operation_tabs.addTab(self.function_widget, "函数处理")
        
        # 图表配置选项卡
        self.chart_widget = ChartWidget()
        self.chart_widget.chart_created.connect(self.handle_chart_created)
        self.operation_tabs.addTab(self.chart_widget, "图表配置")
        
        parent.addWidget(self.operation_tabs)
    
    def create_display_area(self, parent):
        """创建显示区域"""
        # 图表显示组件
        self.chart_display = ChartDisplayWidget()
        parent.addWidget(self.chart_display)
    
    def create_log_area(self):
        """创建日志区域"""
        self.log_area = QFrame()
        self.log_area.setFrameStyle(QFrame.Shape.StyledPanel)
        self.log_area.setMaximumHeight(120)
        
        layout = QVBoxLayout()
        
        # 日志标题
        log_label = QLabel("控制台日志")
        log_label.setStyleSheet("font-weight: bold; color: #333;")
        layout.addWidget(log_label)
        
        # 日志文本框
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(80)
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        self.log_area.setLayout(layout)
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
        
        # 版本信息
        version_label = QLabel("v0.1.0")
        self.status_bar.addPermanentWidget(version_label)
    
    def set_style(self):
        """设置界面样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #c0c4cc;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e4e7ed;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #409eff;
                color: white;
            }
            QPushButton {
                background-color: #409eff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #66b1ff;
            }
            QPushButton:pressed {
                background-color: #3a8ee6;
            }
        """)
    
    # 事件处理方法
    def handle_data_imported(self, data):
        """处理数据导入完成"""
        self.current_data = data
        self.status_label.setText("数据已导入")
        self.add_log("数据导入成功", "success")
        
        # 启用函数处理选项卡
        self.function_widget.set_data(data)
        self.operation_tabs.setTabEnabled(1, True)
    
    def handle_function_applied(self, result):
        """处理函数应用完成"""
        self.processed_data = result
        self.status_label.setText("数据处理完成")
        self.add_log("函数处理完成", "info")
        
        # 启用图表配置选项卡
        self.chart_widget.set_data(result)
        self.operation_tabs.setTabEnabled(2, True)
    
    def handle_chart_created(self, chart):
        """处理图表创建完成"""
        self.current_chart = chart
        self.status_label.setText("图表生成完成")
        self.add_log("图表生成成功", "success")
        
        # 显示图表
        self.chart_display.display_chart(chart)
    
    def add_log(self, message, level="info"):
        """添加日志"""
        timestamp = QTimer().property("currentTime") or "00:00:00"
        log_entry = f"[{timestamp}] {message}"
        self.log_text.append(log_entry)
    
    # 菜单/工具栏事件
    def import_data(self):
        """切换到数据导入选项卡"""
        self.operation_tabs.setCurrentIndex(0)
    
    def show_function_tab(self):
        """显示函数处理选项卡"""
        self.operation_tabs.setCurrentIndex(1)
    
    def show_chart_tab(self):
        """显示图表配置选项卡"""
        self.operation_tabs.setCurrentIndex(2)
    
    def export_chart(self):
        """导出图表"""
        if self.current_chart:
            # 实现图表导出逻辑
            self.add_log("图表导出功能待实现", "warning")
        else:
            self.add_log("没有可导出的图表", "warning")
    
    def show_about(self):
        """显示关于对话框"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(self, "关于 DataCharts", 
                         "DataCharts 数据可视化系统\n版本: v0.1.0\n\n"
                         "一个智能的数据可视化平台，支持多种数据格式导入、"
                         "函数处理和图表生成。")

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("DataCharts System")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("DataCharts Team")
    
    window = MainWindow()
    window.show()
    
    print("DataCharts System Desktop v0.1.0 已启动")
    
    # 检查是否为测试模式
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("测试模式: 应用启动成功")
        return 0
    
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
```

## 响应式设计和用户体验

### 1. 移动端适配 (Vue.js)
```vue
<!-- 响应式样式 -->
<style scoped>
.main-container {
  height: 100vh;
}

.header {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

@media (max-width: 768px) {
  .sidebar {
    width: 300px !important;
  }
  
  .header-content {
    flex-direction: column;
    gap: 10px;
  }
  
  .nav-buttons {
    overflow-x: auto;
  }
}

@media (max-width: 480px) {
  .sidebar {
    width: 100% !important;
    position: absolute;
    z-index: 1000;
    background: white;
  }
}
</style>
```

### 2. 主题切换功能
```typescript
// src/composables/useTheme.ts
import { ref, computed } from 'vue'

const isDark = ref(false)

export const useTheme = () => {
  const theme = computed(() => isDark.value ? 'dark' : 'light')
  
  const toggleTheme = () => {
    isDark.value = !isDark.value
    document.documentElement.setAttribute('data-theme', theme.value)
  }
  
  return {
    isDark,
    theme,
    toggleTheme
  }
}
```

## 实现文件清单

### 新建文件 (Vue.js前端)
1. `frontend/src/components/layout/MainLayout.vue`
2. `frontend/src/components/data/DataImportPanel.vue`
3. `frontend/src/components/function/FunctionPanel.vue`
4. `frontend/src/components/chart/ChartConfigPanel.vue`
5. `frontend/src/components/chart/ChartRenderer.vue`
6. `frontend/src/components/common/WelcomePage.vue`
7. `frontend/src/store/appStore.ts`
8. `frontend/src/services/dataService.ts`
9. `frontend/src/services/chartService.ts`
10. `frontend/src/types/index.ts`

### 新建文件 (PyQt6桌面客户端)
1. `desktop/src/ui/__init__.py`
2. `desktop/src/ui/data_import_widget.py`
3. `desktop/src/ui/function_widget.py`
4. `desktop/src/ui/chart_widget.py`
5. `desktop/src/ui/chart_display_widget.py`
6. `desktop/src/core/app_controller.py`
7. `desktop/resources/styles.qss`

## 成功标准

### 功能标准
- 73 用户界面完整实现
- 73 所有主要功能可通过界面操作
- 73 界面响应流畅
- 73 跨平台兼容性良好

### 用户体验标准
- 73 界面美观，符合现代设计标准
- 73 操作流程清晰直观
- 73 错误提示友好
- 73 响应时间合理 (<2秒)

## 依赖关系

### 前置依赖
- 73 任务6.1 (数据导入处理) 已完成
- 73 任务6.2 (函数处理) 已完成  
- 73 任务6.3 (图表生成) 已完成

### 后续依赖
- 为任务6.6 (系统集成) 提供完整的用户界面

## 估时和里程碑

### 总工期: 3天

#### 第1天
- **上午**: Vue.js前端基础组件实现
- **下午**: 主布局和导航实现

#### 第2天  
- **上午**: PyQt6桌面客户端界面实现
- **下午**: 状态管理和事件处理

#### 第3天
- **上午**: 响应式设计和主题功能
- **下午**: 用户体验优化和测试

### 关键里程碑
- **M1**: 基础界面框架完成 (1天)
- **M2**: 功能界面完成 (2天)
- **M3**: 完整用户体验实现 (3天)