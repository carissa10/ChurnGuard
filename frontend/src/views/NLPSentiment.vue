<template>
  <div class="space-y-8 animate-fade-in">
    <div>
      <h2 class="text-3xl font-extrabold text-slate-800 tracking-tight">Sentiment Analysis</h2>
      <p class="text-slate-500 text-sm mt-1">Lakukan deteksi sentimen ulasan atau teks secara otomatis menggunakan LightGBM.</p>
    </div>

    <!-- Tab Navigation -->
    <div class="flex border-b border-slate-100 -mx-2 px-2 space-x-1">
      <button 
        @click="activeTab = 'single'"
        :class="[
          'px-6 py-3 font-bold text-sm transition-all border-b-2 -mb-[2px] rounded-t-xl',
          activeTab === 'single' 
            ? 'border-primary-600 text-primary-600 bg-primary-50/20' 
            : 'border-transparent text-slate-400 hover:text-slate-600 hover:bg-slate-50/50'
        ]"
      >
        Single Prediction
      </button>
      <button 
        @click="activeTab = 'batch'"
        :class="[
          'px-6 py-3 font-bold text-sm transition-all border-b-2 -mb-[2px] rounded-t-xl',
          activeTab === 'batch' 
            ? 'border-primary-600 text-primary-600 bg-primary-50/20' 
            : 'border-transparent text-slate-400 hover:text-slate-600 hover:bg-slate-50/50'
        ]"
      >
        Batch Prediction
      </button>
    </div>

    <!-- Single Analysis Section -->
    <div v-if="activeTab === 'single'" class="grid grid-cols-1 xl:grid-cols-3 gap-8">
      <div class="xl:col-span-2 bg-white rounded-3xl p-8 border border-slate-100 shadow-premium space-y-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <MessageCircle class="w-6 h-6 text-primary-600" />
            <h3 class="text-xl font-bold text-slate-800 tracking-tight">Data Teks Ulasan</h3>
          </div>
          <button 
            type="button" 
            @click="prefillSampleData" 
            class="text-xs font-semibold text-primary-600 hover:text-primary-500 bg-primary-50 px-3 py-1.5 rounded-lg border border-primary-100 hover:border-primary-200 transition-all"
          >
            Prefill Sample Text
          </button>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div class="grid grid-cols-1 gap-6">
            <div class="space-y-2">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Teks Ulasan</label>
              <textarea 
                v-model="form.text" 
                required 
                rows="6"
                placeholder="misal: Aplikasinya jelek banget, lag parah dan suka force close!"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none text-slate-700 font-medium transition-all resize-none"
              ></textarea>
            </div>

            <div class="space-y-2">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Bahasa</label>
              <select 
                v-model="form.lang" 
                required
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none text-slate-700 font-medium transition-all bg-white"
              >
                <option value="id">Indonesian (ID)</option>
                <option value="en">English (EN)</option>
              </select>
            </div>
          </div>

          <div class="pt-4">
            <button 
              type="submit" 
              :disabled="loading"
              class="w-full flex items-center justify-center space-x-2 px-6 py-4 bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 disabled:from-slate-400 disabled:to-slate-300 text-white rounded-2xl font-bold shadow-lg shadow-primary-500/20 hover:shadow-primary-400/30 transition-all duration-300 hover:-translate-y-0.5 focus:outline-none"
            >
              <Loader2 v-if="loading" class="w-5 h-5 animate-spin" />
              <TrendingUp v-else class="w-5 h-5" />
              <span>{{ loading ? 'Menganalisis Teks...' : 'Mulai Analisis Sentimen' }}</span>
            </button>
          </div>
        </form>
      </div>

      <div class="flex flex-col space-y-6">
        <div class="bg-white rounded-3xl p-8 border border-slate-100 shadow-premium flex-1 flex flex-col justify-between min-h-[400px] relative overflow-hidden">
          <div v-if="!result && !loading" class="flex-1 flex flex-col items-center justify-center text-center space-y-4">
            <div class="w-16 h-16 rounded-2xl bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-400">
              <Info class="w-8 h-8" />
            </div>
            <div>
              <h4 class="font-bold text-slate-700">Belum Ada Analisis</h4>
              <p class="text-xs text-slate-400 mt-1 max-w-[200px] mx-auto leading-normal">
                Input teks ulasan di sebelah kiri lalu klik tombol analisis untuk mengetahui sentimennya.
              </p>
            </div>
          </div>

          <div class="flex-1 flex flex-col items-center justify-center text-center space-y-4">
            <div v-if="loading" class="w-20 h-20 rounded-3xl bg-primary-50 flex items-center justify-center text-primary-600 animate-pulse">
              <Loader2 class="w-10 h-10 animate-spin" />
            </div>
            <div v-if="loading">
              <h4 class="font-bold text-slate-700">Menganalisis Sentimen...</h4>
              <p class="text-xs text-slate-400 mt-1 max-w-[200px] mx-auto leading-normal">
                Menghubungkan ke API backend dan memproses ekstraksi fitur TF-IDF...
              </p>
            </div>
          </div>

          <div v-if="result && !loading" class="flex-1 flex flex-col justify-between space-y-6">
            <div class="space-y-1">
              <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Hasil Klasifikasi</span>
              <h3 class="text-lg font-bold text-slate-800 line-clamp-2" :title="result.text">"{{ result.text }}"</h3>
            </div>

            <div 
              :class="[
                'p-6 rounded-3xl border text-center space-y-3 relative overflow-hidden transition-all duration-500 shadow-md flex-1 flex flex-col justify-center',
                sentimentStyles[result.sentiment]?.bg || 'bg-slate-50 border-slate-200 text-slate-700'
              ]"
            >
              <div 
                :class="[
                  'absolute right-0 top-0 w-32 h-32 rounded-full filter blur-2xl -z-10 translate-x-10 -translate-y-10 opacity-40',
                  sentimentStyles[result.sentiment]?.accent || 'bg-slate-400'
                ]"
              ></div>
              <span class="text-xs font-bold uppercase tracking-widest leading-none">Prediksi Sentimen</span>
              <h2 class="text-3xl font-extrabold tracking-tight">{{ result.sentiment }}</h2>
              
              <div class="flex justify-center mt-2">
                <div class="inline-flex px-3 py-1 bg-white/70 backdrop-blur-sm rounded-full text-xs font-bold shadow-sm items-center space-x-1" :class="sentimentStyles[result.sentiment]?.text">
                  <Activity class="w-4 h-4" />
                  <span>Confidence: {{ (result.confidence * 100).toFixed(2) }}%</span>
                </div>
              </div>
            </div>

          </div>
        </div>

        <div v-if="error" class="p-4 rounded-2xl bg-rose-50 border border-rose-100 text-rose-800 flex items-start space-x-3">
          <AlertCircle class="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div>
            <h5 class="font-bold text-sm">Gagal Melakukan Analisis</h5>
            <p class="text-xs mt-0.5 leading-normal">{{ error }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Batch Analysis Section -->
    <div v-if="activeTab === 'batch'" class="space-y-8">
      <!-- Upload Card -->
      <div class="bg-white rounded-3xl p-8 border border-slate-100 shadow-premium space-y-6">
        <div class="flex items-center space-x-3">
          <FileSpreadsheet class="w-6 h-6 text-primary-600" />
          <h3 class="text-xl font-bold text-slate-800 tracking-tight">Upload File CSV</h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="md:col-span-2">
            <!-- Drag & Drop Zone -->
            <div 
              @dragover.prevent="dragOver = true"
              @dragleave.prevent="dragOver = false"
              @drop.prevent="handleFileDrop"
              @click="$refs.fileInput.click()"
              :class="[
                'border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center min-h-[180px]',
                dragOver ? 'border-primary-500 bg-primary-50/50' : 'border-slate-200 hover:border-primary-400 hover:bg-slate-50/50'
              ]"
            >
              <input 
                type="file" 
                ref="fileInput" 
                @change="handleFileSelect" 
                accept=".csv" 
                class="hidden" 
              />
              <Upload class="w-10 h-10 text-slate-400 mb-3" />
              <p class="font-bold text-slate-700 text-sm">
                {{ csvFile ? csvFile.name : 'Pilih file CSV atau seret ke sini' }}
              </p>
              <p class="text-xs text-slate-400 mt-1">
                {{ csvFile ? `${(csvFile.size / 1024).toFixed(1)} KB` : 'Maksimum ukuran file: 10MB. File harus memiliki kolom teks.' }}
              </p>
            </div>
          </div>

          <div class="space-y-4">
            <div class="space-y-2">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Bahasa CSV</label>
              <select 
                v-model="batchLang" 
                required
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none text-slate-700 font-medium transition-all bg-white"
              >
                <option value="id">Indonesian (ID)</option>
                <option value="en">English (EN)</option>
              </select>
            </div>

            <button 
              type="button"
              @click="runBatchAnalysis"
              :disabled="!csvFile || batchLoading"
              class="w-full flex items-center justify-center space-x-2 px-6 py-4 bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 disabled:from-slate-400 disabled:to-slate-300 text-white rounded-2xl font-bold shadow-lg shadow-primary-500/20 hover:shadow-primary-400/30 transition-all duration-300 hover:-translate-y-0.5 focus:outline-none"
            >
              <Loader2 v-if="batchLoading" class="w-5 h-5 animate-spin" />
              <TrendingUp v-else class="w-5 h-5" />
              <span>{{ batchLoading ? 'Menganalisis CSV...' : 'Mulai Analisis Batch' }}</span>
            </button>
          </div>
        </div>

        <!-- Detected Column Notification -->
        <div v-if="detectedColumn" class="p-4 rounded-xl bg-emerald-50 border border-emerald-100 text-emerald-800 flex items-center space-x-3 text-xs">
          <Info class="w-4 h-4 text-emerald-600 shrink-0" />
          <span>Kolom target teks terdeteksi: <strong class="uppercase font-extrabold">{{ detectedColumn }}</strong></span>
        </div>
      </div>

      <!-- Batch Error -->
      <div v-if="batchError" class="p-4 rounded-2xl bg-rose-50 border border-rose-100 text-rose-800 flex items-start space-x-3">
        <AlertCircle class="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
        <div>
          <h5 class="font-bold text-sm">Gagal Melakukan Analisis Batch</h5>
          <p class="text-xs mt-0.5 leading-normal">{{ batchError }}</p>
        </div>
      </div>

      <!-- Results Section -->
      <div v-if="batchResults && !batchLoading" class="space-y-6">
        <!-- Summary KPIs -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
          <!-- Total Card -->
          <div 
            @click="filterSentiment = null; currentPage = 1"
            :class="[
              'rounded-2xl p-6 border shadow-sm flex flex-col justify-between cursor-pointer transition-all hover:-translate-y-0.5 hover:shadow-md',
              !filterSentiment ? 'bg-white border-primary-400 ring-2 ring-primary-400/40' : 'bg-white border-slate-100 hover:border-slate-200'
            ]"
          >
            <span class="text-xs text-slate-400 font-bold uppercase tracking-wider">Total Teks</span>
            <h3 class="text-3xl font-extrabold text-slate-800 mt-2">{{ batchResults.length }}</h3>
            <span v-if="!filterSentiment" class="text-[10px] text-primary-500 font-bold mt-1">● Semua ditampilkan</span>
          </div>
          <!-- Positive KPI -->
          <div 
            @click="filterSentiment = filterSentiment === 'Positive' ? null : 'Positive'; currentPage = 1"
            :class="[
              'rounded-2xl p-6 border shadow-sm flex flex-col justify-between cursor-pointer transition-all hover:-translate-y-0.5 hover:shadow-md',
              filterSentiment === 'Positive' ? 'bg-emerald-50 border-emerald-400 ring-2 ring-emerald-400/40' : 'bg-emerald-50 border-emerald-100 hover:border-emerald-300'
            ]"
          >
            <div class="flex justify-between items-center">
              <span class="text-xs text-emerald-800 font-bold uppercase tracking-wider">Positif</span>
              <span class="px-2 py-0.5 bg-emerald-500 text-white rounded-full text-[10px] font-extrabold">{{ getPercentage('Positive') }}%</span>
            </div>
            <h3 class="text-3xl font-extrabold text-emerald-700 mt-2">{{ getSentimentCount('Positive') }}</h3>
            <span v-if="filterSentiment === 'Positive'" class="text-[10px] text-emerald-600 font-bold mt-1">● Filter aktif</span>
          </div>
          <!-- Negative KPI -->
          <div 
            @click="filterSentiment = filterSentiment === 'Negative' ? null : 'Negative'; currentPage = 1"
            :class="[
              'rounded-2xl p-6 border shadow-sm flex flex-col justify-between cursor-pointer transition-all hover:-translate-y-0.5 hover:shadow-md',
              filterSentiment === 'Negative' ? 'bg-rose-50 border-rose-400 ring-2 ring-rose-400/40' : 'bg-rose-50 border-rose-100 hover:border-rose-300'
            ]"
          >
            <div class="flex justify-between items-center">
              <span class="text-xs text-rose-800 font-bold uppercase tracking-wider">Negatif</span>
              <span class="px-2 py-0.5 bg-rose-500 text-white rounded-full text-[10px] font-extrabold">{{ getPercentage('Negative') }}%</span>
            </div>
            <h3 class="text-3xl font-extrabold text-rose-700 mt-2">{{ getSentimentCount('Negative') }}</h3>
            <span v-if="filterSentiment === 'Negative'" class="text-[10px] text-rose-600 font-bold mt-1">● Filter aktif</span>
          </div>
          <!-- Neutral KPI -->
          <div 
            @click="filterSentiment = filterSentiment === 'Neutral' ? null : 'Neutral'; currentPage = 1"
            :class="[
              'rounded-2xl p-6 border shadow-sm flex flex-col justify-between cursor-pointer transition-all hover:-translate-y-0.5 hover:shadow-md',
              filterSentiment === 'Neutral' ? 'bg-slate-100 border-slate-400 ring-2 ring-slate-400/40' : 'bg-slate-50 border-slate-100 hover:border-slate-300'
            ]"
          >
            <div class="flex justify-between items-center">
              <span class="text-xs text-slate-800 font-bold uppercase tracking-wider">Netral</span>
              <span class="px-2 py-0.5 bg-slate-500 text-white rounded-full text-[10px] font-extrabold">{{ getPercentage('Neutral') }}%</span>
            </div>
            <h3 class="text-3xl font-extrabold text-slate-700 mt-2">{{ getSentimentCount('Neutral') }}</h3>
            <span v-if="filterSentiment === 'Neutral'" class="text-[10px] text-slate-500 font-bold mt-1">● Filter aktif</span>
          </div>
        </div>

        <!-- Sentiment Distribution bar -->
        <div class="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm space-y-3">
          <div class="flex justify-between items-center text-xs font-bold text-slate-500 uppercase tracking-wider">
            <span>Distribusi Sentimen</span>
            <div class="flex space-x-4">
              <span class="flex items-center text-emerald-600"><span class="w-3 h-3 rounded-full bg-emerald-500 mr-1.5"></span>Positif ({{ getPercentage('Positive') }}%)</span>
              <span class="flex items-center text-rose-600"><span class="w-3 h-3 rounded-full bg-rose-500 mr-1.5"></span>Negatif ({{ getPercentage('Negative') }}%)</span>
              <span class="flex items-center text-slate-500"><span class="w-3 h-3 rounded-full bg-slate-500 mr-1.5"></span>Netral ({{ getPercentage('Neutral') }}%)</span>
            </div>
          </div>
          <div class="h-4 w-full bg-slate-100 rounded-full overflow-hidden flex">
            <div :style="{ width: `${getPercentage('Positive')}%` }" class="bg-emerald-500 h-full transition-all duration-500"></div>
            <div :style="{ width: `${getPercentage('Negative')}%` }" class="bg-rose-500 h-full transition-all duration-500"></div>
            <div :style="{ width: `${getPercentage('Neutral')}%` }" class="bg-slate-500 h-full transition-all duration-500"></div>
          </div>
        </div>

        <!-- Table Card -->
        <div class="bg-white rounded-3xl border border-slate-100 shadow-premium overflow-hidden">
          <div class="p-6 border-b border-slate-50 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <div class="flex items-center gap-3">
                <h3 class="text-lg font-bold text-slate-800">Hasil Prediksi Batch</h3>
                <span v-if="filterSentiment" class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold border"
                  :class="filterSentiment === 'Positive' ? 'bg-emerald-500/10 text-emerald-700 border-emerald-500/20' : filterSentiment === 'Negative' ? 'bg-rose-500/10 text-rose-700 border-rose-500/20' : 'bg-slate-500/10 text-slate-700 border-slate-500/20'"
                >
                  Filter: {{ filterSentiment }}
                  <button @click.stop="filterSentiment = null; currentPage = 1" class="ml-1 opacity-60 hover:opacity-100">✕</button>
                </span>
              </div>
              <p class="text-xs text-slate-400 mt-0.5">Tabel menampilkan data ulasan beserta hasil analisis sentimen.</p>
            </div>
            <button 
              type="button" 
              @click="downloadPredictionCSV" 
              class="flex items-center space-x-2 px-4 py-2.5 bg-primary-600 hover:bg-primary-500 text-white rounded-xl text-xs font-bold shadow-md shadow-primary-500/10 hover:-translate-y-0.5 transition-all"
            >
              <Download class="w-4 h-4" />
              <span>Unduh Hasil (.csv)</span>
            </button>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-slate-50/70 border-b border-slate-100 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  <th class="px-6 py-4">No</th>
                  <th class="px-6 py-4">Content</th>
                  <th class="px-6 py-4">Sentimen</th>
                  <th class="px-6 py-4 text-right">Confidence</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 text-sm font-medium text-slate-600">
                <tr v-for="(row, idx) in paginatedResults" :key="idx" class="hover:bg-slate-50/50 transition-colors">
                  <td class="px-6 py-4 text-xs text-slate-400">{{ (currentPage - 1) * pageSize + idx + 1 }}</td>
                  <td class="px-6 py-4 max-w-xs truncate" :title="row[detectedColumn]">{{ row[detectedColumn] }}</td>
                  <td class="px-6 py-4">
                    <span 
                      :class="[
                        'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold border',
                        row.predicted_sentiment === 'Positive' ? 'bg-emerald-500/10 text-emerald-700 border-emerald-500/20' :
                        row.predicted_sentiment === 'Negative' ? 'bg-rose-500/10 text-rose-700 border-rose-500/20' :
                        'bg-slate-500/10 text-slate-700 border-slate-500/20'
                      ]"
                    >
                      {{ row.predicted_sentiment }}
                    </span>
                  </td>
                  <td class="px-6 py-4 text-right font-semibold text-slate-800">
                    {{ (row.confidence * 100).toFixed(2) }}%
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination -->
          <div class="p-6 border-t border-slate-50 flex items-center justify-between">
            <span class="text-xs text-slate-400 font-semibold">
              Menampilkan {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, filteredResults.length) }} dari {{ filteredResults.length }} data
              <span v-if="filterSentiment" class="text-slate-300">(total {{ batchResults.length }})</span>
            </span>
            <div class="flex items-center space-x-2">
              <button 
                @click="currentPage--" 
                :disabled="currentPage === 1"
                class="p-2 border border-slate-200 rounded-lg disabled:opacity-40 hover:bg-slate-50 transition-all cursor-pointer"
              >
                <ChevronLeft class="w-4 h-4" />
              </button>
              <span class="text-xs font-bold text-slate-600">Halaman {{ currentPage }} dari {{ totalPages }}</span>
              <button 
                @click="currentPage++" 
                :disabled="currentPage === totalPages"
                class="p-2 border border-slate-200 rounded-lg disabled:opacity-40 hover:bg-slate-50 transition-all cursor-pointer"
              >
                <ChevronRight class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import axios from 'axios'
