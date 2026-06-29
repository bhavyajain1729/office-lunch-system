"""
Django admin registration for order models.
"""

from django.contrib import admin

from .models import Order, OrderItem, PaymentQRCode


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["menu_item", "item_name", "unit_price", "quantity"]
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id", "employee", "order_date", "status", "total_amount",
        "utr_number", "payment_verified_by", "created_at",
    ]
    list_filter = ["status", "order_date"]
    search_fields = ["employee__full_name", "employee__email", "utr_number"]
    readonly_fields = ["created_at", "updated_at", "total_amount"]
    inlines = [OrderItemInline]


@admin.register(PaymentQRCode)
class PaymentQRCodeAdmin(admin.ModelAdmin):
    list_display = ["label", "upi_id", "is_active", "uploaded_by", "uploaded_at"]
    list_filter = ["is_active"]
