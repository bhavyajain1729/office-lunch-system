"""
Seeds a small catalog of menu items and publishes today's daily menu,
so the app is immediately usable after a fresh install.

Usage:
    python manage.py seed_demo_data
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from menu.models import DailyMenu, DailyMenuItem, MenuItem

User = get_user_model()

SAMPLE_ITEMS = [
    {"name": "Veg Thali", "category": MenuItem.Category.MAIN_COURSE, "price": "90.00", "is_vegetarian": True,
     "description": "Dal, rice, two sabzis, roti, salad and pickle."},
    {"name": "Chicken Biryani", "category": MenuItem.Category.MAIN_COURSE, "price": "140.00", "is_vegetarian": False,
     "description": "Aromatic basmati rice with spiced chicken, served with raita."},
    {"name": "Paneer Butter Masala with Rice", "category": MenuItem.Category.MAIN_COURSE, "price": "110.00", "is_vegetarian": True,
     "description": "Creamy paneer curry served with steamed rice and a side of roti."},
    {"name": "Masala Dosa", "category": MenuItem.Category.BREAKFAST, "price": "60.00", "is_vegetarian": True,
     "description": "Crispy dosa with spiced potato filling, sambar and chutney."},
    {"name": "Samosa (2 pcs)", "category": MenuItem.Category.SNACK, "price": "30.00", "is_vegetarian": True,
     "description": "Crispy fried pastry with a spiced potato-pea filling."},
    {"name": "Sweet Lassi", "category": MenuItem.Category.BEVERAGE, "price": "40.00", "is_vegetarian": True,
     "description": "Chilled, sweetened yogurt drink."},
    {"name": "Masala Chai", "category": MenuItem.Category.BEVERAGE, "price": "15.00", "is_vegetarian": True,
     "description": "Classic spiced Indian tea."},
    {"name": "Gulab Jamun (2 pcs)", "category": MenuItem.Category.DESSERT, "price": "35.00", "is_vegetarian": True,
     "description": "Soft milk-solid dumplings soaked in rose-flavoured sugar syrup."},
]


class Command(BaseCommand):
    help = "Seed sample menu items and publish today's daily menu for demo purposes."

    def handle(self, *args, **options):
        admin_user = User.objects.filter(role=User.Role.ADMIN).first()

        created_items = []
        for data in SAMPLE_ITEMS:
            item, created = MenuItem.objects.get_or_create(
                name=data["name"],
                defaults={
                    "category": data["category"],
                    "price": data["price"],
                    "is_vegetarian": data["is_vegetarian"],
                    "description": data["description"],
                },
            )
            created_items.append(item)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created menu item: {item.name}"))
            else:
                self.stdout.write(f"Menu item already exists: {item.name}")

        today = timezone.localdate()
        daily_menu, created = DailyMenu.objects.get_or_create(
            date=today,
            defaults={"is_published": True, "created_by": admin_user, "notes": "Seeded demo menu"},
        )
        if not created and not daily_menu.is_published:
            daily_menu.is_published = True
            daily_menu.save(update_fields=["is_published"])

        for item in created_items:
            DailyMenuItem.objects.get_or_create(
                daily_menu=daily_menu, menu_item=item,
                defaults={"quantity_available": 50},
            )

        self.stdout.write(self.style.SUCCESS(
            f"Published daily menu for {today} with {len(created_items)} items."
        ))
