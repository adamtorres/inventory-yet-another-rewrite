import datetime
import logging

from django.db import models


class RecipeMultiplier(models.Model):
    base_multiplier = models.DecimalField(max_digits=9, decimal_places=4)
    comment = models.TextField(blank=True, null=True)

    recipe = models.ForeignKey(
        "meal_planning.Recipe", on_delete=models.CASCADE, related_name="multipliers",
        related_query_name="multipliers")

    def __str__(self):
        return f"{self.recipe.name} x{self.base_multiplier}"

    def average_serving_count(self, serving_size=None):
        return self.serving_counts.average(serving_size)


class IngredientMultiplier(models.Model):
    recipe_multiplier = models.ForeignKey(
        "meal_planning.RecipeMultiplier", on_delete=models.CASCADE, related_name="ingredients",
        related_query_name="ingredients")
    ingredient = models.ForeignKey(
        "meal_planning.Ingredient", on_delete=models.CASCADE, related_name="multipliers",
        related_query_name="multipliers")

    # actual unit_amount is base recipe * RecipeMultiplier
    unit_amount_adjustment = models.DecimalField(
        max_digits=9, decimal_places=4, help_text="If the amount is not linear, use this to make tweaks", default=0)

    def __str__(self):
        new_amount = self.ingredient.unit_amount * self.recipe_multiplier.base_multiplier
        return " ".join([
            str(self.recipe_multiplier),
            self.ingredient.ingredient_group.name,
            self.ingredient.name,
            f"{new_amount}",
            self.ingredient.unit_size,
            f"{self.unit_amount_adjustment}"])
