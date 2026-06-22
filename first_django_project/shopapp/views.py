from django.views.generic import ListView, TemplateView
from .models import Product, Order
import time

start_time = time.time()

class ShopIndexView(TemplateView):
    """Главная страница со списком ссылок"""
    template_name = "shopapp/shop_index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        time_running = time.time() - start_time
        context["time_running"] = time_running
        return context


class ShopProductView(ListView):
    """Список продуктов"""
    model = Product
    template_name = "shopapp/products_list.html"
    context_object_name = "products"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        time_running = time.time() - start_time
        context["time_running"] = time_running
        return context


class ShopOrderView(ListView):
    """Список заказов с загруженными пользователями и продуктами"""
    model = Order
    template_name = "shopapp/orders_list.html"
    context_object_name = "orders"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        time_running = time.time() - start_time
        context["time_running"] = time_running
        return context


    def get_queryset(self):
        """Загрузка связанных данных"""
        return Order.objects.select_related("user").prefetch_related("products")
