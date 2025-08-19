"""
Вьюсеты API: рецепты, теги, ингредиенты, пользователи.
"""

from django.db.models import Count, F, OuterRef, Subquery, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeSerializer,
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
    RecipeIngredients,  # Добавлен: используется в download_shopping_cart
    ShoppingCart,
    Tag,
)
from recipes.permissions import IsAuthorOrAdminPermission
from users.models import User, Subscription


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления рецептами: создание, редактирование, фильтр."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    @staticmethod
    def _create_relation(user, recipe, model, serializer_class):
        """Создаёт связь (избранное / корзина), используя сериализатор."""
        serializer = serializer_class(
            data={"user": user.id, "recipe": recipe.id},
            context={"request": user},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def _delete_relation(user, recipe, model):
        """Удаляет связь. Возвращает 204 или 400, если связи не было."""
        deleted, _ = model.objects.filter(user=user, recipe=recipe).delete()
        if not deleted:
            raise exceptions.ValidationError("Рецепт не найден в списке.")
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=("post",), permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        """Добавить рецепт в избранное."""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._create_relation(
            user, recipe, Favorite, ShortRecipeSerializer
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        """Удалить рецепт из избранного."""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._delete_relation(user, recipe, Favorite)

    @action(
        detail=True, methods=("post",), permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        """Добавить рецепт в список покупок."""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._create_relation(
            user, recipe, ShoppingCart, ShortRecipeSerializer
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        """Удалить рецепт из списка покупок."""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._delete_relation(user, recipe, ShoppingCart)

    @action(
        detail=False, methods=("get",), permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок в формате .txt."""
        ingredients = (
            RecipeIngredients.objects.filter(
                recipe__shopping_cart__user=request.user
            )
            .values(
                name=F("ingredient__name"),
                measurement_unit=F("ingredient__measurement_unit"),
            )
            .annotate(amount=Sum("amount"))
            .order_by("name")
        )

        buy_list_text = "Список покупок с сайта Foodgram:\n\n"
        buy_list_text += "\n".join(
            f"{item['name']}, {item['amount']} {item['measurement_unit']}"
            for item in ingredients
        )

        response = HttpResponse(buy_list_text, content_type="text/plain")
        response["Content-Disposition"] = (
            'attachment; filename="shopping-list.txt"'
        )
        return response


class UserViewSet(viewsets.GenericViewSet):
    """Управление подписками и аватаром."""

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = PageNumberPagination

    @action(
        detail=False, methods=["get"], serializer_class=SubscriptionSerializer
    )
    def subscriptions(self, request):
        """Список авторов, на которых подписан пользователь."""
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
        """Подписаться на автора."""
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
        """Отписаться от автора."""
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
        """Загрузить аватар."""
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
        """Удалить аватар."""
        profile = request.user.profile
        if profile.avatar:
            profile.avatar.delete(save=True)
            profile.avatar = None
            profile.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
