from django.db import models


class GivenDateDetail(models.Model):
    given_date = models.DateField()
    comment = models.TextField()

