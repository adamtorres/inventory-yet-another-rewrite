import datetime
import typing

import dateparser
from django.db import models


class ItemUsageManager(models.Manager):
    def get_for_date(
            self, for_date: datetime.date, for_date_last: typing.Union[None, datetime.date] = None,
            exclude_recorded=False):
        if for_date_last:
            kwargs = {"for_date__range": [min(for_date, for_date_last), max(for_date, for_date_last)]}
        else:
            kwargs = {"for_date": for_date}
        if exclude_recorded:
            kwargs["recorded_date__isnull"] = True
        return self.filter(**kwargs).order_by("usage_group__start_date")

    def get_recorded_date(
            self, recorded_date: datetime.date, recorded_date_last: typing.Union[None, datetime.date] = None):
        if recorded_date_last:
            kwargs = {
                "recorded_date__range": [
                    min(recorded_date, recorded_date_last), max(recorded_date, recorded_date_last)]}
        else:
            kwargs = {"recorded_date": recorded_date}
        return self.filter(**kwargs).order_by("usage_group__start_date")

    def total_for_date(
            self, for_date: datetime.date, for_date_last: typing.Union[None, datetime.date] = None,
            exclude_recorded=False):
        qs = self.get_for_date(for_date, for_date_last=for_date_last, exclude_recorded=exclude_recorded)
        qs = qs.aggregate(
            count=models.Count("for_date", distinct=True),
            first_date=models.Min("for_date"),
            last_date=models.Max("for_date"),
            total=models.Sum("price"),
        )
        return qs

    def total_recorded_date(
            self, recorded_date: datetime.date, recorded_date_last: typing.Union[None, datetime.date] = None):
        qs = self.get_recorded_date(recorded_date, recorded_date_last=recorded_date_last)
        qs = qs.aggregate(
            count=models.Count("for_date", distinct=True),
            first_date=models.Min("for_date"),
            last_date=models.Max("for_date"),
            total=models.Sum("price"),
        )
        return qs

    def group_by_for_date(
            self, for_date: datetime.date, for_date_last: typing.Union[None, datetime.date] = None,
            exclude_recorded=False):
        qs = self.get_for_date(for_date, for_date_last=for_date_last, exclude_recorded=exclude_recorded).order_by()
        qs = qs.values("for_date").annotate(
            count=models.Count("for_date"),
            total=models.Sum("price"),
        )
        return qs

    def group_by_for_date_and_category(
            self, for_date: datetime.date, for_date_last: typing.Union[None, datetime.date] = None,
            exclude_recorded=False):
        qs = self.get_for_date(for_date, for_date_last=for_date_last, exclude_recorded=exclude_recorded).order_by()
        qs = qs.values("for_date", "category").annotate(
            count=models.Count("for_date"),
            total=models.Sum("price"),
        )
        return qs

    def group_by_recorded_date(
            self, recorded_date: datetime.date, recorded_date_last: typing.Union[None, datetime.date] = None):
        qs = self.get_recorded_date(recorded_date, recorded_date_last=recorded_date_last).order_by()
        overall_qs = qs.values("recorded_date").annotate(
            count=models.Count("for_date", distinct=True),
            total=models.Sum("price"),
        )
        by_category_qs = qs.values("recorded_date", "category").annotate(
            total=models.Sum("price"),
            count=models.Count("for_date", distinct=True),
            first_date=models.Min("for_date"),
            last_date=models.Max("for_date"),
        )
        qs = {
            "overall": overall_qs,
            "categories": by_category_qs,
        }
        return qs

    def mark_as_recorded(self, start_date: datetime.date, end_date: datetime.date):
        qs = self.get_for_date(start_date, end_date, exclude_recorded=True)
        today = datetime.date.today()
        qs.update(recorded_date=today)


