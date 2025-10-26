import decimal

from django.db import models

from ..utils import units


class OrderLineItem(models.Model):
    order = models.ForeignKey(
        "market.Order", on_delete=models.CASCADE, related_name="line_items", related_query_name="line_items")
    line_item_position = models.IntegerField(default=0)

    item = models.ForeignKey("market.Item", on_delete=models.SET_NULL, null=True)
    item_str = models.CharField(
        max_length=100, blank=True, null=True, help_text="Backup of str(item) in case the item is deleted.")
    quantity = models.IntegerField()
    pack_quantity = models.IntegerField(help_text="count per bag/plate.", default=12)
    sale_price_per_pack = models.DecimalField(max_digits=9, decimal_places=4)
    sale_price = models.DecimalField(max_digits=9, decimal_places=4, default=0)
    material_cost_per_pack = models.DecimalField(max_digits=9, decimal_places=4, blank=True, default=0, help_text="cost of materials for a single pack.")
    material_cost = models.DecimalField(max_digits=9, decimal_places=4, blank=True, default=0, help_text="cost of materials for the order.")

    class Meta:
        ordering = ['order', 'line_item_position']

    def __str__(self):
        # TODO: save a local copy of item str so it doesn't hit the db again and in case item changes.
        return f"{units.reduce_quantity_by_pack(self.quantity, self.pack_quantity)} {self.item or self.item_str}"

    def calculate_totals(self, commit=True):
        if self.item:
            # TODO: Item.material_cost_per_item does not exist at this time.
            material_cost_per_pack = decimal.Decimal("0")
        else:
            # The Item was removed after this order was created.  Do not change the cost.
            material_cost_per_pack = self.material_cost_per_pack
        material_cost = material_cost_per_pack * decimal.Decimal(self.quantity)
        sale_price = self.sale_price_per_pack * decimal.Decimal(self.quantity / self.pack_quantity)
        needs_saved = False
        if self.material_cost_per_pack != material_cost_per_pack:
            self.material_cost_per_pack = material_cost_per_pack
            needs_saved = True
        if self.material_cost != material_cost:
            self.material_cost = material_cost
            needs_saved = True
        if self.sale_price != sale_price:
            self.sale_price = sale_price
            needs_saved = True
        if commit and needs_saved:
            self.save()

    def item_name(self):
        return f"{self.item or self.item_str}"

    def pack_quantity_str(self):
        return units.humanize_pack_quantity(self.pack_quantity)

    def quantity_str(self):
        return f"{units.reduce_quantity_by_pack(self.quantity, self.pack_quantity)}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.item:
            item_str = str(self.item)
            if self.item_str != item_str:
                self.item_str = item_str
                if update_fields is not None:
                    update_fields.add('item_str')
        return super().save(
            force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
