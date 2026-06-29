"""
Views for menu catalog (admin CRUD) and daily menu (admin manage / employee view).
"""

from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdminRole

from .models import DailyMenu, MenuItem
from .serializers import (
    DailyMenuCreateUpdateSerializer,
    DailyMenuSerializer,
    MenuItemSerializer,
)


# ---------------------------------------------------------------------------
# Master catalog (admin only manages; both roles may read)
# ---------------------------------------------------------------------------
class MenuItemListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/menu/items/        -> any authenticated user (catalog browsing)
    POST /api/menu/items/        -> admin only (create catalog item)
    """

    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filterset_fields = ["category", "is_vegetarian", "is_active"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsAdminRole()]
        return [permissions.IsAuthenticated()]


class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET             -> any authenticated user
    PUT/PATCH/DELETE -> admin only
    """

    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsAdminRole()]


# ---------------------------------------------------------------------------
# Daily menu - admin management
# ---------------------------------------------------------------------------
class DailyMenuListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/menu/daily/   -> admin: list all daily menus (history + drafts)
    POST /api/menu/daily/   -> admin: create a new day's menu
    """

    queryset = DailyMenu.objects.prefetch_related("items__menu_item").all()
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    filterset_fields = ["is_published", "date"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return DailyMenuCreateUpdateSerializer
        return DailyMenuSerializer


class DailyMenuDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/PATCH/DELETE /api/menu/daily/<id>/  -> admin only
    """

    queryset = DailyMenu.objects.prefetch_related("items__menu_item").all()
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return DailyMenuSerializer
        return DailyMenuCreateUpdateSerializer


# ---------------------------------------------------------------------------
# Daily menu - employee facing
# ---------------------------------------------------------------------------
class TodayMenuView(APIView):
    """
    GET /api/menu/today/  -> the published menu for today, for employees
    to browse and add to cart. Returns 404-style empty payload if no
    menu has been published yet.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        daily_menu = (
            DailyMenu.objects.prefetch_related("items__menu_item")
            .filter(date=today, is_published=True)
            .first()
        )
        if not daily_menu:
            return Response(
                {"detail": "No menu has been published for today yet.", "menu": None},
                status=status.HTTP_200_OK,
            )
        serializer = DailyMenuSerializer(daily_menu, context={"request": request})
        return Response({"detail": "", "menu": serializer.data}, status=status.HTTP_200_OK)
