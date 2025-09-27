from django import urls
from django.views import generic
from rest_framework import response, views

from .. import mixins as inv_mixins, models as inv_models, serializers as inv_serializers
from user import mixins as u_mixins


class StatsView(u_mixins.UserAccessMixin, generic.TemplateView):
    template_name = "inventory/stats.html"

