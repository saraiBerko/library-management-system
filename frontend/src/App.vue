<script setup></script>

<template>
  <header>
    <h1>Library Management System</h1>
    <nav>
      <RouterLink to="/">Search Books</RouterLink>
      <RouterLink to="/loans">Loan Management</RouterLink>
    </nav>
  </header>
  <main>
    <RouterView />
  </main>
</template>

<style scoped>
header {
  margin-bottom: var(--spacing-6);
  padding-bottom: var(--spacing-4);
  border-bottom: 1px solid var(--color-border);
}

h1 {
  margin: 0;
}

nav {
  display: flex;
  gap: var(--spacing-4);
  margin-top: var(--spacing-3);
}

nav a {
  text-decoration: none;
  color: var(--color-text-muted);
  padding-bottom: var(--spacing-1);
  border-bottom: 2px solid transparent;
}

nav a:hover {
  color: var(--color-text);
}

nav a.router-link-active {
  color: var(--color-primary);
  font-weight: 600;
  border-bottom-color: var(--color-primary);
}
</style>
