import datetime
import logging

from django.db import models

from . import utils


logger = logging.getLogger(__name__)


class ItemManager(models.Manager):
    def ingredients(self):
        return self.filter(category__ingredient=True).order_by("category__name", "name")

    def example_items(self):
        # simplistic way to get some sample data.
        item_filter_data = [
            {"category__name": "canned & dry", "name": "all purpose flour"},
            {"category__name": "canned & dry", "name": "granulated sugar"},
            {"category__name": "canned & dry", "name": "instant dry yeast"},
            {"category__name": "canned & dry", "name": "peanut butter"},
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

    def selected_item_detail(self, item_category_unit_list, as_of_date=None, as_dict=False):
        """
        Converts pricing for a list of items to the requested unit size.

        :param item_category_unit_list: list of tuples (item name, category name, unit to convert to)
        :param as_of_date: If supplied, will be used to limit the most recent order used for pricing.
        :return: list of Item with added fields.  obj.price_in_unit_value=price of the item in the requested unit.
        obj.order_date=the date of the order used for pricing. obj.per_unit_price=price of the item in its natural unit.
        subunit_size=if available, the subunit of the item.  unit_size=unit size of the order used.  to_unit=requested
        unit size.
        """
        criteria = models.Q()
        to_unit_values = {}
        for item_name, category_name, to_unit in item_category_unit_list:
            criteria |= models.Q(category__name=category_name, name=item_name)
            to_unit_values[f"{item_name}~{category_name}"] = to_unit
        if not criteria:
            return self.model.objects.none()
        data = []
        for item in self.filter(criteria):
            to_unit = to_unit_values[f"{item.name}~{item.category.name}"]
            item.add_attrs_for_price_in_unit(to_unit, as_of_date)
            data.append(item)
        if as_dict:
            from .. import serializers as inv_serializers
            return inv_serializers.APISelectedItemSerializer(data, many=True).data
        return data



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
    _latest_order_as_of_date = None

    def __str__(self):
        return self.name

    def add_attrs_for_price_in_unit(self, to_unit=None, as_of_date: datetime.date=None):
        """
        Adds the attributes needed for pricing this item in the specified unit size.

        :param to_unit: str or UnitSize object.
        :param as_of_date: Used to limit pricing to a maximum date.
        :return: Nothing.  Modifies the Item object by adding attributes.
        price_in_unit_value, order_date, per_unit_price, subunit_size, unit_size, to_unit
        """
        self.price_in_unit_value = self.price_in_unit(to_unit, as_of_date=as_of_date)
        self.order_date = self.latest_order(as_of_date=as_of_date).get("order_date")
        self.per_unit_price = self.latest_order(as_of_date=as_of_date).get("per_unit_price")
        if self.latest_order(as_of_date=as_of_date).get("subunit_size"):
            self.subunit_size = self.latest_order(as_of_date=as_of_date)["subunit_size"].unit
        else:
            self.subunit_size = None
        if self.latest_order(as_of_date=as_of_date).get("unit_size"):
            self.unit_size = self.latest_order(as_of_date=as_of_date)["unit_size"].unit
        else:
            self.unit_size = None
        self.to_unit = to_unit

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

    def latest_order(self, as_of_date: datetime.date=None):
        if self._latest_order and (self._latest_order_as_of_date == as_of_date):
            # Called a lot: logger.critical(f"Item.latest_order(as_of_date={as_of_date}) CACHED!")
            return self._latest_order
        if as_of_date:
            qs = self.source_items.filter(line_items__order__delivered_date__lte=as_of_date)
        else:
            qs = self.source_items.all()
        self._latest_order_as_of_date = as_of_date
        qs = qs.filter(line_items__quantity_delivered__gt=0).order_by("-line_items__order__delivered_date")
        latest_source_item = qs.first()
        if not latest_source_item:
            self._latest_order = {
                "item": self,
                "item_name": self.name,
            }
            return self._latest_order
        if as_of_date:
            qs = latest_source_item.line_items.filter(order__delivered_date__lte=as_of_date)
        else:
            qs = latest_source_item.line_items.all()
        qs = qs.filter(quantity_delivered__gt=0).order_by("-order__delivered_date")
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
            # "_per_quantity_price": latest_order_line_item.per_quantity_price(),
            "_per_unitsize_price": latest_order_line_item.per_unitsize_price(),
            "_per_subunitsize_price": latest_order_line_item.per_subunitsize_price(),
            "_sourceitem_quantity": latest_order_line_item.source_item.quantity,
        }
        return self._latest_order

    def price_in_unit(self, to_unit=None, as_of_date: datetime.date=None):
        from .conversion import Conversion
        from .unit_size import UnitSize
        latest_order = self.latest_order(as_of_date=as_of_date)
        from_unit = latest_order.get("unit_size")
        if not from_unit:
            return 0
        if isinstance(to_unit, str):
            try:
                to_unit = UnitSize.objects.get(unit=to_unit)
            except UnitSize.DoesNotExist:
                return 0
        if from_unit == to_unit:
            # No conversion.  Same units.
            return latest_order["per_unit_price"]
        conversion = Conversion.objects.get_conversion(item=self, from_unit=from_unit, to_unit=to_unit)
        if not conversion:
            return 0
        return latest_order["per_unit_price"] * conversion.multiplier
