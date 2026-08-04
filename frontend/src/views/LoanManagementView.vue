<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBooksStore } from '../stores/books'
import { useMembersStore } from '../stores/members'
import { useLoansStore } from '../stores/loans'
import ErrorBanner from '../components/ErrorBanner.vue'
import NewLoanForm from '../components/NewLoanForm.vue'
import OpenLoansTable from '../components/OpenLoansTable.vue'

const route = useRoute()
const router = useRouter()
const booksStore = useBooksStore()
const membersStore = useMembersStore()
const loansStore = useLoansStore()

const todayIso = new Date().toISOString().slice(0, 10)

function defaultDueDate() {
  const d = new Date()
  d.setDate(d.getDate() + 14)
  return d.toISOString().slice(0, 10)
}

const prefilledBookId = route.query.bookId ? Number(route.query.bookId) : null
const prefilledCopyId = route.query.copyId ? Number(route.query.copyId) : null

const pickedBookId = ref(prefilledBookId)
const pickedCopyId = ref(prefilledCopyId)
const pickedMemberId = ref('')
const dueDate = ref(defaultDueDate())
const formError = ref(null)

function clearBookSelection() {
  pickedBookId.value = null
  pickedCopyId.value = null
  booksStore.clearCurrentBook()
  // The inline book picker's options come from booksStore.results, which is only
  // populated on mount when arriving without a prefilled book — refetch here too,
  // since clearing a prefilled selection doesn't remount the component.
  booksStore.searchBooks({ available: true })
}

watch(pickedBookId, async (id) => {
  pickedCopyId.value = null
  if (id) {
    await booksStore.fetchBook(id)
  }
})

async function submitLoan() {
  formError.value = null
  if (!pickedMemberId.value || !pickedCopyId.value || !dueDate.value) {
    formError.value = 'Please fill in member, copy, and due date.'
    return
  }
  if (dueDate.value < todayIso) {
    formError.value = 'Due date cannot be in the past.'
    return
  }
  const ok = await loansStore.createLoan({
    member_id: Number(pickedMemberId.value),
    copy_id: Number(pickedCopyId.value),
    due_date: dueDate.value,
  })
  if (ok) {
    pickedMemberId.value = ''
    dueDate.value = defaultDueDate()
    clearBookSelection()
    router.replace({ path: '/loans' })
  }
}

async function handleReturn(loanId) {
  const ok = await loansStore.returnLoan(loanId)
  if (ok) {
    // Mirrors clearBookSelection()'s refetch after a successful create — a returned
    // copy becomes available again, and neither returnLoan() nor fetchOpenLoans()
    // refreshes booksStore, so both the inline picker's counts (results) and the
    // currently-picked book's copy list (currentBook), if it's the book that copy
    // belongs to, go stale otherwise.
    await booksStore.searchBooks({ available: true })
    if (pickedBookId.value) {
      await booksStore.fetchBook(pickedBookId.value)
    }
  }
}

onMounted(async () => {
  membersStore.fetchMembers()
  loansStore.fetchOpenLoans()
  if (prefilledBookId) {
    await booksStore.fetchBook(prefilledBookId)
  } else {
    booksStore.searchBooks({ available: true })
  }
})
</script>

<template>
  <section>
    <h2>New Loan</h2>
    <ErrorBanner :message="formError || loansStore.error" />

    <NewLoanForm
      :picked-book-id="pickedBookId"
      :current-book="booksStore.currentBook"
      :book-options="booksStore.results"
      :members="membersStore.members"
      v-model:picked-copy-id="pickedCopyId"
      v-model:picked-member-id="pickedMemberId"
      v-model:due-date="dueDate"
      :today-iso="todayIso"
      @select-book="(id) => (pickedBookId = id)"
      @change-book="clearBookSelection"
      @submit="submitLoan"
    />

    <h2>Open Loans</h2>
    <p v-if="loansStore.loading">Loading...</p>
    <OpenLoansTable
      v-else-if="loansStore.openLoans.length"
      :loans="loansStore.openLoans"
      :today-iso="todayIso"
      @return-loan="handleReturn"
    />
    <p v-else>No open loans.</p>
  </section>
</template>
