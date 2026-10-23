# SteamLens — règles du projet

Application web de visualisation de données Steam (prix, popularité des jeux).
On est 7 sur le projet : les règles sont courtes exprès. Dans le doute, demander à l'équipe.

## Carte du repo

- `backend/` : Django, géré par `uv` (`config/` = réglages, une app Django par domaine).
- `frontend/` : Nuxt 4 / Vue 3 + TypeScript + Tailwind. Le code est dans `frontend/app/` :
  `pages/` (une page = une route), `components/` (morceaux d'écran), `composables/`
  (logique réutilisable `useXxx`), `layouts/`, `middleware/`, `plugins/`, `types/`, `utils/`,
  `assets/`.
- `compose.yml` : lance toute la pile dans podman (voir `docs/podman.md`).
- `docs/` : documentation et backlog.

## Lancer le projet

- Avec podman (le plus simple) : `podman compose up --build` → http://localhost:3000.
- Sans conteneur : `cd backend && uv sync && uv run python manage.py runserver`,
  puis `cd frontend && npm install && npm run dev` (`npm run build` puis `npm run preview`
  pour tester le build).
- Python passe toujours par `uv` (`uv run`, `uv add`), jamais `pip`. Les conteneurs passent
  par `podman`, jamais `docker`.
- `backend/requirements.txt` est généré, ne pas l'éditer : après un `uv add`, le régénérer avec
  `uv export --no-hashes --no-dev --no-emit-project -o requirements.txt`.

## Git

- On ne commite **jamais** directement sur `main` ni `develop`.
- Pas de worktree dans ce projet : une branche normale suffit.
  ```bash
  git switch develop && git pull
  git switch -c feat/graphique-prix
  ```
- Nom de branche : `feat/`, `fix/`, `docs/`, `refactor/`, `test/` ou `chore/`, puis quelques
  mots en minuscules séparés par des tirets (`fix/recherche-jeu`).
- Commits petits : une idée par commit, 10 fichiers au plus.
- Message : `type: ce que ça fait`, 50 caractères au plus, en français.
  Types : `feat`, `fix`, `docs`, `refactor`, `test`, `style`, `chore`.
  Exemple : `feat: courbe des prix sur la fiche jeu`.
- Fini ? Pousser la branche et ouvrir une pull request vers `develop`.
  Un autre membre relit avant la fusion.

## Code

- **300 lignes au plus par fichier.** Trop gros ? Découper (un composant Vue devient un
  dossier avec des sous-composants, un module Python devient un paquet).
- **30 lignes au plus par fonction**, une seule responsabilité.
- **Une classe par fichier** (Python) ; un composant par fichier (Vue).
- Noms clairs, pas d'abréviations : `price_history`, pas `ph`.
  - Python : `snake_case` pour fonctions et variables, `PascalCase` pour les classes.
  - Vue : composants en `PascalCase` (`GameCard.vue`), composables en `useXxx`.
  - Constantes en `UPPER_SNAKE_CASE`, pas de nombre magique dans le code.
- Python : PEP 8 et type hints autant que possible.
- Vue : Composition API, `<script setup lang="ts">`, TypeScript strict, pas de `any`.
- Pas de code commenté laissé dans un commit, pas de `print` / `console.log` oubliés.
- Jamais de secret (clé d'API Steam, mot de passe) dans le code : variables d'environnement.
- Ne pas commiter `.venv/`, `node_modules/`, `.nuxt/`, `db.sqlite3`.

## Skills

Les skills de l'équipe sont dans `.agent/skills/` : `nouvelle-branche`, `commit`, `terminer`,
`lancer`. Elles se mettent à jour avec `git pull` ; on ne les modifie que par une pull request.
