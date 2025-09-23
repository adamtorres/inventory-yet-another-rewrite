import datetime
from django.db import models

from practice_inventory import utils as pi_utils
from . import utils


class SourceItemManager(models.Manager):
    pass


class SourceItem(models.Model):
    source = models.ForeignKey(
        "inventory.Source", on_delete=models.DO_NOTHING, related_name="source_items", related_query_name="source_items")
    item = models.ForeignKey(
        "inventory.Item", on_delete=models.DO_NOTHING, related_name="source_items", related_query_name="source_items")
    brand = models.CharField(max_length=255)
    source_category = models.CharField(max_length=255, help_text="probably won't agree with Item.category")

    delivered_package_amount = models.DecimalField(max_digits=9, decimal_places=4, null=True, blank=True)
    delivered_package_amount_text = models.CharField(
        max_length=255, null=True, blank=True, help_text="An amount that isn't a single number.  Like '9-12#'.")
    delivered_package_unit_size = models.ForeignKey(
        "inventory.UnitSize", on_delete=models.CASCADE, related_name="l0_items", null=True, blank=True)
    level_one_amount = models.DecimalField(max_digits=9, decimal_places=4, null=True, blank=True)
    level_one_amount_text = models.CharField(
        max_length=255, null=True, blank=True, help_text="An amount that isn't a single number.  Like '9-12#'.")
    level_one_unit_size = models.ForeignKey(
        "inventory.UnitSize", on_delete=models.CASCADE, null=True, blank=True, related_name="l1_items")
    level_two_amount = models.DecimalField(max_digits=9, decimal_places=4, null=True, blank=True)
    level_two_amount_text = models.CharField(
        max_length=255, null=True, blank=True, help_text="An amount that isn't a single number.  Like '9-12#'.")
    level_two_unit_size = models.ForeignKey(
        "inventory.UnitSize", on_delete=models.CASCADE, null=True, blank=True, related_name="l2_items")
    level_three_amount = models.DecimalField(max_digits=9, decimal_places=4, null=True, blank=True)
    level_three_amount_text = models.CharField(
        max_length=255, null=True, blank=True, help_text="An amount that isn't a single number.  Like '9-12#'.")
    level_three_unit_size = models.ForeignKey(
        "inventory.UnitSize", on_delete=models.CASCADE, null=True, blank=True, related_name="l3_items")

    active = models.BooleanField(
        default=True, help_text="Products sometimes change their packaging.  This option allows the unit size to remain"
                                " tied to the source item but no longer selectable.")
    #TODO: This shouldn't be here.  unit_amount is the quantity of unit_size.
    quantity = models.IntegerField(default=1, help_text="How many of the UnitSize is there in this package?")
    allow_split_pack = models.BooleanField(
        default=True,
        help_text="Can this package be split?  As in, '4x 1 gallon' be split and purchase '1x 1 gallon'?")

    cryptic_name = models.CharField(
        max_length=1024, help_text="The horribly abbreviated and truncated name as it appears on the invoice.")
    expanded_name = models.CharField(
        max_length=1024,
        help_text="The horribly abbreviated and truncated name but with as many of the abbreviations and truncations "
                  "fixed.", null=False, blank=True, default="")
    common_name = models.CharField(
        max_length=1024,
        help_text="A more friendly version of the name.  This might be slang we use so not always Item.name",
        null=False, blank=True, default="")

    # Note: Some sources reuse codes.  Not frequently, but it has happened.
    # TODO: How to handle changing codes?  Duplicate SourceItem?  ArrayField/JSONField?
    item_number = models.CharField(
        max_length=255, null=False, blank=True, default="",
        help_text="The main number/code used to identify this product at this source for this unit size.")
    extra_number = models.CharField(
        max_length=255, null=False, blank=True, default="",
        help_text="Some sources have a second identifying number/code.")

    raw_import_data = models.JSONField(
        null=True, blank=True, help_text="Raw JSON data that contributed to this object's creation.")

    objects = SourceItemManager()

    def __str__(self):
        name = self.common_name or self.expanded_name or self.cryptic_name
        return f"{self.source} {name} {self.quantity}x {self.get_unit_size_str()}"

    def get_unit_size_str(self, split_pack: bool=False):
        if not self.delivered_package_unit_size.splittable:
            split_pack = False
        if split_pack:
            tmp = ""
        else:
            tmp = f"{pi_utils.minimal_number(self.delivered_package_amount)}{self.delivered_package_unit_size}"
        if self.level_one_amount:
            tmp += f" {pi_utils.minimal_number(self.level_one_amount)}{self.level_one_unit_size}"
        if self.level_two_amount:
            tmp += f" {pi_utils.minimal_number(self.level_two_amount)}{self.level_two_unit_size}"
        if self.level_three_amount:
            tmp += f" {pi_utils.minimal_number(self.level_three_amount)}{self.level_three_unit_size}"
        return tmp

    def total_ordered(self, duration: datetime.timedelta=None, end_date: datetime.date=None) -> dict:
        """

        :param duration: defaults to 1 year.  timedelta()
        :param end_date: defaults to today.  datetime.date
        :return: dict with totals for # of orders, # of packs, $ extended price, # weight
        """
        start_date, end_date = utils.calculate_start_and_end_dates(duration, end_date)
        qs = self.line_items.filter(order__delivered_date__range=[start_date, end_date])
        qs = qs.aggregate(
            orders=models.Count("order__id", distinct=True),
            quantity=models.Sum("quantity_delivered"),
            extended_price=models.Sum("extended_price"),
            weight=models.Sum("total_weight"),
        )
        return_value = {
            "start_date": start_date,
            "end_date": end_date,
        }
        return_value.update(qs)
        return return_value
