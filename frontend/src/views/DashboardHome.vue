<template>
  <div class="space-y-8 animate-fade-in">
    <div class="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
      <div>
        <h2 class="text-3xl font-extrabold text-slate-800 tracking-tight">Dashboard Overview</h2>
        <p class="text-slate-500 text-sm mt-1">Sistem Prediksi Intelijen Pelanggan Netflix ChurnGuard</p>
      </div>
      <div class="flex items-center space-x-2 text-xs font-semibold px-4 py-2 bg-emerald-50 text-emerald-700 border border-emerald-100 rounded-full w-fit">
        <span class="w-2 h-2 bg-emerald-500 rounded-full animate-ping"></span>
        <span>Sistem Analisis Online</span>
      </div>
    </div>

    <div class="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-950 rounded-3xl p-8 text-white relative overflow-hidden shadow-xl border border-slate-800">
      <div class="absolute right-0 top-0 w-96 h-96 bg-primary-600/10 rounded-full filter blur-3xl -z-10 translate-x-20 -translate-y-20"></div>
      <div class="max-w-2xl space-y-4">
        <span class="text-primary-400 font-bold text-xs uppercase tracking-widest">Platform Analitik Prediksi Churn</span>
        <h1 class="text-3xl md:text-4xl font-extrabold tracking-tight leading-tight">
          Sistem Pemantauan <span class="bg-gradient-to-r from-primary-400 to-sky-300 bg-clip-text text-transparent">& Penyelamatan Pelanggan</span>
        </h1>
        <p class="text-slate-300 text-sm md:text-base leading-relaxed">
          Selamat datang di ChurnGuard Analytics. Sistem ini memantau pelanggan yang berisiko berhenti berlangganan, membantu Anda mengambil tindakan pemasaran yang cepat sebelum mereka pergi.
        </p>
        <div class="flex flex-wrap gap-4 pt-4">
          <router-link to="/single-prediction" class="flex items-center space-x-2 px-5 py-3 bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 rounded-xl font-semibold shadow-lg shadow-primary-600/20 hover:shadow-primary-500/30 transition-all duration-300 hover:-translate-y-0.5">
            <UserCheck class="w-5 h-5" />
            <span>Single Prediction</span>
          </router-link>
          <router-link to="/batch-analytics" class="flex items-center space-x-2 px-5 py-3 bg-slate-800 hover:bg-slate-700 rounded-xl font-semibold border border-slate-700 hover:border-slate-600 transition-all duration-300 hover:-translate-y-0.5">
            <FileSpreadsheet class="w-5 h-5" />
            <span>Batch CSV Analytics</span>
          </router-link>
          <router-link to="/nlp-sentiment" class="flex items-center space-x-2 px-5 py-3 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 rounded-xl font-semibold border border-emerald-500/20 transition-all duration-300 hover:-translate-y-0.5">
            <MessageCircle class="w-5 h-5" />
            <span>NLP Sentiment Analysis</span>
          </router-link>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
      <MetricCard label="Total Pelanggan Netflix" value="45.230" :change="3.2" :icon="Users" color="blue" />
      <MetricCard label="Rata-rata Risk Score" :value="averageRiskScoreDisplay" :change="-1.8" :icon="Percent" color="emerald" />
      <MetricCard label="Model Decision Threshold" :value="decisionThresholdDisplay" :icon="Sliders" color="amber" />
      <MetricCard label="Model Accuracy (Validation)" :value="modelAccuracyDisplay" :icon="Award" color="rose" />
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-gradient-to-br from-blue-50 to-blue-100/50 rounded-2xl p-6 border border-blue-200 shadow-md hover:shadow-lg transition-all duration-300">
        <div class="flex items-start space-x-4">
          <div class="w-12 h-12 rounded-xl bg-blue-600 text-white flex items-center justify-center flex-shrink-0">
            <TrendingUp class="w-6 h-6" />
          </div>
          <div>
            <h4 class="font-bold text-slate-800 text-sm md:text-base mb-1">Prediksi Akurat</h4>
            <p class="text-slate-600 text-xs md:text-sm leading-relaxed">Identifikasi pelanggan berisiko churn dengan akurasi 91% menggunakan teknologi AI terdepan.</p>
          </div>
        </div>
      </div>

      <div class="bg-gradient-to-br from-emerald-50 to-emerald-100/50 rounded-2xl p-6 border border-emerald-200 shadow-md hover:shadow-lg transition-all duration-300">
        <div class="flex items-start space-x-4">
          <div class="w-12 h-12 rounded-xl bg-emerald-600 text-white flex items-center justify-center flex-shrink-0">
            <Award class="w-6 h-6" />
          </div>
          <div>
            <h4 class="font-bold text-slate-800 text-sm md:text-base mb-1">Aksi Proaktif</h4>
            <p class="text-slate-600 text-xs md:text-sm leading-relaxed">Ambil tindakan cepat dengan memberikan penawaran khusus sebelum pelanggan pergi.</p>
          </div>
        </div>
      </div>

      <div class="bg-gradient-to-br from-rose-50 to-rose-100/50 rounded-2xl p-6 border border-rose-200 shadow-md hover:shadow-lg transition-all duration-300">
        <div class="flex items-start space-x-4">
          <div class="w-12 h-12 rounded-xl bg-rose-600 text-white flex items-center justify-center flex-shrink-0">
            <Users class="w-6 h-6" />
          </div>
          <div>
            <h4 class="font-bold text-slate-800 text-sm md:text-base mb-1">Tingkatkan Retensi</h4>
            <p class="text-slate-600 text-xs md:text-sm leading-relaxed">Maksimalkan customer lifetime value dan tingkatkan loyalitas pelanggan Netflix.</p>
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
      <div class="xl:col-span-2 bg-white rounded-3xl p-8 border border-slate-100 shadow-premium space-y-6">
        <div class="flex items-center space-x-3">
          <Users class="w-6 h-6 text-primary-600" />
          <h3 class="text-xl font-bold text-slate-800 tracking-tight">Loyalitas Berdasarkan Tipe Paket</h3>
        </div>
        <p class="text-sm text-slate-500 leading-relaxed">
          Analisis real-time pelanggan berdasarkan tipe subscription menunjukkan tingkat loyalitas dan risiko churn untuk setiap segmen:
        </p>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div v-for="type in subscriptionTypes" :key="type.name" class="p-5 rounded-xl border-2 hover:shadow-lg transition-all hover:border-primary-400 group cursor-pointer" :class="type.borderClass">
            <div class="flex items-center justify-between mb-3">
              <h4 class="font-bold text-slate-700 text-sm">{{ type.name }}</h4>
              <span class="text-lg font-bold" :class="type.colorClass">{{ type.percentage }}</span>
            </div>
            <p class="text-xs text-slate-500 mb-3">{{ type.description }}</p>
            <div class="space-y-2 text-xs">
              <div class="flex justify-between">
                <span class="text-slate-600">Pelanggan Aktif:</span>
                <span class="font-semibold text-slate-700">{{ type.activeCount }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-600">Risk Score:</span>
                <span class="font-semibold" :class="type.riskClass">{{ type.riskScore }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-3xl p-8 border border-slate-100 shadow-premium flex flex-col justify-between space-y-6">
        <div class="space-y-4">
          <div class="flex items-center space-x-3">
            <Database class="w-6 h-6 text-primary-600" />
            <h3 class="text-xl font-bold text-slate-800 tracking-tight">Variabel Input (12 Field)</h3>
          </div>
          <p class="text-xs text-slate-500 leading-normal">
            Data pelanggan yang dianalisis oleh model prediksi:
          </p>
          
          <div class="max-h-80 overflow-y-auto pr-2 space-y-1.5 scrollbar-thin">
            <div v-for="field in modelFields" :key="field.name" class="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-100 hover:border-slate-200 hover:bg-slate-100 transition-colors">
              <span class="text-xs font-semibold text-slate-600">{{ field.name }}</span>
              <span class="text-[10px] font-bold px-2.5 py-1 bg-slate-200 text-slate-700 rounded uppercase tracking-wider">{{ field.type }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { 
  Users, 
  Percent, 
  Sliders, 
  Award, 
  UserCheck, 
  FileSpreadsheet, 
  TrendingUp,
  MessageCircle,
  Database
} from '@lucide/vue'
import { computed } from 'vue'
import MetricCard from '../components/MetricCard.vue'

const cachedBatchData = computed(() => {
  const cached = localStorage.getItem('batchAnalyticsCache')
  if (cached) {
    try {
      return JSON.parse(cached)
    } catch (e) {
      return null
    }
  }
  return null
})

const averageRiskScoreDisplay = computed(() => {
  if (cachedBatchData.value && cachedBatchData.value.average_risk_score) {
    return cachedBatchData.value.average_risk_score + '%'
  }
  return '24.18%' 
})

const modelAccuracyDisplay = computed(() => {
  if (cachedBatchData.value && cachedBatchData.value.model_performance) {
    const accuracy = (cachedBatchData.value.model_performance.accuracy * 100).toFixed(2)
    return accuracy + '%'
  }
  return '91.28%' 
})

const decisionThresholdDisplay = computed(() => {
  if (cachedBatchData.value && cachedBatchData.value.model_performance) {
    // Mengalikan dengan 100 dan menambah simbol %
    const thresholdPercent = (cachedBatchData.value.model_performance.decision_threshold * 100).toFixed(2)
    return thresholdPercent + '%'
  }
  return '61.11%'
})

const subscriptionTypes = [
  { 
    name: 'Premium', 
    percentage: '18%', 
    description: 'Paket berlangganan tertinggi',
    activeCount: '8.100',
    riskScore: '12.5%',
    borderClass: 'border-purple-300 bg-purple-50/30 hover:bg-purple-50',
    colorClass: 'text-purple-600',
    riskClass: 'text-emerald-600'
  },
  { 
    name: 'Standard', 
    percentage: '54%', 
    description: 'Paket mid-tier populer',
    activeCount: '24.300',
    riskScore: '24.8%',
    borderClass: 'border-blue-300 bg-blue-50/30 hover:bg-blue-50',
    colorClass: 'text-blue-600',
    riskClass: 'text-amber-600'
  },
  { 
    name: 'Basic', 
    percentage: '28%', 
    description: 'Paket entry-level',
    activeCount: '12.630',
    riskScore: '35.2%',
    borderClass: 'border-slate-300 bg-slate-50/30 hover:bg-slate-50',
    colorClass: 'text-slate-600',
    riskClass: 'text-rose-600'
  }
]

// UPDATE: Mengubah daftar 12 variabel input menjadi format bilingual (Dua Bahasa)
const modelFields = [
  { name: 'CustomerID (ID Pelanggan)', type: 'string' },
  { name: 'age (Umur)', type: 'integer' },
  { name: 'salary_k (Gaji per Bulan/Ribu)', type: 'float' },
  { name: 'tenure_years (Lama Berlangganan/Tahun)', type: 'float' },
  { name: 'number_of_logins (Jumlah Login)', type: 'integer' },
  { name: 'complaints (Jumlah Keluhan)', type: 'integer' },
  { name: 'engagement_score (Skor Keaktifan)', type: 'float' },
  { name: 'subscription_type (Tipe Paket)', type: 'string' },
  { name: 'region (Wilayah Asal)', type: 'string' },
  { name: 'device_type (Jenis Perangkat)', type: 'string' },
  { name: 'signup_date (Tanggal Mendaftar)', type: 'string (date)' },
  { name: 'last_active_date (Tanggal Terakhir Aktif)', type: 'string (date)' }
]
</script>

<style scoped>
.scrollbar-thin::-webkit-scrollbar {
  width: 4px;
}
.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 9999px;
}
</style>