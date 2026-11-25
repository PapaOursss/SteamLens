import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
from sklearn.preprocessing import normalize

from catalog.similarity.tag_matrix import TagMatrix

# t-SNE travaille mieux sur quelques dizaines de dimensions que sur des centaines de tags.
REDUCED_DIMENSIONS = 50
PERPLEXITY = 30
RANDOM_SEED = 1
# En dessous, t-SNE n'a pas de sens : les jeux restent à l'origine.
MIN_PROJECTED_GAMES = 5


def project_to_plane(matrix: TagMatrix) -> np.ndarray:
    """Coordonnées 2D (une ligne par jeu) : les jeux aux tags proches tombent côte à côte."""
    games, tags = matrix.weights.shape
    if games < MIN_PROJECTED_GAMES or tags < 2:
        return np.zeros((games, 2))
    rows = normalize(matrix.weights)
    components = min(REDUCED_DIMENSIONS, tags - 1, games - 1)
    reduced = TruncatedSVD(n_components=components, random_state=RANDOM_SEED).fit_transform(rows)
    tsne = TSNE(
        n_components=2,
        perplexity=min(PERPLEXITY, games - 1),
        init="pca",
        random_state=RANDOM_SEED,
    )
    return tsne.fit_transform(reduced)
