from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.cache import cache_page

from random import random

from .models import Profile
from .mixins import ProfileOwnerOrStaffMixin


class AboutMeView(UpdateView):
    """Страница профиля с возможностью смены аватара"""
    model = Profile
    template_name = "myauth/about-me.html"
    fields = ("avatar", )
    success_url = reverse_lazy("myauth:about-me")

    def get_object(self, queryset=None):
        """Возвращает профиль текущего пользователя"""
        # return self.request.user.profile
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        if created:
            messages.info(self.request, "Профиль был создан автоматически")
        return profile


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        login(self.request, self.object)
        return response

        # response = super().form_valid(form)
        # Profile.objects.create(user=self.object)
        #
        # username = form.cleaned_data.get("username")
        # password = form.cleaned_data.get("password")
        # user = authenticate(
        #     request=self.request,
        #     username=username,
        #     password=password
        # )
        # login(request=self.request, user=user)
        # return response


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/admin/")
        return render(request, "myauth/login.html")

    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "").strip()

    user = authenticate(request=request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect("/admin/")

    return render(request, "myauth/login.html", {"error": "Invalid login credentials"})


def logout_view(request: HttpRequest):
    logout(request)
    return redirect(reverse("myauth:login"))


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")
    http_method_names = ["get", "post", "options"]


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response


@cache_page(60 * 2)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f"Cookie value: {value!r} + {random()}")


@permission_required("myauth.view_profile",
                     raise_exception=True) # проверяет, есть ли у пользователя необходимые разрешения для доступа к представлению
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set!")


@login_required  # гарантирует, что к представлению сможет обратиться только аутентифицированный пользователь
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value: {value!r}")


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})


class ProfileListView(ListView):
    """Список пользователей"""
    model = Profile
    template_name = "myauth/profiles_list.html"
    context_object_name = "profiles"
    queryset = Profile.objects.select_related("user").all()
    ordering = ("user__username",)  # Сортировка по username


class ProfileDetailView(DetailView):
    """Детальная страница профиля пользователя"""
    model = Profile
    template_name = "myauth/profile_detail.html"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        profile = self.object

        if user.is_authenticated and (user.is_staff or user == self.object.user):
            context["can_edit"] = True
        else:
            context["can_edit"] = False
        return context


class ProfileUpdateView(LoginRequiredMixin, ProfileOwnerOrStaffMixin, UpdateView):
    model = Profile
    fields = ("bio", "agreement_accepted", "avatar")
    template_name = "myauth/profile_update.html"
    success_url = reverse_lazy("myauth:about-me")

    def get_object(self, queryset=None):
        """Получаем профиль по pk из URL"""
        pk = self.kwargs.get("pk")
        if pk is None:
            return self.request.user.profile
        return super().get_object(queryset)

    def get_success_url(self):
        """После обновления возвращаем на страницу профиля"""
        return reverse("myauth:profile_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        """Сообщение об успехе"""
        response = super().form_valid(form)
        messages.success(self.request, "Профиль успешно обновлен!")
        return response



