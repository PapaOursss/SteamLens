from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.models import Game, ReviewExcerpt
from catalog.review_words import top_words
from catalog.stopwords import STOPWORDS_BY_LANGUAGE

DEFAULT_LANGUAGE = "english"
# Au-delà, le comptage à la volée ralentit la page sans changer le haut du classement.
MAX_EXCERPTS_PER_SIDE = 5000

WORDS_SIDE = inline_serializer(
    "ReviewWordsSide",
    {
        "reviews": serializers.IntegerField(),
        "words": inline_serializer(
            "ReviewWord",
            {"word": serializers.CharField(), "count": serializers.IntegerField()},
            many=True,
        ),
    },
)


def _side(excerpts: QuerySet[ReviewExcerpt], language: str, is_positive: bool) -> dict:
    texts = list(
        excerpts.filter(is_positive=is_positive)
        .order_by("id")
        .values_list("text", flat=True)[:MAX_EXCERPTS_PER_SIDE]
    )
    return {"reviews": len(texts), "words": top_words(texts, language)}


@extend_schema(
    parameters=[
        OpenApiParameter("language", str, description="english ou french"),
        OpenApiParameter("appid", int, description="un seul jeu (sinon tous les jeux suivis)"),
    ],
    responses=inline_serializer(
        "ReviewWords",
        {
            "language": serializers.CharField(),
            "appid": serializers.IntegerField(allow_null=True),
            "name": serializers.CharField(allow_null=True),
            "positive": WORDS_SIDE,
            "negative": WORDS_SIDE,
        },
    ),
)
@api_view(["GET"])
def review_words(request: Request) -> Response:
    """Mots les plus fréquents des avis 👍 et 👎, sans mots vides (T-40)."""
    language = request.query_params.get("language", DEFAULT_LANGUAGE)
    if language not in STOPWORDS_BY_LANGUAGE:
        return Response(
            {"detail": f"Langue inconnue, au choix : {', '.join(STOPWORDS_BY_LANGUAGE)}."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    excerpts = ReviewExcerpt.objects.filter(language=language)
    game = None
    appid = request.query_params.get("appid")
    if appid:
        game = get_object_or_404(Game, appid=appid)
        excerpts = excerpts.filter(game=game)
    return Response(
        {
            "language": language,
            "appid": game.appid if game else None,
            "name": game.name if game else None,
            "positive": _side(excerpts, language, is_positive=True),
            "negative": _side(excerpts, language, is_positive=False),
        }
    )
