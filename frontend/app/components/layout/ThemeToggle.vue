<template>
  <button type="button" class="button-quiet" @click="toggle()">
    {{ theme === 'dark' ? 'Mode clair' : 'Mode sombre' }}
  </button>
</template>

<script setup lang="ts">
const { theme, toggle, restore } = useTheme()

onMounted(restore)
</script>
