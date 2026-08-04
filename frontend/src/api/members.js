import { apiClient } from './client'

export function listMembers() {
  return apiClient.get('/members').then((res) => res.data)
}