import { 
  MessageCircle, 
  Loader2, 
  TrendingUp, 
  Info, 
  AlertCircle,
  Activity,
  FileSpreadsheet,
  Upload,
  Download,
  ChevronLeft,
  ChevronRight
} from '@lucide/vue'

const activeTab = ref('single')
const loading = ref(false)
const result = ref(null)
const error = ref(null)

const form = reactive({
  text: '',
  lang: 'id'
})

const prefillSampleData = () => {
  form.text = 'Aplikasinya jelek banget njir, sering force close. parah lu dev, benerin ngapa yak.'
  form.lang = 'id'
  error.value = null
}

const handleSubmit = async () => {
  loading.value = true
  result.value = null
  error.value = null
  
  try {
    const response = await axios.post('https://churnguard-production-798a.up.railway.app/api/nlp/predict_single', form)
    if (response.data && response.data.status === 'success') {
      const predictionResult = response.data.result
      result.value = predictionResult

      // ================= KODE UTAMA SINKRONISASI KE HISTORY =================
      const existingHistory = localStorage.getItem('historyAnalyticsCache')
      let historyArray = existingHistory ? JSON.parse(existingHistory) : []

      const sekarang = new Date()
      const formatWaktu = sekarang.toLocaleDateString('id-ID', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      }) + ', ' + sekarang.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })

      const labelSentimen = predictionResult.sentiment
      const statusLower = labelSentimen.toLowerCase()

      let statusTeks = 'Aman / Loyal'
      let statusClass = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
      let warnaHasil = 'text-emerald-400'

      if (statusLower === 'negative') {
        statusTeks = 'Perlu Tindakan'
        statusClass = 'bg-rose-500/10 text-rose-400 border-rose-500/20'
        warnaHasil = 'text-rose-400'
      } else if (statusLower === 'neutral') {
        statusTeks = 'Pantau Berkala'
        statusClass = 'bg-slate-500/10 text-slate-400 border-slate-500/20'
        warnaHasil = 'text-slate-400'
      }

      const dataRiwayatBaru = {
        date: formatWaktu,
        type: 'NLP Sentiment',
        content: `"${form.text}"`,
        result: labelSentimen, 
        resultColor: warnaHasil,
        status: statusTeks,
        statusClass: statusClass
      }

      historyArray.unshift(dataRiwayatBaru)
      localStorage.setItem('historyAnalyticsCache', JSON.stringify(historyArray))

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

