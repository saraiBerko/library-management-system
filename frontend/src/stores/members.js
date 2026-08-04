import { defineStore } from 'pinia'
import { listMembers as listMembersApi } from '../api/members'
import { extractErrorMessage } from '../api/client'

export const useMembersStore = defineStore('members', {
  state: () => ({
    members: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchMembers() {
      this.loading = true
      this.error = null
      try {
        this.members = await listMembersApi()
      } catch (err) {
        this.error = extractErrorMessage(err)
      } finally {
        this.loading = false
      }
    },
  },
})
