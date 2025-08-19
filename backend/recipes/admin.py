"""
Админка: рецепты с ингредиентами и тегами.
"""

from django.contrib import admin
from django.db import models

from .models import Recipe


class RecipeIngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1
    min_num = 1
    validate_min = True


class RecipeTagInline(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1
    min_num = 1
    validate_min = True


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "text",
        "pub_date",
        "author",
        "favorites_count",
    )
    search_fields = ("name", "author__username", "author__email")
    list_filter = ("pub_date", "tags")
    date_hierarchy = "pub_date"
    inlines = (RecipeIngredientInline, RecipeTagInline)

    def favorites_count(self, obj):
        return obj.favorites.count()

    favorites_count.short_description = "В избранном"
    favorites_count.admin_order_field = "favorites_count"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(favorites_count=models.Count("favorites"))
