# SteamLens - Directives & Instructions Projet

Projet d'analyse et de visualisation SteamLens.

## Structure du Projet

- `backend/` : API & logique métier en **Python >= 3.12** avec **Django**, géré avec **uv**.
- `frontend/` : Interface utilisateur en **Nuxt 4 / Vue 3** (TypeScript).

---

## Commandes Fréquentes

### Backend (`cd backend`)
- Installer / synchroniser les dépendances : `uv sync`
- Lancer le serveur Django : `uv run python manage.py runserver`
- Exécuter les migrations : `uv run python manage.py migrate`
- Lancer les tests : `uv run python manage.py test` (ou `uv run pytest`)

### Frontend (`cd frontend`)
- Lancer en développement : `npm run dev`
- Build pour production : `npm run build`
- Prévisualiser le build : `npm run preview`

---

## Directives & Conventions

- **Backend** :
  - Utiliser `uv` pour exécuter et gérer les dépendances Python.
  - Respecter PEP 8 et utiliser les type hints autant que possible.
- **Frontend** :
  - Nuxt 4 avec Vue 3 (Composition API / `<script setup lang="ts">`).
  - TypeScript strict.
- **Général** :
  - Ne pas commiter les dossiers générés (`node_modules`, `.nuxt`, `.venv`, etc.).
