from django import http, urls
from django.views import generic

from .. import models as mp_models, utils as mp_utils
from user import mixins as u_mixins


class RecipeMultiplierDeleteView(u_mixins.UserAccessMixin, generic.DeleteView):
    model = mp_models.RecipeMultiplier

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipe_pk"] = self.kwargs['recipe_pk']
        return context

    def get_success_url(self):
        return urls.reverse("meal_planning:recipe_detail", args=(self.kwargs['recipe_pk'],))


class RecipeMultiplierDetailView(u_mixins.UserAccessMixin, generic.DetailView):
    queryset = mp_models.RecipeMultiplier.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipe_pk"] = self.kwargs['recipe_pk']
        return context


class RecipeMultiplierUpdateView(u_mixins.UserAccessMixin, generic.UpdateView):
    model = mp_models.RecipeMultiplier
    fields = ["base_multiplier", "comment"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipe_pk"] = self.kwargs['recipe_pk']
        return context

    def get_success_url(self):
        return urls.reverse("meal_planning:recipe_multiplier_detail", args=(self.object.recipe.id, self.object.id,))

