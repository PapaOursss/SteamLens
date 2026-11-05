from typing import Any


class FakeFetcher:
    """Remplace un `JsonFetcher` : renvoie des réponses préparées (ou lève les exceptions
    données) et note les paramètres demandés."""

    def __init__(self, responses: list[Any]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, str]] = []

    def __call__(self, url: str, params: dict[str, str]) -> Any:
        self.calls.append(params)
        response = self._responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response
