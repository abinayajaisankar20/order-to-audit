from decimal import Decimal
from django.db import models


class Item(models.Model):
    RAW = "RAW"
    PACK = "PACK"
    FG = "FG"
    ITEM_TYPES = [
        (RAW, "Raw material"),
        (PACK, "Packaging material"),
        (FG, "Finished goods"),
    ]

    name = models.CharField(max_length=100, unique=True)
    item_type = models.CharField(max_length=4, choices=ITEM_TYPES)
    # Stock is always stored in this base unit: g, ml, piece
    base_unit = models.CharField(max_length=10)
    # Unit shown to users: kg, L, piece. 1 display unit = factor base units
    display_unit = models.CharField(max_length=10)
    display_factor = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal("1"))
    hsn_code = models.CharField(max_length=10, blank=True)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    reorder_level = models.DecimalField(max_digits=14, decimal_places=3, default=Decimal("0"))

    def __str__(self):
        return self.name


class Customer(models.Model):
    RETAILER = "RETAILER"
    DISTRIBUTOR = "DISTRIBUTOR"
    TYPES = [(RETAILER, "Retailer"), (DISTRIBUTOR, "Distributor")]

    name = models.CharField(max_length=150, unique=True)
    customer_type = models.CharField(max_length=12, choices=TYPES, default=RETAILER)
    gstin = models.CharField(max_length=15, blank=True)
    state = models.CharField(max_length=50)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=150, unique=True)
    gstin = models.CharField(max_length=15, blank=True)
    state = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.name