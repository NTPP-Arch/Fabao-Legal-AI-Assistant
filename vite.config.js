import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Vite 的基础配置：启用 Vue 单文件组件解析，并为后续本地开发保留扩展空间。
export default defineConfig({
  plugins: [vue()],
  server: {
    // 固定开发端口，方便课堂演示和书签访问。
    port: 5173,
    // 不自动拉起或恢复浏览器窗口，避免开发服务器启动/重载时抢占前台。
    // 访问地址仍保持 http://localhost:5173，可由用户手动打开。
    open: false,
    // 前端统一请求 /api，开发服务器将其转发到已运行的 FastAPI。
    // 当前后端版本的真实前缀是 /api/v1，因此这里同时完成版本前缀映射。
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api/v1')
      }
    }
  }
})
