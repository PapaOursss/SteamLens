/** Les vues du labo, seule liste : la page `/lab` les affiche, le menu s'en sert pour « Labo ». */
export interface LabSection {
  title: string
  to: string
  description: string
}

export interface LabGroup {
  title: string
  sections: LabSection[]
}

export const LAB_GROUPS: LabGroup[] = [
  {
    title: 'Les joueurs',
    sections: [
      { title: 'Course des jeux', to: '/player-race', description: "L'évolution des jeux les plus joués mois par mois depuis 2012." },
      { title: 'Durée de vie', to: '/playtime', description: 'Le temps de jeu médian par genre, et ce que coûte une heure de jeu.' },
      { title: 'Les jeux jamais finis', to: '/achievements', description: "Où les joueurs décrochent, d'après leurs succès." },
      { title: 'Matériel des joueurs', to: '/hardware', description: "L'enquête de Steam mois après mois : langues, systèmes, cartes graphiques." },
      { title: 'Steam Deck', to: '/steam-deck', description: 'Ce qui tourne sous Linux, genre par genre, selon ProtonDB.' },
      { title: 'Twitch', to: '/twitch', description: 'Les jeux les plus regardés, la langue des streams, et la course depuis 2016.' }
    ]
  },
  {
    title: 'Les prix',
    sections: [
      { title: 'Historique des prix', to: '/price-history', description: 'Chaque changement de prix, et les soldes qui reviennent chaque année.' },
      { title: "Pouvoir d'achat", to: '/purchasing-power', description: "Combien d'heures de travail coûte un jeu, pays par pays." },
      { title: 'Chercheur de pépites', to: '/gem-finder', description: 'Les jeux pas chers, très bien notés et encore méconnus.' },
      { title: 'Du prix à l’accueil', to: '/sankey-pricing', description: 'Les jeux chers sont-ils mieux notés ? Du genre au prix, puis au verdict des avis.' },
      { title: 'Ventes régionales', to: '/regional-sales', description: "Ce qui se vend en Amérique du Nord, en Europe, au Japon et ailleurs." }
    ]
  },
  {
    title: 'Les avis',
    sections: [
      { title: 'Avis et review bombings', to: '/reviews', description: "Le ratio d'avis positifs par langue et par semaine, et ses chutes brutales." },
      { title: 'Les mots des avis', to: '/review-words', description: 'Les mots qui reviennent dans les avis positifs et négatifs.' }
    ]
  },
  {
    title: 'Le monde',
    sections: [
      { title: 'Pays des profils', to: '/profile-map', description: "Le pays affiché sur les profils publics d'auteurs d'avis." },
      { title: 'Genres par pays', to: '/genre-map', description: 'Le genre le plus surreprésenté de chaque pays.' },
      { title: "D'où viennent les studios", to: '/studios', description: 'Les jeux par pays du studio, et le genre que chaque pays fait plus que les autres.' },
      { title: 'Google Trends', to: '/trends', description: "L'intérêt pour un jeu ou un genre, pays par pays, date après date." }
    ]
  },
  {
    title: 'Le catalogue',
    sections: [
      { title: 'Réseau des tags', to: '/tag-network', description: 'Les familles de tags qui vont ensemble.' },
      { title: 'La carte des jeux', to: '/game-map', description: 'Tout le catalogue en nuage : les jeux aux tags proches tombent côte à côte.' },
      { title: 'Calendrier des sorties', to: '/releases', description: 'Les sorties par jour de la semaine, par mois, et jour après jour.' },
      { title: 'Steam Wrapped', to: '/wrapped', description: "L'année de Steam en quelques records." }
    ]
  },
  {
    title: 'À vous de jouer',
    sections: [
      { title: 'Plus ou moins', to: '/minigame', description: 'Deux jeux, un chiffre caché : à vous de deviner lequel gagne.' },
      { title: 'Comparateur', to: '/comparer', description: 'Deux à quatre jeux côte à côte : ADN, joueurs et prix.' }
    ]
  }
]

export const LAB_PATHS: string[] = LAB_GROUPS.flatMap((group) => group.sections.map((section) => section.to))
