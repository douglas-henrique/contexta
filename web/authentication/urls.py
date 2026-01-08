"""
URL configuration for authentication app.
"""

from django.urls import path

from .views import (
    ChangePasswordView,
    CustomTokenRefreshView,
    LoginView,
    LogoutView,
    MeView,
    RegisterView,
)

app_name = "authentication"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
]
