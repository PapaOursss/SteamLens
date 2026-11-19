from catalog.views.dashboard import dashboard_stats
from catalog.views.game_view_set import GameViewSet
from catalog.views.rating_comparison import rating_comparison
from catalog.views.stats import genre_stats, tag_stats

__all__ = ["GameViewSet", "dashboard_stats", "genre_stats", "rating_comparison", "tag_stats"]
