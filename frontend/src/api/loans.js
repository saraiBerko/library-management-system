import { apiClient } from './client'

export function listOpenLoans() {
  return apiClient.get('/loans', { params: { open: true } }).then((res) => res.data)
}

export function createLoan(payload) {
  return apiClient.post('/loans', payload).then((res) => res.data)
}

export function returnLoan(id) {
  return apiClient.put(`/loans/${id}/return`).then((res) => res.data)
}
