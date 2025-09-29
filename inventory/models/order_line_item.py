import datetime

from django.db import models
from django.db.models import functions

from . import utils


class OrderLineItemManager(models.Manager):
    @staticmethod
    def _annotations_for_totals():
        return {
            # per_weight_price
            "order_count": models.Count("order__id", distinct=True),
            "order_extended_price": models.Sum("extended_price"),
            "order_tax": models.Sum("tax"),
            "order_line_item_count": models.Count("id"),
            # TODO: Account for backorders or out of stock items. https://github.com/adamtorres/inventory-yet-another-rewrite/issues/35
            "order_rejected_price": models.Sum(models.Case(
                models.When(
                    models.Q(rejected=True),
                    models.F("extended_price") + models.F("tax")),
                default=models.Value(0),
                output_field=models.DecimalField(max_digits=10, decimal_places=4)
            )),
            "order_damaged_price": models.Sum(models.Case(
                models.When(
                    models.Q(damaged=True),
                    models.F("extended_price") + models.F("tax")),
                default=models.Value(0),
                output_field=models.DecimalField(max_digits=10, decimal_places=4)
            )),
        }

    def totals_by_month(self, since_date: datetime.date=None):
        qs = self.annotate(delivered_month=functions.TruncMonth("order__delivered_date"))
        if since_date:
            qs = qs.filter(delivered_month__gte=since_date.replace(day=1))
        annotations_for_totals = self._annotations_for_totals()
        qs = qs.values("delivered_month")
        qs = qs.annotate(**annotations_for_totals)
        qs = qs.order_by("-delivered_month")
        return qs

    def totals_by_month_and_source(self, exclude_inactive=False, since_date: datetime.date=None):
        qs = self.annotate(
            delivered_month=functions.TruncMonth("order__delivered_date"),
            order_source_id=models.F("order__source"),
            order_source_name=models.F("order__source__name"),
        )
        if since_date:
            qs = qs.filter(delivered_month__gte=since_date.replace(day=1))
        if exclude_inactive:
            qs = qs.filter(order__source__active=True)
        annotations_for_totals = self._annotations_for_totals()
        qs = qs.values("delivered_month", "order_source_name", "order_source_id")
        qs = qs.annotate(**annotations_for_totals)
        qs = qs.order_by("-delivered_month", "order_source_name")
        return qs

    def pivoted_totals_by_month_and_source(self, exclude_inactive=False, since_date: datetime.date=None):
        from .source import Source
        totals_by_month_and_source = self.totals_by_month_and_source(
            exclude_inactive=exclude_inactive, since_date=since_date)
        column_header = [f"{s.name}|{s.id}" for s in Source.objects.all().order_by("name")]
        pivoted_order_totals = utils.pivot(
            totals_by_month_and_source, "delivered_month", ["order_source_name", "order_source_id"], column_header)
        return column_header, pivoted_order_totals


