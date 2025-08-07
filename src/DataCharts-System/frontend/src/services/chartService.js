/**
 * 图表服务
 * 
 * 处理图表相关的API调用
 */

import { api } from './api.js'

/**
 * 图表服务类
 */
export class ChartService {
    
    /**
     * 创建图表
     * @param {string} dataId - 数据ID
     * @param {string} chartType - 图表类型
     * @param {object} config - 图表配置
     * @returns {Promise} - 创建结果
     */
    async createChart(dataId, chartType, config = {}) {
        try {
            const result = await api.post('/api/chart/create', {
                data_id: dataId,
                chart_type: chartType,
                config: {
                    title: config.title || '',
                    x_axis: config.xAxis || '',
                    y_axis: config.yAxis || '',
                    width: config.width || 800,
                    height: config.height || 600,
                    options: config.options || {}
                }
            })
            
            if (result.status === 'success') {
                return {
                    chartId: result.chart_id,
                    chartData: result.chart_data,
                    message: '图表创建成功'
                }
            } else {
                throw new Error(result.error_message || '图表创建失败')
            }
        } catch (error) {
            console.error('图表创建失败:', error)
            throw error
        }
    }

    /**
     * 更新图表数据
     * @param {string} chartId - 图表ID
     * @param {string} dataId - 新数据ID
     * @returns {Promise} - 更新结果
     */
    async updateChart(chartId, dataId) {
        try {
            const result = await api.put(`/api/chart/${chartId}`, {
                data_id: dataId
            })
            
            if (result.status === 'success') {
                return {
                    chartData: result.chart_data,
                    message: '图表更新成功'
                }
            } else {
                throw new Error(result.error_message || '图表更新失败')
            }
        } catch (error) {
            console.error('图表更新失败:', error)
            throw error
        }
    }

    /**
     * 导出图表
     * @param {string} chartId - 图表ID
     * @param {string} format - 导出格式 (png, jpg, svg, pdf, json)
     * @returns {Promise} - 导出结果
     */
    async exportChart(chartId, format = 'png') {
        try {
            const response = await fetch(`${api.baseURL}/api/chart/${chartId}/export?format=${format}`)
            
            if (!response.ok) {
                throw new Error(`导出失败: ${response.status}`)
            }
            
            if (format === 'json') {
                return await response.json()
            } else {
                const blob = await response.blob()
                return {
                    blob,
                    filename: `chart.${format}`,
                    type: response.headers.get('content-type')
                }
            }
        } catch (error) {
            console.error('图表导出失败:', error)
            throw error
        }
    }

    /**
     * 获取支持的图表类型
     * @returns {Promise} - 图表类型列表
     */
    async getSupportedChartTypes() {
        try {
            // 这里可以从后端获取，暂时使用硬编码
            return {
                basic: [
                    { type: 'line', name: '折线图', description: '用于显示数据随时间的变化趋势' },
                    { type: 'bar', name: '柱状图', description: '用于比较不同类别的数据' },
                    { type: 'scatter', name: '散点图', description: '用于显示两个变量之间的关系' },
                    { type: 'pie', name: '饼图', description: '用于显示各部分占整体的比例' }
                ],
                advanced: [
                    { type: 'heatmap', name: '热力图', description: '用于显示数据矩阵的密度分布' },
                    { type: 'histogram', name: '直方图', description: '用于显示数据的分布情况' },
                    { type: 'box', name: '箱线图', description: '用于显示数据的统计分布' }
                ]
            }
        } catch (error) {
            console.error('获取图表类型失败:', error)
            throw error
        }
    }

