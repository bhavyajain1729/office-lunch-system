"""
Order models.

Cart is intentionally NOT a server-side model — it lives in the React
frontend (localStorage/state) until checkout, at which point the whole
cart is submitted as one Order with nested OrderItems. This keeps the
data model simple and matches how most lightweight food-ordering apps
work in practice.

Payment has no real gateway: the employee scans a static UPI QR code
(uploaded by the admin) shown at checkout, pays manually, then enters
the UTR / transaction reference number, which an admin later verifies.
"""

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from menu.models import MenuItem


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING_PAYMENT = "PENDING_PAYMENT", "Pending Payment"   # UTR not yet submitted
        PAYMENT_SUBMITTED = "PAYMENT_SUBMITTED", "Payment Submitted"  # UTR submitted, awaiting admin verification
        CONFIRMED = "CONFIRMED", "Confirmed"     # admin verified payment
        REJECTED = "REJECTED", "Rejected"        # admin rejected (bad/duplicate UTR etc.)
        CANCELLED = "CANCELLED", "Cancelled"     # cancelled by employee or admin before payment
        COMPLETED = "COMPLETED", "Completed"     # lunch delivered/collected

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    order_date = models.DateField(help_text="The lunch date this order is for.")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING_PAYMENT)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    # --- UTR / manual payment verification ---
    utr_number = models.CharField(
        max_length=50, blank=True,
        help_text="UPI transaction reference number entered by the employee after paying.",
    )
    utr_submitted_at = models.DateTimeField(null=True, blank=True)
    payment_verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="verified_orders",
    )
    payment_verified_at = models.DateTimeField(null=True, blank=True)
    admin_remarks = models.CharField(max_length=255, blank=True, help_text="Reason for rejection, or any note.")

    special_instructions = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order_date", "status"]),
            models.Index(fields=["employee", "order_date"]),
        ]

    def __str__(self):
        return f"Order #{self.id} - {self.employee.full_name} - {self.order_date} ({self.status})"

    def recalculate_total(self, save=True):
        total = sum(item.line_total for item in self.items.all())
        self.total_amount = total
        if save:
            self.save(update_fields=["total_amount"])
        return total


class OrderItem(models.Model):
    """A single line item within an order, snapshotting name/price at order time."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True, related_name="order_items")

    # Snapshots so historical orders remain accurate even if the catalog item
    # is later edited, deactivated, or deleted.
    item_name = models.CharField(max_length=120)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        db_table = "order_items"

    def __str__(self):
        return f"{self.quantity} x {self.item_name}"

    @property
    def line_total(self):
        return self.unit_price * self.quantity


class PaymentQRCode(models.Model):
    """
    Static UPI QR code(s) uploaded by an admin, shown to employees at
    checkout. Only one should be active at a time; `is_active` controls
    which one the employee-facing checkout endpoint returns.
    """

    label = models.CharField(max_length=100, default="Office Canteen UPI")
    upi_id = models.CharField(max_length=100, blank=True)
    qr_image = models.ImageField(upload_to="qr/")
    is_active = models.BooleanField(default=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="uploaded_qr_codes"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payment_qr_codes"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.label} ({'active' if self.is_active else 'inactive'})"

    def save(self, *args, **kwargs):
        # Ensure only one active QR code exists at a time.
        if self.is_active:
            PaymentQRCode.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
