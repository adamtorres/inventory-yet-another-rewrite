from django import http, urls
from django.views import generic

from .. import models as mp_models


class IngredientGroupCreateView(generic.CreateView):
    model = mp_models.IngredientGroup
    fields = ["recipe", "name"]

    def get_initial(self):
        # Is done before get_context_data
        initial = super().get_initial()
        initial['recipe'] = self.kwargs['recipe_pk']
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipe_pk"] = self.kwargs['recipe_pk']
        return context

    def get_success_url(self):
        return urls.reverse("meal_planning:recipe_detail", args=(self.kwargs['recipe_pk'],))


class IngredientGroupDeleteView(generic.DeleteView):
    model = mp_models.IngredientGroup

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipe_pk"] = self.kwargs['recipe_pk']
        return context

    def get_success_url(self):
        return urls.reverse("meal_planning:recipe_detail", args=(self.object.recipe.pk,))


class IngredientGroupDetailView(generic.DetailView):
    queryset = mp_models.IngredientGroup.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipe_pk"] = self.kwargs['recipe_pk']
        return context


class IngredientGroupListView(generic.ListView):
    model = mp_models.IngredientGroup
    ordering = ["recipe", "name"]


class IngredientGroupUpdateView(generic.UpdateView):
    model = mp_models.IngredientGroup
    fields = ["recipe", "name"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipe_pk"] = self.kwargs['recipe_pk']
        return context

    def get_success_url(self):
        return urls.reverse("meal_planning:recipe_detail", args=(self.object.recipe.id,))
