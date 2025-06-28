from django.db import models


class UnitSize(models.Model):
    """
    Descriptions of can/bag/box sizes.  This is a discrete model so we don't end up with a variety of sizes all meaning
    the same thing.  ex: "50#", "50 pound", "50lb", "50lbs".
    """
    # description = "#10 can", "15 floz can", "16oz bag", "50lb bag", "5 gallon bucket"
    unit = models.CharField(max_length=1024, help_text="oz, floz, lb, pint, gallon")
    amount = models.DecimalField(
        max_digits=9, decimal_places=4, help_text="the quantity of units.  The '15.5' in '15.5floz'")

    class Meta:
        ordering = ["unit", "amount"]

    def __str__(self):
        _unit = "pk" if self.unit == "subunit" else f" {self.unit}"
        if self.amount:
            return f"{self.amount}{_unit}"
        return _unit.strip()
