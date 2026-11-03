import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'
import './assets/styles/global.css'

import App from './App.vue'
import router from './router'

// 创建 Vue 应用实例，并注册 Element Plus 和路由后挂载到 index.html 的 #app 节点。
const app = createApp(App)

app.use(router)
app.use(ElementPlus, {
  // 将 Element Plus 的内置提示、分页等文字切换为中文。
  locale: zhCn
})

app.mount('#app')
