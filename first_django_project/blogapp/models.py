from django.db import models
from django.urls import reverse


class Author(models.Model):
    """Модель Author представляет автора статьи"""

    class Meta:
        ordering = ["name"]
        verbose_name = "Author"
        verbose_name_plural = "Authors"

    name = models.CharField(
        max_length=100,
        verbose_name="Author's name",
        db_index=True,
    )
    bio = models.TextField(
        verbose_name="Author's biography",
        blank=True,
    )

    def __str__(self):
        return self.name


class Category(models.Model):
    """Модель Category представляет категорию статьи"""

    class Meta:
        ordering = ["name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    name = models.CharField(
        max_length=40,
        verbose_name="Category",
        db_index=True,
    )

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель Tag представляет тэг, который можно назначить статье"""

    class Meta:
        ordering = ["name"]
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    name = models.CharField(
        max_length=20,
        verbose_name="Tag",
        db_index=True,
    )

    def __str__(self):
        return self.name


class Article(models.Model):
    """Модель Article представляет статью"""

    class Meta:
        ordering = ["-pub_date", "title"]
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    title = models.CharField(
        max_length=200,
        verbose_name="Article title",
        db_index=True,
    )
    content = models.TextField(
        verbose_name="Content",
        blank=True,
    )
    pub_date = models.DateTimeField(
        verbose_name="The publication date",
        db_index=True,
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name="articles",
        verbose_name="The author of the article",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="articles",
        verbose_name="Category",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="articles",
        verbose_name="Tags",
        blank=True,
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blogapp:article_detail", kwargs={"pk": self.pk})