// Batch analysis refs
const fileInput = ref(null)
const csvFile = ref(null)
const dragOver = ref(false)
const batchLang = ref('id')
const batchLoading = ref(false)
const batchError = ref(null)
const detectedColumn = ref('')
const csvHeaders = ref([])
const csvRawRows = ref([])
const batchResults = ref(null)

// Pagination & Filter
const filterSentiment = ref(null)
const currentPage = ref(1)
const pageSize = ref(100)
const filteredResults = computed(() => {
  if (!batchResults.value) return []
  if (!filterSentiment.value) return batchResults.value
  return batchResults.value.filter(r => r.predicted_sentiment === filterSentiment.value)
})
const totalPages = computed(() => Math.ceil(filteredResults.value.length / pageSize.value) || 1)
const paginatedResults = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredResults.value.slice(start, start + pageSize.value)
})

const parseCSVText = (text) => {
  const lines = text.split(/\r?\n/).filter(line => line.trim() !== '')
  if (lines.length === 0) return { headers: [], rows: [] }
  
  // Auto-detect separator: comma or semicolon
  const separator = lines[0].includes(';') && !lines[0].includes(',') ? ';' : ','
  
  const parseLine = (line, sep = ',') => {
    const fields = []
    let field = ''
    let inQuotes = false
    for (let i = 0; i < line.length; i++) {
      const char = line[i]
      if (char === '"') {
        if (inQuotes && line[i + 1] === '"') {
          field += '"'
          i++
        } else {
          inQuotes = !inQuotes
        }
      } else if (char === sep && !inQuotes) {
        fields.push(field)
        field = ''
      } else {
        field += char
      }
    }
    fields.push(field)
    return fields
  }
  
  const headers = parseLine(lines[0], separator).map(h => h.trim())
  const rows = []
  for (let i = 1; i < lines.length; i++) {
    const fields = parseLine(lines[i], separator)
    const row = {}
    headers.forEach((header, index) => {
      row[header] = fields[index] !== undefined ? fields[index].trim() : ''
    })
    rows.push(row)
  }
  
  return { headers, rows }
}

