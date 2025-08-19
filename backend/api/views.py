"""
Вьюсеты API: рецепты, теги, ингредиенты, пользователи.
"""

from django.db.models import Count, F, OuterRef, Subquery, Sum
from django.http import HttpResponse

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response

# Импортируем всё из api.serializers — где теперь все сериализаторы
from .serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShortRecipeSerializer,
    TagSerializer,
    SubscriptionSerializer,
)
from recipes.filters import RecipeFilter
from .pagination import PageNumberPagination
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from recipes.permissions import IsAuthorOrAdminPermission
from users.models import User, Subscription


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    search_fields = ("^name",)


class RecipeViewSet(viewsets.ModelViewSet):
    """CRUD рецептов + избранное, корзина, скачивание."""

    queryset = Recipe.objects.select_related("author").prefetch_related(
        "tags", "recipe_ingredients__ingredient"
    )
    permission_classes = (IsAuthorOrAdminPermission,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        return self._add_to_relation(request, pk, Favorite)

    @favorite.mapping.delete
    def unfavorite(self, request, pk=None):
        return self._remove_from_relation(request, pk, Favorite)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        return self._add_to_relation(request, pk, ShoppingCart)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self._remove_from_relation(request, pk, ShoppingCart)

    def _add_to_relation(self, request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if model.objects.filter(user=user, recipe=recipe).exists():
            raise exceptions.ValidationError(
                f"Рецепт уже в {model._meta.verbose_name}."
            )
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(
            recipe, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _remove_from_relation(self, request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        deleted, _ = model.objects.filter(user=user, recipe=recipe).delete()
        if not deleted:
            raise exceptions.ValidationError(
                f"Рецепт не был в {model._meta.verbose_name}."
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок."""
        user = request.user
        ingredients = (
            RecipeIngredient.objects.filter(recipe__shopping_list__user=user)
            .values(
                name=F("ingredient__name"),
                unit=F("ingredient__measurement_unit"),
            )
            .annotate(amount=Sum("amount"))
            .order_by("name")
        )
        if not ingredients:
            return Response(
                {"detail": "Список покупок пуст."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        buy_list_text = "Список покупок — Foodgram:\n\n"
        buy_list_text += "\n".join(
            f"{item['name']} — {item['amount']} {item['unit']}"
            for item in ingredients
        )
        buy_list_text += "\n\nСпасибо за использование Foodgram!"
        response = HttpResponse(buy_list_text, content_type="text/plain")
        response["Content-Disposition"] = (
            'attachment; filename="shopping-list.txt"'
        )
        return response


class UserViewSet(viewsets.GenericViewSet):
    """Управление подписками."""

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = PageNumberPagination

    @action(
        detail=False, methods=["get"], serializer_class=SubscriptionSerializer
    )
    def subscriptions(self, request):
        user = request.user
        authors_ids = user.subscriptions.values_list("author_id", flat=True)
        queryset = (
            User.objects.filter(id__in=authors_ids)
            .annotate(
                recipes_count=Subquery(
                    Recipe.objects.filter(author=OuterRef("id")).aggregate(
                        count=Count("id")
                    )["count"]
                )
            )
            .prefetch_related("recipes")
        )
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True, methods=["post"], serializer_class=SubscriptionSerializer
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            raise exceptions.ValidationError("Нельзя подписаться на себя.")
        if Subscription.objects.filter(user=user, author=author).exists():
            raise exceptions.ValidationError("Вы уже подписаны.")
        Subscription.objects.create(user=user, author=author)
        serializer = self.get_serializer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        deleted, _ = Subscription.objects.filter(
            user=user, author=author
        ).delete()
        if not deleted:
            raise exceptions.ValidationError("Вы не были подписаны.")
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["patch"],
        permission_classes=[IsAuthenticated],
        parser_classes=[JSONParser, MultiPartParser],
    )
    def avatar(self, request):
        profile = request.user.profile
        avatar = request.data.get("avatar")
        if not avatar:
            return Response(
                {"avatar": "Это поле обязательно."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        profile.avatar = avatar
        profile.save()
        return Response(
            {"avatar": request.build_absolute_uri(profile.avatar.url)},
            status=status.HTTP_200_OK,
        )

    @avatar.mapping.delete
    def delete_avatar(self, request):
        profile = request.user.profile
        if profile.avatar:
            profile.avatar.delete()
            profile.avatar = None
            profile.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
