import json
from pathlib import Path

from ingestion.http.json_types import JsonValue

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> JsonValue:
    """Réponse d'API enregistrée dans `tests/fixtures/<name>.json`."""
    body: JsonValue = json.loads((FIXTURES_DIR / f"{name}.json").read_text(encoding="utf-8"))
    return body