const detectTextColumn = (headers) => {
  const candidates = ['text', 'review', 'content', 'message', 'sentence', 'ulasan', 'komentar', 'review_text', 'feedback']
  for (const c of candidates) {
    const match = headers.find(h => h.toLowerCase() === c)
    if (match) return match
  }
  return headers[0] || null
}

const handleFileSelect = (event) => {
  const files = event.target.files
  if (files && files.length > 0) {
    loadCSV(files[0])
  }
}

const handleFileDrop = (event) => {
  dragOver.value = false
  const files = event.dataTransfer.files
  if (files && files.length > 0) {
    if (files[0].name.endsWith('.csv')) {
      loadCSV(files[0])
    } else {
      batchError.value = 'Hanya file CSV yang diterima.'
    }
  }
}

const loadCSV = (file) => {
  csvFile.value = file
  batchError.value = null
  batchResults.value = null
  
  const reader = new FileReader()
  reader.onload = (e) => {
    const text = e.target.result
    const { headers, rows } = parseCSVText(text)
    if (headers.length === 0) {
      batchError.value = 'File CSV kosong atau tidak valid.'
      csvFile.value = null
      return
    }
    
    csvHeaders.value = headers
    csvRawRows.value = rows
    
    const col = detectTextColumn(headers)
    if (!col) {
      batchError.value = 'File CSV harus memiliki minimal 1 kolom.'
      csvFile.value = null
      return
    }
    detectedColumn.value = col
    // Auto-run analysis after file is loaded
    runBatchAnalysis()
  }
  reader.onerror = () => {
    batchError.value = 'Gagal membaca file CSV.'
    csvFile.value = null
  }
  reader.readAsText(file)
}

