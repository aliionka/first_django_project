from django.views.generic import ListView, TemplateView, DetailView, CreateView, UpdateView, DeleteView
from .models import Product, Order
import time
from django.http import HttpResponseRedirect
from django.shortcuts import reverse, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib import messages

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


class ProductCreateView(PermissionRequiredMixin, CreateView):
    # если пользователь является суперпользователем, то он сможет создать товар,
    # в противном случае - получит ошибку
    # def test_func(self):
    #     # return self.request.user.groups.filter(name="secret-group").exists()
    #     return self.request.user.is_superuser
    permission_required = "shopapp.add_product"
    raise_exception = True

    model = Product
    fields = "name", "price", "description", "stock_availability"
    success_url = reverse_lazy("shopapp:products_list")
    template_name = "shopapp/create_product.html"

    def form_valid(self, form):
        # Связываем продукт с текущим пользователем
        form.instance.created_by = self.request.user
        # Используем родительский метод через super()
        response = super().form_valid(form)

        # Flash-сообщение пользователю
        messages.success(self.request, f"Продукт '{form.instance.name}' успешно создан!")
        return response


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    model = Product
    fields = "name", "price", "description", "stock_availability"
    template_name_suffix = "_update_form"

    raise_exception = True

    def test_func(self):
        product = self.get_object()
        user = self.request.user

        if user.is_superuser:
            return True

        if user.has_perm("shopapp.change_product"):
            return product.created_by == user
        return False

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


class OrdersListView(LoginRequiredMixin,ListView):
    """Список заказов с загруженными пользователями и продуктами"""
    queryset = Order.objects.select_related("user").prefetch_related("products")
    template_name = "shopapp/order_list.html"


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = ["shopapp.view_order"]
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
