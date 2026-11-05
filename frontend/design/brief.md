# Brief de design : SteamLens

## Sources

Pas de dossier client : `docs/backlog/backlog.md` (cap du projet, releases), `README.md`,
`GEMINI.md`, l'API locale le 2026-11-05. Demande de l'équipe le 2026-11-05 : « refais entièrement
le front ». Tout ce qui suit la demande est une `hypothèse`, à confirmer au choix de la direction.

## Audience

1. Le jury de soutenance, sur grand écran projeté ou ordinateur (`hypothèse`, release v3 « Bonus
   pour la soutenance ») : en dix secondes, comprendre ce que montre le site et voir de vraies
   données.
2. Des joueurs curieux, sur téléphone ou ordinateur (`hypothèse`) : en dix secondes, trouver un
   jeu ou voir ce qui se joue maintenant.
3. L'équipe (7 personnes) : chaque nouvelle vue doit entrer sans inventer un nouveau style.

## Main action

Explorer un jeu ou une carte : chercher un jeu, ouvrir sa fiche. Ensuite, passer aux vues
transversales (genres, monde, tendances). `hypothèse`

## Character

- Joueur, pas puéril : le sujet est le jeu vidéo, pas un tableau de bord de banque.
- Exact, pas froid : chaque chiffre dit sa source et sa date, une donnée absente est dite absente.
- Généreux, pas bavard : beaucoup d'images de jeux et de données, peu de texte d'habillage.

Mots tirés du cap du backlog (« ce qui se joue, où, à quel prix et depuis quand »), `hypothèse`.

## Fixed and open

Fixe : Nuxt 4, Tailwind, ECharts (`GEMINI.md`) ; 300 lignes par fichier ; les routes existantes.
Ouvert : tout le reste, y compris le logo (aucun n'est fourni) et la navigation.

## Photos

Pas de photos : les jaquettes Steam (460 × 215) servies par l'API, nettes jusqu'à environ 900 px
de large. `header_image` est vide pour une partie du catalogue : prévoir le repli par `appid`,
puis une tuile sans image.

## References

- **Liked** : aucune donnée. À demander.
- **Sector** : pas de bibliothèque connue.
- **Neighbours** : SteamDB, SteamCharts, Steam Spy, IsThereAnyDeal : tous des tableaux denses sur
  fond sombre, Steam lui-même en bleu marine. Le défaut à quitter. L'ancien front en était une
  variante (barre latérale, tuiles à emoji, dégradé cyan).

## Motion level

1, sobre (`hypothèse`) : CSS seul, l'interaction vient des graphiques. Un projecteur de soutenance
n'a pas besoin de plus.

## To remember

Steam est un territoire vivant : on voit tout de suite ce qui s'y joue, où, et à quel prix.

## Open questions

- Laquelle des directions ? (l'équipe)
- Le jury est-il bien l'audience première ? (l'équipe)

## Direction retenue

« Le mur », choisie par l'équipe le 2026-11-05 parmi trois maquettes (mur, atlas, affiche). Fond
indigo, mur de jaquettes bord à bord, l'audace à un seul endroit : la mosaïque de l'accueil, où la
surface suit le nombre de joueurs. Tokens : `app/utils/tokens.ts`, seule source des couleurs.
Niveau de mouvement : 1.
