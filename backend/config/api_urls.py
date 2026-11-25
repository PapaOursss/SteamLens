from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from catalog.views import GameViewSet, dashboard_stats, genre_stats, rating_comparison, tag_stats
from catalog.views.achievements import game_achievements, least_finished_games
from catalog.views.game_reviews import game_reviews, review_bombings
from catalog.views.gem_finder import gem_finder
from catalog.views.minigame import game_duel
from catalog.views.playtime import playtime_stats
from catalog.views.proton import proton_stats
from catalog.views.release_calendar_view import release_calendar_stats
from catalog.views.review_sentiment import review_sentiment
from catalog.views.review_words import review_words
from catalog.views.sankey_view import sankey_price_review_stats
from catalog.views.streamgraph import genre_streamgraph
from catalog.views.sunburst import sunburst_igdb
from catalog.views.tag_network import tag_network
from catalog.views.treemap import genre_tags_treemap
from catalog.views.wrapped import steam_wrapped
from config.health import health
from geography.views import world_map
from geography.views_profiles import profile_countries
from geography.views_sales import regional_sales_stats
from geography.views_trends import trends_map_stats
from ingestion.views import sources_overview
from players.views import top_played
from players.views_hardware import hardware_survey
from players.views_history import monthly_player_race
from players.views_hype import hype_stats
from pricing.views import game_deals, price_history, sales_calendar, top_deals

router = DefaultRouter(trailing_slash=True)
router.register("games", GameViewSet, basename="game")

urlpatterns = [
    path("health/", health, name="health"),
    path("sources/", sources_overview, name="sources-overview"),
    path("minigame/duel/", game_duel, name="minigame-duel"),
    path("stats/proton/", proton_stats, name="stats-proton"),
    path("stats/playtime/", playtime_stats, name="stats-playtime"),
    path("stats/hype/", hype_stats, name="stats-hype"),
    path("stats/wrapped/", steam_wrapped, name="stats-wrapped"),
    path("stats/regional-sales/", regional_sales_stats, name="stats-regional-sales"),
    path("stats/dashboard/", dashboard_stats, name="stats-dashboard"),
    path("stats/genres/", genre_stats, name="stats-genres"),
    path("stats/tags/", tag_stats, name="stats-tags"),
    path("stats/tag-network/", tag_network, name="stats-tag-network"),
    path("stats/treemap/", genre_tags_treemap, name="stats-treemap"),
    path("stats/streamgraph/", genre_streamgraph, name="stats-streamgraph"),
    path("stats/sankey-pricing/", sankey_price_review_stats, name="stats-sankey-pricing"),
    path("stats/sunburst-igdb/", sunburst_igdb, name="stats-sunburst-igdb"),
    path("stats/review-sentiment/", review_sentiment, name="stats-review-sentiment"),
    path("stats/rating-comparison/", rating_comparison, name="stats-rating-comparison"),
    path("stats/review-words/", review_words, name="stats-review-words"),
    path("stats/hardware-survey/", hardware_survey, name="stats-hardware-survey"),
    path("stats/price-history/<int:appid>/", price_history, name="stats-price-history"),
    path("stats/deals/<int:appid>/", game_deals, name="stats-game-deals"),
    path("stats/deals/", top_deals, name="stats-top-deals"),
    path("stats/sales-calendar/", sales_calendar, name="stats-sales-calendar"),
    path("stats/release-calendar/", release_calendar_stats, name="stats-release-calendar"),
    path("stats/top-played/", top_played, name="stats-top-played"),
    path("stats/monthly-player-race/", monthly_player_race, name="stats-monthly-player-race"),
    path("stats/reviews/<int:appid>/", game_reviews, name="stats-game-reviews"),
    path("stats/achievements/<int:appid>/", game_achievements, name="stats-game-achievements"),
    path("stats/least-finished/", least_finished_games, name="stats-least-finished"),
    path("stats/gem-finder/", gem_finder, name="stats-gem-finder"),
    path("stats/review-bombings/", review_bombings, name="stats-review-bombings"),
    path("stats/profile-countries/", profile_countries, name="stats-profile-countries"),
    path("stats/trends/", trends_map_stats, name="stats-trends"),
    path("map/<slug:indicator>/", world_map, name="world-map"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    *router.urls,
]
