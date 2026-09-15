
from django.views.generic import ListView, DetailView
from django.contrib.syndication.views import Feed
from django.urls import reverse, reverse_lazy

from .models import Article


class ArticleListView(ListView):
    """Список статей"""
    model = Article
    template_name = "blogapp/articles_list.html"
    context_object_name = "articles"
    ordering = "-pub_date" # Сначала новые
    paginate_by = 10 # Пагинация по 10 статей

    def get_queryset(self):
        """Оптимизация запросов: подгружаем связанные объекты"""
        return Article.objects.select_related("author", "category") \
            .prefetch_related("tags") \
            .defer("content")


class ArticleDetailView(DetailView):
    """Детальная страница статьи"""
    model = Article
    template_name = "blogapp/article_detail.html"
    context_object_name = "article"

    def get_queryset(self):
        """Оптимизация запросов: подгружаем связанные объекты"""
        return Article.objects.select_related("author", "category") \
            .prefetch_related("tags")


class LatestArticleFeed(Feed):
    title = "Blog articles (latest)"
    description = "Updates on changes and addition blog articles"
    link = reverse_lazy("blogapp:articles_list")

    def items(self):
        """
        Реализует получение информации о публикациях
        в списке ленты
        """
        return (
            Article.objects
            .filter(pub_date__isnull=False)
            .order_by("-pub_date")[:5]
        )

    def item_title(self, item: Article):
        """
        Получение заголовка из объекта,
        который возвращается в списке
        """
        return item.title

    def item_description(self, item: Article):
        return item.content[:200]
