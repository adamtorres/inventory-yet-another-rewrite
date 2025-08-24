from django.db import models


class Rating(models.Model):
    recipe = models.ForeignKey(
        "meal_planning.Recipe", on_delete=models.CASCADE, related_name="ratings", related_query_name="ratings")
    value = models.DecimalField(max_digits=3, decimal_places=1, help_text="0=worst, 10=best", null=True, blank=True)
    created = models.DateField(auto_now_add=True)
    comment = models.TextField(blank=True, default="")
