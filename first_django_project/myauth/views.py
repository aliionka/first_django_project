from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test

from .models import Profile


class AboutMeView(TemplateView):
    template_name = "myauth/about-me.html"


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


def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f"Cookie value: {value!r}")


@permission_required("myauth.view_profile", raise_exception=True) # проверяет, есть ли у пользователя необходимые разрешения для доступа к представлению
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set!")


@login_required # гарантирует, что к представлению сможет обратиться только аутентифицированный пользователь
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value: {value!r}")
