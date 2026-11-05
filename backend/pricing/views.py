from collections import Counter

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.models import Game
from pricing.price_history import history_summary, promo_starts


@extend_schema(
    responses=inline_serializer(
        "PriceHistory",
        {
            "appid": serializers.IntegerField(),
            "name": serializers.CharField(),
            "currency": serializers.CharField(allow_null=True),
            "summary": serializers.DictField(),
            "changes": serializers.ListField(child=serializers.DictField()),
        },
    ),
)
@api_view(["GET"])
def price_history(request: Request, appid: int) -> Response:
    """Chaque changement de prix d'un jeu sur Steam et ce qu'on en tire (IsThereAnyDeal)."""
    game = get_object_or_404(Game, appid=appid)
    changes = list(game.price_changes.all())
    return Response(
        {
            "appid": game.appid,
            "name": game.name,
            "currency": changes[0].currency if changes else None,
            "summary": history_summary(changes),
            "changes": [
                {
                    "changed_at": change.changed_at,
                    "price": float(change.price),
                    "regular": float(change.regular),
                    "cut": change.cut,
                }
                for change in changes
            ],
        }
    )


@extend_schema(
    responses=inline_serializer(
        "SalesCalendar",
        {
            "years": serializers.ListField(child=serializers.IntegerField()),
            "cells": serializers.ListField(child=serializers.ListField()),
        },
    ),
)
@api_view(["GET"])
def sales_calendar(request: Request) -> Response:
    """Débuts de promo par année et semaine : les soldes d'été et d'hiver reviennent chaque année.

    `cells` : `[année, semaine ISO, nombre de jeux qui passent en promo]`.
    """
    starts = Counter()
    games = Game.objects.filter(price_changes__isnull=False).distinct()
    for game in games.prefetch_related("price_changes"):
        for start in promo_starts(list(game.price_changes.all())):
            year, week, _ = start.changed_at.isocalendar()
            starts[year, week] += 1
    return Response(
        {
            "years": sorted({year for year, _ in starts}),
            "cells": [[year, week, count] for (year, week), count in sorted(starts.items())],
        }
    )
