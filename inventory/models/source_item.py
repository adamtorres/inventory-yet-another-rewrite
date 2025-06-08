from django.db import models


class SourceItem(models.Model):
    source = models.ForeignKey("inventory.Source", on_delete=models.DO_NOTHING)
    discontinued = models.BooleanField(default=False)
    item = models.ForeignKey("inventory.item", on_delete=models.DO_NOTHING)
    brand = models.CharField(max_length=255)
    # pack/size/unit/count options
    source_category = models.CharField(max_length=255, help_text="probably won't agree with Item.category")
