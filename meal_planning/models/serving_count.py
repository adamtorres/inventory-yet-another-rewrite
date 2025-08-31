from django.db import models


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
