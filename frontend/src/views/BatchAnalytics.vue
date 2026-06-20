<template>
  <div class="space-y-8 animate-fade-in">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
      <div>
        <h2 class="text-3xl font-extrabold text-slate-800 tracking-tight">Batch Analytics</h2>
        <p class="text-slate-500 text-sm mt-1">Unggah file CSV untuk analisis prediksi churn massal dengan akurasi tinggi menggunakan XGBoost.</p>
      </div>
      <!-- Sample CSV Generator for easy testing -->
      <button 
        type="button" 
        @click="downloadSampleCSV"
        class="flex items-center space-x-2 text-xs font-semibold px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 rounded-xl transition-all"
      >
        <Download class="w-4 h-4" />
        <span>Download Sample CSV</span>
      </button>
    </div>

    <!-- Drag & Drop Upload Area -->
    <div 
      @dragover.prevent="dragOver = true"
      @dragleave.prevent="dragOver = false"
      @drop.prevent="handleDrop"
      class="border-2 border-dashed rounded-3xl p-10 flex flex-col items-center justify-center text-center space-y-4 transition-all duration-300 relative overflow-hidden bg-white"
      :class="[
        dragOver ? 'border-primary-500 bg-primary-50/30' : 'border-slate-200 hover:border-primary-300',
        loading ? 'pointer-events-none opacity-60' : ''
      ]"
    >
      <input 
        type="file" 
        ref="fileInput" 
        @change="handleFileSelect" 
        accept=".csv" 
        class="hidden" 
      />
      
      <div class="w-16 h-16 rounded-2xl bg-primary-50 text-primary-600 flex items-center justify-center shadow-sm">
        <UploadCloud class="w-8 h-8 animate-bounce" v-if="dragOver" />
        <UploadCloud class="w-8 h-8" v-else />
      </div>

      <div>
        <h4 class="font-bold text-slate-800 text-lg">Unggah File CSV</h4>
        <p class="text-slate-500 text-xs mt-1 max-w-sm mx-auto leading-normal">
          Tarik & letakkan atau <span @click="$refs.fileInput.click()" class="text-primary-600 font-semibold cursor-pointer hover:text-primary-500 underline">pilih file CSV</span>. Format kolom harus sesuai dengan schema model.
        </p>
      </div>

      <div v-if="selectedFile" class="inline-flex items-center space-x-2 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-bold text-slate-700">
        <FileSpreadsheet class="w-4 h-4 text-slate-500" />
        <span>{{ selectedFile.name }} ({{ formatSize(selectedFile.size) }})</span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center p-12 bg-white rounded-3xl border border-slate-100 shadow-premium space-y-4">
      <div class="w-16 h-16 rounded-2xl bg-primary-50 flex items-center justify-center text-primary-600">
        <Loader2 class="w-8 h-8 animate-spin" />
      </div>
      <div class="text-center">
        <h4 class="font-bold text-slate-800">Memproses Dataset...</h4>
        <p class="text-xs text-slate-400 mt-1">Melakukan preprocessing data dan menjalankan inferensi model XGBoost untuk setiap record...</p>
      </div>
    </div>

    <!-- Error Card -->
    <div v-if="error" class="p-4 rounded-2xl bg-rose-50 border border-rose-100 text-rose-800 flex items-start space-x-3">
      <AlertCircle class="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
      <div>
        <h5 class="font-bold text-sm">Gagal Memproses Batch</h5>
        <p class="text-xs mt-0.5 leading-normal">{{ error }}</p>
        <p class="text-xs mt-2 text-rose-700">💡 Tip: Pastikan format CSV sesuai dengan schema dan backend service berjalan.</p>
      </div>
    </div>

    <!-- Clear Cache Button -->
    <div v-if="batchResponse && !loading" class="flex justify-end">
      <button 
        @click="clearCache"
        class="text-xs font-semibold px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 rounded-lg transition-all"
      >
        ↻ Upload File Baru
      </button>
    </div>

    <!-- Results Overview (Summary Cards & Chart) -->
    <div v-if="batchResponse && !loading" class="space-y-8">
      <!-- Summary Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricCard label="Total Data Upload" :value="batchResponse.total_records" :icon="Users" color="blue" />
        <MetricCard label="Prediksi Churn (Ya)" :value="`${batchResponse.total_churn} (${churnPercentage}%)`" :icon="UserCheck" color="rose" />
        <MetricCard label="Prediksi Tidak Churn (Tidak)" :value="`${notChurnCount} (${notChurnPercentage}%)`" :icon="UserCheck" color="emerald" />
        <MetricCard label="Rata-rata Risk Score" :value="batchResponse.average_risk_score + '%'" :icon="Percent" color="amber" />
      </div>

      <!-- Model Performance Metrics Section -->
      <div v-if="batchResponse && batchResponse.model_performance" class="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <!-- Model Accuracy Card -->
        <div class="bg-white rounded-3xl p-8 border border-slate-100 shadow-premium space-y-6">
          <div class="flex items-center space-x-3">
            <Zap class="w-6 h-6 text-primary-600" />
            <h3 class="text-xl font-bold text-slate-800">Performa Model XGBoost</h3>
          </div>
          <p class="text-sm text-slate-500 leading-relaxed">
            Metrik evaluasi model dari set validasi training. Nilai-nilai ini menunjukkan akurasi dan keandalan prediksi churn.
          </p>
          <div class="grid grid-cols-2 gap-4">
            <div class="p-4 rounded-xl bg-emerald-50 border border-emerald-100 space-y-1">
              <p class="text-[10px] text-emerald-600 font-bold uppercase tracking-wider">Accuracy</p>
              <p class="text-2xl font-extrabold text-emerald-700">{{ formatPercent(batchResponse.model_performance.accuracy) }}</p>
            </div>
            <div class="p-4 rounded-xl bg-blue-50 border border-blue-100 space-y-1">
              <p class="text-[10px] text-blue-600 font-bold uppercase tracking-wider">Precision</p>
              <p class="text-2xl font-extrabold text-blue-700">{{ formatPercent(batchResponse.model_performance.precision) }}</p>
            </div>
            <div class="p-4 rounded-xl bg-amber-50 border border-amber-100 space-y-1">
              <p class="text-[10px] text-amber-600 font-bold uppercase tracking-wider">Recall</p>
              <p class="text-2xl font-extrabold text-amber-700">{{ formatPercent(batchResponse.model_performance.recall) }}</p>
            </div>
            <div class="p-4 rounded-xl bg-rose-50 border border-rose-100 space-y-1">
              <p class="text-[10px] text-rose-600 font-bold uppercase tracking-wider">F1-Score</p>
              <p class="text-2xl font-extrabold text-rose-700">{{ formatPercent(batchResponse.model_performance.f1_score) }}</p>
            </div>
            <div class="p-4 rounded-xl bg-purple-50 border border-purple-100 space-y-1">
              <p class="text-[10px] text-purple-600 font-bold uppercase tracking-wider">AUC-ROC</p>
              <p class="text-2xl font-extrabold text-purple-700">{{ formatPercent(batchResponse.model_performance.auc_score) }}</p>
            </div>
            <div class="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
              <p class="text-[10px] text-slate-600 font-bold uppercase tracking-wider">Threshold</p>
              <p class="text-2xl font-extrabold text-slate-700">{{ batchResponse.model_performance.decision_threshold.toFixed(4) }}</p>
            </div>
          </div>
        </div>

        <!-- Risk Analysis & Recommendations -->
        <div class="bg-white rounded-3xl p-8 border border-slate-100 shadow-premium space-y-6">
          <div class="flex items-center space-x-3">
            <AlertTriangle class="w-6 h-6 text-primary-600" />
            <h3 class="text-xl font-bold text-slate-800">Analisis Risiko & Rekomendasi</h3>
          </div>
          <p class="text-sm text-slate-500 leading-relaxed">
            Ringkasan berdasarkan rule-based analytics dari hasil prediksi batch Anda.
          </p>
          
          <div v-if="batchResponse && batchResponse.risk_analysis" class="space-y-3">
            <!-- Risk Distribution -->
            <div class="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-3">
              <p class="text-xs font-bold text-slate-600 uppercase tracking-wider">Distribusi Segmen Risiko</p>
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-slate-700">🟢 Low Risk (≤30%)</span>
                  <span class="font-bold text-slate-800">{{ batchResponse.risk_analysis.low_risk_count }} ({{ formatRiskPercentage(batchResponse.risk_analysis.low_risk_count) }}%)</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-slate-700">🟡 Medium Risk (31-70%)</span>
                  <span class="font-bold text-slate-800">{{ batchResponse.risk_analysis.medium_risk_count }} ({{ formatRiskPercentage(batchResponse.risk_analysis.medium_risk_count) }}%)</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-slate-700">🔴 High Risk (>70%)</span>
                  <span class="font-bold text-rose-700">{{ batchResponse.risk_analysis.high_risk_count }} ({{ formatRiskPercentage(batchResponse.risk_analysis.high_risk_count) }}%)</span>
                </div>
              </div>
            </div>

            <!-- Rules and Recommendations -->
            <div class="p-4 rounded-xl bg-blue-50 border border-blue-100 space-y-2">
              <p class="text-xs font-bold text-blue-600 uppercase tracking-wider">💡 Rekomendasi Berdasarkan Aturan</p>
              <ul class="text-xs text-blue-700 space-y-1 list-disc list-inside">
                <li v-if="riskAnalysisRules.high_risk_alert">{{ riskAnalysisRules.high_risk_alert }}</li>
                <li v-if="riskAnalysisRules.medium_risk_action">{{ riskAnalysisRules.medium_risk_action }}</li>
                <li v-if="riskAnalysisRules.churn_recommendation">{{ riskAnalysisRules.churn_recommendation }}</li>
                <li v-if="riskAnalysisRules.model_confidence">{{ riskAnalysisRules.model_confidence }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- Chart and Data List Grid -->
      <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <!-- Distribution Chart -->
        <div class="bg-white rounded-3xl p-8 border border-slate-100 shadow-premium flex flex-col justify-between space-y-6">
          <div class="space-y-1">
            <h3 class="text-lg font-bold text-slate-800">Distribusi Segmen Risiko</h3>
            <p class="text-xs text-slate-400">Breakdown risiko pelanggan berdasarkan risk bands (Low, Medium, High)</p>
          </div>
          
          <div class="h-64 flex items-center justify-center relative">
            <Pie v-if="chartData" :data="chartData" :options="chartOptions" />
          </div>

          <!-- Color Legends -->
          <div class="grid grid-cols-3 gap-2 pt-4 border-t border-slate-100 text-center">
            <div class="space-y-1">
              <span class="inline-flex w-3 h-3 bg-emerald-500 rounded-full"></span>
              <p class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Low Risk</p>
              <p class="text-sm font-bold text-slate-800">{{ riskDistribution.low }}</p>
            </div>
            <div class="space-y-1">
              <span class="inline-flex w-3 h-3 bg-amber-500 rounded-full"></span>
              <p class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Medium Risk</p>
              <p class="text-sm font-bold text-slate-800">{{ riskDistribution.medium }}</p>
            </div>
            <div class="space-y-1">
              <span class="inline-flex w-3 h-3 bg-rose-500 rounded-full"></span>
              <p class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">High Risk</p>
              <p class="text-sm font-bold text-slate-800">{{ riskDistribution.high }}</p>
            </div>
          </div>
        </div>

        <!-- Data Grid (Table with Pagination & Search) -->
        <div class="bg-white rounded-3xl p-8 border border-slate-100 shadow-premium space-y-6 flex flex-col justify-between min-h-[500px]">
          <div class="space-y-4">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
              <div class="space-y-1">
                <h3 class="text-lg font-bold text-slate-800">Hasil Prediksi Detail</h3>
                <p class="text-xs text-slate-400">Tabel lengkap dengan Customer ID, prediksi, risk score, dan risk band</p>
              </div>
              
              <!-- Search Box -->
              <div class="relative w-full md:w-64">
                <Search class="absolute left-3.5 top-3.5 w-4 h-4 text-slate-400" />
                <input 
                  v-model="searchQuery" 
                  type="text" 
                  placeholder="Cari Customer ID..."
                  class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none text-xs font-semibold text-slate-700 transition-all bg-slate-50"
                />
              </div>
            </div>

            <!-- Filter Controls -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 bg-slate-50 rounded-2xl border border-slate-100/80">
              <div class="space-y-1.5">
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Churn Prediction:</span>
                <div class="grid grid-cols-3 bg-white rounded-xl p-1 border border-slate-200 shadow-sm text-center">
                  <button 
                    @click="filterChurn = null"
                    :class="[
                      'py-1.5 text-[11px] font-bold rounded-lg transition-all',
                      filterChurn === null ? 'bg-primary-600 text-white shadow-sm' : 'text-slate-500 hover:text-slate-700'
                    ]"
                  >
                    Semua
                  </button>
                  <button 
                    @click="filterChurn = 1"
                    :class="[
                      'py-1.5 text-[11px] font-bold rounded-lg transition-all',
                      filterChurn === 1 ? 'bg-rose-600 text-white shadow-sm' : 'text-slate-500 hover:text-slate-700'
                    ]"
                  >
                    Ya (Churn)
                  </button>
                  <button 
                    @click="filterChurn = 0"
                    :class="[
                      'py-1.5 text-[11px] font-bold rounded-lg transition-all',
                      filterChurn === 0 ? 'bg-emerald-600 text-white shadow-sm' : 'text-slate-500 hover:text-slate-700'
                    ]"
                  >
                    Tidak
                  </button>
                </div>
              </div>

              <div class="space-y-1.5">
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Risk Band:</span>
                <div class="grid grid-cols-4 bg-white rounded-xl p-1 border border-slate-200 shadow-sm text-center">
                  <button 
                    @click="filterRiskBand = null"
                    :class="[
                      'py-1.5 text-[11px] font-bold rounded-lg transition-all',
                      filterRiskBand === null ? 'bg-primary-600 text-white shadow-sm' : 'text-slate-500 hover:text-slate-700'
                    ]"
                  >
                    Semua
                  </button>
                  <button 
                    @click="filterRiskBand = 'Low Risk'"
                    :class="[
                      'py-1.5 text-[11px] font-bold rounded-lg transition-all',
                      filterRiskBand === 'Low Risk' ? 'bg-emerald-600 text-white shadow-sm' : 'text-slate-500 hover:text-slate-700'
                    ]"
                  >
                    Low
                  </button>
                  <button 
                    @click="filterRiskBand = 'Medium Risk'"
                    :class="[
                      'py-1.5 text-[11px] font-bold rounded-lg transition-all',
                      filterRiskBand === 'Medium Risk' ? 'bg-amber-600 text-white shadow-sm' : 'text-slate-500 hover:text-slate-700'
                    ]"
                  >
                    Medium
                  </button>
                  <button 
                    @click="filterRiskBand = 'High Risk'"
                    :class="[
                      'py-1.5 text-[11px] font-bold rounded-lg transition-all',
                      filterRiskBand === 'High Risk' ? 'bg-rose-600 text-white shadow-sm' : 'text-slate-500 hover:text-slate-700'
                    ]"
                  >
                    High
                  </button>
                </div>
              </div>
            </div>

            <!-- Table -->
            <div class="overflow-x-auto border border-slate-100 rounded-2xl">
              <table class="w-full text-left border-collapse">
                <thead>
                  <tr class="bg-slate-50 border-b border-slate-150 text-[10px] text-slate-500 font-bold uppercase tracking-wider">
                    <th class="p-4">Customer ID</th>
                    <th class="p-4">Churn Prediction</th>
                    <th class="p-4">Risk Score</th>
                    <th class="p-4">Risk Band</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100 text-xs">
                  <tr v-for="row in paginatedResults" :key="row.CustomerID" class="hover:bg-slate-50 transition-colors">
                    <td 
                      @click="openRecommendation(row)"
                      class="p-4 font-bold text-primary-600 hover:text-primary-800 hover:underline cursor-pointer font-mono"
                    >
                      {{ row.CustomerID }}
                    </td>
                    <td class="p-4">
                      <span class="inline-flex px-2 py-0.5 rounded font-bold text-[10px]" :class="row.churn_prediction === 1 ? 'bg-rose-50 text-rose-700 border border-rose-100' : 'bg-emerald-50 text-emerald-700 border border-emerald-100'">
                        {{ row.churn_prediction === 1 ? 'Ya' : 'Tidak' }}
                      </span>
                    </td>
                    <td class="p-4 font-extrabold text-slate-700">{{ row.risk_score }}%</td>
                    <td class="p-4">
                      <span class="inline-flex px-2 py-0.5 rounded-full font-bold text-[10px] items-center space-x-1" :class="bandStyles[row.risk_band] || 'bg-slate-100 text-slate-700'">
                        <span class="w-1.5 h-1.5 rounded-full" :class="bandDots[row.risk_band] || 'bg-slate-400'"></span>
                        <span>{{ row.risk_band }}</span>
                      </span>
                    </td>
                  </tr>
                  <tr v-if="filteredResults.length === 0">
                    <td colspan="4" class="p-8 text-center text-slate-400 font-medium">
                      Tidak ada data yang cocok dengan pencarian/filter Anda.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Pagination -->
          <div v-if="totalPages > 1" class="flex items-center justify-between border-t border-slate-100 pt-4 text-xs font-semibold text-slate-500">
            <span>Halaman {{ currentPage }} dari {{ totalPages }}</span>
            <div class="flex items-center space-x-2">
              <button 
                @click="currentPage--" 
                :disabled="currentPage === 1"
                class="p-2 rounded-lg border border-slate-200 disabled:opacity-40 hover:bg-slate-50 transition-colors focus:outline-none"
              >
                <ChevronLeft class="w-4 h-4" />
              </button>
              <button 
                @click="currentPage++" 
                :disabled="currentPage === totalPages"
                class="p-2 rounded-lg border border-slate-200 disabled:opacity-40 hover:bg-slate-50 transition-colors focus:outline-none"
              >
                <ChevronRight class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        <!-- Retention Recommendation Modal -->
        <div v-if="showModal && selectedCustomer" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <!-- Backdrop -->
          <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm shadow-2xl" @click="showModal = false"></div>
          
          <!-- Modal Content -->
          <div class="relative bg-white rounded-3xl w-full max-w-2xl overflow-hidden shadow-2xl border border-slate-150 flex flex-col max-h-[90vh] animate-scale-in">
            <!-- Modal Header -->
            <div class="p-6 border-b border-slate-100 flex justify-between items-start bg-slate-50">
              <div>
                <span class="text-[10px] font-bold text-primary-600 uppercase tracking-widest">Rekomendasi Retensi Pelanggan</span>
                <h3 class="text-2xl font-extrabold text-slate-800 tracking-tight mt-1 flex items-center gap-2">
                  Customer ID: <span class="text-primary-700 font-mono">{{ selectedCustomer.CustomerID }}</span>
                </h3>
              </div>
              <button @click="showModal = false" class="p-2 hover:bg-slate-200/60 rounded-xl text-slate-400 hover:text-slate-600 transition-colors">
                <X class="w-5 h-5" />
              </button>
            </div>
            
            <!-- Modal Body (Scrollable) -->
            <div class="p-6 overflow-y-auto space-y-6">
              <!-- Quick Status Badges -->
              <div class="grid grid-cols-3 gap-4">
                <div class="p-3 bg-slate-50 rounded-2xl border border-slate-150 text-center">
                  <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Prediction</span>
                  <span 
                    class="inline-block mt-1 px-2.5 py-0.5 rounded font-extrabold text-xs"
                    :class="selectedCustomer.churn_prediction === 1 ? 'bg-rose-50 text-rose-700 border border-rose-100' : 'bg-emerald-50 text-emerald-700 border border-emerald-100'"
                  >
                    {{ selectedCustomer.churn_prediction === 1 ? 'Ya (Churn)' : 'Tidak (Loyal)' }}
                  </span>
                </div>
                <div class="p-3 bg-slate-50 rounded-2xl border border-slate-150 text-center">
                  <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Risk Band</span>
                  <span 
                    class="inline-block mt-1 px-2.5 py-0.5 rounded-full font-extrabold text-xs"
                    :class="bandStyles[selectedCustomer.risk_band] || 'bg-slate-100 text-slate-700'"
                  >
                    {{ selectedCustomer.risk_band }}
                  </span>
                </div>
                <div class="p-3 bg-slate-50 rounded-2xl border border-slate-150 text-center">
                  <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Risk Score</span>
                  <span class="block mt-1 text-base font-extrabold text-slate-800">
                    {{ selectedCustomer.risk_score }}%
                  </span>
                </div>
              </div>

              <!-- Customer Demographics and Interaction details -->
              <div class="bg-slate-50 rounded-2xl p-5 border border-slate-100">
                <h4 class="text-xs font-extrabold text-slate-500 uppercase tracking-wider mb-3">Profil & Perilaku Pelanggan</h4>
                
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-semibold text-slate-600">
                  <div v-if="selectedCustomer.age !== undefined">
                    <span class="text-slate-400 block font-medium">Umur</span>
                    <span class="text-slate-800 font-bold">{{ selectedCustomer.age }} Tahun</span>
                  </div>
                  <div v-if="selectedCustomer.subscription_type !== undefined">
                    <span class="text-slate-400 block font-medium">Subscription</span>
                    <span class="text-slate-800 font-bold">{{ selectedCustomer.subscription_type }}</span>
                  </div>
                  <div v-if="selectedCustomer.tenure_years !== undefined">
                    <span class="text-slate-400 block font-medium">Tenure</span>
                    <span class="text-slate-800 font-bold">{{ selectedCustomer.tenure_years }} Tahun</span>
                  </div>
                  <div v-if="selectedCustomer.salary_k !== undefined">
                    <span class="text-slate-400 block font-medium">Salary</span>
                    <span class="text-slate-800 font-bold">${{ selectedCustomer.salary_k }}k</span>
                  </div>
                  <div v-if="selectedCustomer.engagement_score !== undefined">
                    <span class="text-slate-400 block font-medium">Engagement Score</span>
                    <span class="text-slate-800 font-bold">{{ selectedCustomer.engagement_score }}/10</span>
                  </div>
                  <div v-if="selectedCustomer.complaints !== undefined">
                    <span class="text-slate-400 block font-medium">Complaints</span>
                    <span class="font-bold" :class="Number(selectedCustomer.complaints) > 0 ? 'text-rose-600' : 'text-slate-800'">
                      {{ selectedCustomer.complaints }} Keluhan
                    </span>
                  </div>
                  <div v-if="selectedCustomer.number_of_logins !== undefined">
                    <span class="text-slate-400 block font-medium">Jumlah Login</span>
                    <span class="text-slate-800 font-bold">{{ selectedCustomer.number_of_logins }} Kali</span>
                  </div>
                  <div v-if="selectedCustomer.device_type !== undefined">
                    <span class="text-slate-400 block font-medium">Device</span>
                    <span class="text-slate-800 font-bold">{{ selectedCustomer.device_type }}</span>
                  </div>
                </div>
              </div>

              <!-- Actionable Recommendations list -->
              <div class="space-y-4">
                <h4 class="text-xs font-extrabold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                  <Zap class="w-4 h-4 text-amber-500" />
                  <span>Strategi Retention yang Direkomendasikan</span>
                </h4>
                
                <div class="space-y-3">
                  <div 
                    v-for="(rec, index) in getRecommendations(selectedCustomer)" 
                    :key="index"
                    class="p-4 rounded-xl border border-primary-100 bg-primary-50/20 hover:bg-primary-50/40 transition-all space-y-1"
                  >
                    <h5 class="text-sm font-bold text-primary-950 flex items-center gap-1.5">
                      <span class="w-1.5 h-1.5 rounded-full bg-primary-600"></span>
                      {{ rec.title }}
                    </h5>
                    <p class="text-xs text-slate-600 leading-relaxed pl-3 font-medium">
                      {{ rec.desc }}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Modal Footer -->
            <div class="p-6 border-t border-slate-100 flex items-center justify-end space-x-3 bg-slate-50">
              <button 
                @click="copyRetentionStrategy"
                class="flex items-center space-x-2 px-4 py-2.5 bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 rounded-xl text-xs font-bold shadow-sm transition-all"
              >
                <Check class="w-4 h-4 text-emerald-500" v-if="copySuccess" />
                <Copy class="w-4 h-4" v-else />
                <span>{{ copySuccess ? 'Tersalin!' : 'Salin Rekomendasi' }}</span>
              </button>
              <button 
                @click="showModal = false"
                class="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-bold shadow-md transition-all"
              >
                Selesai
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import axios from 'axios'
import { Pie } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement, CategoryScale } from 'chart.js'
import { 
  UploadCloud, 
  Loader2, 
  AlertCircle, 
  Users, 
  UserCheck, 
  Percent, 
  Search, 
  ChevronLeft, 
  ChevronRight, 
  FileSpreadsheet,
  Download,
  Zap,
  AlertTriangle,
  X,
  Copy,
  Check
} from '@lucide/vue'
import MetricCard from '../components/MetricCard.vue'

