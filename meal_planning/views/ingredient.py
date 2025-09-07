import logging

from django import http, urls
from django.views import generic
from rest_framework import response, views

from .. import mixins as mp_mixins, models as mp_models


logger = logging.getLogger(__name__)


class IngredientCreateView(mp_mixins.UserAccessMixin, generic.CreateView):
    model = mp_models.Ingredient
    fields = ["ingredient_group", "name", "category", "unit_size", "unit_amount"]

    def get_initial(self):
        # Is done before get_context_data
        initial = super().get_initial()
        recipe = mp_models.Recipe.objects.get(id=self.kwargs['recipe_pk'])
        if recipe.ingredient_groups.count() == 0:
            recipe.ingredient_groups.create(name="default")
        last_ig = recipe.ingredient_groups.all().last()
        initial['ingredient_group'] = last_ig.id
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipe_pk"] = self.kwargs['recipe_pk']
        return context

    def get_success_url(self):
        if "save_and_add_another" in self.request.POST:
            return urls.reverse("meal_planning:recipe_ingredient_create", args=(self.kwargs['recipe_pk'],))
        return urls.reverse("meal_planning:recipe_detail", args=(self.kwargs['recipe_pk'],))


class IngredientDeleteView(mp_mixins.UserAccessMixin, generic.DeleteView):
    model = mp_models.Ingredient

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipe_pk"] = self.kwargs['recipe_pk']
        return context

    def get_success_url(self):
        return urls.reverse("meal_planning:recipe_detail", args=(self.kwargs['recipe_pk'],))


class IngredientDetailView(mp_mixins.UserAccessMixin, generic.DetailView):
    queryset = mp_models.Ingredient.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipe_pk"] = self.kwargs['recipe_pk']
        return context


class IngredientListView(mp_mixins.UserAccessMixin, generic.ListView):
    model = mp_models.Ingredient
    ordering = ["ingredient_group", "category", "name", "unit_size", "unit_amount"]


class IngredientUpdateView(mp_mixins.UserAccessMixin, generic.UpdateView):
    model = mp_models.Ingredient
    fields = ["ingredient_group", "name", "category", "unit_size", "unit_amount"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipe_pk"] = self.kwargs['recipe_pk']
        return context

    def get_success_url(self):
        return urls.reverse("meal_planning:recipe_ingredient_detail", args=(self.kwargs['recipe_pk'], self.object.id,))
