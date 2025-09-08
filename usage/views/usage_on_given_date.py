import datetime

import dateparser
from django import http, urls
from django.db import models
from django.views import generic

from .. import models as u_models


class UsageOnGivenDateView(generic.TemplateView):
    template_name = "usage/usage_on_given_date.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        given_date = dateparser.parse(kwargs["given_date"]).date()
        context["given_date"] = given_date
        item_qs = u_models.ItemUsage.objects.filter(for_date=given_date).order_by("meal_part", "usage_group__form_order", "id")
        context["used_items"] = item_qs
        context["total"] = item_qs.aggregate(total=models.Sum("price"))["total"]
        context["total_by_meal_part"] = item_qs.order_by("meal_part").values("meal_part").annotate(total=models.Sum("price"))
        return context
