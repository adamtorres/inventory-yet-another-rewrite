import datetime
from typing import Any

from django.db import models
from django.db.models import functions


class SourceManager(models.Manager):
    @staticmethod
    def _add_annotations_for_order_totals(qs: models.QuerySet) -> tuple[list[str], models.QuerySet]:
        fields_annotated = [
            "order_count", "order_line_item_count", "order_extended_price", "order_tax", "order_rejected_price",
            "order_damaged_price",]
        return fields_annotated, qs.annotate(
            order_count=models.Count("orders__id", distinct=True),
            order_line_item_count=models.Count("orders__line_items__id", distinct=True),
            order_extended_price=models.Sum("orders__line_items__extended_price"),
            order_tax=models.Sum("orders__line_items__tax"),
            order_rejected_price=models.Sum(models.Case(
                models.When(
                    models.Q(orders__line_items__rejected=True),
                    models.F("orders__line_items__extended_price") + models.F("orders__line_items__tax")),
                default=models.Value(0),
                output_field=models.DecimalField(max_digits=10, decimal_places=4)
            )),
            order_damaged_price=models.Sum(models.Case(
                models.When(
                    models.Q(orders__line_items__damaged=True),
                    models.F("orders__line_items__extended_price") + models.F("orders__line_items__tax")),
                default=models.Value(0),
                output_field=models.DecimalField(max_digits=10, decimal_places=4)
            )),
        )

    def active(self):
        return self.filter(active=True)

    def order_totals(self):
        _, qs = self._add_annotations_for_order_totals(self.values("id", "name"))
        return qs.order_by("name")

    def order_totals_by_month(self, since_date: datetime.date=None):
        qs = self.annotate(order_month=functions.TruncMonth("orders__delivered_date"))
        if since_date:
            qs = qs.filter(order_month__gte=since_date.replace(day=1))
        qs = qs.values("id", "name", "order_month")
        fields_annotated, qs = self._add_annotations_for_order_totals(qs)
        qs = qs.values("id", "name", "order_month", *fields_annotated)
        return qs.order_by("name", "order_month")


class Source(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    customer_number = models.JSONField(default=list, blank=True, null=True, help_text=(
        "List of customer numbers for this source.  Cannot have a Source per customer number as that would duplicate "
        "the crap out of SourceItems."))

    objects = SourceManager()

    def __str__(self):
        return self.name
