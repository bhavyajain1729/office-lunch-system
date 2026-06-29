"""
URL routes for the accounts app.
Mounted at /api/auth/ in config/urls.py
"""

from django.urls import path

from .views import (
    AdminLoginView,
    EmployeeLoginView,
    EmployeeRegisterView,
    LogoutView,
    ProfileView,
)

urlpatterns = [
    path("register/", EmployeeRegisterView.as_view(), name="employee-register"),
    path("login/employee/", EmployeeLoginView.as_view(), name="employee-login"),
    path("login/admin/", AdminLoginView.as_view(), name="admin-login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
