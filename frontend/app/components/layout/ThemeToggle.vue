<template>
  <button type="button" class="button-quiet" :aria-label="theme === 'dark' ? 'Clair : changer de thème' : 'Sombre : changer de thème'" @click="toggle()">
    {{ theme === 'dark' ? 'Clair' : 'Sombre' }}
  </button>
</template>

<script setup lang="ts">
const { theme, toggle, restore } = useTheme()

onMounted(restore)
</script>
