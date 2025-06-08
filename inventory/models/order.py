from django.db import models


class Order(models.Model):
    source = models.ForeignKey("inventory.Source", on_delete=models.DO_NOTHING)
    delivered_date = models.DateField()
    po_text = models.CharField(max_length=255, null=True, blank=True)
