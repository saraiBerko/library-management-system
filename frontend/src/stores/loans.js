import { defineStore } from 'pinia'
import {
  createLoan as createLoanApi,
  listOpenLoans as listOpenLoansApi,
  returnLoan as returnLoanApi,
} from '../api/loans'
import { extractErrorMessage } from '../api/client'

export const useLoansStore = defineStore('loans', {
  state: () => ({
    openLoans: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchOpenLoans() {
      this.loading = true
      this.error = null
      try {
        this.openLoans = await listOpenLoansApi()
      } catch (err) {
        this.error = extractErrorMessage(err)
      } finally {
        this.loading = false
      }
    },
    async createLoan(payload) {
      this.loading = true
      this.error = null
      try {
        await createLoanApi(payload)
        await this.fetchOpenLoans()
        return true
      } catch (err) {
        this.error = extractErrorMessage(err)
        return false
      } finally {
        this.loading = false
      }
    },
    async returnLoan(id) {
      this.loading = true
      this.error = null
      try {
        await returnLoanApi(id)
        await this.fetchOpenLoans()
        return true
      } catch (err) {
        this.error = extractErrorMessage(err)
        return false
      } finally {
        this.loading = false
      }
    },
  },
})
