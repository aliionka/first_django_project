from django.views.generic import ListView, TemplateView, DetailView, CreateView, UpdateView, DeleteView
from .models import Product, Order
import time
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.urls import reverse_lazy

start_time = time.time()


class ShopIndexView(TemplateView):
    """Главная страница со списком ссылок"""
    template_name = "shopapp/shop_index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        time_running = time.time() - start_time
        context["time_running"] = time_running
        return context


class ProductsListView(ListView):
    """Список продуктов"""
    # model = Product
    template_name = "shopapp/products_list.html"
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductDetailsView(DetailView):
    model = Product
    template_name = "shopapp/product_details.html"
    context_object_name = "product"


class ProductCreateView(CreateView):
    model = Product
    fields = "name", "price", "description", "price", "stock_availability"
    success_url = reverse_lazy("shopapp:products_list")


class ProductUpdateView(UpdateView):
    model = Product
    fields = "name", "price", "description", "price", "stock_availability"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk},
        )


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")
    template_name = "shopapp/product_confirm_delete.html"

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(ListView):
    """Список заказов с загруженными пользователями и продуктами"""
    queryset = Order.objects.select_related("user").prefetch_related("products")
    template_name = "shopapp/order_list.html"


class OrderDetailView(DetailView):
    queryset = Order.objects.select_related("user").prefetch_related("products")
    template_name = "shopapp/order_detail.html"


class OrderCreateView(CreateView):
    model = Order
    fields = "user", "products", "address", "comment"
    success_url = reverse_lazy("shopapp:order_list")


class OrderUpdateView(UpdateView):
    model = Order
    fields = "products", "address", "comment"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:order_detail",
            kwargs={"pk": self.object.pk},
        )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:order_list")
    template_name = "shopapp/order_confirm_delete.html"
