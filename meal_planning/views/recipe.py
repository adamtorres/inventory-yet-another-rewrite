import datetime
import logging

import dateparser
from django import http, urls
from django.views import generic
from rest_framework import response, views

from .. import models as mp_models, utils as mp_utils
from user import mixins as u_mixins


logger = logging.getLogger(__name__)


class RecipeCreateView(u_mixins.UserAccessMixin, generic.CreateView):
    model = mp_models.Recipe
    fields = ["name", "description", "goes_with", "recipe_type"]

    def get_success_url(self):
        return urls.reverse("meal_planning:recipe_detail", args=(self.object.id,))


class RecipeDeleteView(u_mixins.UserAccessMixin, generic.DeleteView):
    model = mp_models.Recipe

    def get_success_url(self):
        return urls.reverse("meal_planning:recipe_list")


class RecipeDetailView(u_mixins.UserAccessMixin, generic.DetailView):
    queryset = mp_models.Recipe.objects.all()

    def duplicate_recipe(self):
        duplicate_object = self.object.duplicate()
        return http.HttpResponseRedirect(self.get_object_url(duplicate_object))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        as_of_date = self.request.GET.get("as_of_date")
        if as_of_date:
            as_of_date = dateparser.parse(as_of_date).date()
        context["ingredient_groups_with_price"], recipe_total, multiplier_totals = (
            self.object.get_pricing_data_for_groups(as_of_date=as_of_date))
        context["total_price"] = recipe_total
        context["multiplier_totals"] = multiplier_totals
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
    def get_object_url(duplicate_recipe):
        return urls.reverse("meal_planning:recipe_detail", args=(duplicate_recipe.id,))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.POST.get("duplicate"):
            return self.duplicate_recipe()
        if request.POST.get("multiply"):
            base_multiplier_str = request.POST.get("base_multiplier")
            base_multiplier = float(base_multiplier_str)
            logger.critical(f"base_multiplier_str={base_multiplier_str!r}, base_multiplier={base_multiplier!r}")
            multiplied_recipe = mp_utils.add_recipe_multiplier(self.object, base_multiplier)
        return http.HttpResponseRedirect(self.get_object_url(self.object))


class RecipeListView(u_mixins.UserAccessMixin, generic.ListView):
    model = mp_models.Recipe
    fields = ["name"]


class RecipeUpdateView(u_mixins.UserAccessMixin, generic.UpdateView):
    model = mp_models.Recipe
    fields = ["name", "description", "goes_with", "recipe_type"]

    def get_success_url(self):
        return urls.reverse("meal_planning:recipe_detail", args=(self.object.id,))
