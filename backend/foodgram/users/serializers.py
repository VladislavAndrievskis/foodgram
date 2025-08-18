from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Recipe
from .models import Profile, Subscription

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name="get_is_subscribed"
    )
    avatar = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()

    def get_avatar(self, obj):
        request = self.context.get("request")
        if hasattr(obj, "profile") and obj.profile.avatar:
            return request.build_absolute_uri(obj.profile.avatar.url)
        return None

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
            "avatar",
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
        )


class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField(method_name="get_recipes")
    recipes_count = serializers.SerializerMethodField(
        method_name="get_recipes_count"
    )

    def get_srs(self):
        from recipes.serializers import ShortRecipeSerializer

        return ShortRecipeSerializer

    def get_recipes(self, obj):
        author_recipes = Recipe.objects.filter(author=obj)
        request = self.context.get("request")
        if "recipes_limit" in request.GET:
            recipes_limit = int(request.GET["recipes_limit"])
            author_recipes = author_recipes[:recipes_limit]
        if author_recipes:
            serializer = self.get_srs()(
                author_recipes,
                context={"request": request},
                many=True,
            )
            return serializer.data
        return []

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(
        required=True,
        help_text="Изображение в формате base64 (data:image/png;base64,...)",
    )

    class Meta:
        model = Profile
        fields = ('avatar',)

    def update(self, instance, validated_data):
        # Удаляем старый аватар если он есть
        if instance.avatar:
            instance.avatar.delete()

        instance.avatar = validated_data['avatar']
        instance.save()
        return instance
