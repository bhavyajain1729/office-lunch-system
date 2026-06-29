"""
Models for menu management: reusable MenuItem catalog + the DailyMenu
that admins publish each day, which is what employees actually see and
order from.
"""

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class MenuItem(models.Model):
    """A reusable catalog item (e.g. 'Veg Thali', 'Chicken Biryani')."""

    class Category(models.TextChoices):
        BREAKFAST = "BREAKFAST", "Breakfast"
        MAIN_COURSE = "MAIN_COURSE", "Main Course"
        SNACK = "SNACK", "Snack"
        BEVERAGE = "BEVERAGE", "Beverage"
        DESSERT = "DESSERT", "Dessert"

    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.MAIN_COURSE)
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    is_vegetarian = models.BooleanField(default=True)
    image = models.ImageField(upload_to="menu_items/", blank=True, null=True)
    is_active = models.BooleanField(default=True, help_text="Inactive items are hidden from the catalog.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "menu_items"
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.name} (₹{self.price})"


class DailyMenu(models.Model):
    """The set of MenuItems available for ordering on a particular date."""

    date = models.DateField(unique=True)
    is_published = models.BooleanField(default=False)
    cutoff_time = models.TimeField(
        null=True, blank=True,
        help_text="Order cutoff time for this day. Falls back to ORDER_CUTOFF_HOUR setting if blank.",
    )
    notes = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name="created_daily_menus",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "daily_menus"
        ordering = ["-date"]

    def __str__(self):
        return f"Menu for {self.date} ({'published' if self.is_published else 'draft'})"


class DailyMenuItem(models.Model):
    """Join table: which MenuItems + at what price/availability for a given DailyMenu."""

    daily_menu = models.ForeignKey(DailyMenu, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="daily_listings")
    # Allows price override for the day without mutating the master catalog price.
    price_override = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    quantity_available = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Leave blank for unlimited quantity.",
    )
    quantity_ordered = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "daily_menu_items"
        unique_together = ("daily_menu", "menu_item")
        ordering = ["menu_item__category", "menu_item__name"]

    def __str__(self):
        return f"{self.menu_item.name} on {self.daily_menu.date}"

    @property
    def effective_price(self):
        return self.price_override if self.price_override is not None else self.menu_item.price

    @property
    def is_sold_out(self):
        if self.quantity_available is None:
            return False
        return self.quantity_ordered >= self.quantity_available