const runBatchAnalysis = async () => {
  if (!csvFile.value || !detectedColumn.value) return
  
  batchLoading.value = true
  batchError.value = null
  currentPage.value = 1
  
  try {
    const formData = new FormData()
    formData.append('file', csvFile.value)
    
    const response = await axios.post(
      `https://churnguard-production-798a.up.railway.app/api/nlp/predict_batch?lang=${batchLang.value}`, 
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )
    
    if (response.data && response.data.status === 'success') {
      const apiResults = response.data.results
      
      const mappedResults = csvRawRows.value.map((row, idx) => {
        const pred = apiResults[idx] || { sentiment: 'Neutral', confidence: 0.5 }
        return {
          ...row,
          predicted_sentiment: pred.sentiment,
          confidence: pred.confidence
        }
      })
      
      batchResults.value = mappedResults

      const existingHistory = localStorage.getItem('historyAnalyticsCache')
      let historyArray = existingHistory ? JSON.parse(existingHistory) : []
      
      const sekarang = new Date()
      const formatWaktu = sekarang.toLocaleDateString('id-ID', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      }) + ', ' + sekarang.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })

      const totalRecs = mappedResults.length
      const posCount = mappedResults.filter(r => r.predicted_sentiment === 'Positive').length
      const negCount = mappedResults.filter(r => r.predicted_sentiment === 'Negative').length
      
      let statusTeks = 'Aman / Loyal'
      let statusClass = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
      let warnaHasil = 'text-emerald-400'

      if (negCount > posCount) {
        statusTeks = 'Perlu Tindakan'
        statusClass = 'bg-rose-500/10 text-rose-400 border-rose-500/20'
        warnaHasil = 'text-rose-400'
      } else if (Math.abs(posCount - negCount) <= totalRecs * 0.1) {
        statusTeks = 'Pantau Berkala'
        statusClass = 'bg-slate-500/10 text-slate-400 border-slate-500/20'
        warnaHasil = 'text-slate-400'
      }

      const dataRiwayatBaru = {
        date: formatWaktu,
        type: 'NLP Batch',
        content: `Batch: "${csvFile.value.name}" (${totalRecs} baris)`,
        result: `${posCount} Positif / ${negCount} Negatif`, 
        resultColor: warnaHasil,
        status: statusTeks,
        statusClass: statusClass
      }

      historyArray.unshift(dataRiwayatBaru)
      localStorage.setItem('historyAnalyticsCache', JSON.stringify(historyArray))
    } else {
      batchError.value = 'Respons API gagal.'
    }
  } catch (err) {
    console.error(err)
    if (err.response && err.response.data && err.response.data.detail) {
      batchError.value = err.response.data.detail
    } else {
      batchError.value = 'Koneksi ke backend FastAPI terputus. Pastikan server backend Anda berjalan di port 8000.'
    }
  } finally {
    batchLoading.value = false
  }
}

