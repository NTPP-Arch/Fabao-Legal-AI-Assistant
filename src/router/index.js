import { createRouter, createWebHistory } from 'vue-router'
import { hasToken } from '../stores/auth'

// 路由懒加载页面组件，进入对应页面时才加载页面代码，减少首页首屏体积。
const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomePage.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/AuthView.vue'),
    meta: { title: '登录 / 注册', public: true }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/AuthView.vue'),
    meta: { title: '注册账号', public: true }
  },
  {
    path: '/ai-consult',
    name: 'ai-consult',
    component: () => import('../views/AiConsult.vue'),
    meta: { title: 'AI法律咨询', requiresAuth: true }
  },
  {
    path: '/doc-generate',
    name: 'doc-generate',
    component: () => import('../views/DocGenerate.vue'),
    meta: { title: '文书生成', requiresAuth: true }
  },
  {
    path: '/contract-review',
    name: 'contract-review',
    component: () => import('../views/ContractReview.vue'),
    meta: { title: '合同审查', requiresAuth: true }
  }
]

// 创建 HTML5 历史模式路由，使 URL 更接近普通网站路径。
const router = createRouter({
  history: createWebHistory(),
  routes,
  // 每次进入新页面时回到顶部，避免沿用上一页的滚动位置。
  scrollBehavior: () => ({ top: 0 })
})

// 根据当前路由设置浏览器标签页标题，提升页面辨识度和可访问性。
router.afterEach((to) => {
  document.title = to.meta.title
    ? `${to.meta.title}｜法宝 - AI法律助手`
    : '法宝 - AI法律助手'
})

// 功能页必须登录；未登录时保存原路径，登录成功后自动回跳。
router.beforeEach((to) => {
  if (to.meta.requiresAuth && !hasToken()) {
    return {
      name: 'login',
      query: { redirect: to.fullPath }
    }
  }

  if ((to.name === 'login' || to.name === 'register') && hasToken()) {
    return to.query.redirect || '/'
  }

  return true
})

export default router
