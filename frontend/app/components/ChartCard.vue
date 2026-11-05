<template>
  <div class="flex flex-col bg-slate-900/80 border border-slate-800 rounded-xl shadow-md p-5 backdrop-blur-sm">
    <header class="flex flex-wrap items-start justify-between gap-3 mb-4">
      <div>
        <h3 class="text-base font-semibold text-slate-100 tracking-tight">
          {{ title }}
        </h3>
        <p v-if="subtitle" class="text-xs text-slate-400 mt-0.5">
          {{ subtitle }}
        </p>
      </div>

      <div class="flex items-center gap-2">
        <slot name="actions" />
        <span
          v-if="source"
          class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-slate-800 text-slate-300 border border-slate-700"
          :title="`Données issues de : ${source}`"
        >
          {{ source }}
        </span>
      </div>
    </header>

    <div
      class="relative w-full flex-1 flex flex-col items-center justify-center"
      :style="{ minHeight: height }"
    >
      <div
        v-if="loading"
        class="absolute inset-0 flex flex-col items-center justify-center bg-slate-900/50 rounded-lg backdrop-blur-xs"
      >
        <slot name="loading">
          <div class="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
          <span class="mt-3 text-xs text-slate-400">Chargement des données...</span>
        </slot>
      </div>

      <div
        v-else-if="empty"
        class="absolute inset-0 flex flex-col items-center justify-center text-center p-6 text-slate-400"
      >
        <slot name="empty">
          <svg
            class="w-10 h-10 text-slate-600 mb-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
            />
          </svg>
          <p class="text-xs">{{ emptyMessage }}</p>
        </slot>
      </div>

      <div v-else class="w-full h-full flex-1">
        <slot />
      </div>
    </div>

    <footer
      v-if="source || $slots.footer"
      class="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500"
    >
      <span v-if="source">Source : {{ source }}</span>
      <div v-if="$slots.footer" class="ml-auto">
        <slot name="footer" />
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string
    subtitle?: string
    source?: string
    loading?: boolean
    empty?: boolean
    emptyMessage?: string
    height?: string
  }>(),
  {
    subtitle: undefined,
    source: undefined,
    loading: false,
    empty: false,
    emptyMessage: 'Aucune donnée disponible pour cet affichage.',
    height: '320px'
  }
)
</script>
