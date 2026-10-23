---
name: nouvelle-branche
description: Commencer une tâche sur une nouvelle branche git. À utiliser quand l'utilisateur veut commencer une fonctionnalité, une correction ou n'importe quel changement.
---

1. Vérifier que rien n'est en cours : `git status`. S'il reste des modifications, demander quoi en faire.
2. Se mettre à jour : `git switch develop && git pull`.
3. Choisir le nom avec l'utilisateur : `feat/`, `fix/`, `docs/`, `refactor/`, `test/` ou `chore/`
   puis quelques mots en minuscules avec des tirets (`feat/courbe-prix`).
4. Créer la branche : `git switch -c <nom>`.

Jamais de travail directement sur `develop` ou `main`. Pas de worktree dans ce projet.
