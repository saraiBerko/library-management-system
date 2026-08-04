import { defineStore } from 'pinia'
import { getBook as getBookApi, searchBooks as searchBooksApi } from '../api/books'
import { extractErrorMessage } from '../api/client'

export const useBooksStore = defineStore('books', {
  state: () => ({
    results: [],
    currentBook: null,
    loading: false,
    error: null,
  }),
  actions: {
    async searchBooks(filters = {}) {
      this.loading = true
      this.error = null
      try {
        this.results = await searchBooksApi(filters)
      } catch (err) {
        this.error = extractErrorMessage(err)
      } finally {
        this.loading = false
      }
    },
    async fetchBook(id) {
      this.loading = true
      this.error = null
      this.currentBook = null
      try {
        this.currentBook = await getBookApi(id)
      } catch (err) {
        this.error = extractErrorMessage(err)
      } finally {
        this.loading = false
      }
    },
    clearCurrentBook() {
      this.currentBook = null
    },
  },
})
