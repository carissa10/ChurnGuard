<template>
  <div class="flex min-h-screen bg-slate-50">
    <!-- Sidebar Navigation -->
    <Sidebar :isOpen="sidebarOpen" @toggle="toggleSidebar" @close="closeSidebar" />

    <!-- Main Layout Container -->
    <div class="flex-1 flex flex-col min-h-screen overflow-hidden">
      <!-- Main Content -->
      <main class="flex-1 overflow-y-auto px-6 py-8 lg:px-10 lg:py-12 mt-16 lg:mt-0">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Sidebar from './components/Sidebar.vue'

const sidebarOpen = ref(false)

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const closeSidebar = () => {
  sidebarOpen.value = false
}
</script>

<style>
/* Smooth Route Transition Animations */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}

/* Base Fade-in animation class */
.animate-fade-in {
  animation: fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
