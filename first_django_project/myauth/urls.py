from django.contrib.auth.views import LoginView
from django.conf import settings
from django.urls import include, path

from .views import (
    get_cookie_view,
    set_cookie_view,
    get_session_view,
    set_session_view,
    MyLogoutView,
    AboutMeView,
    RegisterView,
    FooBarView,
    ProfileListView,
    ProfileDetailView,
    ProfileUpdateView
)


app_name = "myauth"

urlpatterns = [
    path("login/",
         LoginView.as_view(
             template_name="myauth/login.html",
             redirect_authenticated_user=True
         ),
         name="login"),
    path("logout/", MyLogoutView.as_view(), name="logout"),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/<int:pk>/", ProfileDetailView.as_view(), name="profile_detail"),
    path("profiles/", ProfileListView.as_view(), name="profiles_list"),
    path("profile/<int:pk>/update/", ProfileUpdateView.as_view(), name="profile_update"),

    path("cookie/get/", get_cookie_view, name="cookie-get"),
    path("cookie/set/", set_cookie_view, name="cookie-set"),

    path("session/get/", get_session_view, name="session-get"),
    path("session/set/", set_session_view, name="session-set"),

    path("foo-bar/", FooBarView.as_view(), name="foo-bar"),
]

