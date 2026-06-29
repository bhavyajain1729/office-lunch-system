import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MenuItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True)),
                ("category", models.CharField(choices=[("BREAKFAST", "Breakfast"), ("MAIN_COURSE", "Main Course"), ("SNACK", "Snack"), ("BEVERAGE", "Beverage"), ("DESSERT", "Dessert")], default="MAIN_COURSE", max_length=20)),
                ("price", models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0)])),
                ("is_vegetarian", models.BooleanField(default=True)),
                ("image", models.ImageField(blank=True, null=True, upload_to="menu_items/")),
                ("is_active", models.BooleanField(default=True, help_text="Inactive items are hidden from the catalog.")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "menu_items",
                "ordering": ["category", "name"],
            },
        ),
        migrations.CreateModel(
            name="DailyMenu",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(unique=True)),
                ("is_published", models.BooleanField(default=False)),
                ("cutoff_time", models.TimeField(blank=True, null=True, help_text="Order cutoff time for this day. Falls back to ORDER_CUTOFF_HOUR setting if blank.")),
                ("notes", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_daily_menus", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "daily_menus",
                "ordering": ["-date"],
            },
        ),
        migrations.CreateModel(
            name="DailyMenuItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("price_override", models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ("quantity_available", models.PositiveIntegerField(blank=True, help_text="Leave blank for unlimited quantity.", null=True)),
                ("quantity_ordered", models.PositiveIntegerField(default=0)),
                ("daily_menu", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="menu.dailymenu")),
                ("menu_item", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="daily_listings", to="menu.menuitem")),
            ],
            options={
                "db_table": "daily_menu_items",
                "ordering": ["menu_item__category", "menu_item__name"],
            },
        ),
        migrations.AlterUniqueTogether(
            name="dailymenuitem",
            unique_together={("daily_menu", "menu_item")},
        ),
    ]