const downloadPredictionCSV = () => {
  if (!batchResults.value) return
  
  const escapeCSV = (val) => {
    if (val === null || val === undefined) return ''
    const str = String(val)
    if (str.includes(',') || str.includes(';') || str.includes('"') || str.includes('\n') || str.includes('\r')) {
      return `"${str.replace(/"/g, '""')}"`
    }
    return str
  }
  
  const sep = ','
  const headers = [...csvHeaders.value, 'Predicted_Sentiment', 'Confidence']
  const headerRow = headers.map(escapeCSV).join(sep)
  
  const dataRows = batchResults.value.map(row => {
    return headers.map(header => {
      if (header === 'Predicted_Sentiment') {
        return escapeCSV(row.predicted_sentiment)
      } else if (header === 'Confidence') {
        return escapeCSV(row.confidence)
      } else {
        return escapeCSV(row[header])
      }
    }).join(sep)
  })
  
  const csvContent = [headerRow, ...dataRows].join('\n')
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `hasil_analisis_${csvFile.value.name}`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const getSentimentCount = (sentiment) => {
  if (!batchResults.value) return 0
  return batchResults.value.filter(r => r.predicted_sentiment === sentiment).length
}

const getPercentage = (sentiment) => {
  if (!batchResults.value || batchResults.value.length === 0) return 0
  const count = getSentimentCount(sentiment)
  return ((count / batchResults.value.length) * 100).toFixed(1)
}

const sentimentStyles = {
  'Positive': {
    bg: 'bg-emerald-50 border-emerald-200 text-emerald-800',
    accent: 'bg-emerald-500',
    text: 'text-emerald-700'
  },
  'Negative': {
    bg: 'bg-rose-50 border-rose-200 text-rose-800',
    accent: 'bg-rose-500',
    text: 'text-rose-700'
  },
  'Neutral': {
    bg: 'bg-slate-50 border-slate-200 text-slate-800',
    accent: 'bg-slate-500',
    text: 'text-slate-700'
  }
}
</script>
