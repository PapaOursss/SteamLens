from collections.abc import Callable

import httpx

from ingestion.http import ApiError
from ingestion.http.api_client import DEFAULT_TIMEOUT_SECONDS, USER_AGENT
from ingestion.sources.steam_hwsurvey.survey_page import parse_survey
from ingestion.sources.steam_hwsurvey.survey_share import SurveyShare

SURVEY_URL = (
    "https://store.steampowered.com/hwsurvey/Steam-Hardware-Software-Survey-Welcome-to-Steam"
)
SOURCE = "steam_hwsurvey"

TextFetcher = Callable[[str, dict[str, str]], str]


def fetch_page(url: str, params: dict[str, str]) -> str:
    """Page HTML (pas de JSON ici, d'où un GET simple, un seul appel par mois)."""
    try:
        response = httpx.get(
            url, params=params, headers={"User-Agent": USER_AGENT},
            timeout=DEFAULT_TIMEOUT_SECONDS, follow_redirects=True,
        )  # fmt: skip
        response.raise_for_status()
    except httpx.HTTPError as error:
        raise ApiError(SOURCE, url, type(error).__name__) from error
    return response.text


class SurveyClient:
    """Lit l'enquête du mois en cours ; Steam n'en garde pas l'historique, on le construit."""

    def __init__(self, fetch_text: TextFetcher = fetch_page) -> None:
        self._fetch_text = fetch_text

    def current_survey(self) -> list[SurveyShare]:
        return parse_survey(self._fetch_text(SURVEY_URL, {"l": "english"}))
