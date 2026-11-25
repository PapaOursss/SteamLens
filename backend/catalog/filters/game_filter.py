import django_filters
from django.db.models import QuerySet

from catalog.models import Game, GameTag


class GameFilter(django_filters.FilterSet):
    """Filtres de `/api/games/` : `?search=&genre=&tag=&order=`.

    Genre et tag passent par une sous-requête : une jointure ferait des doublons, et le
    `DISTINCT` qui les retire coûtait plusieurs secondes sur tout le catalogue.
    """

    search = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    genre = django_filters.CharFilter(method="filter_genre")
    tag = django_filters.CharFilter(method="filter_tag")
    order = django_filters.OrderingFilter(fields=("name", "release_date", "appid", "owners_mid"))

    class Meta:
        model = Game
        fields = ("search", "genre", "tag", "is_free")

    def filter_genre(self, games: QuerySet[Game], name: str, value: str) -> QuerySet[Game]:
        with_genre = Game.genres.through.objects.filter(genre__name__iexact=value)
        return games.filter(appid__in=with_genre.values("game_id"))

    def filter_tag(self, games: QuerySet[Game], name: str, value: str) -> QuerySet[Game]:
        with_tag = GameTag.objects.filter(tag__name__iexact=value)
        return games.filter(appid__in=with_tag.values("game_id"))
