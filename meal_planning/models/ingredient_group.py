from django.db import models


class IngredientGroup(models.Model):
    recipe = models.ForeignKey(
        "meal_planning.Recipe", on_delete=models.CASCADE, related_name="ingredient_groups",
        related_query_name="ingredient_groups")
    name = models.CharField(max_length=1024, help_text="Is this for the dough, filling, topping, etc?")

    class Meta:
        ordering = ["recipe__name", "name"]

    def __str__(self):
        return f"{self.recipe.name}: {self.name}"
