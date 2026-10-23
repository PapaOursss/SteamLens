---
name: terminer
description: Finir une tâche, pousser la branche et ouvrir une pull request vers develop. À utiliser quand l'utilisateur dit qu'il a fini, veut pousser ou faire relire son travail.
---

1. Tout est commité (`git status` vide) ; sinon lancer la skill `commit`.
2. Vérifier les règles du projet (`GEMINI.md`) sur les fichiers modifiés :
   300 lignes au plus par fichier, 30 lignes au plus par fonction, une classe par fichier,
   pas de `print` / `console.log` oublié, pas de secret.
3. Récupérer `develop` : `git fetch origin && git merge origin/develop`. En cas de conflit,
   l'expliquer à l'utilisateur et le résoudre avec lui.
4. Pousser : `git push -u origin <branche>`.
5. Donner le lien pour ouvrir la pull request vers `develop` :
   `https://github.com/PapaOursss/SteamLens/compare/develop...<branche>?expand=1`.
   Rappeler qu'un autre membre de l'équipe doit relire avant la fusion.
