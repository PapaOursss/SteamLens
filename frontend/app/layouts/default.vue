<template>
  <div class="min-h-screen bg-slate-950 text-slate-100 flex flex-col md:flex-row font-sans">
    <!-- Mobile top bar -->
    <header class="md:hidden flex items-center justify-between px-4 py-3 bg-slate-900 border-b border-slate-800 sticky top-0 z-40">
      <NuxtLink to="/" class="flex items-center gap-2">
        <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 text-white font-bold text-sm shadow">
          SL
        </div>
        <span class="font-bold text-base tracking-wide text-white">SteamLens</span>
      </NuxtLink>

      <button
        type="button"
        class="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors focus:outline-hidden"
        aria-label="Ouvrir le menu"
        @click="isMobileMenuOpen = !isMobileMenuOpen"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            v-if="!isMobileMenuOpen"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 6h16M4 12h16M4 18h16"
          />
          <path
            v-else
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </header>

    <!-- Mobile Drawer Overlay -->
    <div
      v-if="isMobileMenuOpen"
      class="fixed inset-0 bg-black/60 z-40 md:hidden backdrop-blur-xs"
      @click="isMobileMenuOpen = false"
    />

    <!-- Sidebar : Desktop sticky + Mobile drawer -->
    <div
      :class="[
        'fixed md:sticky top-0 bottom-0 left-0 z-50 h-screen transition-transform duration-200 ease-in-out md:translate-x-0',
        isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
      ]"
    >
      <AppSidebar class="h-full" @navigate="isMobileMenuOpen = false" />
    </div>

    <!-- Main Content Area -->
    <main class="flex-1 min-w-0 flex flex-col min-h-screen bg-[#0d1322]">
      <div class="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const isMobileMenuOpen = ref(false)
</script>
