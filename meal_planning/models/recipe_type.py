from django.db import models


class RecipeTypeManager(models.Manager):
    def get_other(self):
        return self.get(name="Other")


class RecipeType(models.Model):
    """
    Entree, Side, Cookie, Dessert, etc
    """
    name = models.CharField(max_length=1024)

    objects = RecipeTypeManager()

    def __str__(self):
        return self.name
