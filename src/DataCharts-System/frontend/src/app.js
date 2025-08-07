/**
 * DataCharts 前端应用主文件
 */

import { dataService } from './services/dataService.js'
import { functionService } from './services/functionService.js'
import { chartService } from './services/chartService.js'

// 应用状态
let appState = {
    currentTab: 'data',
    currentData: null,
    processedData: null,
    currentChart: null,
    chartInstance: null,
    systemStatus: '就绪'
}

// 初始化应用
document.addEventListener('DOMContentLoaded', function() {
    console.log('DataCharts 前端应用启动中...')
    initializeApp()
})

/**
 * 初始化应用
 */
function initializeApp() {
    setupEventListeners()
    setupFileUpload()
    setupFormatSelection()
    addLog('系统已就绪', 'info')
    console.log('DataCharts 前端应用已启动')
}

/**
 * 设置事件监听器
 */
function setupEventListeners() {
    // 导航按钮点击事件
    const navButtons = document.querySelectorAll('.nav-btn')
    navButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const tab = this.getAttribute('data-tab')
            if (tab) {
                switchTab(tab)
            }
        })
    })

    // 函数标签点击事件
    const functionTags = document.querySelectorAll('.function-tag')
    functionTags.forEach(tag => {
        tag.addEventListener('click', function() {
            insertFunctionToInput(this.textContent)
        })
    })

    // 函数输入实时验证
    const functionInput = document.getElementById('function-input')
    if (functionInput) {
        functionInput.addEventListener('input', debounce(validateFunctionInput, 500))
    }
}

/**
 * 设置文件上传
 */
function setupFileUpload() {
    const fileInput = document.getElementById('file-input')
    const dropZone = document.querySelector('.upload-drop-zone')

    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect)
    }

    if (dropZone) {
        // 拖拽上传
        dropZone.addEventListener('dragover', function(e) {
            e.preventDefault()
            this.style.borderColor = '#66b1ff'
            this.style.backgroundColor = '#f0f9ff'
        })

        dropZone.addEventListener('dragleave', function(e) {
            e.preventDefault()
            this.style.borderColor = '#409eff'
            this.style.backgroundColor = '#f8f9fa'
        })

        dropZone.addEventListener('drop', function(e) {
            e.preventDefault()
            this.style.borderColor = '#409eff'
            this.style.backgroundColor = '#f8f9fa'
            
            const files = e.dataTransfer.files
            if (files.length > 0) {
                fileInput.files = files
                handleFileSelect({ target: { files } })
            }
        })
    }
}

/**
 * 设置格式选择
 */
function setupFormatSelection() {
    const formatRadios = document.querySelectorAll('input[name="format"]')
    const manualInput = document.getElementById('manual-input')
    const dropZone = document.querySelector('.upload-drop-zone')

    formatRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'manual') {
                dropZone.style.display = 'none'
                manualInput.style.display = 'block'
            } else {
                dropZone.style.display = 'block'
                manualInput.style.display = 'none'
            }
        })
    })
}

/**
 * 切换选项卡
 */
function switchTab(tabName) {
    // 更新导航按钮状态
    const navButtons = document.querySelectorAll('.nav-btn')
    navButtons.forEach(btn => {
        btn.classList.remove('active')
        if (btn.getAttribute('data-tab') === tabName) {
            btn.classList.add('active')
        }
    })

    // 更新面板显示
    const panels = document.querySelectorAll('.tab-panel')
    panels.forEach(panel => {
        panel.classList.remove('active')
    })

    const targetPanel = document.getElementById(`${tabName}-panel`)
    if (targetPanel) {
        targetPanel.classList.add('active')
    }

    appState.currentTab = tabName
    addLog(`切换到${getTabName(tabName)}`, 'info')
}

/**
 * 获取选项卡中文名称
 */
function getTabName(tabName) {
    const names = {
        'data': '数据导入',
        'function': '函数处理',
        'chart': '图表配置'
    }
    return names[tabName] || tabName
}

/**
 * 处理文件选择
 */
function handleFileSelect(event) {
    const files = event.target.files
    if (files.length > 0) {
        const file = files[0]
        const fileName = file.name
        const fileSize = formatFileSize(file.size)
        
        addLog(`选择文件: ${fileName} (${fileSize})`, 'info')
        
        // 启用上传按钮
        const uploadBtn = document.getElementById('upload-btn')
        if (uploadBtn) {
            uploadBtn.disabled = false
        }
    }
}

