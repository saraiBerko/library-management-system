<script setup>
const props = defineProps({
  loans: {
    type: Array,
    required: true,
  },
  todayIso: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['return-loan'])

function isOverdue(loan) {
  return !loan.returned_date && loan.due_date < props.todayIso
}
</script>

<template>
  <table>
    <thead>
      <tr>
        <th>Book</th>
        <th>Member</th>
        <th>Loan date</th>
        <th>Due date</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="loan in loans" :key="loan.id" :class="{ overdue: isOverdue(loan) }">
        <td>{{ loan.book.title }}</td>
        <td>{{ loan.member.name }}</td>
        <td>{{ loan.loan_date }}</td>
        <td>{{ loan.due_date }}</td>
        <td><button @click="emit('return-loan', loan.id)">Return</button></td>
      </tr>
    </tbody>
  </table>
</template>

<style scoped>
tr.overdue {
  background: color-mix(in srgb, var(--color-danger) 15%, var(--color-surface));
}

tr.overdue td:first-child {
  border-left: 4px solid var(--color-danger);
}
</style>
