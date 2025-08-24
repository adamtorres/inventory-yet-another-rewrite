import logging

from django import http, urls
from django.views import generic
from rest_framework import response, views

from .. import models as mp_models


logger = logging.getLogger(__name__)


class IngredientCreateView(generic.CreateView):
    model = mp_models.Ingredient
    fields = ["recipe", "name", "category", "unit_size", "unit_amount"]

    def get_success_url(self):
        return urls.reverse("meal_planning:ingredient_detail", args=(self.object.id,))


class IngredientDeleteView(generic.DeleteView):
    model = mp_models.Ingredient

    def get_success_url(self):
        return urls.reverse("meal_planning:ingredient_list")

class IngredientDetailView(generic.DetailView):
    queryset = mp_models.Ingredient.objects.all()


class IngredientListView(generic.ListView):
    model = mp_models.Ingredient
    ordering = ["recipe", "category", "name", "unit_size", "unit_amount"]


class IngredientUpdateView(generic.UpdateView):
    model = mp_models.Ingredient
    fields = ["recipe", "name", "category", "unit_size", "unit_amount"]

    def get_success_url(self):
        return urls.reverse("meal_planning:ingredient_detail", args=(self.object.id,))
