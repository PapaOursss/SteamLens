<template>
  <div class="flex min-h-screen flex-col">
    <a
      href="#contenu"
      class="button sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50"
    >
      Aller au contenu
    </a>
    <AppHeader />
    <main id="contenu" class="flex-1">
      <slot />
    </main>
    <AppFooter />
  </div>
</template>
