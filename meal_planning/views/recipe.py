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


class RecipeListView(generic.ListView):
    model = mp_models.Recipe
    fields = ["name"]


class RecipeUpdateView(generic.UpdateView):
    model = mp_models.Recipe
    fields = ["name", "description", "goes_with"]

    def get_success_url(self):
        return urls.reverse("meal_planning:recipe_detail", args=(self.object.id,))
