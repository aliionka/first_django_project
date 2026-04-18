from django.urls import path
from . import views

app_name = "shopapp"

urlpatterns = [
    path("", views.ShopIndexView.as_view(), name="shop_index"),
]