import http from './http'

export function getConversations() {
  return http.get('/chat/conversations')
}

export function createConversation(payload = {}) {
  return http.post('/chat/conversations', payload)
}

export function deleteConversation(id) {
  return http.delete(`/chat/conversations/${id}`)
}

export function getMessages(id) {
  return http.get(`/chat/conversations/${id}/messages`)
}

export function sendMessage(id, content) {
  return http.post(`/chat/conversations/${id}/messages`, { content })
}
