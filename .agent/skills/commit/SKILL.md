---
name: commit
description: Enregistrer le travail en cours dans un commit git propre. À utiliser quand l'utilisateur veut commiter, sauvegarder ou enregistrer ses changements.
---

1. `git branch --show-current` : si c'est `develop` ou `main`, s'arrêter et lancer la skill
   `nouvelle-branche`.
2. `git status` et `git diff` : relire ce qui change. Ne jamais ajouter `.venv/`, `node_modules/`,
   `.nuxt/`, `db.sqlite3`, un fichier `.env` ou un secret.
3. Une idée par commit, 10 fichiers au plus : sinon découper en plusieurs commits.
4. Ajouter les fichiers un par un (`git add <fichier>`), pas `git add .` à l'aveugle.
5. Message : `type: ce que ça fait`, en français, 50 caractères au plus.
   Types : `feat`, `fix`, `docs`, `refactor`, `test`, `style`, `chore`.
   Exemple : `fix: recherche de jeu sans accents`.
6. `git commit -m "<message>"`.
