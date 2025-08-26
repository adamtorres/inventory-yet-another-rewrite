from django.contrib import admin

from . import models as mp_models


admin.site.register(mp_models.Recipe)
admin.site.register(mp_models.Ingredient)
admin.site.register(mp_models.IngredientGroup)
admin.site.register(mp_models.RecipeMultiplier)
admin.site.register(mp_models.IngredientMultiplier)
