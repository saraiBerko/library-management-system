<script setup>
import { computed, onMounted } from 'vue'
import { onBeforeRouteUpdate, useRoute, useRouter } from 'vue-router'
import { useBooksStore } from '../stores/books'
import ErrorBanner from '../components/ErrorBanner.vue'

const route = useRoute()
const router = useRouter()
const booksStore = useBooksStore()

onMounted(() => {
  booksStore.fetchBook(route.params.id)
})

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
      <ul>
        <li v-for="copy in booksStore.currentBook.copies" :key="copy.id">
          Copy #{{ copy.id }} — <span :class="`status-${copy.status}`">{{ copy.status }}</span>
        </li>
      </ul>

      <button :disabled="!firstAvailableCopy" @click="goToLoanForm">Loan</button>
    </div>
  </section>
</template>

<style scoped>
.status-available {
  color: #1a7f37;
}

.status-loaned {
  color: #9a6700;
}

.status-lost {
  color: #b3261e;
}
</style>
