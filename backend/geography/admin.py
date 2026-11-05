from django.contrib import admin

from geography.models import Country, GoogleTrendsInterest, RegionalSales


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("iso2", "iso3", "name_fr", "continent", "main_language")
    search_fields = ("name_fr", "iso2", "iso3")


@admin.register(GoogleTrendsInterest)
class GoogleTrendsInterestAdmin(admin.ModelAdmin):
    list_display = ("game", "country", "date", "interest")
    list_filter = ("date",)
    search_fields = ("game__name", "country__iso3", "country__name_fr")


@admin.register(RegionalSales)
class RegionalSalesAdmin(admin.ModelAdmin):
    list_display = ("name", "platform", "genre", "year", "na_sales", "eu_sales", "jp_sales")
    search_fields = ("name", "genre", "publisher")

