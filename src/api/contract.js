import http from './http'

export function uploadContract(file) {
  const formData = new FormData()
  formData.append('file', file)
  return http.post('/contracts/upload', formData, {
    // 让浏览器自动补充 multipart boundary，手写 Content-Type 反而可能导致后端无法解析。
    timeout: 240000
  })
}

export function reviewContract(id) {
  return http.post(`/contracts/review/${id}`)
}

export function getContracts() {
  return http.get('/contracts/list')
}
