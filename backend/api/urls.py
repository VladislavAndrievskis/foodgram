from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    UserViewSet,
)

# Роутер — только для стандартных действий
router = DefaultRouter()
router.register(r"ingredients", IngredientViewSet, basename="ingredients")
router.register(r"recipes", RecipeViewSet, basename="recipes")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"users", UserViewSet, basename="users")

# Кастомные пути — только для специфичных действий
user_urlpatterns = [
    path(
        "subscriptions/",
        UserViewSet.as_view({"get": "subscriptions"}),
        name="user-subscriptions",
    ),
    path(
        "<int:id>/subscribe/",
        UserViewSet.as_view({"post": "subscribe", "delete": "unsubscribe"}),
        name="user-subscribe",
    ),
    path(
        "avatar/",
        UserViewSet.as_view(
            {"get": "avatar", "put": "avatar", "delete": "avatar"}
        ),
        name="user-avatar",
    ),
]

urlpatterns = [
    path("", include(router.urls)),
    path("", include(user_urlpatterns)),
    path("auth/", include("djoser.urls.authtoken")),
]
