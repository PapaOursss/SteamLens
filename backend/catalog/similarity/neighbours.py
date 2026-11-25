from sklearn.neighbors import NearestNeighbors

from catalog.similarity.tag_matrix import TagMatrix

NEIGHBOUR_COUNT = 10
SCORE_DECIMALS = 3


def nearest_neighbours(
    matrix: TagMatrix, count: int = NEIGHBOUR_COUNT
) -> dict[int, list[tuple[int, float]]]:
    """Pour chaque jeu, ses `count` voisins (appid, similarité cosinus), du plus proche au moins."""
    games = len(matrix.appids)
    if games < 2:
        return {}
    model = NearestNeighbors(n_neighbors=min(count + 1, games), metric="cosine", algorithm="brute")
    model.fit(matrix.weights)
    distances, indices = model.kneighbors(matrix.weights)
    result: dict[int, list[tuple[int, float]]] = {}
    for row, appid in enumerate(matrix.appids):
        pairs = [
            (matrix.appids[index], round(1 - distance, SCORE_DECIMALS))
            for index, distance in zip(indices[row], distances[row], strict=True)
            if index != row
        ]
        result[appid] = pairs[:count]
    return result
