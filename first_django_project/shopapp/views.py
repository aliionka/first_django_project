from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from timeit import default_timer
from django.views.generic import ListView
from .models import Product
import time

start_time = time.time()

class ShopIndexView(ListView):
    model = Product
    template_name = 'shopapp/shop_index.html'
    context_object_name = 'products'  # Чтобы в шаблоне было products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        time_running = time.time() - start_time
        context["time_running"] = time_running
        return context


# def shop_index(request: HttpRequest):
#     print(request.path)
#     print(request.method)
#     print(request.headers)
#     return HttpResponse("<h1>Hello, world!</h1>")

# def shop_index(request: HttpRequest):
#     products = [
#         ('💻 laptop', 2999),
#         ('🎧 headphones', 999),
#         ('📱 smartphone', 1500),
#         ('🎮 joystick', 1000)
#     ]
#     context = {
#         "time_running": default_timer(),
#         "products": products,
#     }
#     return render(request, "shopapp/shop_index.html", context=context)
