"""Вьюсеты API: рецепты, теги, ингредиенты, пользователи."""

from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from django.db.models import Count, F, Sum, Q
from django.http import HttpResponse
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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ("create", "partial_update", "update"):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def get_permissions(self):
        if self.action in ("retrieve", "list", "download_shopping_cart"):
            return (AllowAny(),)
        if self.action in ("create", "favorite", "shopping_cart"):
            return (IsAuthenticated(),)
        return (IsAuthorOrAdminPermission(),)

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
                is_favorited=Count(
                    "favorite", filter=Q(favorite__user=user), distinct=True
                ),
                is_in_shopping_cart=Count(
                    "shoppingcart",
                    filter=Q(shoppingcart__user=user),
                    distinct=True,
                ),
            )

        return queryset

    def _create_relation(self, request, recipe_id, model, serializer_class):
        """Создаёт связь (избранное / корзина) по ID рецепта."""
        data = {"user": request.user.id, "recipe": recipe_id}
        serializer = serializer_class(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _delete_relation(self, user, model, recipe_id):
        """Удаляет связь по ID. Возвращает 204 или 400, если связи не было."""
        deleted, _ = model.objects.filter(
            user=user, recipe_id=recipe_id
        ).delete()
        if not deleted:
            raise exceptions.ValidationError("Рецепт не найден в списке.")
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=["post"], permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        """Добавить рецепт в избранное."""
        return self._create_relation(request, pk, Favorite, FavoriteSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        """Удалить рецепт из избранного."""
        return self._delete_relation(request.user, Favorite, pk)

    @action(
        detail=True, methods=["post"], permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        """Добавить рецепт в список покупок."""
        return self._create_relation(
            request, pk, ShoppingCart, ShoppingCartSerializer
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        """Удалить рецепт из списка покупок."""
        return self._delete_relation(request.user, ShoppingCart, pk)

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
    Кастомный UserViewSet с функционалом подписок и аватара.
    Наследует регистрацию, /me/, авторизацию от Djoser.
    Добавлены: /subscriptions/, /subscribe/, /avatar/.
    """

    lookup_field = "id"

    def get_permissions(self):
        if self.action == "retrieve":
            return (IsAuthenticated(),)
        return super().get_permissions()

    def retrieve(self, request, *args, **kwargs):
        """Получение пользователя по ID."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        serializer_class=SubscriptionSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Список авторов, на которых подписан пользователь."""
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
        """Подписаться на автора."""
        serializer = SubscribeSerializer(
            data={"author": id}, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        """Отписаться от автора."""
        deleted, _ = Subscription.objects.filter(
            user=request.user, author_id=id
        ).delete()
        if not deleted:
            raise exceptions.ValidationError(
                "Вы не подписаны на этого пользователя."
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get", "put", "delete"],
        permission_classes=(IsAuthenticated,),
        parser_classes=[JSONParser, FormParser],
        url_path="me/avatar",
    )
    def avatar(self, request):
        """GET — получить, PUT — обновить, DELETE — удалить аватар."""
        profile, created = Profile.objects.get_or_create(user=request.user)

        if request.method == "GET":
            avatar_url = (
                request.build_absolute_uri(profile.avatar.url)
                if profile.avatar
                else None
            )
            return Response({"avatar": avatar_url}, status=status.HTTP_200_OK)

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
                profile.avatar.delete(save=False)
                profile.avatar = None
                profile.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=True,
        methods=["get"],
        permission_classes=(AllowAny,),
        url_path="avatar",
        url_name="get_user_avatar",
    )
    def get_user_avatar(self, request, id=None):
        """
        Получить аватар пользователя по ID.
        Доступно всем: авторизованным и анонимным.
        """
        user = get_object_or_404(User, id=id)
        profile = getattr(user, "profile", None)

        if profile and profile.avatar:
            avatar_url = request.build_absolute_uri(profile.avatar.url)
            return Response({"avatar": avatar_url}, status=status.HTTP_200_OK)
        else:
            return Response({"avatar": None}, status=status.HTTP_200_OK)
