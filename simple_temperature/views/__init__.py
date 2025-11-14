from django import urls
from django.views import generic

from .. import models as b_models
from .temperature import LeftOffAtView, NewTemperaturesView


class SimpleTemperatureHomepageView(generic.TemplateView):
    template_name = "simple_temperature/homepage.html"
