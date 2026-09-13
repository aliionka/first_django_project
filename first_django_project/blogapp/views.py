
from django.views.generic import ListView, DetailView


from .models import Article


class BasedView(ListView):
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

