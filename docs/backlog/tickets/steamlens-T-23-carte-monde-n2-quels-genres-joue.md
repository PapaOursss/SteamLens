# T-23 · Carte du monde n°2 : quels genres joue-t-on par pays ?
- **Type**: idea
- **Priority**: 🟡 normal
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Dorian · **Due**: —
- **Origin**: demande de l'équipe (carte des styles de jeu par pays)

Steam ne donne pas les joueurs par pays : on l'approche par **la langue des avis** (T-22) et
des streams Twitch (T-21), reportée sur les pays qui parlent cette langue.
- [ ] Table langue → pays (pondérée par la population, via REST Countries)
- [ ] Pour chaque pays : genre le plus surreprésenté par rapport à la moyenne mondiale
  (indice de spécificité, pas juste le plus joué, sinon c'est « Action » partout)
- [ ] Carte : couleur = genre dominant ; clic sur un pays = barres de ses 10 genres
- [ ] Encadré honnête « comment c'est calculé et pourquoi c'est approximatif »
