import dateparser
from django import urls
from django.db import models
from django.views import generic
from rest_framework import generics

from .. import mixins as inv_mixins, models as inv_models, serializers as inv_serializers
from ..models import utils as model_utils
from . import utils as inv_utils


class ItemCreateView(inv_mixins.PopupCreateMixin, generic.CreateView):
    model = inv_models.Item
    fields = ["name", "description", "category"]

    def get_success_url(self):
        return urls.reverse("inventory:item_detail", args=(self.object.id,))


class ItemDeleteView(generic.DeleteView):
    model = inv_models.Item

    def get_success_url(self):
        return urls.reverse("inventory:item_list")


class ItemDetailView(generic.DetailView):
    queryset = inv_models.Item.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["totals"] = self.object.total_ordered()
        start_date, end_date = model_utils.calculate_start_and_end_dates()
        context["source_items"] = self.object.source_items.filter(
            line_items__order__delivered_date__range=[start_date, end_date]).distinct()
        context["orders"] = self.object.get_orders()
        return context


class ItemListCurrentView(generic.ListView):
    model = inv_models.Item
    template_name = "inventory/item_list_current.html"

    # def get_context_data(self, *args, **kwargs):
    #     context = super().get_context_data(*args, **kwargs)
    #     self.object_list
    #     return context

    def get_queryset(self):
        # populates self.object_list
        qs = self.model.objects.example_items()
        qs = qs.prefetch_related("source_items__line_items__order")
        return qs.order_by().order_by("category__name", "name")


class ItemListView(generic.ListView):
    model = inv_models.Item

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by().order_by("category__name", "name")


class ItemUpdateView(generic.UpdateView):
    model = inv_models.Item
    fields = ["name", "description", "category"]

    def get_success_url(self):
        return urls.reverse("inventory:item_detail", args=(self.object.id,))


class ItemSearchView(generic.TemplateView):
    template_name = "inventory/item_search.html"


class APIItemView(inv_utils.APISearchView):
    model = inv_models.Item
    serializer = inv_serializers.APIItemSerializer
    order_fields = ["category__name", "name"]
    prefetch_fields = ['category']
    # select_related_fields = ['category']

    search_terms = {
        'name': [
            "name", "source_items__cryptic_name", "source_items__expanded_name", "source_items__common_name"],
        'category': ["category__name"],
    }


class APISelectedItemDetailView(generics.ListAPIView):
    model = inv_models.Item
    serializer_class = inv_serializers.APISelectedItemSerializer
    pagination_class = None

    def get_queryset(self):
        qs = self.model.objects.all()
        criteria = models.Q()
        to_unit_values = {}
        for item_category_unit in self.request.GET.getlist("item_category_unit"):
            item_name, category_name, to_unit = item_category_unit.split("~", 2)
            criteria |= models.Q(category__name=category_name, name=item_name)
            to_unit_values[f"{item_name}~{category_name}"] = to_unit
        if not criteria:
            return self.model.objects.none()
        data = []
        as_of_date = self.request.GET.get("as_of_date")
        if as_of_date:
            as_of_date = dateparser.parse(as_of_date).date()
        for item in qs.filter(criteria):
            to_unit = to_unit_values[f"{item.name}~{item.category.name}"]
            item.price_in_unit_value = item.price_in_unit(to_unit, as_of_date=as_of_date)
            item.order_date = item.latest_order(as_of_date=as_of_date).get("order_date")
            item.per_unit_price = item.latest_order(as_of_date=as_of_date).get("per_unit_price")
            if item.latest_order(as_of_date=as_of_date).get("subunit_size"):
                item.subunit_size = item.latest_order(as_of_date=as_of_date)["subunit_size"].unit
            else:
                item.subunit_size = None
            if item.latest_order(as_of_date=as_of_date).get("unit_size"):
                item.unit_size = item.latest_order(as_of_date=as_of_date)["unit_size"].unit
            else:
                item.unit_size = None
            item.to_unit = to_unit
            data.append(item)
        return data
