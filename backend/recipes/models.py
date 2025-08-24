"""
Модели: теги, ингредиенты, рецепты, связи.
"""

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .constants import (
    NAME_MAX_LENGTH,
    MEASUREMENT_UNIT_MAX_LENGTH,
    SLUG_MAX_LENGTH,
)

User = get_user_model()


class Tag(models.Model):
    """
    Тег для рецепта (например, завтрак, веган).
    """

    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name="Название тега",
        help_text="Например: завтрак, обед, ужин",
    )
    slug = models.SlugField(
        max_length=SLUG_MAX_LENGTH,
        unique=True,
        verbose_name="Идентификатор",
        help_text="Уникальный слаг (например: breakfast)",
    )

    class Meta:
        verbose_name = "тег"
        verbose_name_plural = "Теги"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Ингредиент с единицей измерения.
    """

    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name="Название ингредиента",
        help_text="Название ингредиента",
    )

    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_MAX_LENGTH,
        verbose_name="Единица измерения ингредиента",
        help_text="Единица измерения ингредиента",
    )

    class Meta:

        verbose_name = "ингредиент"

        verbose_name_plural = "Ингредиенты"

        constraints = (
            models.UniqueConstraint(
                fields=("name", "measurement_unit"), name="unique_ingredient"
            ),
        )

    def __str__(self):

        return self.name


class Recipe(models.Model):
    """
    Основная модель рецепта.
    """

    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name="Название",
        help_text="Например: Борщ",
    )
    text = models.TextField(
        verbose_name="Описание",
        help_text="Пошаговое приготовление",
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Время приготовления (мин)",
    )
    image = models.ImageField(
        upload_to="recipes/images/",
        verbose_name="Фото блюда",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Теги",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredients",
        related_name="recipes",
        verbose_name="Ингредиенты",
    )

    class Meta:
        verbose_name = "рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-pub_date"]

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    """
    Связь рецепт — ингредиент (с количеством).
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredients_in_recipe",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Количество",
    )

    class Meta:
        verbose_name = "ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient",
            )
        ]
        ordering = ["ingredient"]

    def __str__(self):
        return f"{self.ingredient} — {self.amount}"


class UserRecipeRelation(models.Model):
    """
    Йбстрактная модель.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.recipe} — {self.user}"


class Favorite(UserRecipeRelation):
    """
    Избранное.
    """

    class Meta:
        verbose_name = "избранное"
        verbose_name_plural = "Избранное"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_favorite"
            )
        ]
        ordering = ["-id"]

    def __str__(self):
        return f"{self.recipe} — {self.user}"


class ShoppingCart(UserRecipeRelation):
    """
    Список покупок.
    """

    class Meta:
        verbose_name = "список покупок"
        verbose_name_plural = "Список покупок"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_shopping_cart"
            )
        ]
        ordering = ["-id"]
