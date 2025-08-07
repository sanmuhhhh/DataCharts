/**
 * 数据服务
 * 
 * 处理数据相关的API调用
 */

import { apiClient } from './apiClient.js'

/**
 * 数据服务类
 */
export class DataService {
    
    /**
     * 上传文件数据
     * @param {File} file - 文件对象
     * @param {string} format - 数据格式
     * @param {object} options - 上传选项
     * @returns {Promise} - 上传结果
     */
    async uploadFile(file, format, options = {}) {
        try {
                    const response = await apiClient.uploadData(file, { format, ...options })
        const result = response.data
            
            if (result.success) {
                return {
                    dataId: result.data_id,
                    preview: result.summary,
                    message: result.message
                }
            } else {
                throw new Error(result.error || '文件上传失败')
            }
        } catch (error) {
            console.error('文件上传失败:', error)
            throw error
        }
    }

    /**
     * 上传手动输入数据
     * @param {string} data - 手动输入的数据
     * @param {string} format - 数据格式
     * @returns {Promise} - 上传结果
     */
    async uploadManualData(data, format = 'manual') {
        try {
            const result = await api.post('/api/data/upload-manual', {
                data,
                format,
                options: {}
            })
            
            if (result.success) {
                return {
                    dataId: result.data_id,
                    preview: result.summary,
                    message: result.message
                }
            } else {
                throw new Error(result.error || '数据上传失败')
            }
        } catch (error) {
            console.error('手动数据上传失败:', error)
            throw error
        }
    }

    /**
     * 预览数据
     * @param {string} dataId - 数据ID
     * @param {number} rows - 预览行数
     * @returns {Promise} - 预览数据
     */
    async previewData(dataId, rows = 10) {
        try {
            const result = await api.get('/api/data/preview', {
                data_id: dataId,
                rows
            })
            
            if (result.success) {
                return {
                    data: result.preview.head,
                    columns: result.preview.columns,
                    shape: result.preview.shape,
                    types: result.preview.dtypes
                }
            } else {
                throw new Error(result.error || '数据预览失败')
            }
        } catch (error) {
            console.error('数据预览失败:', error)
            throw error
        }
    }

    /**
     * 验证数据
     * @param {string} dataId - 数据ID
     * @returns {Promise} - 验证结果
     */
    async validateData(dataId) {
        try {
            const result = await api.post('/api/data/validate', {
                data_id: dataId
            })
            
            if (result.success) {
                return {
                    isValid: result.validation_passed,
                    summary: result.summary,
                    message: result.message
                }
            } else {
                throw new Error(result.error || '数据验证失败')
            }
        } catch (error) {
            console.error('数据验证失败:', error)
            throw error
        }
    }

    /**
     * 处理数据
     * @param {string} dataId - 数据ID
     * @param {object} options - 处理选项
     * @returns {Promise} - 处理结果
     */
    async processData(dataId, options = {}) {
        try {
            const result = await api.post('/api/data/process', {
                data_id: dataId,
                process_options: options
            })
            
            if (result.success) {
                return {
                    processedDataId: result.processed_data_id,
                    originalDataId: result.original_data_id,
                    report: result.report,
                    message: result.message
                }
            } else {
                throw new Error(result.error || '数据处理失败')
            }
        } catch (error) {
            console.error('数据处理失败:', error)
            throw error
        }
    }

    /**
     * 获取数据信息
     * @param {string} dataId - 数据ID
     * @returns {Promise} - 数据信息
     */
    async getDataInfo(dataId) {
        try {
            const result = await api.get('/api/data/info', {
                data_id: dataId
            })
            
            if (result.success) {
                return {
                    dataId: result.data_id,
                    detectedType: result.detected_type,
                    summary: result.summary,
                    metadata: result.metadata
                }
            } else {
                throw new Error(result.error || '获取数据信息失败')
            }
        } catch (error) {
            console.error('获取数据信息失败:', error)
            throw error
        }
    }

    /**
     * 列出所有数据源
     * @returns {Promise} - 数据源列表
     */
    async listDataSources() {
        try {
            const result = await api.get('/api/data/list')
            
            if (result.success) {
                return {
                    count: result.count,
                    dataSources: result.data_sources
                }
            } else {
                throw new Error(result.error || '获取数据源列表失败')
            }
        } catch (error) {
            console.error('获取数据源列表失败:', error)
            throw error
        }
    }

    /**
     * 删除数据源
     * @param {string} dataId - 数据ID
     * @returns {Promise} - 删除结果
     */
    async deleteDataSource(dataId) {
        try {
            const result = await api.delete(`/api/data/${dataId}`)
            
            if (result.success) {
                return {
                    dataId: result.data_id,
                    message: result.message
                }
            } else {
                throw new Error(result.error || '删除数据源失败')
            }
        } catch (error) {
            console.error('删除数据源失败:', error)
            throw error
        }
    }
}

// 创建默认实例
export const dataService = new DataService()

// 默认导出
export default DataService
