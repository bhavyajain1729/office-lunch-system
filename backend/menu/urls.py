"""
URL routes for the menu app.
Mounted at /api/menu/ in config/urls.py
"""

from django.urls import path

from .views import (
    DailyMenuDetailView,
    DailyMenuListCreateView,
    MenuItemDetailView,
    MenuItemListCreateView,
    TodayMenuView,
)

urlpatterns = [
    # Master catalog
    path("items/", MenuItemListCreateView.as_view(), name="menu-item-list"),
    path("items/<int:pk>/", MenuItemDetailView.as_view(), name="menu-item-detail"),

    # Daily menu - admin management
    path("daily/", DailyMenuListCreateView.as_view(), name="daily-menu-list"),
    path("daily/<int:pk>/", DailyMenuDetailView.as_view(), name="daily-menu-detail"),

    # Daily menu - employee view
    path("today/", TodayMenuView.as_view(), name="today-menu"),
]
