from django.db import models


class SourceItem(models.Model):
    source = models.ForeignKey("inventory.Source", on_delete=models.DO_NOTHING)
    discontinued = models.BooleanField(default=False)

    # Note: Some sources reuse codes.  Not frequently, but it has happened.
    item_number = models.CharField(
        max_length=255, help_text="The main number/code used to identify this product at this source.", null=False,
        blank=True, default="")
    extra_number = models.CharField(
        max_length=255, help_text="Some sources have a second identifying number/code.", null=False, blank=True,
        default="")

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

    item = models.ForeignKey("inventory.item", on_delete=models.DO_NOTHING)
    brand = models.CharField(max_length=255)
    # pack/size/unit/count options
    source_category = models.CharField(max_length=255, help_text="probably won't agree with Item.category")

    def __str__(self):
        return self.common_name or self.expanded_name or self.cryptic_name
