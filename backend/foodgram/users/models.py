from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F, Q
from django.forms import ValidationError

User = get_user_model()


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions",  # Изменено для лучшей читаемости
        verbose_name="Подписчик",
        help_text="Пользователь, оформивший подписку",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers",  # Изменено для лучшей читаемости
        verbose_name="Автор",
        help_text="Пользователь, на которого оформлена подписка",
    )

    class Meta:
        verbose_name = "подписка"
        verbose_name_plural = "подписки"

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
