<template>
  <div class="wrapped-container">
    <header class="wrapped-header">
      <span class="wrapped-tag">SteamLens Rewind</span>
      <h1 class="title">Steam Wrapped {{ year }}</h1>
      <p class="subtitle">L'année du jeu vidéo résumée en cartes interactives.</p>
    </header>

    <div class="cards-carousel">
      <article class="card card-hero">
        <div class="card-badge">Jeu de l'année</div>
        <img :src="wrappedData.game_of_the_year.header_image" :alt="wrappedData.game_of_the_year.name" class="cover-img" />
        <h2 class="card-title">{{ wrappedData.game_of_the_year.name }}</h2>
        <p class="card-stat">Pic historique : {{ wrappedData.game_of_the_year.peak_players.toLocaleString('fr-FR') }} joueurs</p>
      </article>

      <article class="card card-trend">
        <div class="card-badge badge-trend">Genre en essor</div>
        <h2 class="card-title">{{ wrappedData.trending_genre.name }}</h2>
        <div class="growth-box">+{{ wrappedData.trending_genre.growth_percent }}%</div>
        <p class="card-desc">Porté par le succès phénoménal de <strong>{{ wrappedData.trending_genre.flagship_game }}</strong>.</p>
      </article>

      <article class="card card-deal">
        <div class="card-badge badge-deal">Plus grosse promo</div>
        <h2 class="card-title">{{ wrappedData.biggest_discount.name }}</h2>
        <div class="discount-pill">-{{ wrappedData.biggest_discount.discount_percent }}%</div>
        <p class="card-desc">Tombé à seulement {{ wrappedData.biggest_discount.final_price_eur.toFixed(2) }} € lors des soldes.</p>
      </article>

      <article class="card card-flop">
        <div class="card-badge badge-flop">Le coup dur</div>
        <h2 class="card-title">{{ wrappedData.biggest_flop.name }}</h2>
        <p class="card-desc">{{ wrappedData.biggest_flop.reason }}</p>
      </article>

      <article class="card card-country">
        <div class="card-badge badge-country">Zone la plus chère</div>
        <h2 class="card-title">{{ wrappedData.most_expensive_country.country }}</h2>
        <div class="premium-stat">+{{ wrappedData.most_expensive_country.premium_percent }}%</div>
        <p class="card-desc">{{ wrappedData.most_expensive_country.reason }}</p>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const year = ref(2026)

const wrappedData = ref({
  game_of_the_year: {
    appid: 730,
    name: 'Counter-Strike 2',
    header_image: 'https://cdn.akamai.steamstatic.com/steam/apps/730/header.jpg',
    peak_players: 1420000
  },
  trending_genre: {
    name: 'Roguelike Deckbuilder',
    growth_percent: 145,
    flagship_game: 'Balatro'
  },
  biggest_discount: {
    name: 'The Witcher 3: Wild Hunt',
    discount_percent: 80,
    final_price_eur: 5.99
  },
  biggest_flop: {
    name: 'The Day Before',
    reason: 'Retiré des ventes 4 jours après son lancement suite à 85% d\'avis négatifs.'
  },
  most_expensive_country: {
    country: 'Suisse (CHF)',
    premium_percent: 18.5,
    reason: 'Prix de base systématiquement ajustés au-dessus de la zone Euro.'
  }
})
</script>

<style scoped>
.wrapped-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem;
  font-family: system-ui, -apple-system, sans-serif;
  color: #1f2937;
  text-align: center;
}
.wrapped-tag {
  text-transform: uppercase;
  font-weight: 800;
  letter-spacing: 0.1em;
  font-size: 0.8rem;
  background: #fdf2f8;
  color: #db2777;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
}
.title { font-size: 2.5rem; font-weight: 900; margin: 0.75rem 0 0.5rem 0; }
.subtitle { color: #6b7280; margin: 0 0 2.5rem 0; font-size: 1.1rem; }
.cards-carousel {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}
.card {
  border-radius: 1rem;
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  background: #fff;
}
.card-hero { background: linear-gradient(145deg, #1e293b, #0f172a); color: #fff; }
.card-hero .card-title { color: #fff; }
.card-hero .card-stat { color: #94a3b8; }
.cover-img { width: 100%; height: 130px; object-fit: cover; border-radius: 0.5rem; margin: 1rem 0; }
.card-badge {
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  background: #38bdf8;
  color: #0369a1;
  margin-bottom: 0.5rem;
}
.badge-trend { background: #dcfce7; color: #166534; }
.badge-deal { background: #fef08a; color: #854d0e; }
.badge-flop { background: #fee2e2; color: #991b1b; }
.badge-country { background: #ede9fe; color: #5b21b6; }
.card-title { font-size: 1.35rem; font-weight: 800; margin: 0.5rem 0; }
.growth-box { font-size: 2.2rem; font-weight: 900; color: #16a34a; margin: 0.5rem 0; }
.discount-pill { font-size: 2.2rem; font-weight: 900; color: #ea580c; margin: 0.5rem 0; }
.premium-stat { font-size: 2.2rem; font-weight: 900; color: #7c3aed; margin: 0.5rem 0; }
.card-desc { font-size: 0.9rem; color: #4b5563; line-height: 1.4; margin: 0; }
</style>
