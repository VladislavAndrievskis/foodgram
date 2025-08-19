from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import Profile, Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "author", "subscribers_count")
    list_select_related = ("user", "author")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__email",
        "author__username",
        "author__first_name",
        "author__email",
    )

    @admin.display(description="Подписчики у автора")
    def subscribers_count(self, obj):
        return obj.author.subscribers.count()

    subscribers_count.short_description = "Количество подписчиков автора"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipes_count",
        "subscribers_count",
        "avatar_preview",
    )
    search_fields = ("user__username", "user__first_name", "user__email")
    readonly_fields = ("avatar_preview",)
    fields = ("user", "avatar", "avatar_preview")

    def get_queryset(self, request):
        """Оптимизация запросов: аннотация рецептов и подписчиков"""
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .prefetch_related("user__recipes")
            .annotate(
                _recipes_count=Count("user__recipes", distinct=True),
                _subscribers_count=Count("user__subscribers", distinct=True),
            )
        )

    @admin.display(description="Рецепты")
    def recipes_count(self, obj):
        return obj._recipes_count

    @admin.display(description="Подписчики")
    def subscribers_count(self, obj):
        return obj._subscribers_count

    @admin.display(description="Аватар")
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="'
                'border-radius: 50%; '
                'width: 50px; '
                'height: 50px; '
                'object-fit: cover;" />',
                obj.avatar.url,
            )
        return "Нет аватара"
