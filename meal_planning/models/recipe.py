from django.db import models


class RecipeManager(models.Manager):
    pass


class Recipe(models.Model):
    name = models.CharField(max_length=1024)
    description = models.TextField(help_text="General description of this recipe.")
    goes_with = models.TextField(
        help_text="ideas on entrees, sides, or desserts this recipe would normally be paired with")
    # TODO: Add a type field for entree, side, dessert, bread, other

    objects = RecipeManager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"

    def average_rating(self):
        avg_value = self.ratings.filter(value__isnull=False).aggregate(avg_value=models.Avg("value"))["avg_value"]
        return avg_value
