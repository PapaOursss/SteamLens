import django_filters

from catalog.models import Game


class GameFilter(django_filters.FilterSet):
    """Filtres de `/api/games/` : `?search=&genre=&tag=&order=`."""

    search = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    genre = django_filters.CharFilter(field_name="genres__name", lookup_expr="iexact")
    tag = django_filters.CharFilter(field_name="tags__name", lookup_expr="iexact")
    order = django_filters.OrderingFilter(fields=("name", "release_date", "appid"))

    class Meta:
        model = Game
        fields = ("search", "genre", "tag", "is_free")
