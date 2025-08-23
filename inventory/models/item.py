import datetime
import logging

from django.db import models

from . import utils


logger = logging.getLogger(__name__)


class ItemManager(models.Manager):
    def example_items(self):
        # simplistic way to get some sample data.
        item_filter_data = [
            {"category__name": "canned & dry", "name": "all purpose flour"},
            {"category__name": "canned & dry", "name": "granulated sugar"},
            {"category__name": "canned & dry", "name": "instant dry yeast"},
            {"category__name": "canned & dry", "name": "pork gravy mix"},
            {"category__name": "canned & dry", "name": "pumpkin puree"},
            {"category__name": "canned & dry", "name": "semisweet chocolate chip"},
            {"category__name": "canned & dry", "name": "sliced peach"},
            {"category__name": "canned & dry", "name": "wheat flour"},
            {"category__name": "dairy", "name": "butter"},
            {"category__name": "dairy", "name": "egg"},
            {"category__name": "dairy", "name": "margarine"},
            {"category__name": "meats", "name": "beef bottom round"},
            {"category__name": "meats", "name": "burger patty"},
            {"category__name": "meats", "name": "italian style meatballs"},
            {"category__name": "paper & disposable", "name": "3 compartment foam"},
            {"category__name": "paper & disposable", "name": "saddle pack bag"},
            {"category__name": "paper & disposable", "name": "foil 3 compartment tray"},
            {"category__name": "poultry", "name": "cordon bleu"},
        ]
        criteria = models.Q()
        for ifd in item_filter_data:
            criteria |= models.Q(**ifd)
        return self.filter(criteria)


class Item(models.Model):
    name = models.CharField(max_length=255)
    source_item_search_criteria = models.JSONField(
        help_text="overly complicated JSON object used to suggest this item for new source items.", null=True,
        blank=True)
    description = models.TextField(help_text="General description of the item and how it'd likely be used.")
    category = models.ForeignKey(
        "inventory.Category", on_delete=models.DO_NOTHING, related_name="items", related_query_name="items")

    objects = ItemManager()

    _latest_order = None

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

    def latest_order(self):
        if self._latest_order:
            return self._latest_order
        qs = self.source_items.filter(line_items__quantity_delivered__gt=0).order_by("-line_items__order__delivered_date")
        latest_source_item = qs.first()
        if not latest_source_item:
            self._latest_order = {
                "item": self,
                "item_name": self.name,
            }
            return self._latest_order
        qs = latest_source_item.line_items.filter(quantity_delivered__gt=0).order_by("-order__delivered_date")
        latest_order_line_item = qs.first()
        if not latest_order_line_item:
            self._latest_order = {
                "item": self,
                "source_item": latest_source_item,
                "item_name": self.name,
                "unit_size": latest_source_item.unit_size,
                "subunit_size": latest_source_item.subunit_size,
            }
            return self._latest_order
        self._latest_order = {
            "order": latest_order_line_item.order,
            "order_line_item": latest_order_line_item,
            "source_item": latest_source_item,
            "item": self,

            "order_date": latest_order_line_item.order.delivered_date,
            "item_name": self.name,
            "unit_amount": latest_source_item.unit_amount,
            "unit_size": latest_source_item.unit_size,
            "subunit_amount": latest_source_item.subunit_amount,
            "subunit_size": latest_source_item.subunit_size,
            "extended_price": latest_order_line_item.extended_price,
            "quantity_delivered": latest_order_line_item.quantity_delivered,
            "per_pack_price": latest_order_line_item.per_pack_price,
            "per_unit_price": latest_order_line_item.per_unit_price,
            "per_something_price": latest_order_line_item.per_unit_price / latest_source_item.unit_amount,
        }
        return self._latest_order

    def price_in_unit(self, to_unit=None):
        from .conversion import Conversion
        from .unit_size import UnitSize
        latest_order = self.latest_order()
        from_unit = latest_order["unit_size"]
        if isinstance(to_unit, str):
            to_unit = UnitSize.objects.get(unit=to_unit)
        conversion = Conversion.objects.get_conversion(item=self, from_unit=from_unit, to_unit=to_unit)
        if not conversion:
            return 0
        # logger.critical(f"Item.price_in_unit: from_unit={from_unit}, to_unit={to_unit}")
        # logger.critical(
        #     f"per_unit_price({latest_order["per_unit_price"]}) * conversion.multiplier({conversion.multiplier}) = "
        #     f"{latest_order["per_unit_price"] * conversion.multiplier}")
        # for k, v in latest_order.items():
        #     logger.critical(f"latest_order[{k}] = {v!r}")
        return latest_order["per_unit_price"] * conversion.multiplier
