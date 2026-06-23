from django.urls import path
from .views import ShopIndexView, ShopProductView, ShopOrderView

app_name = "shopapp"

urlpatterns = [
    path("", ShopIndexView.as_view(), name="shop_index"),
    path("products/", ShopProductView.as_view(), name="products_list"),
    path("orders/", ShopOrderView.as_view(), name="orders_list")
]
