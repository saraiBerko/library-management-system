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
  margin-bottom: 1.5rem;
}

nav {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}

nav a {
  text-decoration: none;
}

nav a.router-link-active {
  font-weight: bold;
}
</style>
