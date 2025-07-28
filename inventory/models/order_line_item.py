from django.db import models


class OrderLineItem(models.Model):
    order = models.ForeignKey(
        "inventory.Order", on_delete=models.CASCADE, related_name="line_items", related_query_name="line_items")
    source_item = models.ForeignKey(
        "inventory.SourceItem", on_delete=models.DO_NOTHING, related_query_name="line_items",
        related_name="line_items")

    line_item_number = models.IntegerField(default=0, help_text="the ordering on the invoice")

    quantity_ordered = models.IntegerField(default=1)
    quantity_delivered = models.IntegerField(default=0)
    remote_stock = models.BooleanField(default=False)
    expect_backorder_delivery = models.BooleanField(
        default=False, help_text="Sysco substitutes out-of-stock items.  GemState sends them later.")

    per_pack_price = models.DecimalField(max_digits=9, decimal_places=4)
    extended_price = models.DecimalField(max_digits=9, decimal_places=4)
    tax = models.DecimalField(max_digits=9, decimal_places=4, default=0)
    per_weight_price = models.DecimalField(max_digits=9, decimal_places=4, blank=True, null=True)

    per_pack_weights = models.JSONField(default=list, blank=True, null=True)
    # pg_fields.ArrayField(models.DecimalField(max_digits=8, decimal_places=4), default=list)
    total_weight = models.DecimalField(max_digits=9, decimal_places=4, blank=True, null=True)
    notes = models.TextField(blank=True, default="", help_text="Anything remarkable about this specific item?")
    damaged = models.BooleanField(default=False, help_text="Item damaged but not necessarily sent back.")
    rejected = models.BooleanField(default=False, help_text="Item sent back because of damage, incorrect, etc.")
    rejected_reason = models.TextField(null=True, blank=True, help_text="Why was this item sent back?")

    raw_import_data = models.JSONField(
        null=True, blank=True, help_text="Raw JSON data that contributed to this object's creation.")

    class Meta:
        ordering = ["-order__delivered_date", "order__source", "line_item_number"]

    def __str__(self):
        return f"{self.line_item_number} {self.quantity_ordered}x {self.source_item}"

    @property
    def per_unit_price(self):
        try:
            return self.per_pack_price / self.source_item.quantity
        except ZeroDivisionError:
            return 0.0