/**
 * 上传数据
 */
async function uploadData() {
    const selectedFormat = document.querySelector('input[name="format"]:checked').value
    const uploadBtn = document.getElementById('upload-btn')
    const validateBtn = document.getElementById('validate-btn')
    
    try {
        uploadBtn.disabled = true
        uploadBtn.textContent = '上传中...'
        
        let result
        
        if (selectedFormat === 'manual') {
            const manualData = document.getElementById('manual-input').value
            if (!manualData.trim()) {
                throw new Error('请输入数据')
            }
            result = await dataService.uploadManualData(manualData, selectedFormat)
        } else {
            const fileInput = document.getElementById('file-input')
            if (!fileInput.files || fileInput.files.length === 0) {
                throw new Error('请选择文件')
            }
            result = await dataService.uploadFile(fileInput.files[0], selectedFormat)
        }
        
        appState.currentData = {
            dataId: result.dataId,
            preview: result.preview,
            format: selectedFormat
        }
        
        // 显示数据预览
        displayDataPreview(result.preview)
        
        // 启用验证按钮
        validateBtn.disabled = false
        
        // 更新状态
        updateSystemStatus('数据已导入')
        addLog(result.message || '数据上传成功', 'success')
        
    } catch (error) {
        addLog('数据上传失败: ' + error.message, 'error')
    } finally {
        uploadBtn.disabled = false
        uploadBtn.textContent = '上传数据'
    }
}

/**
 * 验证数据
 */
async function validateData() {
    if (!appState.currentData) {
        addLog('没有可验证的数据', 'warning')
        return
    }
    
    try {
        const result = await dataService.validateData(appState.currentData.dataId)
        
        if (result.isValid) {
            addLog('数据验证通过', 'success')
            updateSystemStatus('数据验证通过')
        } else {
            addLog('数据验证失败', 'warning')
        }
        
    } catch (error) {
        addLog('数据验证失败: ' + error.message, 'error')
    }
}

/**
 * 显示数据预览
 */
function displayDataPreview(preview) {
    const previewContainer = document.getElementById('data-preview')
    
    if (!preview || !preview.data) {
        previewContainer.innerHTML = '<div class="preview-placeholder">暂无预览数据</div>'
        return
    }
    
    // 创建预览表格
    let html = '<table class="preview-table">'
    
    // 表头
    if (preview.columns && preview.columns.length > 0) {
        html += '<thead><tr>'
        preview.columns.forEach(col => {
            html += `<th>${col}</th>`
        })
        html += '</tr></thead>'
    }
    
    // 数据行（只显示前5行）
    html += '<tbody>'
    const maxRows = Math.min(5, preview.data ? preview.data.length : 0)
    for (let i = 0; i < maxRows; i++) {
        html += '<tr>'
        const row = preview.data[i]
        if (Array.isArray(row)) {
            row.forEach(cell => {
                html += `<td>${cell}</td>`
            })
        } else if (typeof row === 'object') {
            Object.values(row).forEach(cell => {
                html += `<td>${cell}</td>`
            })
        }
        html += '</tr>'
    }
    html += '</tbody></table>'
    
    // 添加数据信息
    if (preview.shape) {
        html += `<div style="margin-top: 0.5rem; font-size: 0.85rem; color: #666;">
            数据维度: ${preview.shape[0]} 行 × ${preview.shape[1]} 列
        </div>`
    }
    
    previewContainer.innerHTML = html
}

/**
 * 解析函数
 */
async function parseFunction() {
    const functionInput = document.getElementById('function-input')
    const expression = functionInput.value.trim()
    
    if (!expression) {
        addLog('请输入函数表达式', 'warning')
        return
    }
    
    try {
        const result = await functionService.parseExpression(expression)
        
        if (result.isValid) {
            addLog(`函数解析成功，变量: [${result.variables.join(', ')}]`, 'success')
            
            // 显示解析结果
            const suggestionsDiv = document.getElementById('function-suggestions')
            suggestionsDiv.innerHTML = `
                <div style="color: #67c23a;">77 解析成功</div>
                <div style="font-size: 0.8rem; color: #666;">
                    变量: ${result.variables.join(', ') || '无'}
                </div>
            `
            
            // 启用应用按钮
            const applyBtn = document.getElementById('apply-btn')
            if (applyBtn) {
                applyBtn.disabled = false
            }
        }
        
    } catch (error) {
        addLog('函数解析失败: ' + error.message, 'error')
        const suggestionsDiv = document.getElementById('function-suggestions')
        suggestionsDiv.innerHTML = `<div style="color: #f56c6c;">71 ${error.message}</div>`
    }
}

