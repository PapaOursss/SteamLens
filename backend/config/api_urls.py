from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from catalog.views import GameViewSet, genre_stats, tag_stats
from catalog.views.minigame import game_duel
from catalog.views.proton import proton_stats
from config.health import health
from geography.views import world_map
from ingestion.views import sources_overview
from players.views import top_played

router = DefaultRouter(trailing_slash=True)
router.register("games", GameViewSet, basename="game")

urlpatterns = [
    path("health/", health, name="health"),
    path("sources/", sources_overview, name="sources-overview"),
    path("minigame/duel/", game_duel, name="minigame-duel"),
    path("stats/proton/", proton_stats, name="stats-proton"),
    path("stats/genres/", genre_stats, name="stats-genres"),
    path("stats/tags/", tag_stats, name="stats-tags"),
    path("stats/top-played/", top_played, name="stats-top-played"),
    path("map/<slug:indicator>/", world_map, name="world-map"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    *router.urls,
]