ChartJS.register(Title, Tooltip, Legend, ArcElement, CategoryScale)

const fileInput = ref(null)
const selectedFile = ref(null)
const dragOver = ref(false)
const loading = ref(false)
const error = ref(null)
const batchResponse = ref(null)

const searchQuery = ref('')
const currentPage = ref(1)
const itemsPerPage = 8

// Filters
const filterChurn = ref(null)
const filterRiskBand = ref(null)

// Parsed CSV storage
const csvHeaders = ref([])
const csvRawRows = ref([])

// Retention Modal state
const showModal = ref(false)
const selectedCustomer = ref(null)
const copySuccess = ref(false)

// Load cache on component mount
onMounted(() => {
  const cachedData = localStorage.getItem('batchAnalyticsCache')
  if (cachedData) {
    try {
      batchResponse.value = JSON.parse(cachedData)
    } catch (e) {
      console.error('Failed to parse cached data', e)
    }
  }
})

const formatSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const handleFileSelect = (event) => {
  const files = event.target.files
  if (files.length > 0) {
    processFile(files[0])
  }
}

const handleDrop = (event) => {
  dragOver.value = false
  const files = event.dataTransfer.files
  if (files.length > 0) {
    processFile(files[0])
  }
}

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

const processFile = (file) => {
  if (!file.name.endsWith('.csv')) {
    error.value = 'Hanya file CSV (.csv) yang didukung untuk diunggah.'
    selectedFile.value = null
    return
  }
  selectedFile.value = file
  error.value = null
  
  const reader = new FileReader()
  reader.onload = (e) => {
    const text = e.target.result
    const { headers, rows } = parseCSVText(text)
    if (headers.length === 0) {
      error.value = 'File CSV kosong atau tidak valid.'
      selectedFile.value = null
      return
    }
    
    csvHeaders.value = headers
    csvRawRows.value = rows
    
    uploadFile()
  }
  reader.onerror = () => {
    error.value = 'Gagal membaca file CSV.'
    selectedFile.value = null
  }
  reader.readAsText(file)
}

