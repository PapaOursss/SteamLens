from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

UNKNOWN_LANGUAGE = "other"


@dataclass(frozen=True)
class StreamTally:
    """Ce qu'on garde des streams d'une catégorie : des totaux, jamais qui stream."""

    viewers: int = 0
    streams: int = 0
    viewers_by_language: Counter[str] = field(default_factory=Counter)


def tally_streams(streams: Iterable[dict[str, Any]]) -> StreamTally:
    viewers = 0
    count = 0
    by_language: Counter[str] = Counter()
    for stream in streams:
        watching = int(stream.get("viewer_count") or 0)
        viewers += watching
        count += 1
        by_language[(stream.get("language") or UNKNOWN_LANGUAGE).lower()] += watching
    return StreamTally(viewers, count, by_language)
