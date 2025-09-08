import datetime
import typing

from django.db import models


class UsageGroupManager(models.Manager):
    def get_for_date(
            self, for_date: datetime.date, for_date_last: typing.Union[None, datetime.date] = None,
            exclude_recorded=False):
        if for_date_last:
            kwargs = {"used_items__for_date__range": [min(for_date, for_date_last), max(for_date, for_date_last)]}
        else:
            kwargs = {"used_items__for_date": for_date}
        if exclude_recorded:
            kwargs["used_items__recorded_date__isnull"] = True
        return self.filter(**kwargs).order_by("start_date").distinct()

    def total_by_name(
            self, for_date: datetime.date, for_date_last: typing.Union[None, datetime.date] = None,
            exclude_recorded=False):
        ugs = self.get_for_date(for_date, for_date_last=for_date_last, exclude_recorded=exclude_recorded)
        ugs_ret = []
        for ug in ugs:
            ug_ret = ug.total(exclude_recorded)
            cts = ug.total_by_category(exclude_recorded)
            ug_ret["categories"] = {}
            for ct in cts:
                ug_ret["categories"][ct["category"]] = ct["total"]
            ug_ret["usage_group"] = ug
            ugs_ret.append(ug_ret)
        return ugs_ret


class UsageGroup(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    name_on_form = models.CharField(max_length=1024, default="", blank=True)
    form_order = models.IntegerField(default=0)

    objects = UsageGroupManager()

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        if self.name_on_form:
            return f"{self.name_on_form} {self.start_date} - {self.end_date}"
        return f"{self.start_date} - {self.end_date}"

    # TODO: add grouping on name_on_form and used_item.category
    def total(self, exclude_recorded=False):
        if exclude_recorded:
            kwargs = {"recorded_date__isnull": True}
        else:
            kwargs = {}
        return self.used_items.filter(**kwargs).aggregate(
            total=models.Sum("price"),
            first_date=models.Min("for_date"),
            last_date=models.Max("for_date"),
        )

    def total_by_category(self, exclude_recorded=False):
        if exclude_recorded:
            kwargs = {"recorded_date__isnull": True}
        else:
            kwargs = {}
        return self.used_items.filter(**kwargs).values("category").annotate(
            total=models.Sum("price"),
            first_date=models.Min("for_date"),
            last_date=models.Max("for_date"),
        )
