from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

from ingestion.sources.json_fetcher import JsonFetcher, live_fetcher
from ingestion.sources.steam_reviews.recent_review import RecentReview
from ingestion.sources.steam_reviews.review_counts import ReviewCounts

API_URL = "https://store.steampowered.com/appreviews/{appid}"
FIRST_CURSOR = "*"
REVIEWS_PER_PAGE = 100
DEFAULT_MAX_PAGES = 5
SUCCESS = 1


class SteamReviewsClient:
    """Lit `appreviews` du Store (sans clé) : totaux par langue et avis récents paginés.

    Jamais de cache disque : les réponses contiennent le SteamID des auteurs, qu'on ne doit
    pas écrire, même temporairement (T-22, T-37).
    """

    def __init__(self, fetch_json: JsonFetcher | None = None) -> None:
        self._fetch_json = fetch_json or live_fetcher("steam_reviews")

    def counts(self, appid: int, language: str) -> ReviewCounts | None:
        """None quand Steam ne renvoie rien pour ce jeu."""
        payload = self._request(appid, language=language, num_per_page="0", filter="all")
        if payload is None:
            return None
        summary = payload.get("query_summary") or {}
        return ReviewCounts(
            appid=appid,
            language=language,
            positive=int(summary.get("total_positive", 0)),
            negative=int(summary.get("total_negative", 0)),
        )

    def recent_reviews(
        self, appid: int, max_pages: int = DEFAULT_MAX_PAGES
    ) -> Iterator[RecentReview]:
        """Avis du plus récent au plus ancien, toutes langues, page par page (`cursor`)."""
        cursor = FIRST_CURSOR
        for _ in range(max_pages):
            payload = self._request(
                appid, language="all", filter="recent", cursor=cursor,
                num_per_page=str(REVIEWS_PER_PAGE),
            )  # fmt: skip
            reviews = (payload or {}).get("reviews") or []
            yield from (_recent_review(review) for review in reviews)
            next_cursor = (payload or {}).get("cursor")
            if len(reviews) < REVIEWS_PER_PAGE or not next_cursor or next_cursor == cursor:
                return
            cursor = next_cursor

    def _request(self, appid: int, **params: str) -> dict[str, Any] | None:
        payload = self._fetch_json(
            API_URL.format(appid=appid), {"json": "1", "purchase_type": "all", **params}
        )
        if not isinstance(payload, dict) or payload.get("success") != SUCCESS:
            return None
        return payload


def _recent_review(review: dict[str, Any]) -> RecentReview:
    author = review.get("author") or {}
    return RecentReview(
        created_at=datetime.fromtimestamp(int(review["timestamp_created"]), UTC),
        voted_up=bool(review.get("voted_up")),
        author_steamid=str(author.get("steamid", "")),
    )
