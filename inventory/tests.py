from decimal import Decimal as D

from django.core.management import call_command
from django.test import TestCase

from inventory.models import StockMovement, stock_balance
from masters.models import Item


class OpeningBalanceTest(TestCase):
    EXPECTED = {
        "Flour": D("100000"),
        "Cooking oil": D("30000"),
        "Salt and spice mix": D("5000"),
        "200 g pouch": D("500"),
        "Carton (20 packets)": D("30"),
        "Murukku 200 g": D("50"),
    }

    def test_opening_balances(self):
        call_command("seed_benchmark")
        for name, qty in self.EXPECTED.items():
            self.assertEqual(stock_balance(Item.objects.get(name=name)), qty, name)

    def test_seed_is_repeatable(self):
        call_command("seed_benchmark")
        call_command("seed_benchmark")
        self.assertEqual(StockMovement.objects.count(), 6)

    def test_ledger_rows_cannot_be_edited(self):
        call_command("seed_benchmark")
        row = StockMovement.objects.first()
        row.qty = D("1")
        with self.assertRaises(ValueError):
            row.save()