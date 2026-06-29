import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("menu", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order_date", models.DateField(help_text="The lunch date this order is for.")),
                ("status", models.CharField(choices=[("PENDING_PAYMENT", "Pending Payment"), ("PAYMENT_SUBMITTED", "Payment Submitted"), ("CONFIRMED", "Confirmed"), ("REJECTED", "Rejected"), ("CANCELLED", "Cancelled"), ("COMPLETED", "Completed")], default="PENDING_PAYMENT", max_length=20)),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ("utr_number", models.CharField(blank=True, help_text="UPI transaction reference number entered by the employee after paying.", max_length=50)),
                ("utr_submitted_at", models.DateTimeField(blank=True, null=True)),
                ("payment_verified_at", models.DateTimeField(blank=True, null=True)),
                ("admin_remarks", models.CharField(blank=True, help_text="Reason for rejection, or any note.", max_length=255)),
                ("special_instructions", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("employee", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="orders", to=settings.AUTH_USER_MODEL)),
                ("payment_verified_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="verified_orders", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "orders",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("item_name", models.CharField(max_length=120)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0)])),
                ("quantity", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ("menu_item", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="order_items", to="menu.menuitem")),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="orders.order")),
            ],
            options={
                "db_table": "order_items",
            },
        ),
        migrations.CreateModel(
            name="PaymentQRCode",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("label", models.CharField(default="Office Canteen UPI", max_length=100)),
                ("upi_id", models.CharField(blank=True, max_length=100)),
                ("qr_image", models.ImageField(upload_to="qr/")),
                ("is_active", models.BooleanField(default=True)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("uploaded_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="uploaded_qr_codes", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "payment_qr_codes",
                "ordering": ["-uploaded_at"],
            },
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(fields=["order_date", "status"], name="orders_order_d_a4f7c1_idx"),
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(fields=["employee", "order_date"], name="orders_employe_b2e9a0_idx"),
        ),
    ]
