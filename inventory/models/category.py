from django.db import models

from . import utils

class CategoryManager(models.Manager):
    def total_ordered(self, category_names: list[str]=None):
        start_date, end_date = utils.calculate_start_and_end_dates()
        qs = self.filter(items__source_items__line_items__order__delivered_date__range=[start_date, end_date])
        qs = qs.values("id", "name").annotate(
            extended_price=models.Sum("items__source_items__line_items__extended_price"),
            orders=models.Count("items__source_items__line_items__order__id", distinct=True),
        )
        return {
            "start_date": start_date,
            "end_date": end_date,
            "data": qs,
        }


class Category(models.Model):
    name = models.CharField(max_length=255)

    objects = CategoryManager()

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def total_ordered(self):
        start_date, end_date = utils.calculate_start_and_end_dates()
        qs = self.items.filter(source_items__line_items__order__delivered_date__range=[start_date, end_date])
        qs = qs.aggregate(
            extended_price=models.Sum("source_items__line_items__extended_price"),
            orders=models.Count("source_items__line_items__order__id", distinct=True),
        )
        return qs
