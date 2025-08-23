import logging

from django import http, urls
from django.views import generic
from rest_framework import response, views

from .. import forms as inv_forms, mixins as inv_mixins, models as inv_models, serializers as inv_serializers


logger = logging.getLogger(__name__)


class ConversionCreateView(inv_mixins.PopupCreateMixin, generic.CreateView):
    model = inv_models.Conversion
    form_class = inv_forms.ConversionForm

    def get_success_url(self):
        return urls.reverse("inventory:conversion_detail", args=(self.object.id,))


class ConversionDeleteView(generic.DeleteView):
    model = inv_models.Conversion

    def get_success_url(self):
        return urls.reverse("inventory:conversion_list")

class ConversionDetailView(generic.DetailView):
    queryset = inv_models.Conversion.objects.all()


class ConversionListView(generic.ListView):
    model = inv_models.Conversion
    ordering = ["item__name", "from_unit__unit", "to_unit__unit"]


class ConversionUpdateView(generic.UpdateView):
    model = inv_models.Conversion
    form_class = inv_forms.ConversionForm

    def get_success_url(self):
        return urls.reverse("inventory:conversion_detail", args=(self.object.id,))
