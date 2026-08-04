import { createRouter, createWebHistory } from 'vue-router'
import BookSearchView from '../views/BookSearchView.vue'
import BookDetailView from '../views/BookDetailView.vue'
import LoanManagementView from '../views/LoanManagementView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'book-search', component: BookSearchView },
    { path: '/books/:id', name: 'book-detail', component: BookDetailView },
    { path: '/loans', name: 'loan-management', component: LoanManagementView },
  ],
})

export default router
