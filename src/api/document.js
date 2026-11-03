import http from './http'

export function generateDocument(payload) {
  return http.post('/documents/generate', payload)
}

export function getDocuments() {
  return http.get('/documents/list')
}

export function getDocument(id) {
  return http.get(`/documents/${id}`)
}
