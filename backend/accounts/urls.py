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
    SessionListView,
    SessionTerminateView,
    TerminateAllOtherSessionsView,
    ValidateSessionView,
    get_current_user_view,
)

urlpatterns = [
    # Authentication
    path("register/", EmployeeRegisterView.as_view(), name="employee-register"),
    path("login/employee/", EmployeeLoginView.as_view(), name="employee-login"),
    path("login/admin/", AdminLoginView.as_view(), name="admin-login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    
    # Profile & Current User
    path("profile/", ProfileView.as_view(), name="profile"),
    path("me/", get_current_user_view, name="current-user"),
    
    # Session Management
    path("sessions/", SessionListView.as_view(), name="session-list"),
    path("sessions/<uuid:session_id>/terminate/", SessionTerminateView.as_view(), name="session-terminate"),
    path("sessions/terminate-all-others/", TerminateAllOtherSessionsView.as_view(), name="terminate-all-other-sessions"),
    path("validate-session/", ValidateSessionView.as_view(), name="validate-session"),
]
