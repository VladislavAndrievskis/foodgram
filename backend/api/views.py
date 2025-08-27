"""Вьюсеты API: рецепты, теги, ингредиенты, пользователи."""

from djoser.views import UserViewSet as DjoserUserViewSet
from django.db.models import Count, F, Sum, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeSerializer,
    TagSerializer,
    SubscribeSerializer,
    SubscriptionSerializer,
    AvatarSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
)
from recipes.filters import RecipeFilter
from .pagination import PageNumberPagination
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)
from recipes.permissions import IsAuthorOrAdminPermission
from users.models import User, Subscription, Profile


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)
    permission_classes = (AllowAny,)


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

    def get_queryset(self):
        queryset = (
            Recipe.objects.select_related("author")
            .prefetch_related(
                "ingredients_in_recipe__ingredient",
                "tags",
            )
            .order_by("-pub_date")
        )

        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited_user=Count(
                    "favorite", filter=Q(favorite__user=user), distinct=True
                ),
                is_in_shopping_cart_user=Count(
                    "shoppingcart",
                    filter=Q(shoppingcart__user=user),
                    distinct=True,
                ),
            )

        return queryset

    def _create_relation(self, request, recipe, model, serializer_class):
        """Создаёт связь (избранное / корзина)."""
        serializer = serializer_class(
            data={"user": request.user.id, "recipe": recipe.id},
            context={"request": request},
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
        detail=True, methods=["post"], permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        """Добавить рецепт в избранное."""
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._create_relation(
            request, recipe, Favorite, FavoriteSerializer
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        """Удалить рецепт из избранного."""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._delete_relation(user, recipe, Favorite)

    @action(
        detail=True, methods=["post"], permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        """Добавить рецепт в список покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._create_relation(
            request, recipe, ShoppingCart, ShoppingCartSerializer
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        """Удалить рецепт из списка покупок."""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._delete_relation(user, recipe, ShoppingCart)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="download_shopping_cart",
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок в формате .txt."""
        recipe_ids = request.user.shoppingcart.values_list(
            "recipe_id", flat=True
        )

        if not recipe_ids:
            return HttpResponse(
                "Ваш список покупок пуст. Добавьте рецепты.",
                content_type="text/plain; charset=utf-8",
                status=400,
            )

        ingredients = (
            RecipeIngredients.objects.filter(recipe__in=recipe_ids)
            .values(
                name=F("ingredient__name"),
                measurement_unit=F("ingredient__measurement_unit"),
            )
            .annotate(amount=Sum("amount"))
            .order_by("name")
        )

        # Генерируем текст
        text = "Список покупок:\n\n"
        text += "\n".join(
            f"{item['name']} — {item['amount']} {item['measurement_unit']}"
            for item in ingredients
        )
        text += "\n\nСпасибо, что используете Foodgram"

        response = HttpResponse(text, content_type="text/plain; charset=utf-8")
        response["Content-Disposition"] = (
            'attachment; filename="shopping-list.txt"'
        )
        return response


class UserViewSet(DjoserUserViewSet):
    """
    Кастомизированный UserViewSet с функционалом подписок.
    Наследует всё от Djoser: регистрация, /me/, авторизация.
    Добавлены: /users/subscriptions/, /users/{id}/subscribe/.
    """

    @action(
        detail=False,
        methods=["get"],
        serializer_class=SubscriptionSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        user = request.user
        authors_ids = user.subscriptions.values_list("author_id", flat=True)
        queryset = User.objects.filter(id__in=authors_ids).annotate(
            recipes_count=Count("recipes")
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        serializer = SubscribeSerializer(
            data={"author": author.id}, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        """Отписаться от автора."""
        author = get_object_or_404(User, id=id)
        subscription = get_object_or_404(
            Subscription, user=request.user, author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get", "put", "delete"],  # ← добавили "get"
        permission_classes=[IsAuthenticated],
        parser_classes=[JSONParser, FormParser],
    )
    def avatar(self, request):
        user = request.user
        profile, created = Profile.objects.get_or_create(user=user)

        if request.method == "GET":
            if profile.avatar:
                avatar_url = request.build_absolute_uri(profile.avatar.url)
                return Response(
                    {"avatar": avatar_url}, status=status.HTTP_200_OK
                )
            return Response({"avatar": None}, status=status.HTTP_200_OK)

        elif request.method == "PUT":
            serializer = AvatarSerializer(
                profile, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            avatar_url = request.build_absolute_uri(profile.avatar.url)
            return Response({"avatar": avatar_url}, status=status.HTTP_200_OK)

        elif request.method == "DELETE":
            if profile.avatar:
                profile.avatar.delete(save=True)
                profile.avatar = None
                profile.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
