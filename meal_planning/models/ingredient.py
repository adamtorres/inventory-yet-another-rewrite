from django.db import models


class Ingredient(models.Model):
    recipe = models.ForeignKey(
        "meal_planning.Recipe", on_delete=models.CASCADE, related_name="ingredients",
        related_query_name="ingredients")
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    unit_size = models.CharField(max_length=1024)
    unit_amount = models.DecimalField(max_digits=9, decimal_places=4)
    # TODO: Want to add an ordering to the ingredients. Cannot be automagic since the recipe might be cookie or entree.

    class Meta:
        ordering = ["recipe__name", "category", "name"]

    def __str__(self):
        return f"{self.recipe.name}: {self.name}, {self.unit_amount} {self.unit_size}"