const uploadFile = async () => {
  if (!selectedFile.value) return
  
  loading.value = true
  error.value = null
  batchResponse.value = null
  searchQuery.value = ''
  currentPage.value = 1
  
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  
  try {
    const response = await axios.post('https://churnguard-production-798a.up.railway.app/api/predict_batch', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.data && response.data.status === 'success') {
      const apiResults = response.data.results
      
      // Merge original CSV rows with prediction results
      const mappedResults = apiResults.map((res, idx) => {
        const originalRow = csvRawRows.value[idx] || {}
        return {
          ...originalRow,
          ...res
        }
      })
      response.data.results = mappedResults
      
      batchResponse.value = response.data
      // Save to localStorage cache
      localStorage.setItem('batchAnalyticsCache', JSON.stringify(response.data))
    } else {
      error.value = 'Failed to analyze batch dataset.'
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

// Clear cache and allow new upload
const clearCache = () => {
  localStorage.removeItem('batchAnalyticsCache')
  batchResponse.value = null
  selectedFile.value = null
  searchQuery.value = ''
  currentPage.value = 1
  filterChurn.value = null
  filterRiskBand.value = null
  error.value = null
}

// Risk Band Distribution Counters
const riskDistribution = computed(() => {
  if (!batchResponse.value) return { low: 0, medium: 0, high: 0 }
  
  let low = 0, medium = 0, high = 0
  batchResponse.value.results.forEach(res => {
    if (res.risk_band === 'Low Risk') low++
    else if (res.risk_band === 'Medium Risk') medium++
    else if (res.risk_band === 'High Risk') high++
  })
  
  return { low, medium, high }
})

// Calculate Churn Percentage and Not Churn Count
const notChurnCount = computed(() => {
  if (!batchResponse.value) return 0
  return batchResponse.value.total_records - batchResponse.value.total_churn
})

const churnPercentage = computed(() => {
  if (!batchResponse.value) return 0
  const percentage = (batchResponse.value.total_churn / batchResponse.value.total_records) * 100
  return percentage.toFixed(2)
})

const notChurnPercentage = computed(() => {
  if (!batchResponse.value) return 0
  const percentage = (notChurnCount.value / batchResponse.value.total_records) * 100
  return percentage.toFixed(2)
})

// Chart.js reactive configurations
const chartData = computed(() => {
  if (!batchResponse.value) return null
  
  const dist = riskDistribution.value
  return {
    labels: ['Low Risk', 'Medium Risk', 'High Risk'],
    datasets: [
      {
        backgroundColor: ['#10b981', '#f59e0b', '#f43f5e'],
        data: [dist.low, dist.medium, dist.high],
        borderWidth: 0
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      padding: 10,
      cornerRadius: 12,
      bodyFont: {
        size: 11,
        weight: 'bold'
      }
    }
  }
}

// Table filtering & pagination
const filteredResults = computed(() => {
  if (!batchResponse.value) return []
  const query = searchQuery.value.toLowerCase().trim()
  
  let results = batchResponse.value.results
  
  // Search query filter
  if (query) {
    results = results.filter(res => 
      res.CustomerID.toLowerCase().includes(query)
    )
  }
  
  // Churn Prediction filter
  if (filterChurn.value !== null) {
    results = results.filter(res => res.churn_prediction === filterChurn.value)
  }
  
  // Risk Band filter
  if (filterRiskBand.value !== null) {
    results = results.filter(res => res.risk_band === filterRiskBand.value)
  }
  
  return results
})

const totalPages = computed(() => {
  return Math.ceil(filteredResults.value.length / itemsPerPage)
})

const paginatedResults = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredResults.value.slice(start, end)
})

// Watch search query and filters to reset pagination to page 1
watch([searchQuery, filterChurn, filterRiskBand], () => {
  currentPage.value = 1
})

const bandStyles = {
  'Low Risk': 'bg-emerald-50 text-emerald-700 border border-emerald-100',
  'Medium Risk': 'bg-amber-50 text-amber-700 border border-amber-100',
  'High Risk': 'bg-rose-50 text-rose-700 border border-rose-100'
}

const bandDots = {
  'Low Risk': 'bg-emerald-500',
  'Medium Risk': 'bg-amber-500',
  'High Risk': 'bg-rose-500'
}

// Generate sample CSV downloadable file
const downloadSampleCSV = () => {
  const csvHeaders = "CustomerID,age,salary_k,tenure_years,number_of_logins,complaints,engagement_score,subscription_type,region,device_type,signup_date,last_active_date\n"
  const csvRows = [
    "CUST-0001,42,88.4,4.2,18,0,7.8,Premium,Asia,Desktop,2022-01-10,2026-05-15",
    "CUST-0002,28,24.5,0.8,6,2,3.1,Basic,Europe,Mobile,2025-09-20,2026-04-18",
    "CUST-0003,35,45.2,2.1,12,0,5.6,Standard,North America,Tablet,2024-03-01,2026-05-12",
    "CUST-0004,50,95.0,6.0,24,1,8.9,Premium,South America,Desktop,2020-06-15,2026-05-14",
    "CUST-0005,19,15.6,0.3,4,3,1.8,Basic,Asia,Mobile,2025-12-05,2026-03-22"
  ].join("\n")
  
  const csvContent = "data:text/csv;charset=utf-8," + encodeURIComponent(csvHeaders + csvRows)
  
  const link = document.createElement("a")
  link.setAttribute("href", csvContent)
  link.setAttribute("download", "getflix_churn_sample.csv")
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Format decimal as percentage (e.g., 0.9128 -> 91.28%)
const formatPercent = (value) => {
  if (!value && value !== 0) return '-'
  return (value * 100).toFixed(2) + '%'
}

// Format risk segment count as percentage of total records
const formatRiskPercentage = (count) => {
  if (!batchResponse.value || !count) return '0'
  const percentage = (count / batchResponse.value.total_records) * 100
  return percentage.toFixed(1)
}

// Rule-based analytics recommendations
const riskAnalysisRules = computed(() => {
  if (!batchResponse.value || !batchResponse.value.risk_analysis) {
    return {
      high_risk_alert: null,
      medium_risk_action: null,
      churn_recommendation: null,
      model_confidence: null
    }
  }

  const risk = batchResponse.value.risk_analysis
  const total = batchResponse.value.total_records
  const highRiskPercent = (risk.high_risk_count / total) * 100
  const mediumRiskPercent = (risk.medium_risk_count / total) * 100
  const churnPercent = (batchResponse.value.total_churn / total) * 100
  const modelAccuracy = batchResponse.value.model_performance.accuracy

  const rules = {
    high_risk_alert: null,
    medium_risk_action: null,
    churn_recommendation: null,
    model_confidence: null
  }

  // Rule 1: High Risk Alert
  if (highRiskPercent > 20) {
    rules.high_risk_alert = `⚠️ PRIORITAS TINGGI: ${risk.high_risk_count} pelanggan (${highRiskPercent.toFixed(1)}%) dalam kategori risiko tinggi. Tindakan proaktif diperlukan.`
  }

  // Rule 2: Medium Risk Action
  if (mediumRiskPercent > 30) {
    rules.medium_risk_action = `📋 TINDAK LANJUT: ${risk.medium_risk_count} pelanggan (${mediumRiskPercent.toFixed(1)}%) dalam risiko sedang. Pertimbangkan strategi engagement.`
  }

  // Rule 3: Churn Recommendation
  if (churnPercent > 25) {
    rules.churn_recommendation = `🚨 CHURN RATE KRITIS: ${churnPercent.toFixed(1)}% prediksi churn. Escalate ke tim retention segera.`
  } else if (churnPercent > 15) {
    rules.churn_recommendation = `⚡ CHURN RATE NORMAL: ${churnPercent.toFixed(1)}% prediksi churn. Monitor dan implementasi retention plan.`
  } else {
    rules.churn_recommendation = `✅ CHURN RATE SEHAT: ${churnPercent.toFixed(1)}% prediksi churn. Customer base stabil, terus pertahankan.`
  }

  // Rule 4: Model Confidence
  if (modelAccuracy > 0.95) {
    rules.model_confidence = `✨ Model SANGAT ANDAL: Akurasi ${(modelAccuracy * 100).toFixed(2)}%. Rekomendasi ini dapat dipercaya sepenuhnya.`
  } else if (modelAccuracy > 0.90) {
    rules.model_confidence = `👍 Model ANDAL: Akurasi ${(modelAccuracy * 100).toFixed(2)}%. Rekomendasi memiliki confidence tinggi.`
  } else {
    rules.model_confidence = `ℹ️ Model CUKUP AKURAT: Akurasi ${(modelAccuracy * 100).toFixed(2)}%. Pertimbangkan sebagai indikasi awal.`
  }

  return rules
})

// Retention modal helper methods
const openRecommendation = (customer) => {
  selectedCustomer.value = customer
  showModal.value = true
  copySuccess.value = false
}

const copyRetentionStrategy = () => {
  if (!selectedCustomer.value) return
  
  const recs = getRecommendations(selectedCustomer.value)
  const textToCopy = recs.map((r, i) => `${i + 1}. ${r.title}: ${r.desc}`).join('\n')
  
  navigator.clipboard.writeText(`Rekomendasi Retention untuk Customer ID: ${selectedCustomer.value.CustomerID}\nPrediction: ${selectedCustomer.value.churn_prediction === 1 ? 'Churn' : 'Loyal'} (${selectedCustomer.value.risk_band})\n\n${textToCopy}`)
    .then(() => {
      copySuccess.value = true
      setTimeout(() => {
        copySuccess.value = false
      }, 2000)
    })
    .catch(err => {
      console.error('Failed to copy text: ', err)
    })
}

const getRecommendations = (customer) => {
  if (!customer) return []
  
  const recs = []
  const hasComplaints = customer.complaints !== undefined && Number(customer.complaints) > 0
  const isHighRisk = customer.risk_band === 'High Risk' || customer.churn_prediction === 1
  const isMediumRisk = customer.risk_band === 'Medium Risk'
  const lowEngagement = customer.engagement_score !== undefined && Number(customer.engagement_score) < 4.0
  const lowActivity = customer.number_of_logins !== undefined && Number(customer.number_of_logins) < 5
  const isPremium = customer.subscription_type === 'Premium'
  const tenureShort = customer.tenure_years !== undefined && Number(customer.tenure_years) < 1.0

  if (isHighRisk) {
    if (hasComplaints) {
      recs.push({
        title: "Penyelesaian Keluhan Segera",
        desc: `Pelanggan memiliki ${customer.complaints} keluhan terdaftar. Hubungi secara personal dalam 24 jam untuk menyelesaikan masalah dan berikan kompensasi (e.g. gratis langganan 1 bulan).`
      })
    }
    if (lowEngagement || lowActivity) {
      recs.push({
        title: "Re-engagement Push & Insentif",
        desc: "Kirim email/notifikasi penawaran personalisasi khusus dengan diskon loyalitas up to 30% untuk langganan berikutnya, serta perkenalkan kembali benefit utama platform."
      })
    }
    if (isPremium) {
      recs.push({
        title: "Layanan Account Manager Dedicated",
        desc: "Tunjuk perwakilan khusus untuk menangani pelanggan VIP premium ini demi mengembalikan kepercayaan mereka secara proaktif."
      })
    } else {
      recs.push({
        title: "Penawaran Uji Coba Upgrade Gratis",
        desc: "Tawarkan uji coba gratis paket Premium selama 14-30 hari untuk merangsang kembali interaksi dan memperlihatkan nilai tambah layanan."
      })
    }
    recs.push({
      title: "Feedback Survey Terarah",
      desc: "Kirimkan survei kepuasan singkat 1-pertanyaan untuk mendiagnosis penyebab utama potensi churn mereka."
    })
  } else if (isMediumRisk) {
    if (hasComplaints) {
      recs.push({
        title: "Follow-up Keluhan Rutin",
        desc: "Pastikan keluhan sebelumnya sudah diselesaikan sepenuhnya. Lakukan pengecekan status via automated email/WhatsApp."
      })
    }
    recs.push({
      title: "Program Loyalitas & Reward",
      desc: "Berikan poin reward ekstra atau undang ke program referral berhadiah untuk memperkuat retention loop."
    })
    if (lowEngagement) {
      recs.push({
        title: "Rekomendasi Konten Terpersonalisasi",
        desc: "Gunakan algoritma rekomendasi untuk mengirim email berisi konten terpopuler sesuai minat mereka guna mendongkrak engagement score."
      })
    }
  } else {
    recs.push({
      title: "Apresiasi Loyalitas (Nurturing)",
      desc: "Kirimkan email ucapan terima kasih atas loyalitas mereka. Tidak perlu diskon agresif, cukup jaga hubungan baik."
    })
    if (customer.subscription_type !== 'Premium') {
      recs.push({
        title: "Kampanye Upselling",
        desc: `Pelanggan sangat loyal (${customer.subscription_type || 'Basic'}). Tawarkan promo upgrade ke tingkat subscription lebih tinggi dengan potongan harga khusus.`
      })
    }
  }
  
  return recs
}

</script>
