<script setup>
defineProps({
  books: {
    type: Array,
    required: true,
  },
})

const emit = defineEmits(['select-book'])
</script>

<template>
  <table>
    <thead>
      <tr>
        <th>Title</th>
        <th>Author(s)</th>
        <th>Year</th>
        <th>Available copies</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="book in books" :key="book.id" class="clickable-row" @click="emit('select-book', book.id)">
        <td>{{ book.title }}</td>
        <td>{{ book.authors.map((a) => a.name).join(', ') }}</td>
        <td>{{ book.publication_year }}</td>
        <td>{{ book.available_copies }}</td>
      </tr>
    </tbody>
  </table>
</template>

<style scoped>
.clickable-row {
  cursor: pointer;
}

.clickable-row:hover {
  background: var(--color-bg);
}
</style>
