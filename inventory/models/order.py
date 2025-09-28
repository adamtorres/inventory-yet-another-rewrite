import typing

from django.db import models


class OrderManager(models.Manager):
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
        return self.values("id", "order_number", "delivered_date", "source__name").annotate(
            # per_weight_price
            order_extended_price = models.Sum("line_items__extended_price"),
            order_tax = models.Sum("line_items__tax"),
            order_line_item_count=models.Count("line_items__id"),
            # TODO: Account for backorders or out of stock items. https://github.com/adamtorres/inventory-yet-another-rewrite/issues/35
            order_rejected_price=models.Sum(models.Case(
                models.When(
                    models.Q(line_items__rejected=True),
                    models.F("line_items__extended_price")+models.F("line_items__tax")),
                default=models.Value(0),
                output_field=models.DecimalField(max_digits=10, decimal_places=4)
            )),
            order_damaged_price=models.Sum(models.Case(
                models.When(
                    models.Q(line_items__damaged=True),
                    models.F("line_items__extended_price")+models.F("line_items__tax")),
                default=models.Value(0),
                output_field=models.DecimalField(max_digits=10, decimal_places=4)
            )),
        ).order_by("delivered_date", "source__name")


class Order(models.Model):
    source = models.ForeignKey(
        "inventory.Source", on_delete=models.DO_NOTHING, related_name="orders", related_query_name="orders")
    delivered_date = models.DateField()
    order_number = models.CharField(max_length=1024, blank=True, default="")
    po_text = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(help_text="Is there anything noteworthy about this order but not a specific item?", blank=True, default="")
    # TODO: Add calculated fields for totals - definitely $ but item count?

    objects = OrderManager()

    def __str__(self):
        return f"{self.source} - {self.delivered_date} - {self.order_number}"
