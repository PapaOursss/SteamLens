from django.db.models import Count, Sum
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.models import Genre, Tag

TOP_TAGS_LIMIT = 50


@extend_schema(
    responses=inline_serializer(
        "GenreStat",
        {"name": serializers.CharField(), "games": serializers.IntegerField()},
        many=True,
    ),
)
@api_view(["GET"])
def genre_stats(request: Request) -> Response:
    """Nombre de jeux par genre, du plus fourni au moins fourni."""
    genres = (
        Genre.objects.annotate(games_count=Count("games"))
        .filter(games_count__gt=0)
        .order_by("-games_count", "name")
    )
    return Response([{"name": genre.name, "games": genre.games_count} for genre in genres])


@extend_schema(
    responses=inline_serializer(
        "TagStat",
        {
            "name": serializers.CharField(),
            "games": serializers.IntegerField(),
            "votes": serializers.IntegerField(),
        },
        many=True,
    ),
)
@api_view(["GET"])
def tag_stats(request: Request) -> Response:
    """Les tags les plus posés, avec leurs votes cumulés (treemap, nuage de tags)."""
    tags = (
        Tag.objects.annotate(games_count=Count("game_tags"), votes=Sum("game_tags__votes"))
        .filter(games_count__gt=0)
        .order_by("-games_count", "name")[:TOP_TAGS_LIMIT]
    )
    return Response(
        [{"name": tag.name, "games": tag.games_count, "votes": tag.votes or 0} for tag in tags]
    )
