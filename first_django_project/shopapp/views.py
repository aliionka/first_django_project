from django.views.generic import ListView, TemplateView
from .models import Product, Order
import time
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from .forms import ProductForm, OrderForm

from django.shortcuts import redirect, reverse

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


def create_product(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            # Product.objects.create(**form.cleaned_data)
            # url = reverse("shopapp:products_list")
            form.save()
            return redirect("shopapp:products_list")
    else:
        form = ProductForm()
    context = {
        "form": form
    }
    return render(request, "shopapp/create_product.html", context=context)


def create_order(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.save()
            form.save_m2m()
            return redirect("shopapp:orders_list")
    else:
        form = OrderForm()
    context = {
        "form": form
    }
    return render(request, "shopapp/create_order.html", context=context)
