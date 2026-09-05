from django.urls import path
from .views import BasedView, ArticleDetailView

app_name = 'blogapp'

urlpatterns = [
    path("", BasedView.as_view(), name="articles_list"),
    path("<int:pk>/", ArticleDetailView.as_view(), name="article_detail"),
]
