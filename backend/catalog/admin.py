from django.contrib import admin

from catalog.models import (
    Company,
    Game,
    GameMode,
    Genre,
    Platform,
    ReviewSummary,
    Tag,
    Theme,
)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("appid", "name", "release_date", "is_free")
    search_fields = ("name", "appid")
    list_filter = ("is_free", "genres")


@admin.register(ReviewSummary)
class ReviewSummaryAdmin(admin.ModelAdmin):
    list_display = ("game", "language", "positive", "negative", "date")
    list_filter = ("language",)


admin.site.register((Company, GameMode, Genre, Platform, Tag, Theme))
