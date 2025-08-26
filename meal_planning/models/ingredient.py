from django.db import models


class Ingredient(models.Model):
    recipe = models.ForeignKey(
        "meal_planning.Recipe", on_delete=models.CASCADE, related_name="ingredients",
        related_query_name="ingredients", null=True, blank=True)
    ingredient_group = models.ForeignKey(
        "meal_planning.IngredientGroup", on_delete=models.CASCADE, related_name="ingredients",
        related_query_name="ingredients", null=True, blank=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    unit_size = models.CharField(max_length=1024)
    unit_amount = models.DecimalField(max_digits=9, decimal_places=4)
    # TODO: Want to add an ordering to the ingredients. Cannot be automagic since the recipe might be cookie or entree.

    class Meta:
        ordering = ["ingredient_group__recipe__name", "ingredient_group__name", "category", "name"]

    def __str__(self):
        if self.ingredient_group:
            return f"{self.ingredient_group.recipe.name}: {self.ingredient_group.name}: {self.name}, {self.unit_amount} {self.unit_size}"
        return f"?: {self.name}, {self.unit_amount} {self.unit_size}"
