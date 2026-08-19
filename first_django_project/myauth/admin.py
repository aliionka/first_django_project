from django.contrib import admin
from django.utils.html import format_html
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "bio_short", "agreement_accepted", "avatar_preview")
    list_display_links = ("id", "user")
    list_filter = ("agreement_accepted", )
    search_fields = ("user__username", "user__first_name", "user__last_name", "bio")
    fieldsets = (
        (None, {
            "fields": ("user", "bio", "agreement_accepted", "avatar"),
        }),
    )
    readonly_fields = ("avatar_preview",)

    def bio_short(self, obj: Profile) -> str:
        """Короткое описание bio"""
        if len(obj.bio) < 48:
            return obj.bio
        return obj.bio[:48] + "..."
    bio_short.short_description = "Bio"

    def avatar_preview(self, obj: Profile) -> str:
        """Превью аватара"""
        if obj.avatar:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit:cover; border-radius:50%;" />',
                obj.avatar.url
            )
        return "The avatar is missing"
    avatar_preview.short_description = "Avatar"

