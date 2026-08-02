import { apiClient } from './client'

export function getBooks() {
  return apiClient.get('/books').then((res) => res.data)
}

export function createBook(book) {
  return apiClient.post('/books', book).then((res) => res.data)
}

export function deleteBook(id) {
  return apiClient.delete(`/books/${id}`)
}
