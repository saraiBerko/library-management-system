<script setup>
import { computed } from 'vue'

const props = defineProps({
  pickedBookId: {
    type: Number,
    default: null,
  },
  currentBook: {
    type: Object,
    default: null,
  },
  bookOptions: {
    type: Array,
    default: () => [],
  },
  members: {
    type: Array,
    default: () => [],
  },
  todayIso: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['select-book', 'change-book', 'submit'])

const pickedCopyId = defineModel('pickedCopyId', { default: '' })
const pickedMemberId = defineModel('pickedMemberId', { default: '' })
const dueDate = defineModel('dueDate', { default: '' })

// The book picker's own selection is driven by the parent (it owns the fetch that
// follows a change), so it's read from a prop and written via an emit rather than
// a plain v-model.
const selectedBookId = computed({
  get: () => props.pickedBookId,
  set: (value) => emit('select-book', value),
})

const availableCopiesOfPickedBook = computed(() => {
  if (!props.currentBook || props.currentBook.id !== props.pickedBookId) return []
  return props.currentBook.copies.filter((copy) => copy.status === 'available')
})
</script>

<template>
  <form @submit.prevent="emit('submit')">
    <div v-if="pickedBookId && currentBook">
      <p>
        Book: <strong>{{ currentBook.title }}</strong>
        <button type="button" @click="emit('change-book')">Change book</button>
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
        <select v-model="selectedBookId">
          <option disabled value="">Select a book</option>
          <option v-for="book in bookOptions" :key="book.id" :value="book.id">
            {{ book.title }} ({{ book.available_copies }} available)
          </option>
        </select>
      </label>
    </div>

    <label>
      Member:
      <select v-model="pickedMemberId">
        <option disabled value="">Select a member</option>
        <option v-for="member in members" :key="member.id" :value="member.id">
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
</template>

<style scoped>
form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
  max-width: 28rem;
  margin-bottom: var(--spacing-6);
}
</style>
