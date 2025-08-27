"""Маршруты API."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    UserViewSet,
)

# Роутер — только для наших моделей
router = DefaultRouter()
router.register(r"ingredients", IngredientViewSet, basename="ingredients")
router.register(r"recipes", RecipeViewSet, basename="recipes")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"users", UserViewSet, basename="users")

# Кастомные пути для UserViewSet
user_urlpatterns = [
    path("users/", UserViewSet.as_view({"get": "list"}), name="user-list"),
    path(
        "users/<int:id>/",
        UserViewSet.as_view({"get": "retrieve"}),
        name="user-detail",
    ),
    path(
        "users/subscriptions/",
        UserViewSet.as_view({"get": "subscriptions"}),
        name="user-subscriptions",
    ),
    path(
        "users/<int:id>/subscribe/",
        UserViewSet.as_view({"post": "subscribe", "delete": "unsubscribe"}),
        name="user-subscribe",
    ),
    path(
        "users/avatar/",
        UserViewSet.as_view(
            {"get": "avatar", "put": "avatar", "delete": "avatar"}
        ),
        name="user-avatar",
    ),
]

urlpatterns = [
    path("", include(router.urls)),
    path("api/", include(user_urlpatterns)),
    path("auth/", include("djoser.urls.authtoken")),
]
