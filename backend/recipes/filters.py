from django_filters import rest_framework as filters
from .models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.ChoiceFilter(
        choices=(("0", "False"), ("1", "True")), method="filter_is_favorited"
    )
    is_in_shopping_cart = filters.ChoiceFilter(
        choices=(("0", "False"), ("1", "True")),
        method="filter_is_in_shopping_cart",
    )
    author = filters.NumberFilter(field_name="author", lookup_expr="exact")
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ("author", "tags")

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset.none()
        if value == "1":
            return queryset.filter(favorite__user=self.request.user)
        return queryset.exclude(favorite__user=self.request.user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset.none()
        if value == "1":
            return queryset.filter(shoppingcart__user=self.request.user)
        return queryset.exclude(shoppingcart__user=self.request.user)
