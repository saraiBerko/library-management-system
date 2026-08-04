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
  background: #fdecea;
  color: #b3261e;
  border: 1px solid #f5c6c2;
  border-radius: 4px;
  padding: 0.5rem 0.75rem;
}
</style>
