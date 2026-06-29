"""
Serializers for menu catalog & daily menu management.
"""

from django.utils import timezone
from rest_framework import serializers

from .models import DailyMenu, DailyMenuItem, MenuItem


class MenuItemSerializer(serializers.ModelSerializer):
    """Used by admins for full catalog CRUD."""

    class Meta:
        model = MenuItem
        fields = [
            "id", "name", "description", "category", "price",
            "is_vegetarian", "image", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DailyMenuItemWriteSerializer(serializers.Serializer):
    """Used inside DailyMenuSerializer when admins set the day's lineup."""

    menu_item_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(), source="menu_item"
    )
    price_override = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, allow_null=True)
    quantity_available = serializers.IntegerField(required=False, allow_null=True, min_value=0)


class DailyMenuItemSerializer(serializers.ModelSerializer):
    """Read representation of an item within a published daily menu."""

    menu_item = MenuItemSerializer(read_only=True)
    effective_price = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    is_sold_out = serializers.BooleanField(read_only=True)

    class Meta:
        model = DailyMenuItem
        fields = [
            "id", "menu_item", "price_override", "quantity_available",
            "quantity_ordered", "effective_price", "is_sold_out",
        ]


class DailyMenuSerializer(serializers.ModelSerializer):
    """Read representation of a full day's menu, for both admin and employee views."""

    items = DailyMenuItemSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)
    is_order_open = serializers.SerializerMethodField()

    class Meta:
        model = DailyMenu
        fields = [
            "id", "date", "is_published", "cutoff_time", "notes",
            "items", "created_by_name", "is_order_open", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_is_order_open(self, obj):
        from django.conf import settings

        now = timezone.localtime()
        if obj.date != now.date():
            return False
        cutoff = obj.cutoff_time or now.replace(
            hour=settings.ORDER_CUTOFF_HOUR, minute=0, second=0, microsecond=0
        ).time()
        return now.time() < cutoff


class DailyMenuCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Used by admins to create/update a DailyMenu along with its item lineup
    in a single request:

    {
      "date": "2026-07-01",
      "is_published": true,
      "cutoff_time": "11:00:00",
      "notes": "Special Monday lineup",
      "items": [
        {"menu_item_id": 3, "price_override": 90.00, "quantity_available": 40},
        {"menu_item_id": 7}
      ]
    }
    """

    items = DailyMenuItemWriteSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = DailyMenu
        fields = ["id", "date", "is_published", "cutoff_time", "notes", "items"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        request = self.context.get("request")
        daily_menu = DailyMenu.objects.create(
            created_by=request.user if request else None, **validated_data
        )
        self._sync_items(daily_menu, items_data)
        return daily_menu

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items_data is not None:
            self._sync_items(instance, items_data, replace=True)
        return instance

    @staticmethod
    def _sync_items(daily_menu, items_data, replace=False):
        if replace:
            daily_menu.items.all().delete()
        for item in items_data:
            DailyMenuItem.objects.update_or_create(
                daily_menu=daily_menu,
                menu_item=item["menu_item"],
                defaults={
                    "price_override": item.get("price_override"),
                    "quantity_available": item.get("quantity_available"),
                },
            )

    def to_representation(self, instance):
        # Return the full nested representation after create/update.
        return DailyMenuSerializer(instance, context=self.context).data
