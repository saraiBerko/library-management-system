<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useBooksStore } from '../stores/books'
import ErrorBanner from '../components/ErrorBanner.vue'

const router = useRouter()
const booksStore = useBooksStore()

const q = ref('')
const genre = ref('')
const availableOnly = ref(false)
const allGenres = ref([])

function runSearch() {
  const filters = {}
  if (q.value) filters.q = q.value
  if (genre.value) filters.genre = genre.value
  if (availableOnly.value) filters.available = true
  booksStore.searchBooks(filters)
}

function openBook(id) {
  router.push(`/books/${id}`)
}

onMounted(async () => {
  await booksStore.searchBooks()
  allGenres.value = [...new Set(booksStore.results.map((book) => book.genre))].sort()
})
</script>

<template>
  <section>
    <form @submit.prevent="runSearch">
      <input v-model="q" placeholder="Search by title or author" />
      <select v-model="genre">
        <option value="">All genres</option>
        <option v-for="g in allGenres" :key="g" :value="g">{{ g }}</option>
      </select>
      <label>
        <input v-model="availableOnly" type="checkbox" />
        Available only
      </label>
      <button type="submit">Search</button>
    </form>

    <ErrorBanner :message="booksStore.error" />
    <p v-if="booksStore.loading">Loading...</p>

    <table v-else-if="booksStore.results.length">
      <thead>
        <tr>
          <th>Title</th>
          <th>Author(s)</th>
          <th>Year</th>
          <th>Available copies</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="book in booksStore.results" :key="book.id" class="clickable-row" @click="openBook(book.id)">
          <td>{{ book.title }}</td>
          <td>{{ book.authors.map((a) => a.name).join(', ') }}</td>
          <td>{{ book.publication_year }}</td>
          <td>{{ book.available_copies }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else>No books found.</p>
  </section>
</template>

<style scoped>
form {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
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

.clickable-row {
  cursor: pointer;
}

.clickable-row:hover {
  background: rgba(0, 0, 0, 0.05);
}
</style>
