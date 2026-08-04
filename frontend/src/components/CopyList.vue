<script setup>
defineProps({
  copies: {
    type: Array,
    required: true,
  },
})
</script>

<template>
  <ul class="copy-list">
    <li v-for="copy in copies" :key="copy.id">
      <span>Copy #{{ copy.id }}</span>
      <span class="badge" :class="`badge-${copy.status}`">{{ copy.status }}</span>
    </li>
  </ul>
</template>

<style scoped>
.copy-list {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.copy-list li {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.badge {
  font-size: 0.8em;
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: 999px;
  text-transform: capitalize;
}

.badge-available {
  color: var(--color-success);
  background: var(--color-success-bg);
}

.badge-loaned {
  color: var(--color-warning);
  background: var(--color-warning-bg);
}

.badge-lost {
  color: var(--color-danger);
  background: var(--color-danger-bg);
}
</style>
