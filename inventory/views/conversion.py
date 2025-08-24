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


class ConversionDuplicateView(inv_mixins.PopupCreateMixin, generic.CreateView):
    model = inv_models.Conversion
    form_class = inv_forms.ConversionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # for k, v in context.items():
        #     logger.critical(f"ConversionDuplicateView.get_context_data: {k!r} = {v!r}")
        # logger.critical(context["form"].initial)
        filter_kwargs = {"from_unit": context["form"].initial["from_unit"]}
        context["filter_from_unit"] = context["form"].initial["from_unit"]
        if context["form"].initial.get("item"):
            filter_kwargs["item"] = context["form"].initial.get("item")
            context["filter_item"] = context["form"].initial.get("item")
        else:
            filter_kwargs["item__isnull"] = True
            context["filter_item"] = None
        other_conversions_qs = self.model.objects.filter(**filter_kwargs)
        other_conversions_qs = other_conversions_qs.order_by("item__category__name", "item__name", "from_unit__unit")
        context["other_conversions"] = other_conversions_qs
        return context

    def get_initial(self):
        initial = super().get_initial()
        obj = self.model.objects.get(id=self.kwargs['pk'])
        initial['item'] = obj.item
        initial['from_unit'] = obj.from_unit
        return initial

    def get_success_url(self):
        return urls.reverse("inventory:conversion_detail", args=(self.object.id,))


class ConversionListView(generic.ListView):
    model = inv_models.Conversion
    ordering = ["item__name", "from_unit__unit", "to_unit__unit"]


class ConversionUpdateView(generic.UpdateView):
    model = inv_models.Conversion
    form_class = inv_forms.ConversionForm

    def get_success_url(self):
        return urls.reverse("inventory:conversion_detail", args=(self.object.id,))
