import http, { TOKEN_KEY } from './http'

export function register(payload) {
  return http.post('/auth/register', payload)
}

export async function login(payload) {
  const response = await http.post('/auth/login', payload)
  if (response?.data?.access_token) {
    localStorage.setItem(TOKEN_KEY, response.data.access_token)
  }
  return response
}

export function getCurrentUser() {
  return http.get('/auth/me')
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY)
}
