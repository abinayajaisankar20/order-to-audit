from decimal import Decimal as D

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from inventory.models import StockMovement, stock_balance
from masters.models import Customer, Item, Supplier

# name, type, base_unit, display_unit, display_factor, rate per BASE unit, opening qty in BASE unit
ITEMS = [
    ("Flour", "RAW", "g", "kg", D("1000"), D("0.042"), D("100000")),
    ("Cooking oil", "RAW", "ml", "L", D("1000"), D("0.140"), D("30000")),
    ("Salt and spice mix", "RAW", "g", "kg", D("1000"), D("0.200"), D("5000")),
    ("200 g pouch", "PACK", "piece", "piece", D("1"), D("2.50"), D("500")),
    ("Carton (20 packets)", "PACK", "piece", "piece", D("1"), D("15"), D("30")),
]

ROLES = {
    "admin": "Admin",
    "salesman_a": "Salesman",
    "salesman_b": "Salesman",
    "production": "Production",
    "auditor": "Auditor",
    "owner": "Owner",
}


class Command(BaseCommand):
    help = "Load the benchmark master data and opening stock (safe to run again)."

    @transaction.atomic
    def handle(self, *args, **options):
        now = timezone.now()

        # Raw and packaging items + opening stock
        for name, itype, base, disp, factor, rate, opening in ITEMS:
            item, _ = Item.objects.update_or_create(
                name=name,
                defaults=dict(item_type=itype, base_unit=base, display_unit=disp,
                              display_factor=factor),
            )
            self._opening(item, opening, rate, now)

        # Finished product
        murukku, _ = Item.objects.update_or_create(
            name="Murukku 200 g",
            defaults=dict(item_type="FG", base_unit="packet", display_unit="packet",
                          display_factor=D("1"), hsn_code="21069099",
                          gst_rate=D("5"), selling_price=D("50")),
        )
        self._opening(murukku, D("50"), D("0"), now)

        # Customers
        Customer.objects.update_or_create(
            name="Retailer A",
            defaults=dict(customer_type="RETAILER", state="Tamil Nadu",
                          gstin="33AAAAA0000A1Z5"),
        )
        Customer.objects.update_or_create(
            name="Distributor B",
            defaults=dict(customer_type="DISTRIBUTOR", state="Karnataka",
                          gstin="29BBBBB0000B1Z5"),
        )
        Supplier.objects.update_or_create(
            name="Flour Supplier", defaults=dict(state="Tamil Nadu"),
        )

        # Roles and test logins
        for group in set(ROLES.values()):
            Group.objects.get_or_create(name=group)
        for username, group in ROLES.items():
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password("test1234")
            user.is_staff = username == "admin"
            user.is_superuser = username == "admin"
            user.save()
            user.groups.set([Group.objects.get(name=group)])

        self.stdout.write(self.style.SUCCESS("Benchmark data loaded."))
        for item in Item.objects.order_by("id"):
            bal = stock_balance(item) / item.display_factor
            self.stdout.write(f"  {item.name}: {bal} {item.display_unit}")

    def _opening(self, item, qty, rate, when):
        """Add the opening-stock ledger row only once."""
        if StockMovement.objects.filter(item=item, movement_type="OPENING").exists():
            return
        StockMovement.objects.create(
            item=item, date=when, qty=qty, rate=rate,
            movement_type="OPENING", source_type="opening", note="Opening stock",
        )