/**
 * 应用函数
 */
async function applyFunction() {
    const functionInput = document.getElementById('function-input')
    const expression = functionInput.value.trim()
    
    if (!expression || !appState.currentData) {
        addLog('请先导入数据并输入函数表达式', 'warning')
        return
    }
    
    try {
        const result = await functionService.applyFunction(
            appState.currentData.dataId, 
            expression
        )
        
        appState.processedData = result.resultData
        
        addLog(`函数应用成功，处理时间: ${(result.processingTime * 1000).toFixed(2)}ms`, 'success')
        updateSystemStatus('函数处理完成')
        
        // 自动切换到图表配置
        setTimeout(() => {
            switchTab('chart')
        }, 1000)
        
    } catch (error) {
        addLog('函数应用失败: ' + error.message, 'error')
    }
}

/**
 * 创建图表
 */
async function createChart() {
    const chartType = document.querySelector('input[name="chart-type"]:checked').value
    const title = document.getElementById('chart-title').value
    const xAxis = document.getElementById('chart-x-axis').value
    const yAxis = document.getElementById('chart-y-axis').value
    const width = parseInt(document.getElementById('chart-width').value) || 800
    const height = parseInt(document.getElementById('chart-height').value) || 600
    
    const dataToUse = appState.processedData || appState.currentData
    
    if (!dataToUse) {
        addLog('请先导入数据', 'warning')
        return
    }
    
    try {
        // 如果有处理后的数据，使用处理后的数据；否则使用原始数据
        const dataId = appState.processedData ? 
            appState.processedData.dataId || appState.currentData.dataId : 
            appState.currentData.dataId
        
        const config = {
            title: title || `${getChartTypeName(chartType)}`,
            xAxis: xAxis || 'X轴',
            yAxis: yAxis || 'Y轴',
            width,
            height,
            options: {}
        }
        
        const result = await chartService.createChart(dataId, chartType, config)
        
        appState.currentChart = result.chartData
        
        // 渲染图表
        renderChart(result.chartData)
        
        addLog('图表创建成功', 'success')
        updateSystemStatus('图表生成完成')
        
        // 启用导出按钮
        const exportBtn = document.getElementById('export-chart-btn')
        if (exportBtn) {
            exportBtn.disabled = false
        }
        
    } catch (error) {
        addLog('图表创建失败: ' + error.message, 'error')
        
        // 如果后端创建失败，尝试使用前端生成示例图表
        try {
            const sampleConfig = chartService.generatePreviewConfig(chartType)
            renderChart(sampleConfig)
            addLog('使用示例数据生成图表', 'info')
        } catch (fallbackError) {
            addLog('图表生成完全失败', 'error')
        }
    }
}

/**
 * 渲染图表
 */
function renderChart(chartData) {
    const canvas = document.getElementById('chart-canvas')
    const welcomeMessage = document.querySelector('.welcome-message')
    
    if (!canvas) return
    
    // 销毁现有图表
    if (appState.chartInstance) {
        appState.chartInstance.destroy()
    }
    
    // 隐藏欢迎消息，显示图表
    if (welcomeMessage) {
        welcomeMessage.style.display = 'none'
    }
    canvas.style.display = 'block'
    
    // 创建新图表
    const ctx = canvas.getContext('2d')
    appState.chartInstance = new Chart(ctx, chartData)
}

/**
 * 导出图表
 */
async function exportChart() {
    if (!appState.chartInstance) {
        addLog('没有可导出的图表', 'warning')
        return
    }
    
    try {
        // 使用Chart.js的导出功能
        const dataURL = appState.chartInstance.toBase64Image('image/png', 1.0)
        
        // 创建下载链接
        const link = document.createElement('a')
        link.download = 'chart.png'
        link.href = dataURL
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        addLog('图表导出成功', 'success')
        
    } catch (error) {
        addLog('图表导出失败: ' + error.message, 'error')
    }
}

