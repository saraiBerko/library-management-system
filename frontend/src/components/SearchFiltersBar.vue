<script setup>
defineProps({
  genres: {
    type: Array,
    default: () => [],
  },
})

const q = defineModel('q', { default: '' })
const genre = defineModel('genre', { default: '' })
const availableOnly = defineModel('availableOnly', { default: false })

const emit = defineEmits(['search'])
</script>

<template>
  <form @submit.prevent="emit('search')">
    <input v-model="q" placeholder="Search by title or author" />
    <select v-model="genre">
      <option value="">All genres</option>
      <option v-for="g in genres" :key="g" :value="g">{{ g }}</option>
    </select>
    <label>
      <input v-model="availableOnly" type="checkbox" />
      Available only
    </label>
    <button type="submit">Search</button>
  </form>
</template>

<style scoped>
form {
  display: flex;
  gap: var(--spacing-2);
  align-items: center;
  margin-bottom: var(--spacing-4);
  flex-wrap: wrap;
}
</style>
