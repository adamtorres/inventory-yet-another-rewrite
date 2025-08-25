import logging

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO: reformat the dict so the value is a dict {"ingredients": list, "total": 0.0, "ingredient_group": ig_object}
        context["ingredient_groups_with_price"] = self.object.get_pricing_data_for_groups()
        ig_totals = {}
        recipe_total = 0.0
        for ig_name, ig in context["ingredient_groups_with_price"].items():
            ig_totals[ig_name] = sum([i.ingredient_price for i in ig])
            recipe_total += ig_totals[ig_name]
        context["total_price"] = recipe_total
        return context


class RecipeListView(generic.ListView):
    model = mp_models.Recipe
    fields = ["name"]


class RecipeUpdateView(generic.UpdateView):
    model = mp_models.Recipe
    fields = ["name", "description", "goes_with"]

    def get_success_url(self):
        return urls.reverse("meal_planning:recipe_detail", args=(self.object.id,))