/**
 * 获取图表类型中文名称
 */
function getChartTypeName(type) {
    const names = {
        'line': '折线图',
        'bar': '柱状图',
        'scatter': '散点图',
        'pie': '饼图'
    }
    return names[type] || type
}

/**
 * 插入函数到输入框
 */
function insertFunctionToInput(functionName) {
    const functionInput = document.getElementById('function-input')
    if (functionInput) {
        const currentValue = functionInput.value
        const cursorPos = functionInput.selectionStart || currentValue.length
        const newValue = currentValue.slice(0, cursorPos) + functionName + '()' + currentValue.slice(cursorPos)
        functionInput.value = newValue
        functionInput.focus()
        functionInput.setSelectionRange(cursorPos + functionName.length + 1, cursorPos + functionName.length + 1)
    }
}

/**
 * 实时验证函数输入
 */
async function validateFunctionInput() {
    const functionInput = document.getElementById('function-input')
    const suggestionsDiv = document.getElementById('function-suggestions')
    const expression = functionInput.value.trim()
    
    if (!expression) {
        suggestionsDiv.innerHTML = ''
        return
    }
    
    try {
        const result = await functionService.validateSyntax(expression)
        
        if (result.isValid) {
            suggestionsDiv.innerHTML = '<div style="color: #67c23a;">77 语法正确</div>'
        } else {
            suggestionsDiv.innerHTML = '<div style="color: #f56c6c;">71 语法错误</div>'
        }
        
    } catch (error) {
        suggestionsDiv.innerHTML = `<div style="color: #f56c6c;">71 ${error.message}</div>`
    }
}

/**
 * 添加日志
 */
function addLog(message, type = 'info') {
    const logContainer = document.getElementById('log-container')
    const logEntry = document.createElement('div')
    logEntry.className = `log-entry ${type}`
    
    const timestamp = new Date().toLocaleTimeString()
    logEntry.innerHTML = `[${timestamp}] ${message}`
    
    logContainer.appendChild(logEntry)
    logContainer.scrollTop = logContainer.scrollHeight
    
    // 保持最近50条日志
    while (logContainer.children.length > 50) {
        logContainer.removeChild(logContainer.firstChild)
    }
}

/**
 * 更新系统状态
 */
function updateSystemStatus(status) {
    appState.systemStatus = status
    const statusElement = document.getElementById('system-status')
    if (statusElement) {
        statusElement.textContent = `状态: ${status}`
    }
}

/**
 * 格式化文件大小
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * 防抖函数
 */
function debounce(func, wait) {
    let timeout
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout)
            func(...args)
        }
        clearTimeout(timeout)
        timeout = setTimeout(later, wait)
    }
}

/**
 * 显示导出对话框
 */
function showExportDialog() {
    if (!appState.currentChart) {
        addLog('没有可导出的图表', 'warning')
        return
    }
    
    const formats = ['PNG', 'JPG', 'SVG', 'PDF', 'JSON']
    const format = prompt(`选择导出格式 (${formats.join('/')})`, 'PNG')
    
    if (format && formats.includes(format.toUpperCase())) {
        exportChart()
    }
}

/**
 * 显示帮助对话框
 */
function showHelpDialog() {
    const helpContent = `
DataCharts 使用指南:

1. 数据导入
   - 支持 CSV, Excel, JSON, TXT 格式
   - 可手动输入数据
   - 自动验证数据格式

2. 函数处理 (可选)
   - 支持数学函数: sin, cos, tan, log, exp, sqrt
   - 支持统计函数: mean, std, var, median
   - 支持数据变换: normalize, standardize, scale

3. 图表生成
   - 支持折线图、柱状图、散点图、饼图
   - 可自定义标题、轴标签、尺寸
   - 支持多种格式导出

快捷键:
- 点击函数标签快速插入
- 支持拖拽上传文件
    `
    
    alert(helpContent)
}

// 将函数添加到全局作用域，以便HTML中的onclick可以访问
window.uploadData = uploadData
window.validateData = validateData
window.parseFunction = parseFunction
window.applyFunction = applyFunction
window.createChart = createChart
window.exportChart = exportChart
window.showExportDialog = showExportDialog
window.showHelpDialog = showHelpDialog

console.log('DataCharts 前端应用模块已加载')
