import datetime
import typing

from django.db import models
from django.db.models import functions


class OrderManager(models.Manager):
    @staticmethod
    def _annotations_for_totals():
        return {
            # per_weight_price
            "order_extended_price": models.Sum("line_items__extended_price"),
            "order_tax": models.Sum("line_items__tax"),
            "order_line_item_count": models.Count("line_items__id"),
            # TODO: Account for backorders or out of stock items. https://github.com/adamtorres/inventory-yet-another-rewrite/issues/35
            "order_rejected_price": models.Sum(models.Case(
                models.When(
                    models.Q(line_items__rejected=True),
                    models.F("line_items__extended_price") + models.F("line_items__tax")),
                default=models.Value(0),
                output_field=models.DecimalField(max_digits=10, decimal_places=4)
            )),
            "order_damaged_price": models.Sum(models.Case(
                models.When(
                    models.Q(line_items__damaged=True),
                    models.F("line_items__extended_price") + models.F("line_items__tax")),
                default=models.Value(0),
                output_field=models.DecimalField(max_digits=10, decimal_places=4)
            )),
        }

    def get_stats(self) -> dict[str, typing.Any]:
        order_stats = self.aggregate(
            order_count=models.Count("id"),
            first_delivered_date=models.Min("delivered_date"),
            last_delivered_date=models.Max("delivered_date"),
        )
        order_totals = self.totals()
        order_totals_stats = order_totals.aggregate(
            total_extended_price=models.Sum("order_extended_price"),
            total_tax=models.Sum("order_tax"),
            total_line_item_count=models.Sum("order_line_item_count"),
            total_rejected_price=models.Sum("order_rejected_price"),
            total_damaged_price=models.Sum("order_damaged_price"),
        )
        order_stats.update(order_totals_stats)
        return order_stats

    def totals(self):
        """
        Digs through Order.line_items for totals and counts
        :return:
        """
        qs = self.values("id", "order_number", "delivered_date", "source__name")
        qs = qs.annotate(**self._annotations_for_totals())
        qs = qs.order_by("delivered_date", "source__name")
        return qs

    def totals_by_month(self, since_date: datetime.date=None):
        # This keeps wanting to group by Order.id
        qs = self.annotate(delivered_month=functions.TruncMonth("delivered_date"))
        if since_date:
            qs = qs.filter(delivered_month__gte=since_date.replace(day=1))
        annotations_for_totals = self._annotations_for_totals()
        qs = qs.annotate(**annotations_for_totals)
        qs = qs.values("delivered_month", *annotations_for_totals.keys())
        qs = qs.order_by("delivered_month")
        return qs


class Order(models.Model):
    source = models.ForeignKey(
        "inventory.Source", on_delete=models.DO_NOTHING, related_name="orders", related_query_name="orders")
    delivered_date = models.DateField()
    order_number = models.CharField(max_length=1024, blank=True, default="")
    po_text = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(
        help_text="Is there anything noteworthy about this order but not a specific item?", blank=True, default="")
    # TODO: Add calculated fields for totals - definitely $ but item count?
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, editable=False)
    modified = models.DateTimeField(auto_now=True, null=False, blank=False, editable=False)

    objects = OrderManager()

    def __str__(self):
        return f"{self.source} - {self.delivered_date} - {self.order_number}"

    def get_next_line_item_number(self):
        return (
            self.line_items.all().aggregate(max_line_item_number=models.Max("line_item_number"))['max_line_item_number']
            or 0
        ) + 1
