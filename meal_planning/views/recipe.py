import datetime
import logging

import dateparser
from django import http, urls
from django.views import generic
from rest_framework import response, views

from .. import models as mp_models


logger = logging.getLogger(__name__)


class RecipeCreateView(generic.CreateView):
    model = mp_models.Recipe
    fields = ["name", "description", "goes_with"]

    def get_success_url(self):
        return urls.reverse("meal_planning:recipe_detail", args=(self.object.id,))


class RecipeDeleteView(generic.DeleteView):
    model = mp_models.Recipe

    def get_success_url(self):
        return urls.reverse("meal_planning:recipe_list")


class RecipeDetailView(generic.DetailView):
    queryset = mp_models.Recipe.objects.all()

    def duplicate_object(self):
        new_recipe = type(self.object)()

        for field in self.object._meta.fields:
            if field.primary_key:
                continue  # Skip copying the primary key
            if field.name == "name":
                modified_name = f"{getattr(self.object, field.name)} (copied on {datetime.date.today()})"
                setattr(new_recipe, field.name, modified_name)
            else:
                setattr(new_recipe, field.name, getattr(self.object, field.name))
        new_recipe.save()

        for ig in self.object.ingredient_groups.all():
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        as_of_date = self.request.GET.get("as_of_date")
        if as_of_date:
            as_of_date = dateparser.parse(as_of_date).date()
        context["ingredient_groups_with_price"], recipe_total = self.object.get_pricing_data_for_groups(
            as_of_date=as_of_date)
        context["total_price"] = recipe_total
        context["date_options"] = {
            "6 months ago": datetime.date.today() - datetime.timedelta(days=365*0.5),
            "1 year ago": datetime.date.today() - datetime.timedelta(days=365),
            "1.5 years ago": datetime.date.today() - datetime.timedelta(days=365*1.5),
            "2 years ago": datetime.date.today() - datetime.timedelta(days=365*2),
            "2.5 years ago": datetime.date.today() - datetime.timedelta(days=365*2.5),
            "3 years ago": datetime.date.today() - datetime.timedelta(days=365*3),
            "3.5 years ago": datetime.date.today() - datetime.timedelta(days=365*3.5),
        }
        return context

    @staticmethod
    def get_duplicate_success_url(duplicate_recipe):
        return urls.reverse("meal_planning:recipe_detail", args=(duplicate_recipe.id,))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        duplicate_object = self.duplicate_object()
        return http.HttpResponseRedirect(self.get_duplicate_success_url(duplicate_object))


class RecipeListView(generic.ListView):
    model = mp_models.Recipe
    fields = ["name"]


class RecipeUpdateView(generic.UpdateView):
    model = mp_models.Recipe
    fields = ["name", "description", "goes_with"]

    def get_success_url(self):
        return urls.reverse("meal_planning:recipe_detail", args=(self.object.id,))
