"""
shopapp/views.py.

В этом модуле лежат различные наборы представлений
для интернет-магазина: по товарам, заказм и т.д.
"""
from csv import DictWriter
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.views.generic import (ListView, TemplateView,
                                  DetailView, CreateView,
                                  UpdateView, DeleteView, View)
from django.http import Http404
from .models import Product, Order
import time
from django.http import (HttpResponseRedirect,
                         HttpRequest,
                         JsonResponse,
                         HttpResponse)
from django.shortcuts import reverse, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin,
                                        UserPassesTestMixin)
from django.contrib.auth.decorators import user_passes_test, permission_required, login_required
from django.contrib import messages
from django.forms import inlineformset_factory
import logging
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.syndication.views import Feed
from django.contrib.auth import get_user_model

from shopapp.serializers import OrderSerializer
from .forms import ProductForm, ProductImageForm
from .models import ProductImage
from .serializers import ProductSerializer, OrderSerializer
from .common import save_csv_products

logger = logging.getLogger(__name__)

start_time = time.time()


class ProductViewSet(ModelViewSet):
    """Создает ViewSet для модели Product в Django REST Framework."""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = [  # по каким полям можно фильтровать
        "name",
        "description",
        "price",
        "discount",
        "archived"
    ]
    ordering_fields = [
        "name",
        "price",
        "discount",
    ]

    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })
        return response

    @action(
        detail=False,
        methods=["post"],
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES["file"].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        print("Hello products list!")
        return super().list(*args, **kwargs)


class OrderViewSet(ModelViewSet):
    """Создает ViewSet для модели Order в Django REST Framework."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["order_date", "user", "address"]
    filterset_fields = [
        "order_date",
        "user",
        "address",
        "promocode"
    ]
    ordering_fields = [
        "order_date",
        "user",
    ]


class ShopIndexView(TemplateView):
    """Главная страница со списком ссылок."""

    template_name = "shopapp/shop_index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        time_running = time.time() - start_time
        context["time_running"] = time_running
        print("lala")
        return context


class ProductsListView(ListView):
    """Список продуктов."""

    # model = Product
    template_name = "shopapp/products_list.html"
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductDetailsView(DetailView):
    """Подробное описание продукта."""

    # model = Product
    queryset = Product.objects.prefetch_related("images")
    template_name = "shopapp/product_details.html"
    context_object_name = "product"


class ProductCreateView(PermissionRequiredMixin, CreateView):
    """Создание продукта."""

    # если пользователь является суперпользователем, то он сможет создать
    # товар, в противном случае - получит ошибку
    # def test_func(self):
    #     # return self.request.user.groups.filter(
    #     name="secret-group"
    #     ).exists()
    #     return self.request.user.is_superuser
    permission_required = "shopapp.add_product"
    raise_exception = True

    model = Product
    fields = "name", "price", "description", "stock_availability", "preview",
    success_url = reverse_lazy("shopapp:products_list")
    template_name = "shopapp/create_product.html"

    def form_valid(self, form):
        # Связываем продукт с текущим пользователем
        form.instance.created_by = self.request.user
        # Используем родительский метод через super()
        response = super().form_valid(form)

        # Flash-сообщение пользователю
        messages.success(self.request,
                         f"Продукт '{form.instance.name}' успешно создан!")
        return response


ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    form=ProductImageForm,
    extra=3,
    max_num=5,
    can_delete=True,
)


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    """Изменение продукта."""

    model = Product
    # fields = "name", "price", "description", "stock_availability", "preview",
    template_name_suffix = "_update_form"
    form_class = ProductForm
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["image_formset"] = ProductImageFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object
            )
        else:
            context["image_formset"] = ProductImageFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context["image_formset"]

        if image_formset.is_valid():
            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

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
    """Удаление продукта."""

    model = Product
    success_url = reverse_lazy("shopapp:products_list")
    template_name = "shopapp/product_confirm_delete.html"

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class ProductDataExportView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        cache_key = "products_data_export"
        products_data = cache.get(cache_key)
        if products_data in None:
            products = Product.objects.order_by("pk").all()
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": product.price,
                    "archived": product.archived,
                }
                for product in products
            ]
            cache.set(cache_key, products_data, 300)
        return JsonResponse({"products": products_data})


class OrdersListView(LoginRequiredMixin, ListView):
    """Список заказов с загруженными пользователями и продуктами."""

    queryset = Order.objects.select_related("user").prefetch_related("products")
    template_name = "shopapp/order_list.html"


class OrderDetailView(PermissionRequiredMixin, DetailView):
    """Подробное описание заказа."""

    permission_required = ["shopapp.view_order"]
    queryset = Order.objects.select_related("user").prefetch_related("products")
    template_name = "shopapp/order_detail.html"


class OrderCreateView(CreateView):
    """Создание заказа."""

    model = Order
    fields = "user", "products", "address", "comment"
    success_url = reverse_lazy("shopapp:order_list")


class OrderUpdateView(UpdateView):
    """Изменение заказа."""

    model = Order
    fields = "products", "address", "comment"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:order_detail",
            kwargs={"pk": self.object.pk},
        )


class OrderDeleteView(DeleteView):
    """Удаление заказа."""

    model = Order
    success_url = reverse_lazy("shopapp:order_list")
    template_name = "shopapp/order_confirm_delete.html"


class OrdersExportViews(LoginRequiredMixin, View):
    """
    Экспорт заказов в формате JSON.

    GET /orders/export/
    Параметры:
        - limit (optional):
                максимальное количество заказов (по умолчанию 100)
        - offset (optional):
                сдвиг для пагинации (по умолчанию 0)
        - user_id (optional):
                фильтр по пользователю
    """

    def get(self, request: HttpRequest) -> JsonResponse:
        try:
            orders = Order.objects.select_related(
                "user"
            ).prefetch_related("products")

            # Фильтрация
            user_id = request.GET.get("user_id")
            if user_id:
                try:
                    orders = orders.filter(user_id=int(user_id))
                except ValueError:
                    return JsonResponse(
                        {"error": "Invalid format user_id"},
                        status=400
                    )

            # Пагинация (offset + limit)
            limit = request.GET.get("limit", 100)  # По умолчанию 100
            try:
                limit = int(limit)
                if limit > 1000:
                    limit = 1000
            except ValueError:
                limit = 100

            offset = request.GET.get("offset", 0)
            try:
                offset = int(offset)
            except ValueError:
                offset = 0

            # общее количество заказов
            total_count = orders.count()

            orders = orders.order_by("-order_date")[offset:offset + limit]

            orders_data = [
                {
                    "pk": order.pk,
                    "address": order.address,
                    "promocode": order.promocode,
                    "user_id": order.user.pk,
                    "user_name": order.user.username,
                    "list_id_products": [
                        product.pk for product in order.products.all()
                    ],
                    "order_date": order.order_date.isoformat(),
                }
                for order in orders
            ]
            return JsonResponse({
                "count": len(orders_data),
                "total": total_count,
                "offset": offset,
                "limit": limit,
                "orders": orders_data,
            })

        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return JsonResponse({"error": "Internal server error"}, status=500)


class LatestProductsFeed(Feed):
    title = "Products list (latest)"
    description = "Updates on changes and addition products"
    link = reverse_lazy("shopapp:products_list")

    def items(self):
        """
        Реализует получение информации о продукатах
        """
        return (
            Product.objects
            .filter(created_at__isnull=False)
            .order_by("name")[:5]
        )

    def item_title(self, item: Product):
        """
        Получение заголовка из объекта,
        который возвращается в списке
        """
        return item.name

    def item_description(self, item: Product):
        return item.description[:50]

    def item_link(self, item):
        return item.get_absolute_url()


class UserOrdersListView(LoginRequiredMixin, ListView):
    """Список заказов с авторизированного пользователя"""

    template_name = "shopapp/user_order_list.html"

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        User = get_user_model()
        self.owner = User.objects.filter(pk=user_id).first()
        if self.owner is None:
            raise Http404("Пользователь не найден")
        return Order.objects.filter(user=self.owner).select_related("user").prefetch_related("products")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["owner"] = self.owner
        return context


class ExportUserOrderListView(LoginRequiredMixin, View):
    """
    Экспорт заказов пользователя в JSON.

    GET /users/<int:user_id>/orders/export/

    Query-параметры:
        - limit (optional): максимум заказов на странице (по умолчанию 100, макс 1000)
        - offset (optional): сдвиг для пагинации (по умолчанию 0)
    """

    CACHE_TIMEOUT = 300

    def get(self, request: HttpRequest) -> JsonResponse:
        user_id = self.kwargs["user_id"]

        # Пагинация (offset + limit)
        limit = request.GET.get("limit", 100)  # По умолчанию 100
        try:
            limit = int(limit)
            if limit > 1000:
                limit = 1000
            elif limit < 0:
                limit = 0
        except ValueError:
            limit = 100

        offset = request.GET.get("offset", 0)
        try:
            offset = int(offset)
            if offset < 0:
                offset = 0
        except ValueError:
            offset = 0

        # Ключ кэша
        cache_key = f"export_orders_u{user_id}_l{limit}_o{offset}"
        cached = cache.get(cache_key)
        if cached is not None:
            return JsonResponse(cached)

        owner = get_object_or_404(get_user_model(), pk=user_id)

        orders_qs = (
            Order.objects.filter(user=owner)
            .select_related("user")
            .prefetch_related("products")
            .order_by("pk")
        )

        # общее количество заказов
        total_count = orders_qs.count()
        page = orders_qs[offset:offset + limit]

        orders_data = OrderSerializer(page, many=True).data

        payload = {
            "count": total_count,
            "offset": offset,
            "limit": limit,
            "orders": orders_data,
        }
        cache.set(cache_key, payload, self.CACHE_TIMEOUT)
        return JsonResponse(payload)
