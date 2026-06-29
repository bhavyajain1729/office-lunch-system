"""
Serializers for the orders app: checkout (cart -> order), UTR payment
submission, order history (employee) and order management (admin).
"""

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from menu.models import DailyMenuItem, MenuItem

from .models import Order, OrderItem, PaymentQRCode


# ---------------------------------------------------------------------------
# Checkout (cart submission)
# ---------------------------------------------------------------------------
class CartItemInputSerializer(serializers.Serializer):
    """One line of the cart submitted by the employee at checkout."""

    menu_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, max_value=50)


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "menu_item", "item_name", "unit_price", "quantity", "line_total"]
        read_only_fields = fields


class CheckoutSerializer(serializers.Serializer):
    """
    POST body for creating an order from the cart:
    {
      "order_date": "2026-07-01",
      "special_instructions": "No spicy please",
      "items": [{"menu_item_id": 3, "quantity": 2}, ...]
    }
    """

    order_date = serializers.DateField()
    special_instructions = serializers.CharField(required=False, allow_blank=True, max_length=255)
    items = CartItemInputSerializer(many=True, allow_empty=False)

    def validate_order_date(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError("Cannot place an order for a past date.")
        return value

    def validate(self, attrs):
        from menu.models import DailyMenu

        order_date = attrs["order_date"]
        daily_menu = DailyMenu.objects.filter(date=order_date, is_published=True).first()
        if not daily_menu:
            raise serializers.ValidationError(
                {"order_date": "No published menu is available for this date."}
            )

        if order_date == timezone.localdate():
            now = timezone.localtime()
            cutoff = daily_menu.cutoff_time or now.replace(
                hour=settings.ORDER_CUTOFF_HOUR, minute=0, second=0, microsecond=0
            ).time()
            if now.time() >= cutoff:
                raise serializers.ValidationError(
                    {"order_date": f"Ordering for today closed at {cutoff.strftime('%H:%M')}."}
                )

        resolved_lines = []
        menu_item_ids = [i["menu_item_id"] for i in attrs["items"]]
        listings = {
            dmi.menu_item_id: dmi
            for dmi in DailyMenuItem.objects.select_related("menu_item").filter(
                daily_menu=daily_menu, menu_item_id__in=menu_item_ids
            )
        }

        for line in attrs["items"]:
            listing = listings.get(line["menu_item_id"])
            if not listing or not listing.menu_item.is_active:
                raise serializers.ValidationError(
                    {"items": f"Item {line['menu_item_id']} is not available on today's menu."}
                )
            remaining = None
            if listing.quantity_available is not None:
                remaining = listing.quantity_available - listing.quantity_ordered
                if remaining < line["quantity"]:
                    raise serializers.ValidationError(
                        {"items": f"Only {max(remaining, 0)} left of '{listing.menu_item.name}'."}
                    )
            resolved_lines.append({"listing": listing, "quantity": line["quantity"]})

        attrs["daily_menu"] = daily_menu
        attrs["resolved_lines"] = resolved_lines
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        employee = self.context["request"].user
        resolved_lines = validated_data["resolved_lines"]

        order = Order.objects.create(
            employee=employee,
            order_date=validated_data["order_date"],
            special_instructions=validated_data.get("special_instructions", ""),
            total_amount=0,
            status=Order.Status.PENDING_PAYMENT,
        )

        for line in resolved_lines:
            listing = line["listing"]
            OrderItem.objects.create(
                order=order,
                menu_item=listing.menu_item,
                item_name=listing.menu_item.name,
                unit_price=listing.effective_price,
                quantity=line["quantity"],
            )
            listing.quantity_ordered = listing.quantity_ordered + line["quantity"]
            listing.save(update_fields=["quantity_ordered"])

        order.recalculate_total()
        return order


# ---------------------------------------------------------------------------
# UTR submission
# ---------------------------------------------------------------------------
class UTRSubmitSerializer(serializers.Serializer):
    utr_number = serializers.CharField(max_length=50, min_length=4)

    def validate_utr_number(self, value):
        value = value.strip()
        if not value.isalnum():
            raise serializers.ValidationError("UTR number should contain only letters and numbers.")
        return value

    def save(self, **kwargs):
        order = self.context["order"]
        order.utr_number = self.validated_data["utr_number"]
        order.utr_submitted_at = timezone.now()
        order.status = Order.Status.PAYMENT_SUBMITTED
        order.save(update_fields=["utr_number", "utr_submitted_at", "status", "updated_at"])
        return order


# ---------------------------------------------------------------------------
# Order read/history serializers
# ---------------------------------------------------------------------------
class OrderSerializer(serializers.ModelSerializer):
    """Used for employee order history and admin order management list/detail."""

    items = OrderItemSerializer(many=True, read_only=True)
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    employee_email = serializers.CharField(source="employee.email", read_only=True)
    employee_department = serializers.CharField(source="employee.department", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "employee", "employee_name", "employee_email", "employee_department",
            "order_date", "status", "total_amount", "utr_number", "utr_submitted_at",
            "payment_verified_by", "payment_verified_at", "admin_remarks",
            "special_instructions", "items", "created_at", "updated_at",
        ]
        read_only_fields = fields


# ---------------------------------------------------------------------------
# Admin order management
# ---------------------------------------------------------------------------
class OrderStatusUpdateSerializer(serializers.Serializer):
    """Admin endpoint to confirm/reject/complete/cancel an order."""

    status = serializers.ChoiceField(choices=Order.Status.choices)
    admin_remarks = serializers.CharField(required=False, allow_blank=True, max_length=255)

    def validate_status(self, value):
        allowed_transitions = {
            Order.Status.PAYMENT_SUBMITTED: {Order.Status.CONFIRMED, Order.Status.REJECTED},
            Order.Status.CONFIRMED: {Order.Status.COMPLETED, Order.Status.CANCELLED},
            Order.Status.PENDING_PAYMENT: {Order.Status.CANCELLED},
            Order.Status.REJECTED: {Order.Status.CANCELLED},
        }
        order = self.context["order"]
        allowed = allowed_transitions.get(order.status, set())
        if value not in allowed and value != order.status:
            raise serializers.ValidationError(
                f"Cannot move order from '{order.status}' to '{value}'."
            )
        return value

    def save(self, **kwargs):
        order = self.context["order"]
        admin_user = self.context["request"].user

        order.status = self.validated_data["status"]
        order.admin_remarks = self.validated_data.get("admin_remarks", order.admin_remarks)

        if order.status == Order.Status.CONFIRMED:
            order.payment_verified_by = admin_user
            order.payment_verified_at = timezone.now()

        order.save(update_fields=[
            "status", "admin_remarks", "payment_verified_by", "payment_verified_at", "updated_at",
        ])
        return order


# ---------------------------------------------------------------------------
# Payment QR code
# ---------------------------------------------------------------------------
class PaymentQRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentQRCode
        fields = ["id", "label", "upi_id", "qr_image", "is_active", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]
