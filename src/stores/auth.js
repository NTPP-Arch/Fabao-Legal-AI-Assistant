import { reactive } from 'vue'
import { getCurrentUser, logout as logoutRequest } from '../api/auth'
import { TOKEN_KEY } from '../api/http'

/**
 * 轻量全局认证状态。
 * 不额外引入状态管理库，满足当前项目规模并让 Header、路由和登录页共享状态。
 */
export const authState = reactive({
  user: null,
  loading: false
})

export function hasToken() {
  return Boolean(localStorage.getItem(TOKEN_KEY))
}

export async function loadCurrentUser() {
  if (!hasToken() || authState.loading) return authState.user
  authState.loading = true
  try {
    const response = await getCurrentUser()
    authState.user = response.data
    return authState.user
  } catch {
    authState.user = null
    localStorage.removeItem(TOKEN_KEY)
    return null
  } finally {
    authState.loading = false
  }
}

export function setUser(user) {
  authState.user = user
}

export function clearAuth() {
  logoutRequest()
  authState.user = null
}
