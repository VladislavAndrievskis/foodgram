from django.contrib import admin
from django.db import models

from .models import Recipe, Tag, Ingredient, ShoppingCart, Favorite


class RecipeIngredientInline(admin.TabularInline):
    """Инлайн для ингредиентов в рецепте."""

    model = Recipe.ingredients.through
    extra = 1
    min_num = 1
    validate_min = True


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "pub_date",
        "author",
        "favorites_count_display",
    )
    list_display_links = ("id", "name")
    search_fields = ("name", "author__username", "author__email")
    list_filter = ("pub_date", "author", "tags")
    date_hierarchy = "pub_date"
    inlines = (RecipeIngredientInline,)
    readonly_fields = ("favorites_count_display",)

    @admin.display(description="В избранном", ordering="favorites_count")
    def favorites_count_display(self, obj):
        return obj.favorites_count

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(favorites_count=models.Count("favorite", distinct=True))
        )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ-панель для тегов."""

    list_display = ("id", "name", "slug")
    list_display_links = ("id", "name")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ-панель для управления ингредиентами."""

    list_display = ("id", "name", "measurement_unit")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    list_filter = ("name", "measurement_unit")
    ordering = ("name",)
    save_on_top = True
    verbose_name = "Ингредиент"
    verbose_name_plural = "Ингредиенты"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe", "created")
    list_select_related = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")
    list_filter = ("user", "recipe")
    date_hierarchy = "created"
    ordering = ("-created",)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe", "created")
    list_select_related = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")
    list_filter = ("user", "recipe")
    date_hierarchy = "created"
    ordering = ("-created",)
