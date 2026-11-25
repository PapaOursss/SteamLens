import re
from collections import Counter
from collections.abc import Iterable

from catalog.stopwords import STOPWORDS_BY_LANGUAGE

# Suites de lettres (accents compris) ; l'apostrophe coupe : « l'histoire » donne « histoire ».
WORD_PATTERN = re.compile(r"[^\W\d_]+")
MIN_WORD_LENGTH = 3
DEFAULT_WORD_LIMIT = 60


def review_words(text: str, language: str) -> list[str]:
    """Les mots d'un avis, en minuscules, sans mots vides ni mots trop courts."""
    stopwords = STOPWORDS_BY_LANGUAGE.get(language, frozenset())
    return [
        word
        for word in WORD_PATTERN.findall(text.lower())
        if len(word) >= MIN_WORD_LENGTH and word not in stopwords
    ]


def top_words(
    texts: Iterable[str], language: str, limit: int = DEFAULT_WORD_LIMIT
) -> list[dict[str, str | int]]:
    """Les mots les plus fréquents, comptés une fois par avis (un avis qui répète un mot
    ne pèse pas plus lourd que les autres)."""
    counts: Counter[str] = Counter()
    for text in texts:
        counts.update(set(review_words(text, language)))
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
    return [{"word": word, "count": count} for word, count in ranked]
