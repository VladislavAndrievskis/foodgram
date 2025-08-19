"""
Фильтры для рецептов: по тегам, избранному, списку покупок.
"""

from django_filters import rest_framework as filters
from .models import Recipe


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method="filter_is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart"
    )
    author = filters.NumberFilter(field_name="author", lookup_expr="exact")
    tags = filters.AllValuesMultipleFilter(
        field_name="tags__slug",
        label="Теги (по slug)",
    )

    class Meta:
        model = Recipe
        fields = ("author", "tags", "is_favorited", "is_in_shopping_cart")

    def filter_is_favorited(self, queryset, name, value):
        if not self.request.user.is_authenticated:
            return Recipe.objects.none()
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset.exclude(favorites__user=self.request.user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if not self.request.user.is_authenticated:
            return Recipe.objects.none()
        if value:
            return queryset.filter(shopping_list__user=self.request.user)
        return queryset.exclude(shopping_list__user=self.request.user)
