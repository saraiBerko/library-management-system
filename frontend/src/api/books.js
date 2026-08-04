import { apiClient } from './client'

export function searchBooks(params = {}) {
  return apiClient.get('/books', { params }).then((res) => res.data)
}

export function getBook(id) {
  return apiClient.get(`/books/${id}`).then((res) => res.data)
}
