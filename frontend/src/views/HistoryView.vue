<template>
  <div class="p-6 text-white min-h-screen bg-slate-950/20">
    <div class="mb-6">
      <h1 class="text-2xl font-bold tracking-tight bg-gradient-to-r from-primary-400 to-sky-300 bg-clip-text text-transparent">
        History Analytics
      </h1>
      <p class="text-sm text-slate-400 mt-1">
        Rekam jejak real-time hasil prediksi dan analisis sentimen pelanggan oleh Tim Marketing.
      </p>
    </div>

    <div class="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-md shadow-xl">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-slate-800 bg-slate-950/40 text-xs font-semibold tracking-wider text-slate-400 uppercase">
              <th class="px-6 py-4">Tanggal & Waktu</th>
              <th class="px-6 py-4">Tipe Analisis</th>
              <th class="px-6 py-4">Konten / Ulasan</th>
              <th class="px-6 py-4">Hasil Sentimen</th>
              <th class="px-6 py-4">Status Tindakan</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800 text-sm text-slate-300">
            <tr v-if="historyData.length === 0">
              <td colspan="5" class="px-6 py-12 text-center text-slate-500 italic">
                Belum ada riwayat masuk. Silakan lakukan analisis ulasan terlebih dahulu di halaman NLP Sentiment.
              </td>
            </tr>
            
            <tr v-for="(item, index) in historyData" :key="index" class="hover:bg-slate-800/30 transition-colors">
              <td class="px-6 py-4 font-medium text-slate-400 whitespace-nowrap">{{ item.date }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-0.5 rounded text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  {{ item.type }}
                </span>
              </td>
              <td class="px-6 py-4 max-w-xs truncate font-serif italic text-slate-400">{{ item.content }}</td>
              <td class="px-6 py-4 font-bold whitespace-nowrap" :class="item.resultColor">{{ item.result }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border" :class="item.statusClass">
                  {{ item.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="px-6 py-4 border-t border-slate-800 bg-slate-950/20 flex items-center justify-between text-xs text-slate-500">
        <span>Total: {{ historyData.length }} riwayat analisis aktif</span>
        <span class="flex items-center text-emerald-500 font-medium">
          <span class="w-1.5 h-1.5 bg-emerald-500 rounded-full mr-1.5 animate-pulse"></span>
          Terhubung dengan NLP Page
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// Computed property ini membaca localStorage secara otomatis tiap kali komponen dirender
const historyData = computed(() => {
  const cached = localStorage.getItem('historyAnalyticsCache')
  if (cached) {
    try {
      return JSON.parse(cached)
    } catch (e) {
      return []
    }
  }
  // Jika masih baru dan kosong, return array kosong (bukan data bohong lagi)
  return []
})
</script>