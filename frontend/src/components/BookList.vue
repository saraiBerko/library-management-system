<script setup>
import { onMounted, ref } from 'vue'
import { createBook, deleteBook, getBooks } from '../api/books'

const books = ref([])
const form = ref({ title: '', author: '', isbn: '' })

async function loadBooks() {
  books.value = await getBooks()
}

async function addBook() {
  await createBook(form.value)
  form.value = { title: '', author: '', isbn: '' }
  await loadBooks()
}

async function removeBook(id) {
  await deleteBook(id)
  await loadBooks()
}

onMounted(loadBooks)
</script>

<template>
  <section>
    <form @submit.prevent="addBook">
      <input v-model="form.title" placeholder="Title" required />
      <input v-model="form.author" placeholder="Author" required />
      <input v-model="form.isbn" placeholder="ISBN" required />
      <button type="submit">Add Book</button>
    </form>

    <ul>
      <li v-for="book in books" :key="book.id">
        {{ book.title }} — {{ book.author }}
        <button @click="removeBook(book.id)">Delete</button>
      </li>
    </ul>
  </section>
</template>
