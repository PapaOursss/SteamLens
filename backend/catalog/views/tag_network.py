import math
from collections import defaultdict
from itertools import combinations
from typing import Any

import networkx as nx
from django.db.models import Count
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.models import GameTag, Tag

TOP_TAGS_LIMIT = 150
MIN_EDGE_WEIGHT = 2
EDGES_PER_TAG = 4
COMMUNITY_SEED = 1

Pair = tuple[int, int]


def _co_occurrences(tag_ids: set[int]) -> dict[Pair, int]:
    """Compte, pour chaque paire de tags, les jeux qui portent les deux."""
    game_to_tags: dict[int, list[int]] = defaultdict(list)
    for game_id, tag_id in GameTag.objects.filter(tag_id__in=tag_ids).values_list(
        "game_id", "tag_id"
    ):
        game_to_tags[game_id].append(tag_id)

    counts: dict[Pair, int] = defaultdict(int)
    for tags in game_to_tags.values():
        for pair in combinations(sorted(tags), 2):
            counts[pair] += 1
    return counts


def _association_strengths(
    co_occurrences: dict[Pair, int], tag_counts: dict[int, int]
) -> dict[Pair, float]:
    """Force d'un lien : jeux partagés rapportés à la taille des deux tags (cosinus).

    Sans cette division, les tags présents partout (Action, Singleplayer) captent tous
    les liens forts et les tags de niche restent isolés.
    """
    return {
        (first, second): count / math.sqrt(tag_counts[first] * tag_counts[second])
        for (first, second), count in co_occurrences.items()
        if count >= MIN_EDGE_WEIGHT
    }


def _strongest_pairs(strengths: dict[Pair, float]) -> set[Pair]:
    """Garde les EDGES_PER_TAG liens les plus forts de chaque tag."""
    pairs_by_tag: dict[int, list[Pair]] = defaultdict(list)
    for pair in strengths:
        pairs_by_tag[pair[0]].append(pair)
        pairs_by_tag[pair[1]].append(pair)
    kept: set[Pair] = set()
    for pairs in pairs_by_tag.values():
        pairs.sort(key=lambda pair: (-strengths[pair], pair))
        kept.update(pairs[:EDGES_PER_TAG])
    return kept


def _tag_communities(
    tag_ids: set[int], strengths: dict[Pair, float], pairs: set[Pair]
) -> dict[int, int]:
    """Familles de tags par modularité (Louvain), numérotées de la plus grande à la plus petite."""
    graph = nx.Graph()
    graph.add_nodes_from(tag_ids)
    graph.add_weighted_edges_from(
        (first, second, strengths[(first, second)]) for first, second in pairs
    )
    communities = nx.community.louvain_communities(graph, weight="weight", seed=COMMUNITY_SEED)
    communities.sort(key=lambda members: (-len(members), min(members)))
    return {tag_id: index for index, members in enumerate(communities) for tag_id in members}


def _build_tag_network_data() -> dict[str, Any]:
    top_tags = list(
        Tag.objects.annotate(games_count=Count("game_tags"))
        .filter(games_count__gt=0)
        .order_by("-games_count", "name")[:TOP_TAGS_LIMIT]
    )
    tag_counts = {tag.id: tag.games_count for tag in top_tags}
    co_occurrences = _co_occurrences(set(tag_counts))
    strengths = _association_strengths(co_occurrences, tag_counts)
    pairs = _strongest_pairs(strengths)
    communities = _tag_communities(set(tag_counts), strengths, pairs)

    nodes = [
        {"id": tag.id, "name": tag.name, "games": tag.games_count, "community": communities[tag.id]}
        for tag in top_tags
    ]
    edges = sorted(
        (
            {"source": first, "target": second, "weight": co_occurrences[(first, second)]}
            for first, second in pairs
        ),
        key=lambda edge: (-edge["weight"], edge["source"], edge["target"]),
    )
    return {"nodes": nodes, "edges": edges}


@extend_schema(
    responses=inline_serializer(
        "TagNetworkResponse",
        {
            "nodes": inline_serializer(
                "TagNode",
                {
                    "id": serializers.IntegerField(),
                    "name": serializers.CharField(),
                    "games": serializers.IntegerField(),
                    "community": serializers.IntegerField(),
                },
                many=True,
            ),
            "edges": inline_serializer(
                "TagEdge",
                {
                    "source": serializers.IntegerField(),
                    "target": serializers.IntegerField(),
                    "weight": serializers.IntegerField(),
                },
                many=True,
            ),
        },
    ),
)
@api_view(["GET"])
def tag_network(request: Request) -> Response:
    """Réseau de co-occurrence des tags principaux avec détection de communautés."""
    data = _build_tag_network_data()
    return Response(data)
