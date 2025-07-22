import datetime

from django.db import models

from . import utils


class Item(models.Model):
    name = models.CharField(max_length=255)
    source_item_search_criteria = models.JSONField(
        help_text="overly complicated JSON object used to suggest this item for new source items.", null=True,
        blank=True)
    description = models.TextField(help_text="General description of the item and how it'd likely be used.")
    category = models.ForeignKey(
        "inventory.Category", on_delete=models.DO_NOTHING, related_name="items", related_query_name="items")

    def __str__(self):
        return self.name

    def get_orders(self, duration: datetime.timedelta=None, end_date: datetime.date=None):
        start_date, end_date = utils.calculate_start_and_end_dates(duration=duration, end_date=end_date)
        qs = self.source_items.filter(line_items__order__delivered_date__range=[start_date, end_date])
        qs = qs.annotate(
            delivered_date=models.F("line_items__order__delivered_date"),
            quantity_delivered=models.F("line_items__quantity_delivered"),
            extended_price=models.F("line_items__extended_price"),
            order_id=models.F("line_items__order__id"),
        )
        qs = qs.order_by("-delivered_date")
        return qs

    def total_ordered(self, duration: datetime.timedelta=None, end_date: datetime.date=None) -> dict:
        """

        :param duration: defaults to 1 year.  timedelta()
        :param end_date: defaults to today.  datetime.date
        :return: dict with totals for # of orders, # of packs, $ extended price, # weight
        """
        start_date, end_date = utils.calculate_start_and_end_dates(duration, end_date)

        qs = self.source_items.filter(line_items__order__delivered_date__range=[start_date, end_date])
        qs = qs.aggregate(
            orders=models.Count("line_items__order__id", distinct=True),
            quantity=models.Sum("line_items__quantity_delivered"),
            extended_price=models.Sum("line_items__extended_price"),
            weight=models.Sum("line_items__total_weight"),
        )
        return_value = {
            "start_date": start_date,
            "end_date": end_date,
        }
        return_value.update(qs)
        return return_value
