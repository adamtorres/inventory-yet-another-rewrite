import logging

from django import urls
from django.contrib.sites.models import Site
from django.db import models
import requests


logger = logging.getLogger(__name__)


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

    def get_pricing_data(self):
        ingredient_dict = {}
        for i in self.ingredients.all():
            ingredient_dict[f"{i.name}~{i.category}~{i.unit_size}"] = i
            i.ingredient_price = 0.0
            i.no_pricing_data = True
        ingredient_list = [f"{i.name}~{i.category}~{i.unit_size}" for i in self.ingredients.all()]
        ugly_domain = Site.objects.get_current().domain
        url = f"http://{ugly_domain}{urls.reverse("inventory:api_selected_items")}"
        api_response = requests.get(url, params={"item_category_unit": ingredient_list})
        pricing_data = api_response.json()
        for pd in pricing_data:
            # name, category, other_unit
            i = ingredient_dict[f"{pd["name"]}~{pd["category"]}~{pd["other_unit"]}"]
            i.per_original_unit_price = pd["per_unit_price"]
            i.original_unit_size = pd["unit_size"]
            i.order_date = pd["order_date"]
            i.per_unit_price = pd["per_other_unit_price"]
            logger.critical(f"{pd["name"]}: (float({i.unit_amount})={float(i.unit_amount)}) * {i.per_unit_price}")
            i.ingredient_price = float(i.unit_amount) * i.per_unit_price
            i.no_pricing_data = False
        return list(ingredient_dict.values())
