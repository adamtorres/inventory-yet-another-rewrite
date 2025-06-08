from django.db import models


class OrderLineItem(models.Model):
    order = models.ForeignKey("inventory.Order", on_delete=models.CASCADE)
    item = models.ForeignKey("inventory.Item", on_delete=models.DO_NOTHING, null=True, blank=True)
    source_item = models.ForeignKey("inventory.SourceItem", on_delete=models.DO_NOTHING)

    quantity_ordered = models.IntegerField(default=1)
    quantity_delivered = models.IntegerField(default=0)
    remote_stock = models.BooleanField(default=False)

    # pack/size/unit/count option chosen
    unit_size = models.CharField(max_length=255)

    per_pack_price = models.DecimalField(max_digits=9, decimal_places=4)
    extended_price = models.DecimalField(max_digits=9, decimal_places=4)
    tax = models.DecimalField(max_digits=9, decimal_places=4)
    per_weight_price = models.DecimalField(max_digits=9, decimal_places=4)

    per_pack_weights = models.DecimalField(max_digits=9, decimal_places=4)
    # pg_fields.ArrayField(models.DecimalField(max_digits=8, decimal_places=4), default=list)
    total_weight = models.DecimalField(max_digits=9, decimal_places=4)