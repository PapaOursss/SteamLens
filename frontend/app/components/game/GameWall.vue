<template>
  <div>
    <GameWallLayout class="hidden md:block" :games="games" :width="DESKTOP.width" :height="DESKTOP.height" />
    <GameWallLayout class="md:hidden" :games="games" :width="PHONE.width" :height="PHONE.height" />
  </div>
</template>

<script setup lang="ts">
import type { TopPlayedGame } from '~/types'

const DESKTOP = { width: 1440, height: 700 }
const PHONE = { width: 375, height: 640 }

defineProps<{ games: TopPlayedGame[] }>()
</script>
