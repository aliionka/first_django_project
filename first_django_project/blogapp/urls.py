from django.urls import path
from .views import (
    ArticleListView,
    ArticleDetailView,
    LatestArticleFeed,
)
from django.contrib.sitemaps.views import sitemap
from .sitemaps import BlogSitemap

app_name = 'blogapp'

sitemaps = {
    "blog": BlogSitemap,
}

urlpatterns = [
    path("", ArticleListView.as_view(), name="articles_list"),
    path("<int:pk>/", ArticleDetailView.as_view(), name="article_detail"),
    path("latest/feed/", LatestArticleFeed(), name="articles_feed"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]
