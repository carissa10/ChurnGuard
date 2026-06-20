<template>
  <div>
    <header class="lg:hidden flex items-center justify-between px-6 py-4 dark-glass border-b border-slate-800 text-white fixed top-0 w-full z-40">
      <div class="flex items-center space-x-3">
        <TrendingUp class="w-8 h-8 text-primary-400 animate-pulse" />
        <span class="font-bold text-xl tracking-tight bg-gradient-to-r from-primary-400 to-sky-300 bg-clip-text text-transparent">ChurnGuard</span>
      </div>
      <button @click="$emit('toggle')" class="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors focus:outline-none">
        <Menu v-if="!isOpen" class="w-6 h-6" />
        <X v-else class="w-6 h-6" />
      </button>
    </header>

    <aside 
      :class="[
        'w-64 h-screen dark-glass border-r border-slate-800 text-white flex flex-col justify-between fixed lg:sticky top-0 z-30 transition-transform duration-300',
        isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      ]"
    >
      <div>
        <div class="flex items-center space-x-3 px-6 py-8 border-b border-slate-800">
          <TrendingUp class="w-8 h-8 text-primary-400 animate-pulse" />
          <div>
            <h1 class="font-bold text-xl tracking-tight bg-gradient-to-r from-primary-400 to-sky-300 bg-clip-text text-transparent">ChurnGuard</h1>
            <span class="text-xs text-slate-500 font-medium tracking-widest uppercase">and Analytics</span>
          </div>
        </div>

        <nav class="mt-8 px-4 space-y-2">
          <router-link 
            v-for="item in menuItems" 
            :key="item.path" 
            :to="item.path"
            @click="$emit('close')"
            class="flex items-center space-x-3 px-4 py-3.5 rounded-xl font-medium transition-all duration-200 group"
            :class="isActive(item.path) 
              ? 'bg-gradient-to-r from-primary-600 to-primary-500 text-white shadow-lg shadow-primary-500/20' 
              : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/50'"
          >
            <component 
              :is="item.icon" 
              class="w-5 h-5 transition-transform duration-200 group-hover:scale-110" 
              :class="isActive(item.path) ? 'text-white' : 'text-slate-500 group-hover:text-primary-400'"
            />
            <span>{{ item.name }}</span>
          </router-link>
        </nav>
      </div>

      <div class="p-6 border-t border-slate-800 bg-slate-950/40">
        <div class="flex items-center space-x-3">
          <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-primary-500 to-sky-400 flex items-center justify-center font-bold text-sm text-white shadow-inner">
            AD
          </div>
          <div>
            <p class="text-xs text-slate-400 font-semibold leading-tight">Admin Dashboard</p>
            <p class="text-[10px] text-slate-500 font-medium">churnguard@company.com</p>
          </div>
        </div>
      </div>
    </aside>
    
    <div 
      v-if="isOpen" 
      @click="$emit('close')" 
      class="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-20 transition-opacity"
    ></div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { 
  LayoutDashboard, 
  UserCheck, 
  FileSpreadsheet, 
  TrendingUp, 
  Menu, 
  X,
  MessageCircle,
  History 
} from '@lucide/vue'

defineProps({
  isOpen: Boolean
})

defineEmits(['toggle', 'close'])

const route = useRoute()

const menuItems = [
  { name: 'Dashboard Home', path: '/', icon: LayoutDashboard },
  { name: 'Single Prediction', path: '/single-prediction', icon: UserCheck },
  { name: 'Batch Analytics', path: '/batch-analytics', icon: FileSpreadsheet },
  { name: 'NLP Sentiment', path: '/nlp-sentiment', icon: MessageCircle },
  { name: 'History Analytics', path: '/history', icon: History }
]

const isActive = (path) => {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}
</script>