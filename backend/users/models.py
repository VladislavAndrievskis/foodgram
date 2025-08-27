from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import F, Q
from django.core.exceptions import ValidationError

User = get_user_model()


class Subscription(models.Model):
    """Подписка пользователя на автора."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Подписчик",
        help_text="Пользователь, оформивший подписку",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribers",
        verbose_name="Автор",
        help_text="Пользователь, на которого оформлена подписку",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.CheckConstraint(
                check=~Q(user=F("author")), name="no_self_subscribe"
            ),
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_subscription"
            ),
        ]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["author"]),
        ]

    def __str__(self):
        return f"Подписка {self.user.username} на {self.author.username}"

    def clean(self):
        if self.user == self.author:
            raise ValidationError("Нельзя подписаться на самого себя")


class Profile(models.Model):
    """Профиль пользователя с аватаром."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )
    avatar = models.ImageField(
        verbose_name="Аватар",
        upload_to="users/avatars/",
        blank=True,
        null=True,
        default="",
        validators=[FileExtensionValidator(["png", "jpg", "jpeg"])],
    )

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Профиль {self.user.username}"
