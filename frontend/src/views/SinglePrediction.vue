<template>
  <div class="space-y-8 animate-fade-in">
    <!-- Header -->
    <div>
      <h2 class="text-3xl font-extrabold text-slate-800 tracking-tight">Single Prediction</h2>
      <p class="text-slate-500 text-sm mt-1">Lakukan kalkulasi probabilitas churn individu dengan validasi data instan.</p>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
      <!-- Input Form Card -->
      <div class="xl:col-span-2 bg-white rounded-3xl p-8 border border-slate-100 shadow-premium space-y-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <UserCheck class="w-6 h-6 text-primary-600" />
            <h3 class="text-xl font-bold text-slate-800 tracking-tight">Data Profil Pelanggan</h3>
          </div>
          <!-- Quick Prefill Button for UX -->
          <button 
            type="button" 
            @click="prefillSampleData" 
            class="text-xs font-semibold text-primary-600 hover:text-primary-500 bg-primary-50 px-3 py-1.5 rounded-lg border border-primary-100 hover:border-primary-200 transition-all"
          >
            Prefill Sample Data
          </button>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- CustomerID -->
            <div class="space-y-2">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Customer ID</label>
              <input 
                v-model="form.CustomerID" 
                type="text" 
                required 
                placeholder="misal: CUST-4819"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none text-slate-700 font-medium transition-all"
              />
            </div>

            <!-- Age -->
            <div class="space-y-2">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Umur (Tahun)</label>
              <input 
                v-model.number="form.age" 
                type="number" 
                required 
                min="0"
                max="120"
                placeholder="misal: 35"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none text-slate-700 font-medium transition-all"
              />
            </div>

            <!-- Salary -->
            <div class="space-y-2">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Salary (k$ / Tahun)</label>
              <input 
                v-model.number="form.salary_k" 
                type="number" 
                step="0.1" 
                required 
                min="0"
                placeholder="misal: 45.5"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none text-slate-700 font-medium transition-all"
              />
            </div>

            <!-- Tenure Years -->
            <div class="space-y-2">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Tenure (Tahun)</label>
              <input 
                v-model.number="form.tenure_years" 
                type="number" 
                step="0.01" 
                required 
                min="0"
                placeholder="misal: 2.5"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none text-slate-700 font-medium transition-all"
              />
            </div>

            <!-- Logins -->
            <div class="space-y-2">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Jumlah Logins</label>
              <input 
                v-model.number="form.number_of_logins" 
                type="number" 
                required 
                min="0"
                placeholder="misal: 15"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none text-slate-700 font-medium transition-all"
              />
            </div>

            <!-- Complaints -->
            <div class="space-y-2">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Jumlah Komplain</label>
              <input 
                v-model.number="form.complaints" 
                type="number" 
                required 
                min="0"
                placeholder="misal: 1"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none text-slate-700 font-medium transition-all"
              />
            </div>

            <!-- Engagement Score -->
            <div class="space-y-2">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Engagement Score (0.0 - 10.0)</label>
              <input 
                v-model.number="form.engagement_score" 
                type="number" 
                step="0.1" 
                required 
                min="0"
                max="10"
                placeholder="misal: 4.8"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none text-slate-700 font-medium transition-all"
              />
            </div>

            <!-- Subscription Type -->
            <div class="space-y-2">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Tipe Langganan</label>
              <select 
                v-model="form.subscription_type" 
                required
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none text-slate-700 font-medium transition-all bg-white"
              >
                <option value="" disabled>Pilih Tipe</option>
                <option value="Basic">Basic</option>
                <option value="Standard">Standard</option>
                <option value="Premium">Premium</option>
              </select>
            </div>

            <!-- Region -->
            <div class="space-y-2">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Wilayah (Region)</label>
              <select 
                v-model="form.region" 
                required
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none text-slate-700 font-medium transition-all bg-white"
              >
                <option value="" disabled>Pilih Wilayah</option>
                <option value="Asia">Asia</option>
                <option value="Europe">Europe</option>
                <option value="North America">North America</option>
                <option value="South America">South America</option>
              </select>
            </div>

            <!-- Device Type -->
            <div class="space-y-2">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Tipe Perangkat</label>
              <select 
                v-model="form.device_type" 
                required
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none text-slate-700 font-medium transition-all bg-white"
              >
                <option value="" disabled>Pilih Perangkat</option>
                <option value="Desktop">Desktop</option>
                <option value="Mobile">Mobile</option>
                <option value="Tablet">Tablet</option>
              </select>
            </div>

            <!-- Signup Date -->
            <div class="space-y-2">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Tanggal Signup</label>
              <input 
                v-model="form.signup_date" 
                type="date" 
                required
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none text-slate-700 font-medium transition-all"
              />
            </div>

            <!-- Last Active Date -->
            <div class="space-y-2">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Tanggal Aktif Terakhir</label>
              <input 
                v-model="form.last_active_date" 
                type="date" 
                required
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none text-slate-700 font-medium transition-all"
              />
            </div>
          </div>

          <!-- Submit Button -->
          <div class="pt-4">
            <button 
              type="submit" 
              :disabled="loading"
              class="w-full flex items-center justify-center space-x-2 px-6 py-4 bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 disabled:from-slate-400 disabled:to-slate-300 text-white rounded-2xl font-bold shadow-lg shadow-primary-500/20 hover:shadow-primary-400/30 transition-all duration-300 hover:-translate-y-0.5 focus:outline-none"
            >
              <Loader2 v-if="loading" class="w-5 h-5 animate-spin" />
              <TrendingUp v-else class="w-5 h-5" />
              <span>{{ loading ? 'Sedang Memproses Estimasi...' : 'Mulai Analisis Churn' }}</span>
            </button>
          </div>
        </form>
      </div>

      <!-- Result Card -->
      <div class="flex flex-col space-y-6">
        <!-- Result Presentation -->
        <div class="bg-white rounded-3xl p-8 border border-slate-100 shadow-premium flex-1 flex flex-col justify-between min-h-[400px] relative overflow-hidden">
          <div v-if="!result && !loading" class="flex-1 flex flex-col items-center justify-center text-center space-y-4">
            <div class="w-16 h-16 rounded-2xl bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-400">
              <Info class="w-8 h-8" />
            </div>
            <div>
              <h4 class="font-bold text-slate-700">Belum Ada Estimasi</h4>
              <p class="text-xs text-slate-400 mt-1 max-w-[200px] mx-auto leading-normal">
                Input data profil pelanggan di sebelah kiri lalu klik tombol analisis untuk memulai.
              </p>
            </div>
          </div>

          <!-- Loading State -->
          <div v-else-if="loading" class="flex-1 flex flex-col items-center justify-center text-center space-y-4">
            <div class="w-20 h-20 rounded-3xl bg-primary-50 flex items-center justify-center text-primary-600 animate-pulse">
              <Loader2 class="w-10 h-10 animate-spin" />
            </div>
            <div>
              <h4 class="font-bold text-slate-700">Menganalisis Pola Churn...</h4>
              <p class="text-xs text-slate-400 mt-1 max-w-[200px] mx-auto leading-normal">
                Menghubungkan ke API backend dan memproses data masukan ke model XGBoost...
              </p>
            </div>
          </div>

          <!-- Success Result Presenter -->
          <div v-else-if="result" class="flex-1 flex flex-col justify-between space-y-6">
            <!-- Header Result -->
            <div class="space-y-1">
              <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Hasil Analisis Churn</span>
              <h3 class="text-lg font-bold text-slate-800">Customer ID: {{ result.CustomerID }}</h3>
            </div>

            <!-- Risk Band Visualizer (Large) -->
            <div 
              :class="[
                'p-6 rounded-3xl border text-center space-y-3 relative overflow-hidden transition-all duration-500 shadow-md',
                bandStyles[result.risk_band]?.bg || 'bg-slate-50 border-slate-200 text-slate-700'
              ]"
            >
              <div 
                :class="[
                  'absolute right-0 top-0 w-32 h-32 rounded-full filter blur-2xl -z-10 translate-x-10 -translate-y-10 opacity-40',
                  bandStyles[result.risk_band]?.accent || 'bg-slate-400'
                ]"
              ></div>
              <span class="text-xs font-bold uppercase tracking-widest leading-none">Status Kategori Risiko</span>
              <h2 class="text-3xl font-extrabold tracking-tight">{{ result.risk_band }}</h2>
              
              <div class="inline-flex px-3 py-1 bg-white/70 backdrop-blur-sm rounded-full text-xs font-bold shadow-sm items-center space-x-1" :class="bandStyles[result.risk_band]?.text">
                <AlertCircle class="w-4 h-4" />
                <span>{{ result.churn_prediction === 1 ? 'Diprediksi Churn (Ya)' : 'Diprediksi Tetap (Tidak)' }}</span>
              </div>
            </div>

            <!-- Risk Score & Churn Status -->
            <div class="grid grid-cols-2 gap-4">
              <div class="p-4 rounded-2xl bg-slate-50 border border-slate-100 hover:border-slate-200 transition-colors">
                <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Risk Score</span>
                <p class="text-2xl font-black text-slate-800 tracking-tight mt-1">{{ result.risk_score }}%</p>
              </div>
              <div 
                :class="[
                  'p-4 rounded-2xl border-2 transition-colors flex flex-col items-center justify-center',
                  result.churn_prediction === 1 
                    ? 'bg-rose-50 border-rose-300 text-rose-700' 
                    : 'bg-emerald-50 border-emerald-300 text-emerald-700'
                ]"
              >
                <span class="text-[10px] font-bold uppercase tracking-wider">Status Prediksi</span>
                <p class="text-2xl font-black tracking-tight mt-1">{{ result.churn_prediction === 1 ? 'CHURN' : 'TIDAK CHURN' }}</p>
              </div>
            </div>

            <!-- Details Advice -->
            <div class="p-4 rounded-2xl bg-slate-50 border border-slate-100 text-slate-600 flex items-start space-x-3 text-xs leading-relaxed">
              <Info class="w-5 h-5 text-slate-400 shrink-0 mt-0.5" />
              <p>
                <strong>Rekomendasi Tindakan:</strong>
                {{ adviceList[result.risk_band] || 'Pantau performa keaktifan secara periodik.' }}
              </p>
            </div>
          </div>
        </div>

        <!-- Error Card -->
        <div v-if="error" class="p-4 rounded-2xl bg-rose-50 border border-rose-100 text-rose-800 flex items-start space-x-3">
          <AlertCircle class="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div>
            <h5 class="font-bold text-sm">Gagal Melakukan Estimasi</h5>
            <p class="text-xs mt-0.5 leading-normal">{{ error }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios'
import { 
  UserCheck, 
  Loader2, 
  TrendingUp, 
  Info, 
  AlertCircle 
} from '@lucide/vue'

const loading = ref(false)
const result = ref(null)
const error = ref(null)

const form = reactive({
  CustomerID: '',
  age: null,
  salary_k: null,
  tenure_years: null,
  number_of_logins: null,
  complaints: null,
  engagement_score: null,
  subscription_type: '',
  region: '',
  device_type: '',
  signup_date: '',
  last_active_date: ''
})

const prefillSampleData = () => {
  form.CustomerID = 'CUST-' + Math.floor(1000 + Math.random() * 9000)
  form.age = 34
  form.salary_k = 48.6
  form.tenure_years = 1.8
  form.number_of_logins = 12
  form.complaints = 0
  form.engagement_score = 5.2
  form.subscription_type = 'Premium'
  form.region = 'Asia'
  form.device_type = 'Desktop'
  form.signup_date = '2024-05-18'
  form.last_active_date = '2026-05-10'
  error.value = null
}

const handleSubmit = async () => {
  loading.value = true
  result.value = null
  error.value = null
  
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/predict_single', form)
    if (response.data && response.data.status === 'success') {
      result.value = response.data.result
    } else {
      error.value = 'Failed to get a successful prediction response.'
    }
  } catch (err) {
    console.error(err)
    if (err.response && err.response.data && err.response.data.detail) {
      error.value = err.response.data.detail
    } else {
      error.value = 'Koneksi ke backend FastAPI terputus. Pastikan server backend Anda berjalan di port 8000.'
    }
  } finally {
    loading.value = false
  }
}

const bandStyles = {
  'Low Risk': {
    bg: 'bg-emerald-50 border-emerald-200 text-emerald-800',
    accent: 'bg-emerald-500',
    text: 'text-emerald-700'
  },
  'Medium Risk': {
    bg: 'bg-amber-50 border-amber-200 text-amber-800',
    accent: 'bg-amber-500',
    text: 'text-amber-700'
  },
  'High Risk': {
    bg: 'bg-rose-50 border-rose-200 text-rose-800',
    accent: 'bg-rose-500',
    text: 'text-rose-700'
  }
}

const adviceList = {
  'Low Risk': 'Pelanggan berada dalam batas aman. Pertahankan layanan standar dan tawarkan fitur penambah kepuasan.',
  'Medium Risk': 'Pelanggan mulai menunjukkan sinyal ketidakpuasan. Rekomendasi program reward loyalitas atau email kuesioner proaktif.',
  'High Risk': 'Sangat Kritis! Hubungi tim CS segera untuk menawarkan insentif khusus, diskon langganan, atau penyelesaian keluhan prioritas.'
}
</script>
