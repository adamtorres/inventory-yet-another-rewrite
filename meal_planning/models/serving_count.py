from django.db import models


class ServingCountManager(models.Manager):
    def average(self, serving_size=None):
        """
        Returns the average and most recent date made for the specified serving size.
        If no serving size provided, returns averages for the most recent serving size.
        """
        if not serving_size:
            last_made_date = self.aggregate(last_made=models.Max("date_made"))["last_made"]
            if not last_made_date:
                return {"average": None, "last_made": None}
            last_made_serving_size = self.filter(date_made=last_made_date).first().serving_size
            qs = self.filter(serving_size=last_made_serving_size)
            qs = qs.values("serving_size").annotate(average=models.Avg("count"), last_made=models.Max("date_made"))
            return qs[0]
        return self.filter(serving_size=serving_size).aggregate(
            average=models.Avg("count"), last_made=models.Max("date_made"))


class ServingCount(models.Model):
    """
    Tracks the times a recipe was made and how much it made.
    Ex: 16x Oatmeal Raisin made 433ct on 8/27/25 using the #24 scoop
    """
    recipe = models.ForeignKey(
        "meal_planning.Recipe", on_delete=models.CASCADE, related_name="serving_counts",
        related_query_name="serving_counts")
    recipe_multiplier = models.ForeignKey(
        "meal_planning.RecipeMultiplier", on_delete=models.CASCADE, related_name="serving_counts",
        related_query_name="serving_counts")
    date_made = models.DateField()
    serving_size = models.CharField(max_length=1024, help_text="Describe the scoop used or piece size")
    count = models.DecimalField(max_digits=9, decimal_places=4)

    objects = ServingCountManager()

    def __str__(self):
        return f"{self.recipe_multiplier} / {self.date_made} / {self.serving_size} / {self.count}"
