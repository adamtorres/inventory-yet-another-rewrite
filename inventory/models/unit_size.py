from django.db import models


class UnitSize(models.Model):
    """
    Descriptions of can/bag/box sizes.  This is a discrete model so we don't end up with a variety of sizes all meaning
    the same thing.  ex: "50#", "50 pound", "50lb", "50lbs".
    """
    # description = "#10 can", "15 floz can", "16oz bag", "50lb bag", "5 gallon bucket"
    unit = models.CharField(max_length=1024, help_text="oz, floz, lb, pint, gallon")
    # TODO: split `unit` into `name` and `abbr`?

    class Meta:
        ordering = ["unit"]

    def __str__(self):
        return "pk" if self.unit == "subunit" else self.unit

    @property
    def splittable(self):
        return self.unit == "count"
