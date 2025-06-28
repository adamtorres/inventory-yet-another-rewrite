from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=255)
    source_item_search_criteria = models.JSONField(
        help_text="overly complicated JSON object used to suggest this item for new source items.", null=True,
        blank=True)
    description = models.TextField(help_text="General description of the item and how it'd likely be used.")
    category = models.ForeignKey("inventory.Category", on_delete=models.DO_NOTHING)
    unit_size = models.ForeignKey("inventory.UnitSize", on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return self.name