class ItemUsage(models.Model):
    NO_SPECIFIC_DAY = "_"
    WEDNESDAY = "W"
    THURSDAY = "T"
    FRIDAY = "F"
    NEXT_WEDNESDAY = "NW"
    NEXT_THURSDAY = "NT"
    NEXT_FRIDAY = "NF"
    OTHER = "O"
    FOR_DOW_CHOICES = {
        NO_SPECIFIC_DAY: "No Specific Day",
        WEDNESDAY: "Wednesday",
        THURSDAY: "Thursday",
        FRIDAY: "Friday",
        NEXT_WEDNESDAY:  "Next Wednesday",
        NEXT_THURSDAY:  "Next Thursday",
        NEXT_FRIDAY:  "Next Friday",
        OTHER: "Other",
    }
    FOR_DOW_TO_OFFSET = {
        WEDNESDAY: 2,
        THURSDAY: 3,
        FRIDAY: 4,
        NEXT_WEDNESDAY: 9,
        NEXT_THURSDAY: 10,
        NEXT_FRIDAY: 11,
    }

    CONGREGATE = "congregate"
    BAKERY = "bakery"
    NONFOOD = "nonfood"
    OTHER = "other"
    CATEGORY_CHOICES = {
        CONGREGATE: "Congregate",
        BAKERY: "Bakery",
        NONFOOD: "Nonfood",
        OTHER: "Other",
    }

    ENTREE = "entree"
    SIDE = "side"
    DESSERT = "dessert"
    BREAD = "bread"
    MEAL_PART_CHOICES = {
        ENTREE: "Entree",
        SIDE: "Side",
        DESSERT: "Dessert",
        BREAD: "Bread",
        OTHER: "Other",
    }

    usage_group = models.ForeignKey(
        "usage.UsageGroup", on_delete=models.CASCADE, related_name="used_items", related_query_name="used_items")
    for_dow = models.CharField(max_length=1024, choices=FOR_DOW_CHOICES, default=NO_SPECIFIC_DAY, blank=False)
    for_other_dow = models.CharField(max_length=15, help_text="A specific date for when for_dow is 'other'.", null=True, blank=True)
    donated = models.BooleanField(default=False, help_text="Item was donated.  Price is likely 0.")
    estimate = models.BooleanField(default=False, help_text="No accurate price available.  This is a best-guess.")
    price = models.DecimalField(max_digits=9, decimal_places=4, default=0)
    description = models.CharField(max_length=1024, default="", blank=True)
    for_date = models.DateField(blank=True, null=True)
    category = models.CharField(max_length=1024, choices=CATEGORY_CHOICES, default=CONGREGATE, blank=False)
    recorded_date = models.DateField(null=True, blank=True, default=None)
    quantity = models.IntegerField(default=0, help_text="How many on the packages were used")
    used_size = models.CharField(max_length=1024, null=True, blank=True, help_text="The size of each package used")
    comment = models.TextField(null=True, blank=True, help_text="A further description for this specific instance of usage")
    meal_part = models.CharField(max_length=64, choices=MEAL_PART_CHOICES, default=OTHER, blank=False)

    objects = ItemUsageManager()

    def __str__(self):
        _str = ""
        if self.for_dow != self.NO_SPECIFIC_DAY:
            _str += self.FOR_DOW_CHOICES[self.for_dow]
            if self.for_date:
                _str += f"({self.for_date})"
            _str += ": "
        _str += f"${self.price:,.2f}"
        if self.estimate:
            _str += "(estimate)"
        if self.description:
            _str += ": " + self.description
        return _str

    def determine_for_date(self):
        sd_dow = self.usage_group.start_date.weekday()
        monday = self.usage_group.start_date - datetime.timedelta(days=sd_dow)
        if self.for_dow == self.NO_SPECIFIC_DAY:
            # When no date set, pick the start date of the group so these get included on reports.
            return self.usage_group.start_date
        if self.for_dow == self.OTHER:
            # Interpret the for_other_dow as a date.  Raise whatever error needed if the result is not a date object.
            return dateparser.parse(self.for_other_dow).date()
        return monday + datetime.timedelta(days=self.FOR_DOW_TO_OFFSET[self.for_dow])

    def set_for_date(self, commit=True):
        self.for_date = self.determine_for_date()
        if commit:
            self.save()
