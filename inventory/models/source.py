from django.db import models


class Source(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    customer_number = models.CharField(max_length=1024, default="", blank=True)

    def __str__(self):
        return self.name
