from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from catalog.views import GameViewSet, genre_stats, tag_stats
from config.health import health
from geography.views import world_map
from players.views import top_played

router = DefaultRouter(trailing_slash=True)
router.register("games", GameViewSet, basename="game")

urlpatterns = [
    path("health/", health, name="health"),
    path("stats/genres/", genre_stats, name="stats-genres"),
    path("stats/tags/", tag_stats, name="stats-tags"),
    path("stats/top-played/", top_played, name="stats-top-played"),
    path("map/<slug:indicator>/", world_map, name="world-map"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    *router.urls,
]
