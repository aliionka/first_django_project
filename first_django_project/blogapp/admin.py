from django.contrib import admin
from .models import Author, Article, Category, Tag


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "content_short", "pub_date", "author", "category")
    list_display_links = ("id", "title")
    list_filter = ("title", )
    fieldsets = (
        (None, {
            "fields": ("title", "author", "content_short", "pub_date", "category", "tags"),
        }),
    )

    def content_short(self, obj: Article) -> str:
        """Короткое описание content"""
        if len(obj.content) < 48:
            return obj.content
        return obj.content[:48] + "..."
    content_short.short_description = "Content"


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "bio",)
    list_display_links = ("id", "name")
    list_filter = ("name", )
    fieldsets = (
        (None, {
            "fields": ("name", "bio"),
        }),
    )

    def bio_short(self, obj: Author) -> str:
        """Короткое описание bio"""
        if len(obj.bio) < 48:
            return obj.bio
        return obj.bio[:48] + "..."
    bio_short.short_description = "Bio"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)
    list_display_links = ("id", "name")
    list_filter = ("name", )
    fieldsets = (
        (None, {
            "fields": ("name", ),
        }),
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)
    list_display_links = ("id", "name")
    list_filter = ("name", )
    fieldsets = (
        (None, {
            "fields": ("name", ),
        }),
    )
