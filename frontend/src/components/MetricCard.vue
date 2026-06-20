<template>
  <div class="bg-white rounded-2xl p-6 border border-slate-100 shadow-premium hover:shadow-premium-hover transition-all duration-300 flex items-center justify-between group">
    <div class="space-y-2">
      <span class="text-xs text-slate-500 font-semibold uppercase tracking-wider">{{ label }}</span>
      <h3 class="text-3xl font-extrabold text-slate-800 tracking-tight transition-transform duration-300 group-hover:translate-x-1">
        {{ value }}
      </h3>
      <p v-if="change !== undefined" class="text-xs flex items-center space-x-1 font-medium" :class="isPositive ? 'text-emerald-600' : 'text-rose-600'">
        <span>{{ isPositive ? '↑' : '↓' }}</span>
        <span>{{ Math.abs(change) }}% dibanding bulan lalu</span>
      </p>
    </div>
    
    <div :class="[
      'w-14 h-14 rounded-xl flex items-center justify-center transition-all duration-300 group-hover:scale-110 shadow-sm',
      colorClasses[color] || 'bg-slate-100 text-slate-600'
    ]">
      <component :is="icon" class="w-6 h-6" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: String,
  value: [String, Number],
  change: Number,
  icon: Object,
  color: {
    type: String,
    default: 'blue'
  }
})

const isPositive = computed(() => props.change >= 0)

const colorClasses = {
  blue: 'bg-primary-50 text-primary-600',
  emerald: 'bg-emerald-50 text-emerald-600',
  amber: 'bg-amber-50 text-amber-600',
  rose: 'bg-rose-50 text-rose-600',
  indigo: 'bg-indigo-50 text-indigo-600',
  violet: 'bg-violet-50 text-violet-600'
}
</script>
