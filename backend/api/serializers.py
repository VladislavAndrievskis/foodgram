"""Сериализаторы API: теги, ингредиенты, рецепты, пользователи."""

from django.core.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from django.core.validators import MinValueValidator
from rest_framework import serializers

from recipes.models import (
    Ingredient,
    Recipe,
    Tag,
    RecipeIngredients,
    Favorite,
    ShoppingCart,
)
from .constants import MIN_AMOUNT, MIN_COOKING_TIME
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
    """Сериализатор добавки ингредиентов при создании/обновлении рецепта."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        validators=[
            MinValueValidator(
                MIN_AMOUNT, f"Количество не может быть меньше {MIN_AMOUNT}."
            )
        ]
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
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()

    def get_avatar(self, obj):
        request = self.context["request"]
        if hasattr(obj, "profile") and obj.profile.avatar:
            return request.build_absolute_uri(obj.profile.avatar.url)
        return None


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""

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
        Profile.objects.get_or_create(user=user)
        return user


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Краткий сериализатор рецепта для подписок."""

    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")

    def get_image(self, obj):
        request = self.context["request"]
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецепта."""

    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientsSerializer(
        source="ingredients_in_recipe", many=True, read_only=True
    )
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True, default=False
    )

    class Meta:
        model = Recipe
        exclude = ("pub_date",)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["ingredients"] = data.get("ingredients", [])
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
                MIN_COOKING_TIME, f"Минимум {MIN_COOKING_TIME} минут."
            )
        ]
    )

    class Meta:
        model = Recipe
        exclude = ("pub_date",)

    def validate(self, data):
        tags = data.get("tags")
        ingredients = data.get("ingredients")

        if not tags:
            raise ValidationError("Добавьте хотя бы один тег.")
        if len(tags) != len(set(tags)):
            raise ValidationError("Теги не должны повторяться.")

        if not ingredients:
            raise ValidationError("Добавьте хотя бы один ингредиент.")
        ingredient_ids = [item["id"].id for item in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError("Ингредиенты не должны повторяться.")

        return data

    def validate_cooking_time(self, value):
        """Явная валидация cooking_time — лучше, чем в create."""
        if not isinstance(value, int) or value < MIN_COOKING_TIME:
            raise ValidationError(
                f"Время должно быть целым числом ≥ {MIN_COOKING_TIME}."
            )
        return value

    def _create_ingredients_and_tags(
        self, recipe, ingredients_data, tags_data
    ):
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
        recipe = Recipe.objects.create(author=author, **validated_data)
        self._create_ingredients_and_tags(recipe, ingredients_data, tags_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients", None)
        tags_data = validated_data.pop("tags", None)

        # Обновляем базовые поля
        instance = super().update(instance, validated_data)

        # Обновляем теги и ингредиенты — даже если None
        if tags_data is not None:
            instance.tags.set(tags_data)

        if ingredients_data is not None:
            instance.ingredients_in_recipe.all().delete()
            self._create_ingredients_and_tags(
                instance, ingredients_data, tags_data
            )

        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class UserRecipeRelationSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для избранного и списка покупок."""

    class Meta:
        model = None  # будет переопределено в наследниках
        fields = ("user", "recipe")

    def validate(self, data):
        model = self.Meta.model
        user = data["user"]
        recipe = data["recipe"]

        if model.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(
                f"Этот рецепт уже в {model._meta.verbose_name}."
            )
        return data


class FavoriteSerializer(UserRecipeRelationSerializer):
    """Сериализатор для избранного."""

    class Meta(UserRecipeRelationSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(UserRecipeRelationSerializer):
    """Сериализатор для списка покупок."""

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
        recipes = obj.recipes.all()

        # Обработка recipes_limit
        recipes_limit = request.query_params.get("recipes_limit")
        if recipes_limit:
            try:
                limit = int(recipes_limit)
                if limit < 0:
                    raise ValidationError(
                        "recipes_limit не может быть отрицательным."
                    )
                recipes = recipes[:limit]
            except (ValueError, TypeError):
                raise ValidationError(
                    "recipes_limit должен быть целым числом."
                )

        if recipes:
            return ShortRecipeSerializer(
                recipes, many=True, context={"request": request}
            ).data
        return []

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["recipes_count"] = instance.recipes.count()  # всегда актуально
        return data


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки."""

    class Meta:
        model = Subscription
        fields = ("author",)

    def validate_author(self, value):
        user = self.context["request"].user
        if user == value:
            raise ValidationError("Нельзя подписаться на себя.")
        if Subscription.objects.filter(user=user, author=value).exists():
            raise ValidationError("Вы уже подписаны на этого пользователя.")
        return value

    def create(self, validated_data):
        return Subscription.objects.create(
            user=self.context["request"].user, **validated_data
        )

    def to_representation(self, instance):
        return SubscriptionSerializer(
            instance.author, context={"request": self.context["request"]}
        ).data


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара пользователя."""

    avatar = Base64ImageField(
        required=True, help_text="Изображение в формате base64"
    )

    class Meta:
        model = Profile
        fields = ("avatar",)

    def update(self, instance, validated_data):
        if instance.avatar:
            instance.avatar.delete(save=False)
        instance.avatar = validated_data["avatar"]
        instance.save()
        return instance
