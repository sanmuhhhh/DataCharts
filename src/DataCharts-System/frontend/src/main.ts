/**
 * 数据可视化系统前端主文件
 * 
 * 根据设计文档规范提供数据可视化功能
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

app.mount('#app')

// 系统版本信息
export const SYSTEM_VERSION = "0.1.0"
export const SYSTEM_NAME = "DataCharts System"

// 基础测试
console.log(`${SYSTEM_NAME} Frontend v${SYSTEM_VERSION} 已加载`)