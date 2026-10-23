# SteamLens - Règles du projet & Contexte agent

Application web de visualisation de données Steam (évolution des prix, popularité des jeux).

## Architecture globale

- **Backend** : Django (Python 3.12+), géré avec [`uv`](https://docs.astral.sh/uv/) dans le dossier `backend/`.
- **Frontend** : Nuxt 4 / Vue 3 + TypeScript + Tailwind CSS dans le dossier `frontend/`.
- **Outillage** : `kiln` (optionnel) ou commandes natives (`uv`, `npm`).

---

## Commandes utiles

### Backend (`backend/`)
Toujours utiliser `uv` pour exécuter les outils Python :
- Installer / synchroniser les dépendances :
  ```bash
  cd backend && uv sync
  ```
- Exécuter les migrations :
  ```bash
  cd backend && uv run python manage.py migrate
  ```
- Lancer le serveur de développement :
  ```bash
  cd backend && uv run python manage.py runserver
  ```
- Ajouter un paquet :
  ```bash
  cd backend && uv add <paquet>
  ```
- Lancer les tests / linters :
  ```bash
  cd backend && uv run pytest  # ou manage.py test
  ```

### Frontend (`frontend/`)
- Installer les dépendances :
  ```bash
  cd frontend && npm install
  ```
- Lancer le serveur de développement :
  ```bash
  cd frontend && npm run dev
  ```
- Build de production / vérification de type :
  ```bash
  cd frontend && npm run build
  ```
- Prévisualiser le build :
  ```bash
  cd frontend && npm run preview
  ```

### Avec `kiln` (si disponible sur le poste)
- `kiln install` : installe les dépendances et outils.
- `kiln dev` : lance backend et frontend simultanément.
- `kiln check` : tests, linters, typage.
- `kiln doctor` : diagnostique l'environnement.

---

## Règles et conventions de code

1. **Gestion d'environnement Python** :
   - Ne jamais invoquer `python` ou `pip` directement sans passer par `uv run`.
   - Respecter PEP 8 et utiliser les type hints autant que possible.
   - Ne pas committer le dossier `backend/.venv/` ni `backend/db.sqlite3`.

2. **Frontend** :
   - Nuxt 4 avec Vue 3 (Composition API / `<script setup lang="ts">`).
   - Préférer le typage strict TypeScript.
   - Ne pas committer `frontend/node_modules/` ni `frontend/.nuxt/`.

3. **Style et propreté** :
   - Conserver les conventions de code et les docstrings existantes.
   - Respecter les contraintes définies dans `charter.toml`.
