import datetime

import dateparser
from django.db import models


class SettingManager(models.Manager):
    def get_group(self, group_name):
        return {s.name: s.value for s in self.filter(group=group_name).order_by("name")}

    def get_value(self, group, name):
        return self.get(group=group, name=name).value

    def get_report_date_range(self):
        value = self.get_value("report", "date_range")
        if "duration" in value:
            value["duration"] = datetime.datetime.today().date() - dateparser.parse(value["duration"]).date()
        if "end_date" in value:
            value["end_date"] = dateparser.parse(value["end_date"])
        return value


class Setting(models.Model):
    group = models.CharField(max_length=1024)
    name = models.CharField(max_length=1024)
    value = models.JSONField()

    objects = SettingManager()

    class Meta:
        constraints = [models.UniqueConstraint(fields=["group", "name"], name="unique_group_name")]
        ordering = ["group", "name"]

    def __str__(self):
        return f"{self.group} / {self.name}"