    /**
     * 获取图表配置模板
     * @param {string} chartType - 图表类型
     * @returns {object} - 配置模板
     */
    getChartConfigTemplate(chartType) {
        const templates = {
            line: {
                title: '折线图',
                xAxis: 'X轴',
                yAxis: 'Y轴',
                width: 800,
                height: 600,
                options: {
                    line_tension: 0.1,
                    fill_area: false,
                    point_radius: 3,
                    show_grid: true,
                    show_legend: true
                }
            },
            bar: {
                title: '柱状图',
                xAxis: 'X轴',
                yAxis: 'Y轴',
                width: 800,
                height: 600,
                options: {
                    border_width: 1,
                    show_data_labels: false,
                    show_grid: true,
                    show_legend: true
                }
            },
            scatter: {
                title: '散点图',
                xAxis: 'X轴',
                yAxis: 'Y轴',
                width: 800,
                height: 600,
                options: {
                    point_radius: 5,
                    point_hover_radius: 8,
                    show_grid: true,
                    show_legend: true
                }
            },
            pie: {
                title: '饼图',
                xAxis: '',
                yAxis: '',
                width: 800,
                height: 600,
                options: {
                    border_width: 2,
                    legend_position: 'right',
                    show_legend: true
                }
            },
            heatmap: {
                title: '热力图',
                xAxis: 'X轴',
                yAxis: 'Y轴',
                width: 800,
                height: 600,
                options: {
                    show_labels: true,
                    color_scheme: 'viridis'
                }
            }
        }
        
        return templates[chartType] || templates.line
    }

    /**
     * 验证图表配置
     * @param {object} config - 图表配置
     * @returns {object} - 验证结果
     */
    validateChartConfig(config) {
        const errors = []
        const warnings = []
        
        if (!config.title || config.title.trim() === '') {
            warnings.push('建议设置图表标题')
        }
        
        if (config.width < 300 || config.width > 2000) {
            errors.push('图表宽度应在300-2000像素之间')
        }
        
        if (config.height < 200 || config.height > 1500) {
            errors.push('图表高度应在200-1500像素之间')
        }
        
        return {
            isValid: errors.length === 0,
            errors,
            warnings
        }
    }

    /**
     * 下载导出的图表文件
     * @param {Blob} blob - 文件数据
     * @param {string} filename - 文件名
     */
    downloadChart(blob, filename) {
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
    }

    /**
     * 生成图表预览配置
     * @param {string} chartType - 图表类型
     * @param {object} sampleData - 示例数据
     * @returns {object} - 预览配置
     */
    generatePreviewConfig(chartType, sampleData = null) {
        const config = this.getChartConfigTemplate(chartType)
        
        if (!sampleData) {
            // 生成默认示例数据
            sampleData = this.generateSampleData(chartType)
        }
        
        return {
            type: chartType,
            data: sampleData,
            options: config.options
        }
    }

    /**
     * 生成示例数据
     * @param {string} chartType - 图表类型
     * @returns {object} - 示例数据
     */
    generateSampleData(chartType) {
        switch (chartType) {
            case 'line':
                return {
                    labels: ['1月', '2月', '3月', '4月', '5月', '6月'],
                    datasets: [{
                        label: '销售额',
                        data: [12, 19, 3, 5, 2, 3],
                        borderColor: '#409EFF',
                        backgroundColor: '#409EFF20'
                    }]
                }
            
            case 'bar':
                return {
                    labels: ['产品A', '产品B', '产品C', '产品D'],
                    datasets: [{
                        label: '销量',
                        data: [25, 45, 30, 35],
                        backgroundColor: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C']
                    }]
                }
            
            case 'scatter':
                return {
                    datasets: [{
                        label: '数据点',
                        data: [
                            { x: 1, y: 2 },
                            { x: 2, y: 4 },
                            { x: 3, y: 1 },
                            { x: 4, y: 3 },
                            { x: 5, y: 5 }
                        ],
                        backgroundColor: '#409EFF'
                    }]
                }
            
            case 'pie':
                return {
                    labels: ['Chrome', 'Firefox', 'Safari', 'Edge'],
                    datasets: [{
                        data: [45, 25, 20, 10],
                        backgroundColor: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C']
                    }]
                }
            
            default:
                return {}
        }
    }
}

// 创建默认实例
export const chartService = new ChartService()

// 默认导出
export default ChartService
