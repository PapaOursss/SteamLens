import math
from collections import defaultdict
from dataclasses import dataclass

from scipy.sparse import csr_matrix

from catalog.models import GameTag

# Moins de tags : le jeu ressemble à n'importe quel autre qui porte les mêmes.
MIN_TAGS_PER_GAME = 3
# Tags importés sans votes (Kaggle) : chacun compte comme un vote.
VOTE_WHEN_UNKNOWN = 1


@dataclass(frozen=True)
class TagMatrix:
    """Une ligne par jeu, une colonne par tag ; poids = log(1 + votes)."""

    appids: list[int]
    tag_ids: list[int]
    weights: csr_matrix

    def head(self, size: int) -> "TagMatrix":
        """Les `size` premières lignes seulement."""
        return TagMatrix(self.appids[:size], self.tag_ids, self.weights[:size])

    def main_tag(self, row: int) -> int:
        """Le tag le plus voté du jeu de la ligne `row`."""
        line = self.weights.getrow(row)
        return self.tag_ids[line.indices[line.data.argmax()]]


def _votes_by_game() -> dict[int, dict[int, int]]:
    votes: dict[int, dict[int, int]] = defaultdict(dict)
    for game_id, tag_id, count in GameTag.objects.values_list("game_id", "tag_id", "votes"):
        votes[game_id][tag_id] = count
    return {game_id: tags for game_id, tags in votes.items() if len(tags) >= MIN_TAGS_PER_GAME}


def build_tag_matrix(appids: list[int] | None = None) -> TagMatrix:
    """Matrice des tags pondérés ; `appids` limite et ordonne les lignes."""
    votes = _votes_by_game()
    rows = [appid for appid in appids if appid in votes] if appids is not None else sorted(votes)
    tag_ids = sorted({tag_id for appid in rows for tag_id in votes[appid]})
    column = {tag_id: index for index, tag_id in enumerate(tag_ids)}
    data, row_indices, column_indices = [], [], []
    for row, appid in enumerate(rows):
        for tag_id, count in votes[appid].items():
            data.append(math.log1p(count or VOTE_WHEN_UNKNOWN))
            row_indices.append(row)
            column_indices.append(column[tag_id])
    weights = csr_matrix((data, (row_indices, column_indices)), shape=(len(rows), len(tag_ids)))
    return TagMatrix(appids=rows, tag_ids=tag_ids, weights=weights)
