from django.db import models


class ConversionManager(models.Manager):
    def get_conversion(self, item=None, from_unit=None, to_unit=None):
        kwargs = {
            "from_unit": from_unit,
            "to_unit": to_unit,
        }
        if item:
            kwargs["item"] = item
        else:
            kwargs["item__isnull"] = True
        first_conversion = self.filter(**kwargs).first()
        if item and not first_conversion:
            kwargs["item__isnull"] = True
            del kwargs["item"]
            first_conversion = self.filter(**kwargs).first()
        return first_conversion

"""
cup = UnitSize.objects.get(unit="cup")
ten_can = UnitSize.objects.get(unit="#10 can")
pound = UnitSize.objects.get(unit="lb")
pump_pur = Item.objects.get(name="pumpkin puree")
gran_sugar = Item.objects.get(name="granulated sugar")

Conversion.objects.create(from_unit=ten_can, to_unit=cup, multiplier=0.0833)
Conversion.objects.create(from_unit=cup, to_unit=ten_can, multiplier=12)
Conversion.objects.create(item=gran_sugar, from_unit=pound, to_unit=cup, multiplier=3.7833)
Conversion.objects.create(item=gran_sugar, from_unit=cup, to_unit=pound, multiplier=0.2643)

pump_pur.price_in_unit(cup) * 12
float(gran_sugar.price_in_unit(cup))*3.78*50
"""

class Conversion(models.Model):
    item = models.ForeignKey(
        "inventory.Item", on_delete=models.CASCADE, related_name="conversions", related_query_name="conversions",
        blank=True, null=True
    )
    from_unit = models.ForeignKey(
        "inventory.UnitSize", on_delete=models.CASCADE, related_name="from_conversions",
        related_query_name="from_conversions")
    to_unit = models.ForeignKey(
        "inventory.UnitSize", on_delete=models.CASCADE, related_name="to_conversions",
        related_query_name="to_conversions")
    multiplier = models.DecimalField(max_digits=9, decimal_places=4, default=1)

    objects = ConversionManager()

    def __str__(self):
        return f"(1 {self.from_unit}) * {self.multiplier} = 1 {self.to_unit}"
