from .. import models as mp_models


def add_recipe_multiplier(recipe, base_multiplier):
    new_recipe = mp_models.RecipeMultiplier.objects.create(recipe=recipe, base_multiplier=base_multiplier)
    for ig in recipe.ingredient_groups.all():
        for i in ig.ingredients.all():
            mp_models.IngredientMultiplier.objects.create(recipe_multiplier=new_recipe, ingredient=i)
    return new_recipe
