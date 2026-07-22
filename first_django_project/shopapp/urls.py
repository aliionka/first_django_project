from django.urls import path
from .views import ShopIndexView, ShopProductView, ShopOrderView, create_product, create_order

app_name = "shopapp"

urlpatterns = [
    path("", ShopIndexView.as_view(), name="shop_index"),
    path("products/", ShopProductView.as_view(), name="products_list"),
    path("products/create/", create_product, name="create_product"),
    path("orders/", ShopOrderView.as_view(), name="orders_list"),
    path("orders/create/", create_order, name="create_order"),
]
