import datetime
import logging

from django import urls
from django.contrib.sites.models import Site
from django.db import models
import requests

from django.conf import settings


logger = logging.getLogger(__name__)


class RecipeManager(models.Manager):
    pass


class Recipe(models.Model):
    name = models.CharField(max_length=1024)
    description = models.TextField(help_text="General description of this recipe.")
    goes_with = models.TextField(
        help_text="ideas on entrees, sides, or desserts this recipe would normally be paired with")
    recipe_type = models.ForeignKey(
        "meal_planning.RecipeType", on_delete=models.CASCADE, related_name="recipes", related_query_name="recipes")

    objects = RecipeManager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} / {self.recipe_type}"

    def append_pricing_to_dict(self, pricing_data, ingredient_dict):
        multiplier_totals = {
            m.base_multiplier: {"average_serving_count": m.average_serving_count()} for m in self.multipliers.all()}
        for pd in pricing_data:
            # name, category, other_unit
            i = ingredient_dict[f"{pd["name"]}~{pd["category"]}~{pd["other_unit"]}"]
            i.per_original_unit_price = pd["per_unit_price"]
            i.original_unit_size = pd["unit_size"]
            i.order_date = pd["order_date"]
            i.per_unit_price = pd["per_other_unit_price"]
            # logger.critical(f"{pd["name"]}: (float({i.unit_amount})={float(i.unit_amount)}) * {i.per_unit_price}")
            i.ingredient_price = float(i.unit_amount) * float(i.per_unit_price)
            i.no_pricing_data = pd["per_unit_price"] is None
            i.multiplied_bits = []
            for im in i.multipliers.all():
                base_multiplier = im.recipe_multiplier.base_multiplier
                multiplied_ingredient_price = float(i.ingredient_price) * float(base_multiplier)
                adjustment_price = float(i.per_unit_price) * float(im.unit_amount_adjustment)
                adjusted_multiplied_ingredient_price = multiplied_ingredient_price + adjustment_price
                i.multiplied_bits.append({
                    "multiplier": base_multiplier,
                    "ingredient_price": adjusted_multiplied_ingredient_price,
                    "unit_amount": i.unit_amount * base_multiplier + im.unit_amount_adjustment,
                    "adjustment": im.unit_amount_adjustment,
                })
                if i.ingredient_group.name not in multiplier_totals[base_multiplier]:
                    multiplier_totals[base_multiplier][i.ingredient_group.name] = 0.0
                multiplier_totals[base_multiplier][i.ingredient_group.name] += adjusted_multiplied_ingredient_price
        return multiplier_totals

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
        data, _ = self.get_pricing_data_from_qs(self.ingredients.all())
        return data

    def get_pricing_data_for_group(self, ingredient_group):
        if isinstance(ingredient_group, str):
            ingredient_group = self.ingredient_groups.get(name=ingredient_group)
        data, _ = self.get_pricing_data_from_qs(ingredient_group.ingredients.all())
        return data

    def get_pricing_data_for_groups(self, as_of_date: datetime.date=None):
        ingredient_group_pricing = {}
        total = 0.0
        total_per_multiplier = {multiplier.base_multiplier: 0.0 for multiplier in self.multipliers.all().order_by("base_multiplier")}
        for ingredient_group in self.ingredient_groups.all():
            ingredients, multiplier_totals = self.get_pricing_data_from_qs(
                ingredient_group.ingredients.all(), as_of_date=as_of_date)

            ingredient_group_pricing[ingredient_group.name] = {
                "ingredient_group": ingredient_group,
                "ingredients": ingredients,
                "total": sum([i.ingredient_price for i in ingredients]),
                "multiplier_totals": [multiplier_totals[multiplier][ingredient_group.name] for multiplier in sorted(multiplier_totals.keys())],
            }
            # TODO: multiplier_totals[multiplier]["average_serving_count"]
            total += ingredient_group_pricing[ingredient_group.name]["total"]
            for multiplier in multiplier_totals.keys():
                total_per_multiplier[multiplier] += multiplier_totals[multiplier][ingredient_group.name]
        return ingredient_group_pricing, total, total_per_multiplier

    def get_pricing_data_from_qs(self, ingredient_group_qs, as_of_date: datetime.date=None):
        ingredient_dict = self.prepare_ingredient_dict(ingredient_group_qs)
        pricing_data = self.make_api_call(
            [(i.name, i.category, i.unit_size) for i in ingredient_dict.values()], as_of_date=as_of_date)
        multiplier_totals = self.append_pricing_to_dict(pricing_data, ingredient_dict)
        return list(ingredient_dict.values()), multiplier_totals

    @staticmethod
    def make_api_call(prepared_ingredient_list, as_of_date: datetime.date=None) -> dict:
        from inventory import models as inv_models
        return inv_models.Item.objects.selected_item_detail(prepared_ingredient_list, as_of_date, as_dict=True)

    @staticmethod
    def prepare_ingredient_dict(qs) -> dict:
        ingredient_dict = {}
        for i in qs:
            ingredient_dict[f"{i.name}~{i.category}~{i.unit_size}"] = i
            i.ingredient_price = 0.0
            i.no_pricing_data = True
        return ingredient_dict
