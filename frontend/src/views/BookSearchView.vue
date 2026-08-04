<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useBooksStore } from '../stores/books'
import ErrorBanner from '../components/ErrorBanner.vue'
import SearchFiltersBar from '../components/SearchFiltersBar.vue'
import BookResultsTable from '../components/BookResultsTable.vue'

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
    <SearchFiltersBar v-model:q="q" v-model:genre="genre" v-model:available-only="availableOnly" :genres="allGenres" @search="runSearch" />

    <ErrorBanner :message="booksStore.error" />
    <p v-if="booksStore.loading">Loading...</p>
    <BookResultsTable v-else-if="booksStore.results.length" :books="booksStore.results" @select-book="openBook" />
    <p v-else>No books found.</p>
  </section>
</template>
