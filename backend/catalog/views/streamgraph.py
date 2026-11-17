from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.genre_streamgraph import build_genre_streamgraph


@extend_schema(
    responses=inline_serializer(
        "GenreStreamgraphResponse",
        {
            "years": serializers.ListField(child=serializers.IntegerField()),
            "genres": serializers.ListField(child=serializers.CharField()),
            "series": serializers.ListField(
                child=serializers.ListField(child=serializers.IntegerField())
            ),
            "events": serializers.ListField(
                child=inline_serializer(
                    "StreamgraphEvent",
                    {
                        "year": serializers.IntegerField(),
                        "title": serializers.CharField(),
                        "description": serializers.CharField(),
                    },
                )
            ),
        },
    ),
)
@api_view(["GET"])
def genre_streamgraph(request: Request) -> Response:
    """Nombre de sorties de jeux par genre et par année avec événements clés."""
    data = build_genre_streamgraph()
    return Response(data)
