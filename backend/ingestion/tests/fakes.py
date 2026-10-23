import json
from pathlib import Path
from typing import Any

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(relative_path: str) -> Any:
    return json.loads((FIXTURES / relative_path).read_text(encoding="utf-8"))


class FakeFetcher:
    """Renvoie des réponses préparées et garde la trace des paramètres demandés."""

    def __init__(self, responses: list[Any]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, str]] = []

    def __call__(self, url: str, params: dict[str, str]) -> Any:
        self.calls.append(params)
        return self._responses.pop(0)


class FakeClock:
    """Horloge manuelle : `sleep` avance le temps au lieu d'attendre."""

    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds
