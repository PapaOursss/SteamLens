# T-49 · Tests sans réseau : fixtures des réponses d'API
- **Type**: task
- **Priority**: 🟡 normal
- **Status**: blocked — waiting for the import commands (T-06 to T-11)
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Antoine · **Due**: —
- **Origin**: fiabilité des imports

- [x] Une réponse réelle par source sans clé enregistrée dans `backend/tests/fixtures/`
  (`load_fixture()`) ; les sources à clé suivront leurs clés (`urgent.md`)
- [ ] Un test par commande d'import (parsing, idempotence) avec `respx` ou `responses`
- [x] Un test par endpoint de T-12
