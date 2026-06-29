"""
Django admin registration for menu models.
"""

from django.contrib import admin

from .models import DailyMenu, DailyMenuItem, MenuItem


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "is_vegetarian", "is_active", "updated_at"]
    list_filter = ["category", "is_vegetarian", "is_active"]
    search_fields = ["name", "description"]


class DailyMenuItemInline(admin.TabularInline):
    model = DailyMenuItem
    extra = 1
    autocomplete_fields = ["menu_item"]


@admin.register(DailyMenu)
class DailyMenuAdmin(admin.ModelAdmin):
    list_display = ["date", "is_published", "cutoff_time", "created_by", "created_at"]
    list_filter = ["is_published", "date"]
    inlines = [DailyMenuItemInline]
    search_fields = ["notes"]
