<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBooksStore } from '../stores/books'
import { useMembersStore } from '../stores/members'
import { useLoansStore } from '../stores/loans'
import ErrorBanner from '../components/ErrorBanner.vue'

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

const availableCopiesOfPickedBook = computed(() => {
  if (!booksStore.currentBook || booksStore.currentBook.id !== pickedBookId.value) return []
  return booksStore.currentBook.copies.filter((copy) => copy.status === 'available')
})

function isOverdue(loan) {
  return !loan.returned_date && loan.due_date < todayIso
}

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
  await loansStore.returnLoan(loanId)
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

    <form @submit.prevent="submitLoan">
      <div v-if="pickedBookId && booksStore.currentBook">
        <p>
          Book: <strong>{{ booksStore.currentBook.title }}</strong>
          <button type="button" @click="clearBookSelection">Change book</button>
        </p>
        <label>
          Copy:
          <select v-model="pickedCopyId">
            <option disabled value="">Select a copy</option>
            <option v-for="copy in availableCopiesOfPickedBook" :key="copy.id" :value="copy.id">
              Copy #{{ copy.id }}
            </option>
          </select>
        </label>
      </div>
      <div v-else>
        <label>
          Book:
          <select v-model="pickedBookId">
            <option disabled value="">Select a book</option>
            <option v-for="book in booksStore.results" :key="book.id" :value="book.id">
              {{ book.title }} ({{ book.available_copies }} available)
            </option>
          </select>
        </label>
      </div>

      <label>
        Member:
        <select v-model="pickedMemberId">
          <option disabled value="">Select a member</option>
          <option v-for="member in membersStore.members" :key="member.id" :value="member.id">
            {{ member.name }}{{ member.is_active ? '' : ' (inactive)' }}
          </option>
        </select>
      </label>

      <label>
        Due date:
        <input v-model="dueDate" type="date" :min="todayIso" />
      </label>

      <button type="submit">Create Loan</button>
    </form>

    <h2>Open Loans</h2>
    <p v-if="loansStore.loading">Loading...</p>
    <table v-else-if="loansStore.openLoans.length">
      <thead>
        <tr>
          <th>Book</th>
          <th>Member</th>
          <th>Loan date</th>
          <th>Due date</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="loan in loansStore.openLoans" :key="loan.id" :class="{ overdue: isOverdue(loan) }">
          <td>{{ loan.book.title }}</td>
          <td>{{ loan.member.name }}</td>
          <td>{{ loan.loan_date }}</td>
          <td>{{ loan.due_date }}</td>
          <td><button @click="handleReturn(loan.id)">Return</button></td>
        </tr>
      </tbody>
    </table>
    <p v-else>No open loans.</p>
  </section>
</template>

<style scoped>
form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-width: 28rem;
  margin-bottom: 2rem;
}

table {
  border-collapse: collapse;
  width: 100%;
}

th,
td {
  text-align: left;
  padding: 0.5rem;
  border-bottom: 1px solid #ddd;
}

tr.overdue {
  background: #fdecea;
}
</style>
