from django.contrib import admin
from django.utils.html import format_html

from .models import Profile, Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "author")
    search_fields = ("user", "author")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "avatar_preview")
    search_fields = ("user__username", "user__first_name", "user__email")
    readonly_fields = ("avatar_preview",)  # Показать превью при редактировании

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="100" height="100" style="border:50%">',
                obj.avatar.url
            )
        return "Нет аватара"

    avatar_preview.short_description = "Текущий аватар"

    # Чтобы поле avatar было в форме
    fields = ("user", "avatar", "avatar_preview")
