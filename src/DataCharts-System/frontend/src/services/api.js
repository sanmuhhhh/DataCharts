/**
 * API服务基础配置
 * 
 * 提供与后端API的通信功能
 */

// API基础配置
const API_BASE_URL = 'http://localhost:8000'

/**
 * API请求封装
 */
class ApiService {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL
    }

    /**
     * 发送HTTP请求
     * @param {string} url - 请求URL
     * @param {object} options - 请求选项
     * @returns {Promise} - 请求结果
     */
    async request(url, options = {}) {
        const fullUrl = `${this.baseURL}${url}`
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        }

        const config = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers,
            },
        }

        try {
            const response = await fetch(fullUrl, config)
            
            if (!response.ok) {
                throw new Error(`HTTP错误! 状态: ${response.status}`)
            }

            const contentType = response.headers.get('content-type')
            if (contentType && contentType.includes('application/json')) {
                return await response.json()
            } else {
                return await response.text()
            }
        } catch (error) {
            console.error('API请求失败:', error)
            throw error
        }
    }

    /**
     * GET请求
     */
    async get(url, params = {}) {
        const urlParams = new URLSearchParams(params)
        const queryString = urlParams.toString()
        const fullUrl = queryString ? `${url}?${queryString}` : url
        
        return this.request(fullUrl, {
            method: 'GET',
        })
    }

    /**
     * POST请求
     */
    async post(url, data = {}) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data),
        })
    }

    /**
     * PUT请求
     */
    async put(url, data = {}) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data),
        })
    }

    /**
     * DELETE请求
     */
    async delete(url) {
        return this.request(url, {
            method: 'DELETE',
        })
    }

    /**
     * 文件上传
     */
    async uploadFile(url, file, additionalData = {}) {
        const formData = new FormData()
        formData.append('file', file)
        
        // 添加额外数据
        Object.keys(additionalData).forEach(key => {
            formData.append(key, additionalData[key])
        })

        return this.request(url, {
            method: 'POST',
            body: formData,
            headers: {
                // 让浏览器自动设置Content-Type
            },
        })
    }
}

// 创建默认API实例
export const api = new ApiService()

// 导出API服务类
export default ApiService
