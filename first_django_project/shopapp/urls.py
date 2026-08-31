from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    ShopIndexView,
    ProductsListView,
    ProductCreateView,
    ProductUpdateView,
    OrdersListView,
    ProductDetailsView,
    ProductDeleteView,
    OrderDetailView,
    OrderCreateView,
    OrderUpdateView,
    OrderDeleteView,
    OrdersExportViews,
    ProductViewSet,
    OrderViewSet,
)

app_name = "shopapp"

routers = DefaultRouter()
routers.register("products", ProductViewSet)
routers.register("orders", OrderViewSet)

urlpatterns = [
    path("", ShopIndexView.as_view(), name="shop_index"),
    path("products/", ProductsListView.as_view(), name="products_list"),

    path("api/", include(routers.urls)),

    path("products/create/", ProductCreateView.as_view(), name="create_product"),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name="product_details"),
    path("products/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/delete/", ProductDeleteView.as_view(), name="product_delete"),

    path("orders/", OrdersListView.as_view(), name="order_list"),
    path("orders/export/", OrdersExportViews.as_view(), name="orders_export"),

    path("orders/create/", OrderCreateView.as_view(), name="create_order"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("products/<int:pk>/delete/", ProductDeleteView.as_view(), name="product_delete"),
    path("orders/<int:pk>/update/", OrderUpdateView.as_view(), name="order_update"),
    path("orders/<int:pk>/delete/", OrderDeleteView.as_view(), name="order_delete"),

]
