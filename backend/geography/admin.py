from django.contrib import admin

from geography.models import Country


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("iso2", "iso3", "name_fr", "continent", "main_language")
    search_fields = ("name_fr", "iso2", "iso3")
