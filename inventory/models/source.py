from django.db import models


class Source(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    customer_number = models.JSONField(default=list, blank=True, null=True, help_text=(
        "List of customer numbers for this source.  Cannot have a Source per customer number as that would duplicate "
        "the crap out of SourceItems."))

    def __str__(self):
        return self.name
