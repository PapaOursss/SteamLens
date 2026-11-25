<template>
  <div>
    <PageIntro title="Le labo">
      Les vues qui sortent du cadre : des questions plus étroites, rangées par thème, et deux jeux.
    </PageIntro>

    <nav aria-label="Thèmes du labo" class="gutter -mt-2 mb-4 flex flex-wrap gap-1">
      <a v-for="group in LAB_GROUPS" :key="group.title" :href="`#${anchor(group.title)}`" class="button-quiet">
        {{ group.title }}
      </a>
    </nav>

    <section v-for="group in LAB_GROUPS" :id="anchor(group.title)" :key="group.title" class="gutter scroll-mt-4 py-6">
      <h2 class="mb-2 text-3xl md:text-4xl">{{ group.title }}</h2>
      <ul class="grid gap-x-8 md:grid-cols-2">
        <li v-for="section in group.sections" :key="section.to" class="border-t border-line">
          <NuxtLink :to="section.to" class="group block py-4">
            <span class="block font-display text-2xl font-extrabold tracking-tight group-hover:text-hot">{{ section.title }}</span>
            <span class="mt-1 block max-w-prose leading-relaxed text-soft">{{ section.description }}</span>
          </NuxtLink>
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup lang="ts">
useHead({ title: 'Labo' })

/** « Les joueurs » devient « les-joueurs » : l'ancre de la section. */
function anchor(title: string): string {
  return title
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '')
}
</script>
