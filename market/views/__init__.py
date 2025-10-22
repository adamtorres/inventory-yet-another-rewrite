from django import urls
from django.views import generic

from .. import models as mkt_models


class MarketHomepageView(generic.TemplateView):
    template_name = "market/homepage.html"
