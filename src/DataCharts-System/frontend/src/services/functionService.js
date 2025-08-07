/**
 * 函数服务
 * 
 * 处理函数相关的API调用
 */

import { api } from './api.js'

/**
 * 函数服务类
 */
export class FunctionService {
    
    /**
     * 解析函数表达式
     * @param {string} expression - 函数表达式
     * @returns {Promise} - 解析结果
     */
    async parseExpression(expression) {
        try {
            const result = await api.post('/api/function/parse', {
                expression
            })
            
            if (result.status === 'success') {
                return {
                    isValid: result.is_valid,
                    parsedExpression: result.parsed_expression,
                    variables: result.parsed_expression?.variables || [],
                    parameters: result.parsed_expression?.parameters || {},
                    message: result.message || '表达式解析成功'
                }
            } else {
                throw new Error(result.error_message || '表达式解析失败')
            }
        } catch (error) {
            console.error('表达式解析失败:', error)
            throw error
        }
    }

    /**
     * 验证函数语法
     * @param {string} expression - 函数表达式
     * @returns {Promise} - 验证结果
     */
    async validateSyntax(expression) {
        try {
            const result = await api.post('/api/function/validate', {
                expression
            })
            
            if (result.status === 'success') {
                return {
                    isValid: result.is_valid,
                    analysis: result.analysis,
                    message: result.message || '语法验证完成'
                }
            } else {
                throw new Error(result.error_message || '语法验证失败')
            }
        } catch (error) {
            console.error('语法验证失败:', error)
            throw error
        }
    }

    /**
     * 应用函数到数据
     * @param {string} dataId - 数据ID
     * @param {string} expression - 函数表达式
     * @param {object} options - 应用选项
     * @returns {Promise} - 应用结果
     */
    async applyFunction(dataId, expression, options = {}) {
        try {
            const result = await api.post('/api/function/apply', {
                data_id: dataId,
                expression,
                options
            })
            
            if (result.status === 'success') {
                return {
                    resultData: result.result_data,
                    dataType: result.data_type,
                    processingTime: result.processing_time,
                    message: result.message || '函数应用成功'
                }
            } else {
                throw new Error(result.error_message || '函数应用失败')
            }
        } catch (error) {
            console.error('函数应用失败:', error)
            throw error
        }
    }

    /**
     * 获取支持的函数库
     * @returns {Promise} - 函数库信息
     */
    async getFunctionLibrary() {
        try {
            const result = await api.get('/api/function/library')
            
            if (result.status === 'success') {
                return {
                    supportedFunctions: result.supported_functions,
                    functionCategories: result.function_categories,
                    totalFunctions: result.total_functions,
                    executionEnvironment: result.execution_environment
                }
            } else {
                throw new Error(result.error_message || '获取函数库失败')
            }
        } catch (error) {
            console.error('获取函数库失败:', error)
            throw error
        }
    }

    /**
     * 获取特定函数信息
     * @param {string} functionName - 函数名
     * @returns {Promise} - 函数信息
     */
    async getFunctionInfo(functionName) {
        try {
            const result = await api.get(`/api/function/info/${functionName}`)
            
            if (result.status === 'success') {
                return {
                    functionInfo: result.function_info
                }
            } else {
                throw new Error(result.error_message || '获取函数信息失败')
            }
        } catch (error) {
            console.error('获取函数信息失败:', error)
            throw error
        }
    }

    /**
     * 测试函数执行
     * @param {string} expression - 函数表达式
     * @param {object} testData - 测试数据
     * @returns {Promise} - 测试结果
     */
    async testFunction(expression, testData = {}) {
        try {
            const result = await api.post('/api/function/test', {
                expression,
                test_data: testData
            })
            
            if (result.status === 'success') {
                return {
                    testResult: result.test_result,
                    testDataUsed: result.test_data_used
                }
            } else {
                throw new Error(result.error_message || '函数测试失败')
            }
        } catch (error) {
            console.error('函数测试失败:', error)
            throw error
        }
    }

    /**
     * 验证函数是否可以应用到指定数据
     * @param {string} expression - 函数表达式
     * @param {string} dataId - 数据ID
     * @returns {Promise} - 验证结果
     */
    async validateWithData(expression, dataId) {
        try {
            const result = await api.post('/api/function/validate-with-data', {
                expression,
                data_id: dataId
            })
            
            if (result.status === 'success') {
                return {
                    validation: result.validation
                }
            } else {
                throw new Error(result.error_message || '数据验证失败')
            }
        } catch (error) {
            console.error('数据验证失败:', error)
            throw error
        }
    }

    /**
     * 获取函数使用建议
     * @param {string} expression - 当前表达式
     * @param {string} dataId - 数据ID
     * @returns {Promise} - 建议列表
     */
    async getFunctionSuggestions(expression, dataId) {
        try {
            // 首先验证表达式
            const validation = await this.validateWithData(expression, dataId)
            
            const suggestions = []
            
            if (validation.validation?.missing_variables?.length > 0) {
                suggestions.push({
                    type: 'error',
                    message: `缺少变量: ${validation.validation.missing_variables.join(', ')}`,
                    suggestions: validation.validation.suggestions || []
                })
            }
            
            if (validation.validation?.available_variables?.length > 0) {
                suggestions.push({
                    type: 'info',
                    message: `可用变量: ${validation.validation.available_variables.join(', ')}`
                })
            }
            
            return suggestions
            
        } catch (error) {
            console.error('获取函数建议失败:', error)
            return [{
                type: 'error',
                message: '无法获取函数建议: ' + error.message
            }]
        }
    }
}

// 创建默认实例
export const functionService = new FunctionService()

// 默认导出
export default FunctionService
