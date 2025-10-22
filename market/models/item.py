from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        "market.Category", on_delete=models.SET_NULL, null=True, blank=True, related_name="market_items",
        related_query_name="market_items")
    tags = models.ManyToManyField("market.Tag", related_name="items", related_query_name="items", blank=True)

    # Depends on the size.  A sugar cookie could be a jumbo size.  Is that enough of a change to make a separate item?
    # material_cost_per_item = models.DecimalField(max_digits=9, decimal_places=4, default=0)

    class Meta:
        ordering = ['category__name', 'name']

    def __str__(self):
        return self.name
