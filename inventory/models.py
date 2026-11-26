from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models import Sum


class StockMovement(models.Model):
    """The stock ledger. Rows are only ever added, never edited or deleted.
    Stock balance = sum of qty. Corrections are new reversing rows."""

    OPENING = "OPENING"
    PURCHASE = "PURCHASE"
    PRODUCTION_ISSUE = "PRODUCTION_ISSUE"
    PRODUCTION_OUTPUT = "PRODUCTION_OUTPUT"
    WASTAGE = "WASTAGE"
    SALE = "SALE"
    ADJUSTMENT = "ADJUSTMENT"
    TYPES = [
        (OPENING, "Opening stock"),
        (PURCHASE, "Purchase"),
        (PRODUCTION_ISSUE, "Production issue"),
        (PRODUCTION_OUTPUT, "Production output"),
        (WASTAGE, "Wastage / damage"),
        (SALE, "Sale / dispatch"),
        (ADJUSTMENT, "Adjustment"),
    ]

    item = models.ForeignKey("masters.Item", on_delete=models.PROTECT, related_name="movements")
    date = models.DateTimeField()
    # In the item's BASE unit. Positive = stock in, negative = stock out.
    qty = models.DecimalField(max_digits=16, decimal_places=3)
    # Cost per base unit at the time of the movement
    rate = models.DecimalField(max_digits=14, decimal_places=6, default=Decimal("0"))
    movement_type = models.CharField(max_length=20, choices=TYPES)
    # Link back to the source document
    source_type = models.CharField(max_length=30, blank=True)
    source_id = models.PositiveIntegerField(null=True, blank=True)
    note = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "id"]

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValueError("Stock ledger rows cannot be edited. Add a reversing entry instead.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Stock ledger rows cannot be deleted. Add a reversing entry instead.")

    def __str__(self):
        return f"{self.item} {self.qty} ({self.movement_type})"


def stock_balance(item):
    """Current stock of an item in base units, derived from the ledger."""
    total = StockMovement.objects.filter(item=item).aggregate(t=Sum("qty"))["t"]
    return total or Decimal("0")