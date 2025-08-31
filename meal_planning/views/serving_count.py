from django import http, urls
from django.views import generic

from .. import models as mp_models, utils as mp_utils


class ServingCountCreateView(generic.CreateView):
    model = mp_models.ServingCount
    fields = ["recipe", "recipe_multiplier", "date_made", "serving_size", "count"]

    def get_initial(self):
        # Is done before get_context_data
        initial = super().get_initial()
        initial['recipe'] = self.kwargs['recipe_pk']
        initial['recipe_multiplier'] = self.kwargs['multiplier_pk']
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipe_pk"] = self.kwargs['recipe_pk']
        context["multiplier_pk"] = self.kwargs['multiplier_pk']
        return context

    def get_success_url(self):
        return urls.reverse(
            "meal_planning:serving_count_detail", args=(
                self.object.recipe.id, self.object.recipe_multiplier_id, self.object.id))


class ServingCountDetailView(generic.DetailView):
    queryset = mp_models.ServingCount.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipe_pk"] = self.kwargs['recipe_pk']
        context["multiplier_pk"] = self.kwargs['multiplier_pk']
        return context


# TODO: Listing of ServingCount objects on a given multiplier.  Use the average to show on the recipe detail page.
# recipe.serving_counts.average() seems to work on the ServingCounts attached to the recipe.
