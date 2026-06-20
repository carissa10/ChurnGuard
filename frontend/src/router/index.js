import { createRouter, createWebHistory } from 'vue-router'
import DashboardHome from '../views/DashboardHome.vue'
import SinglePrediction from '../views/SinglePrediction.vue'
import BatchAnalytics from '../views/BatchAnalytics.vue'
import NLPSentiment from '../views/NLPSentiment.vue'
import HistoryView from '../views/HistoryView.vue' // <-- 1. Import halaman History berhasil ditambahkan

const routes = [
  {
    path: '/',
    name: 'DashboardHome',
    component: DashboardHome,
    meta: { title: 'Dashboard Home' }
  },
  {
    path: '/single-prediction',
    name: 'SinglePrediction',
    component: SinglePrediction,
    meta: { title: 'Single Prediction' }
  },
  {
    path: '/batch-analytics',
    name: 'BatchAnalytics',
    component: BatchAnalytics,
    meta: { title: 'Batch Analytics' }
  },
  {
    path: '/nlp-sentiment',
    name: 'NLPSentiment',
    component: NLPSentiment,
    meta: { title: 'NLP Sentiment Analysis' }
  },
  {
    path: '/history', // <-- 2. Rute URL baru untuk menu History
    name: 'HistoryAnalytics',
    component: HistoryView,
    meta: { title: 'History Analytics' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

export default router