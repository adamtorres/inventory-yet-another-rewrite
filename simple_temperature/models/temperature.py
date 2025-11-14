from django.db import models


class TemperatureManager(models.Manager):
    def get_last_event_datetime(self):
        return self.aggregate(
            left_off_at=models.Max("event_datetime"),
            count=models.Count("id"),
        )


class Temperature(models.Model):
    event_datetime = models.DateTimeField()
    fahrenheit = models.DecimalField(max_digits=7, decimal_places=4)
    celsius = models.DecimalField(max_digits=7, decimal_places=4)
    location = models.CharField(max_length=1024, null=True, blank=True)
    raw_data = models.JSONField(null=True, blank=True)
    key_slug = models.CharField(max_length=1024, null=True, blank=True)

    objects = TemperatureManager()

    def __str__(self):
        return f"{self.event_datetime} / {self.location or self.key_slug} / {self.fahrenheit}"
