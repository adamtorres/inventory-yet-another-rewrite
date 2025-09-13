import dateparser
from django import urls
from django.db import models
from django.views import generic
from rest_framework import generics

from .. import mixins as inv_mixins, models as inv_models, serializers as inv_serializers
from ..models import utils as model_utils
from . import utils as inv_utils
from user import mixins as u_mixins


class ItemCreateView(u_mixins.UserAccessMixin, inv_mixins.PopupCreateMixin, generic.CreateView):
    model = inv_models.Item
    fields = ["name", "description", "category"]

    def get_success_url(self):
        return urls.reverse("inventory:item_detail", args=(self.object.id,))


class ItemDeleteView(u_mixins.UserAccessMixin, generic.DeleteView):
    model = inv_models.Item

    def get_success_url(self):
        return urls.reverse("inventory:item_list")


class ItemDetailView(u_mixins.UserAccessMixin, generic.DetailView):
    queryset = inv_models.Item.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["totals"] = self.object.total_ordered()
        start_date, end_date = model_utils.calculate_start_and_end_dates()
        context["source_items"] = self.object.source_items.filter(
            line_items__order__delivered_date__range=[start_date, end_date]).distinct()
        context["orders"] = self.object.get_orders()
        return context


class ItemListCurrentView(u_mixins.UserAccessMixin, generic.ListView):
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


class ItemListView(u_mixins.UserAccessMixin, generic.ListView):
    model = inv_models.Item
    paginate_by = 20

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["category"] = self.request.GET.get('category')
        context["categories"] = inv_models.Category.objects.all().order_by('name')
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.GET.get('category')
        if category:
            qs = qs.filter(category__name__iexact=category)
        return qs.order_by().order_by("category__name", "name")


class ItemUpdateView(u_mixins.UserAccessMixin, generic.UpdateView):
    model = inv_models.Item
    fields = ["name", "description", "category"]

    def get_success_url(self):
        return urls.reverse("inventory:item_detail", args=(self.object.id,))


class ItemSearchView(u_mixins.UserAccessMixin, generic.TemplateView):
    template_name = "inventory/item_search.html"
    model = inv_models.Item


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
        item_category_unit_list = []
        for item_category_unit in self.request.GET.getlist("item_category_unit"):
            item_category_unit_list.append(item_category_unit.split("~", 2))
        if self.request.GET.get("as_of_date"):
            as_of_date = dateparser.parse(self.request.GET.get("as_of_date")).date()
        else:
            as_of_date = None
        return self.model.objects.selected_item_detail(item_category_unit_list, as_of_date)
