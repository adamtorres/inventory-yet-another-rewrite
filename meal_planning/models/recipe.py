import datetime
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
    # TODO: Add a type field for entree, side, dessert, bread, cookie, cake, other
    # This type would be used to show cookie:dz, 1/2dz pricing.  Or entree:just count pricing, maybe steam table pan?

    objects = RecipeManager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"

    @staticmethod
    def append_pricing_to_dict(pricing_data, ingredient_dict):
        for pd in pricing_data:
            # name, category, other_unit
            i = ingredient_dict[f"{pd["name"]}~{pd["category"]}~{pd["other_unit"]}"]
            i.per_original_unit_price = pd["per_unit_price"]
            i.original_unit_size = pd["unit_size"]
            i.order_date = pd["order_date"]
            i.per_unit_price = pd["per_other_unit_price"]
            logger.critical(f"{pd["name"]}: (float({i.unit_amount})={float(i.unit_amount)}) * {i.per_unit_price}")
            i.ingredient_price = float(i.unit_amount) * i.per_unit_price
            i.no_pricing_data = pd["per_unit_price"] is None

    def average_rating(self):
        avg_value = self.ratings.filter(value__isnull=False).aggregate(avg_value=models.Avg("value"))["avg_value"]
        return avg_value

    def duplicate(self):
        new_recipe = type(self)()

        for field in self._meta.fields:
            if field.primary_key:
                continue  # Skip copying the primary key
            if field.name == "name":
                modified_name = f"{getattr(self, field.name)} (copied on {datetime.date.today()})"
                setattr(new_recipe, field.name, modified_name)
            else:
                setattr(new_recipe, field.name, getattr(self, field.name))
        new_recipe.save()

        for ig in self.ingredient_groups.all():
            new_ig = type(ig)()
            for field in ig._meta.fields:
                if field.primary_key:
                    continue  # Skip copying the primary key
                if field.name == "recipe":
                    new_ig.recipe = new_recipe
                else:
                    setattr(new_ig, field.name, getattr(ig, field.name))
            new_ig.save()
            for i in ig.ingredients.all():
                new_i = type(i)()
                for field in i._meta.fields:
                    if field.primary_key:
                        continue  # Skip copying the primary key
                    if field.name == "ingredient_group":
                        new_i.ingredient_group = new_ig
                    else:
                        setattr(new_i, field.name, getattr(i, field.name))
                new_i.save()
        return new_recipe

    def get_pricing_data(self):
        return self.get_pricing_data_from_qs(self.ingredients.all())

    def get_pricing_data_for_group(self, ingredient_group):
        if isinstance(ingredient_group, str):
            ingredient_group = self.ingredient_groups.get(name=ingredient_group)
        return self.get_pricing_data_from_qs(ingredient_group.ingredients.all())

    def get_pricing_data_for_groups(self, as_of_date: datetime.date=None):
        ingredient_group_pricing = {}
        total = 0.0
        for ingredient_group in self.ingredient_groups.all():
            ingredients = self.get_pricing_data_from_qs(ingredient_group.ingredients.all(), as_of_date=as_of_date)
            ingredient_group_pricing[ingredient_group.name] = {
                "ingredient_group": ingredient_group,
                "ingredients": ingredients,
                "total": sum([i.ingredient_price for i in ingredients]),
            }
            total += ingredient_group_pricing[ingredient_group.name]["total"]
        return ingredient_group_pricing, total

    def get_pricing_data_from_qs(self, ingredient_group_qs, as_of_date: datetime.date=None):
        ingredient_dict = self.prepare_ingredient_dict(ingredient_group_qs)
        pricing_data = self.make_api_call(list(ingredient_dict.keys()), as_of_date=as_of_date)
        self.append_pricing_to_dict(pricing_data, ingredient_dict)
        return list(ingredient_dict.values())

    @staticmethod
    def make_api_call(prepared_ingredient_list, as_of_date: datetime.date=None) -> dict:
        ugly_domain = Site.objects.get_current().domain
        url = f"http://{ugly_domain}{urls.reverse("inventory:api_selected_items")}"
        params = {"item_category_unit": prepared_ingredient_list}
        if as_of_date:
            params["as_of_date"] = as_of_date
        api_response = requests.get(url, params=params)
        return api_response.json()

    @staticmethod
    def prepare_ingredient_dict(qs) -> dict:
        ingredient_dict = {}
        for i in qs:
            ingredient_dict[f"{i.name}~{i.category}~{i.unit_size}"] = i
            i.ingredient_price = 0.0
            i.no_pricing_data = True
        return ingredient_dict
