from django.db import models


class SourceItem(models.Model):
    source = models.ForeignKey("inventory.Source", on_delete=models.DO_NOTHING)
    discontinued = models.BooleanField(default=False)

    item = models.ForeignKey("inventory.item", on_delete=models.DO_NOTHING)
    brand = models.CharField(max_length=255)
    source_category = models.CharField(max_length=255, help_text="probably won't agree with Item.category")
    unit_size = models.ForeignKey("inventory.UnitSize", on_delete=models.CASCADE, null=True)
    active = models.BooleanField(
        default=True, help_text="Products sometimes change their packaging.  This option allows the unit size to remain"
                                " tied to the source item but no longer selectable.")

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
    item_number = models.CharField(
        max_length=255, null=False, blank=True, default="",
        help_text="The main number/code used to identify this product at this source for this unit size.")
    extra_number = models.CharField(
        max_length=255, null=False, blank=True, default="",
        help_text="Some sources have a second identifying number/code.")

    def __str__(self):
        return self.common_name or self.expanded_name or self.cryptic_name
