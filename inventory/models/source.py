from django.db import models


class Source(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"name={self.name!r}"