class OrderLineItem(models.Model):
    order = models.ForeignKey(
        "inventory.Order", on_delete=models.CASCADE, related_name="line_items", related_query_name="line_items")
    source_item = models.ForeignKey(
        "inventory.SourceItem", on_delete=models.DO_NOTHING, related_query_name="line_items",
        related_name="line_items")

    line_item_number = models.IntegerField(default=0, help_text="the ordering on the invoice")

    quantity_ordered = models.IntegerField(default=1)
    quantity_delivered = models.IntegerField(default=0)
    remote_stock = models.BooleanField(default=False)
    expect_backorder_delivery = models.BooleanField(
        default=False, help_text="Sysco substitutes out-of-stock items.  GemState sends them later.")

    per_pack_price = models.DecimalField(max_digits=9, decimal_places=4)
    extended_price = models.DecimalField(max_digits=9, decimal_places=4)
    tax = models.DecimalField(max_digits=9, decimal_places=4, default=0)
    per_weight_price = models.DecimalField(max_digits=9, decimal_places=4, blank=True, null=True)

    per_pack_weights = models.JSONField(default=list, blank=True, null=True)
    # pg_fields.ArrayField(models.DecimalField(max_digits=8, decimal_places=4), default=list)
    total_weight = models.DecimalField(max_digits=9, decimal_places=4, blank=True, null=True)
    notes = models.TextField(blank=True, default="", help_text="Anything remarkable about this specific item?")
    damaged = models.BooleanField(default=False, help_text="Item damaged but not necessarily sent back.")
    rejected = models.BooleanField(default=False, help_text="Item sent back because of damage, incorrect, etc.")
    rejected_reason = models.TextField(null=True, blank=True, help_text="Why was this item sent back?")

    raw_import_data = models.JSONField(
        null=True, blank=True, help_text="Raw JSON data that contributed to this object's creation.")

    objects = OrderLineItemManager()

    class Meta:
        ordering = ["-order__delivered_date", "order__source", "line_item_number"]

    def __str__(self):
        return f"{self.line_item_number} {self.quantity_ordered}x {self.source_item}"

    @property
    def per_unit_price(self):
        try:
            # pack = 6x #10 cans.  quantity = 6, unit_amount = 1, subunit_amount = None
            # pack = 1x 50lb APF.  quantity = 1, unit_amount = 50, subunit_amount = None
            # pack = 6x 5lb tubs of pb.  quantity = 6, unit_amount = 5, subunit_amount = None
            # pack = 6x 8pk pudding cups.  quantity 6, unit_amount = 8, subunit_amount = 3oz
            tmp_val = self.per_pack_price / self.source_item.quantity
            print(f"OLI.per_unit_price: tmp_val({tmp_val}) = per_pack_price({self.per_pack_price}) / source_item.quantity({self.source_item.quantity})")
            if not self.source_item.unit_amount:
                print(f"OLI.per_unit_price: no unit_amount. Using tmp_val = '{tmp_val}'")
                return tmp_val
            print(
                f"OLI.per_unit_price: tmp_val({tmp_val / self.source_item.unit_amount}) = tmp_val({tmp_val}) / "
                f"source_item.unit_amount({self.source_item.unit_amount})")
            tmp_val /= self.source_item.unit_amount
            if not self.source_item.subunit_amount:
                print(f"OLI.per_unit_price: no subunit_amount. Using tmp_val = '{tmp_val}'")
                return tmp_val
            print(
                f"OLI.per_unit_price: subunit_amount available.  Using {tmp_val / self.source_item.subunit_amount} = "
                f"tmp_val({tmp_val}) / source_item.subunit_amount({self.source_item.subunit_amount})")
            return tmp_val / self.source_item.subunit_amount
        except ZeroDivisionError:
            return 0.0

    # def per_quantity_price(self):
    #     """
    #         pack = 6x #10 cans.  quantity = 6, unit_amount = 1(why? there are 6 #10 cans), subunit_amount = None
    #             returns a single #10 can price
    #         pack = 1x 50lb APF.  quantity = 1, unit_amount = 50, subunit_amount = None
    #             returns a single 50# bag of APF price
    #         pack = 6x 5lb tubs of pb.  quantity = 6, unit_amount = 5, subunit_amount = None
    #             returns a single 5lb tub price
    #         pack = 6x 8pk pudding cups.  quantity 6, unit_amount = 8, subunit_amount = 3oz
    #             returns a single 8pk price
    #
    #     :return:
    #     """
    #     return self.per_pack_price / self.source_item.quantity

    def per_subunitsize_price(self):
        """
            pack = 6x #10 cans.  quantity = 6, unit_amount = 1, subunit_amount = None
                returns None?  per_quantity_price is a #10 can.  what smaller default division is there?
            pack = 1x 50lb APF.  quantity = 1, unit_amount = 50, subunit_amount = None
                returns None?
            pack = 6x 5lb tubs of pb.  quantity = 6, unit_amount = 5, subunit_amount = None
                returns None?
            pack = 6x 8pk pudding cups.  quantity 6, unit_amount = 8, subunit_amount = 3oz
                returns a single oz pudding price

        :return:
        """
        if not self.source_item.subunit_amount:
            return None
        return self.per_unitsize_price() / self.source_item.subunit_amount

    def per_unitsize_price(self):
        """
            pack = 6x #10 cans.  quantity = 6, unit_amount = 1, subunit_amount = None
                returns None?  per_quantity_price is a #10 can.  what smaller default division is there?
            pack = 1x 50lb APF.  quantity = 1, unit_amount = 50, subunit_amount = None
                returns a single pound of APF price
            pack = 6x 5lb tubs of pb.  quantity = 6, unit_amount = 5, subunit_amount = None
                returns a single pound of pb price
            pack = 6x 8pk pudding cups.  quantity 6, unit_amount = 8, subunit_amount = 3oz
                returns a single pudding cup price

        :return:
        """
        if not self.source_item.unit_amount:
            return None
        return self.per_pack_price / self.source_item.unit_amount
