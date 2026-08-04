<script setup>
import { computed, onMounted } from 'vue'
import { onBeforeRouteUpdate, useRoute, useRouter } from 'vue-router'
import { useBooksStore } from '../stores/books'
import ErrorBanner from '../components/ErrorBanner.vue'
import CopyList from '../components/CopyList.vue'

const route = useRoute()
const router = useRouter()
const booksStore = useBooksStore()

onMounted(() => {
  booksStore.fetchBook(route.params.id)
})

// Vue Router reuses this component instance when navigating between two
// /books/:id routes, so onMounted alone wouldn't refetch. onBeforeRouteUpdate is
// used instead of watch(() => route.params.id) because it can be awaited — the
// navigation itself pauses until the new book has loaded, avoiding a frame where
// the previous book's data is shown under the new URL.
onBeforeRouteUpdate(async (to) => {
  await booksStore.fetchBook(to.params.id)
})

const firstAvailableCopy = computed(() =>
  booksStore.currentBook?.copies.find((copy) => copy.status === 'available')
)

function goToLoanForm() {
  const copy = firstAvailableCopy.value
  if (!copy) return
  router.push({ path: '/loans', query: { bookId: booksStore.currentBook.id, copyId: copy.id } })
}
</script>

<template>
  <section>
    <ErrorBanner :message="booksStore.error" />
    <p v-if="booksStore.loading">Loading...</p>
    <div v-else-if="booksStore.currentBook">
      <h2>{{ booksStore.currentBook.title }}</h2>
      <p>Author(s): {{ booksStore.currentBook.authors.map((a) => a.name).join(', ') }}</p>
      <p>Year: {{ booksStore.currentBook.publication_year }}</p>
      <p>Genre: {{ booksStore.currentBook.genre }}</p>

      <h3>Copies</h3>
      <CopyList :copies="booksStore.currentBook.copies" />

      <button
        :disabled="!firstAvailableCopy"
        :title="!firstAvailableCopy ? 'No copies currently available' : undefined"
        @click="goToLoanForm"
      >
        Loan
      </button>
    </div>
  </section>
</template>
