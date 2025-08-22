"""
Сериализаторы API: теги, ингредиенты, рецепты, пользователи.
"""

from django.core.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from django.core.validators import MinValueValidator
from rest_framework import serializers

from recipes.models import (
    Ingredient,
    Recipe,
    Tag,
    RecipeIngredients,
    UserRecipeRelation,
    Favorite,
    ShoppingCart,
)
from users.models import User, Subscription, Profile


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов в рецепте."""

    id = serializers.PrimaryKeyRelatedField(
        source="ingredient", read_only=True
    )
    name = serializers.SlugRelatedField(
        source="ingredient", slug_field="name", read_only=True
    )
    measurement_unit = serializers.SlugRelatedField(
        source="ingredient", slug_field="measurement_unit", read_only=True
    )

    class Meta:
        model = RecipeIngredients
        fields = ("id", "name", "measurement_unit", "amount")


class CreateUpdateRecipeIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов при создании рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), write_only=True
    )
    amount = serializers.IntegerField(
        validators=[
            MinValueValidator(
                1, "Количество ингредиента должно быть 1 или более."
            )
        ],
        write_only=True,
    )

    class Meta:
        model = RecipeIngredients
        fields = ("id", "amount")


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

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

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if not user or user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()

    def get_avatar(self, obj):
        request = self.context.get("request")
        if hasattr(obj, "profile") and obj.profile.avatar:
            return request.build_absolute_uri(obj.profile.avatar.url)
        return None


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя."""

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
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Короткий сериализатор для избранного и корзины."""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = serializers.SerializerMethodField()
    ingredients = RecipeIngredientsSerializer(
        source="ingredients_in_recipe",
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ("pub_date",)

    def get_tags(self, obj):
        request = self.context.get("request")
        if request and request.method in ("PUT", "PATCH", "POST"):
            return obj.tags.values_list("id", flat=True)
        return TagSerializer(obj.tags.all(), many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        try:
            return request.user.favorite.filter(recipe=obj).exists()
        except Exception:
            return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        try:
            return request.user.shopping_cart.filter(recipe=obj).exists()
        except Exception:
            return False

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data.get("ingredients"):
            data["ingredients"] = []
        return data


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и редактирования рецепта."""

    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = CreateUpdateRecipeIngredientsSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=[
            MinValueValidator(
                1, message="Время приготовления должно быть не менее 1 минуты."
            )
        ]
    )

    class Meta:
        model = Recipe
        exclude = ("pub_date",)

    def validate_tags(self, value):
        if not value:
            raise ValidationError("Нужно добавить хотя бы один тег.")
        return value

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError("Нужно добавить хотя бы один ингредиент.")
        ingredient_ids = [item["id"].id for item in value]
        if len(set(ingredient_ids)) != len(ingredient_ids):
            raise ValidationError(
                "У рецепта не может быть два одинаковых ингредиента."
            )
        return value

    @staticmethod
    def _create_ingredients_and_tags(recipe, ingredients_data, tags_data):
        RecipeIngredients.objects.bulk_create(
            [
                RecipeIngredients(
                    recipe=recipe, ingredient=item["id"], amount=item["amount"]
                )
                for item in ingredients_data
            ]
        )
        recipe.tags.set(tags_data)

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        author = self.context["request"].user

        cooking_time = validated_data.get("cooking_time")
        if isinstance(cooking_time, str):
            try:
                validated_data["cooking_time"] = int(cooking_time)
            except (ValueError, TypeError):
                raise ValidationError({"cooking_time": "должно быть целым."})

        recipe = Recipe.objects.create(author=author, **validated_data)
        self._create_ingredients_and_tags(recipe, ingredients_data, tags_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients", None)
        tags_data = validated_data.pop("tags", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags_data is not None:
            instance.tags.set(tags_data)

        if ingredients_data is not None:
            instance.ingredients_in_recipe.all().delete()
            self._create_ingredients_and_tags(instance, ingredients_data, tags_data)

        return instance

    def to_representation(self, instance):
        return RecipeSerializer(
            instance, context={"request": self.context.get("request")}
        ).data


class UserRecipeRelationSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для связей пользователь-рецепт."""

    class Meta:
        model = UserRecipeRelation
        fields = ("user", "recipe")
        # abstract не нужно указывать здесь

    def validate(self, data):
        user = data["user"]
        recipe = data["recipe"]
        model = self.Meta.model

        if model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError("Уже добавлено.")
        return data


class FavoriteSerializer(UserRecipeRelationSerializer):
    """Сериализатор для избранного."""

    class Meta(UserRecipeRelationSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(UserRecipeRelationSerializer):
    """Сериализатор для корзины."""

    class Meta(UserRecipeRelationSerializer.Meta):
        model = ShoppingCart


class SubscriptionSerializer(UserSerializer):
    """Сериализатор для отображения подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)

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

    def get_recipes(self, obj):
        request = self.context["request"]
        author_recipes = obj.recipes.all()

        recipes_limit = None
        if "recipes_limit" in request.GET:
            try:
                recipes_limit = int(request.GET["recipes_limit"])
                if recipes_limit < 0:
                    raise ValidationError("recipes_limit не может быть отрицательным.")
            except (ValueError, TypeError):
                raise ValidationError("recipes_limit должен быть целым числом.")

        if recipes_limit is not None:
            author_recipes = author_recipes[:recipes_limit]

        if author_recipes.exists():
            serializer = ShortRecipeSerializer(
                author_recipes,
                context={"request": request},
                many=True,
            )
            return serializer.data
        return []

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["recipes_count"] = getattr(instance, "recipes_count", 0)
        return data


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара."""

    avatar = Base64ImageField(
        required=True,
        help_text="Изображение в формате base64 (data:image/png;base64,...)",
    )

    class Meta:
        model = Profile
        fields = ("avatar",)

    def update(self, instance, validated_data):
        if instance.avatar:
            instance.avatar.delete()
        instance.avatar = validated_data["avatar"]
        instance.save()
        return instance
