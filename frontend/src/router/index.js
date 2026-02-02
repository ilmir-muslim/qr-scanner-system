import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import ScanView from '../views/ScanView.vue'
import HistoryView from '../views/HistoryView.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/scan',
    name: 'Scan',
    component: ScanView
  },
  {
    path: '/history',
    name: 'History',
    component: HistoryView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router