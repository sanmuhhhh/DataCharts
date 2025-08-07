<template>
  <div id="app">
    <el-container>
      <el-header class="header">
        <h1>{{ title }}</h1>
        <span class="version">v{{ version }}</span>
      </el-header>
      
      <el-main class="main">
        <div class="welcome">
          <el-card class="welcome-card">
            <h2>欢迎使用 DataCharts 数据可视化系统</h2>
            <p>版本: {{ version }}</p>
            <p>状态: 前端应用已启动</p>
            <el-divider />
            <p>系统功能:</p>
            <ul>
              <li>数据导入和处理</li>
              <li>函数表达式解析</li>
              <li>多种图表类型生成</li>
              <li>矩阵数据可视化</li>
            </ul>
          </el-card>
        </div>
        
        <router-view />
      </el-main>
      
      <el-footer class="footer">
        <p>&copy; 2024 DataCharts Team. 数据可视化系统前端.</p>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { SYSTEM_VERSION, SYSTEM_NAME } from './main'

const title = ref(SYSTEM_NAME)
const version = ref(SYSTEM_VERSION)
</script>

<style scoped>
#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: #409EFF;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header h1 {
  margin: 0;
  font-size: 24px;
}

.version {
  font-size: 14px;
  opacity: 0.8;
}

.main {
  flex: 1;
  padding: 20px;
  background-color: #f5f5f5;
}

.welcome {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.welcome-card {
  max-width: 600px;
  text-align: center;
}

.welcome-card h2 {
  color: #409EFF;
  margin-bottom: 20px;
}

.welcome-card ul {
  text-align: left;
  max-width: 300px;
  margin: 0 auto;
}

.footer {
  background-color: #f0f0f0;
  text-align: center;
  padding: 10px;
  border-top: 1px solid #ddd;
}

.footer p {
  margin: 0;
  color: #666;
  font-size: 12px;
}
</style>