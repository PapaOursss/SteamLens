<template>
  <div>
    <PageIntro title="Le labo">
      Les vues qui sortent du cadre : des questions plus étroites, et un jeu.
    </PageIntro>

    <ul class="gutter">
      <li v-for="experiment in EXPERIMENTS" :key="experiment.to" class="border-t border-line">
        <NuxtLink :to="experiment.to" class="group grid gap-1 py-5 md:grid-cols-[minmax(0,2fr)_minmax(0,3fr)] md:items-baseline md:gap-8">
          <span class="font-display text-3xl font-extrabold tracking-tight group-hover:text-hot md:text-4xl">{{ experiment.title }}</span>
          <span class="max-w-prose leading-relaxed text-soft">{{ experiment.description }}</span>
        </NuxtLink>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
const EXPERIMENTS = [
  { title: 'Plus ou moins', to: '/minigame', description: 'Deux jeux, un chiffre caché : à vous de deviner lequel gagne.' },
  { title: 'Steam Wrapped', to: '/wrapped', description: "L'année de Steam en quelques records." },
  { title: 'Steam Deck', to: '/steam-deck', description: 'Ce qui tourne sous Linux, genre par genre, selon ProtonDB.' },
  { title: 'Durée de vie', to: '/playtime', description: "Le temps de jeu médian par genre, et ce que coûte une heure de jeu." },
  { title: 'Ventes régionales', to: '/regional-sales', description: "Ce qui se vend en Amérique du Nord, en Europe et au Japon." },
  { title: 'Historique des prix', to: '/price-history', description: 'Chaque changement de prix, et les soldes qui reviennent chaque année.' },
  { title: 'Avis et review bombings', to: '/reviews', description: "Le ratio d'avis positifs par langue et par semaine, et ses chutes brutales." },
  { title: 'Matériel des joueurs', to: '/hardware', description: "L'enquête de Steam mois après mois : langues, systèmes, cartes graphiques." },
  { title: 'Les jeux jamais finis', to: '/achievements', description: "Où les joueurs décrochent, d'après leurs succès." },
  { title: 'Pays des profils', to: '/profile-map', description: "Le pays affiché sur les profils publics d'auteurs d'avis." },
  { title: 'Google Trends', to: '/trends', description: "L'intérêt pour un jeu ou un genre, pays par pays, date après date." },
  { title: 'Course des jeux', to: '/player-race', description: "L'évolution des jeux les plus joués mois par mois depuis 2012." }
]

useHead({ title: 'Labo' })
</script>
