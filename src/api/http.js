/**
 * Axios 统一实例。
 *
 * 业务模块只需要关心请求参数和后端 data，不重复处理 token、错误提示和超时。
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'

export const TOKEN_KEY = 'fabao_access_token'

const http = axios.create({
  baseURL: '/api',
  // FastGPT 工作流可能需要较长时间，和后端 E2E 验收脚本保持 240 秒一致。
  timeout: 240000,
  headers: {
    'Content-Type': 'application/json'
  }
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  // FormData 必须由浏览器自动设置 multipart boundary。
  // 实例默认的 application/json 会让 axios 把 FormData 序列化成 JSON 字符串（File 变成 {}），
  // 后端拿不到 file 字段，返回 422 请求参数校验失败。
  if (typeof FormData !== 'undefined' && config.data instanceof FormData) {
    delete config.headers['Content-Type']
  }
  return config
})

http.interceptors.response.use(
  (response) => {
    const payload = response.data
    // 后端所有业务响应都使用 code/message/data；HTTP 2xx 但业务失败时也统一提示。
    if (payload && typeof payload === 'object' && 'code' in payload && payload.code >= 400) {
      const error = new Error(payload.message || '请求失败')
      error.response = response
      ElMessage.error(error.message)
      return Promise.reject(error)
    }
    return payload
  },
  (error) => {
    const status = error.response?.status
    const payload = error.response?.data
    const message = payload?.message || error.message || '网络请求失败'

    if (status === 401) {
      localStorage.removeItem(TOKEN_KEY)
      window.dispatchEvent(new CustomEvent('fabao-auth-expired'))
    }

    // 统一由拦截器展示错误，页面只负责结束 loading 状态。
    ElMessage.error(message)
    error.userMessage = message
    return Promise.reject(error)
  }
)

export default http
