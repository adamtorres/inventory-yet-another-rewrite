import logging

from django import http, urls
from django.views import generic
from rest_framework import response, views

from .. import models as mp_models


logger = logging.getLogger(__name__)


class IngredientCreateView(generic.CreateView):
    model = mp_models.Ingredient
    fields = ["recipe", "name", "category", "unit_size", "unit_amount"]

    def get_initial(self):
        initial = super().get_initial()
        initial['recipe'] = self.kwargs['recipe_pk']
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipe_pk"] = self.kwargs['recipe_pk']
        return context

    def get_success_url(self):
        if "save_and_add_another" in self.request.POST:
            return urls.reverse("meal_planning:recipe_ingredient_create", args=(self.object.recipe.pk,))
        return urls.reverse("meal_planning:recipe_detail", args=(self.object.recipe.pk,))


class IngredientDeleteView(generic.DeleteView):
    model = mp_models.Ingredient

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipe_pk"] = self.kwargs['recipe_pk']
        return context

    def get_success_url(self):
        return urls.reverse("meal_planning:recipe_detail", args=(self.object.recipe.pk,))


class IngredientDetailView(generic.DetailView):
    queryset = mp_models.Ingredient.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipe_pk"] = self.kwargs['recipe_pk']
        return context


class IngredientListView(generic.ListView):
    model = mp_models.Ingredient
    ordering = ["recipe", "category", "name", "unit_size", "unit_amount"]


class IngredientUpdateView(generic.UpdateView):
    model = mp_models.Ingredient
    fields = ["recipe", "name", "category", "unit_size", "unit_amount"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipe_pk"] = self.kwargs['recipe_pk']
        return context

    def get_success_url(self):
        return urls.reverse("meal_planning:recipe_ingredient_detail", args=(self.object.recipe.id, self.object.id,))
