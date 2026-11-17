from collections import defaultdict
from typing import Any

from django.db.models import Count
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.models import GameTag, Tag

TOP_TAGS_LIMIT = 150
MIN_EDGE_WEIGHT = 2
MAX_EDGES = 600


def _compute_tag_communities(
    nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
) -> dict[int, int]:
    """Détecte les communautés de tags via la propagation de labels (LPA)."""
    node_ids = [node["id"] for node in nodes]
    if not node_ids:
        return {}

    labels: dict[int, int] = {nid: nid for nid in node_ids}
    adj: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for edge in edges:
        u, v, w = edge["source"], edge["target"], edge["weight"]
        adj[u].append((v, w))
        adj[v].append((u, w))

    for _ in range(10):
        changed = False
        for u in node_ids:
            if not adj[u]:
                continue
            weights: dict[int, int] = defaultdict(int)
            for v, w in adj[u]:
                weights[labels[v]] += w
            best_label = max(weights.keys(), key=lambda l: (weights[l], -l))
            if best_label != labels[u]:
                labels[u] = best_label
                changed = True
        if not changed:
            break

    unique_labels = sorted({labels[u] for u in node_ids})
    label_map = {lbl: idx for idx, lbl in enumerate(unique_labels)}
    return {u: label_map[labels[u]] for u in node_ids}


def _build_tag_network_data() -> dict[str, Any]:
    top_tags = list(
        Tag.objects.annotate(games_count=Count("game_tags"))
        .filter(games_count__gt=0)
        .order_by("-games_count", "name")[:TOP_TAGS_LIMIT]
    )
    if not top_tags:
        return {"nodes": [], "edges": []}

    tag_ids = {t.id for t in top_tags}
    tag_counts = {t.id: t.games_count for t in top_tags}
    tag_names = {t.id: t.name for t in top_tags}

    game_tags_qs = (
        GameTag.objects.filter(tag_id__in=tag_ids)
        .values_list("game_id", "tag_id")
        .order_by("game_id")
    )

    game_to_tags: dict[int, list[int]] = defaultdict(list)
    for game_id, tag_id in game_tags_qs:
        game_to_tags[game_id].append(tag_id)

    co_occurrences: dict[tuple[int, int], int] = defaultdict(int)
    for tags in game_to_tags.values():
        if len(tags) < 2:
            continue
        sorted_tags = sorted(tags)
        for i in range(len(sorted_tags)):
            t1 = sorted_tags[i]
            for j in range(i + 1, len(sorted_tags)):
                t2 = sorted_tags[j]
                co_occurrences[(t1, t2)] += 1

    sorted_edges = sorted(
        [
            {"source": t1, "target": t2, "weight": count}
            for (t1, t2), count in co_occurrences.items()
            if count >= MIN_EDGE_WEIGHT
        ],
        key=lambda e: e["weight"],
        reverse=True,
    )[:MAX_EDGES]

    raw_nodes = [
        {"id": tid, "name": tag_names[tid], "games": tag_counts[tid]}
        for tid in tag_ids
    ]
    raw_nodes.sort(key=lambda n: n["games"], reverse=True)

    community_map = _compute_tag_communities(raw_nodes, sorted_edges)
    for node in raw_nodes:
        node["community"] = community_map.get(node["id"], 0)

    return {"nodes": raw_nodes, "edges": sorted_edges}


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
