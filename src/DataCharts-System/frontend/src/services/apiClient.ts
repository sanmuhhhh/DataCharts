/**
 * API客户端服务
 * 
 * 统一的API通信接口
 */

interface ApiResponse<T> {
  data: T
  status: number
  message?: string
}

interface UploadProgress {
  loaded: number
  total: number
  progress: number
}

class ApiClient {
  private baseURL: string
  private timeout: number

  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL
    this.timeout = 30000
  }

  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
      },
      ...options
    }

    try {
      const response = await fetch(url, defaultOptions)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      
      return {
        data,
        status: response.status,
        message: data.message || 'Success'
      }
    } catch (error) {
      console.error('API Request failed:', error)
      throw error
    }
  }

  // 数据相关API
  async uploadData(file: File, options?: any): Promise<ApiResponse<any>> {
    const formData = new FormData()
    formData.append('file', file)
    
    if (options) {
      formData.append('options', JSON.stringify(options))
    }

    return this.request('/api/data/upload', {
      method: 'POST',
      body: formData,
      headers: {} // 让浏览器自动设置Content-Type
    })
  }

  async uploadManualData(content: string, format: string): Promise<ApiResponse<any>> {
    return this.request('/api/data/manual', {
      method: 'POST',
      body: JSON.stringify({
        content,
        format,
        options: {}
      })
    })
  }

  async getData(dataId: string): Promise<ApiResponse<any>> {
    return this.request(`/api/data/${dataId}`)
  }

  async getDataPreview(dataId: string, rows: number = 10): Promise<ApiResponse<any>> {
    return this.request(`/api/data/${dataId}/preview?rows=${rows}`)
  }

  async processData(dataId: string, options: any): Promise<ApiResponse<any>> {
    return this.request('/api/data/process', {
      method: 'POST',
      body: JSON.stringify({
        data_id: dataId,
        preprocess_options: options
      })
    })
  }

  async listData(skip: number = 0, limit: number = 20): Promise<ApiResponse<any>> {
    return this.request(`/api/data/?skip=${skip}&limit=${limit}`)
  }

  async deleteData(dataId: string): Promise<ApiResponse<any>> {
    return this.request(`/api/data/${dataId}`, {
      method: 'DELETE'
    })
  }

  // 函数相关API
  async parseFunction(expression: string): Promise<ApiResponse<any>> {
    return this.request('/api/function/parse', {
      method: 'POST',
      body: JSON.stringify({ expression })
    })
  }

  async applyFunction(dataId: string, expression: string): Promise<ApiResponse<any>> {
    return this.request('/api/function/apply', {
      method: 'POST',
      body: JSON.stringify({
        data_id: dataId,
        expression
      })
    })
  }

  async getFunctionLibrary(): Promise<ApiResponse<any>> {
    return this.request('/api/function/library')
  }

  async validateFunction(expression: string): Promise<ApiResponse<any>> {
    return this.request('/api/function/validate', {
      method: 'POST',
      body: JSON.stringify({ expression })
    })
  }

  // 图表相关API
  async createChart(dataId: string, chartType: string, config: any): Promise<ApiResponse<any>> {
    return this.request('/api/chart/create', {
      method: 'POST',
      body: JSON.stringify({
        data_id: dataId,
        chart_type: chartType,
        config
      })
    })
  }

  async getChart(chartId: string): Promise<ApiResponse<any>> {
    return this.request(`/api/chart/${chartId}`)
  }

  async updateChart(chartId: string, dataId?: string, config?: any): Promise<ApiResponse<any>> {
    return this.request(`/api/chart/${chartId}`, {
      method: 'PUT',
      body: JSON.stringify({
        data_id: dataId,
        config
      })
    })
  }

  async exportChart(chartId: string, format: string = 'png'): Promise<Blob> {
    const response = await fetch(
      `${this.baseURL}/api/chart/${chartId}/export?format=${format}`
    )
    
    if (!response.ok) {
      throw new Error(`Export failed: ${response.statusText}`)
    }
    
    return response.blob()
  }

  async listCharts(skip: number = 0, limit: number = 20): Promise<ApiResponse<any>> {
    return this.request(`/api/chart/?skip=${skip}&limit=${limit}`)
  }

  async getChartTypes(): Promise<ApiResponse<any>> {
    return this.request('/api/chart/types')
  }

  async deleteChart(chartId: string): Promise<ApiResponse<any>> {
    return this.request(`/api/chart/${chartId}`, {
      method: 'DELETE'
    })
  }

  // 系统相关API
  async getSystemInfo(): Promise<ApiResponse<any>> {
    return this.request('/api/system/info')
  }

  async healthCheck(): Promise<ApiResponse<any>> {
    return this.request('/api/system/health')
  }

  async get版本(): Promise<ApiResponse<any>> {
    return this.request('/api/system/version')
  }

  // 工具方法
  async testConnection(): Promise<boolean> {
    try {
      await this.healthCheck()
      return true
    } catch {
      return false
    }
  }

  setBaseURL(url: string): void {
    this.baseURL = url
  }

  getBaseURL(): string {
    return this.baseURL
  }
}

// 创建默认实例
export const apiClient = new ApiClient()

// 导出类型和实例
export default ApiClient
export type { ApiResponse, UploadProgress }
