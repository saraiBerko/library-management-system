<script setup>
defineProps({
  message: {
    type: String,
    default: null,
  },
})
</script>

<template>
  <p v-if="message" class="error-banner">{{ message }}</p>
</template>

<style scoped>
.error-banner {
  background: var(--color-danger-bg);
  color: var(--color-danger);
  border: 1px solid var(--color-danger);
  border-radius: var(--radius);
  padding: var(--spacing-2) var(--spacing-3);
  margin-bottom: var(--spacing-4);
}
</style>
