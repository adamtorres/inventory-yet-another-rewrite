from django import urls
from django.views import generic

from .. import models as inv_models, serializers as inv_serializers
from . import utils as inv_utils


class OrderCreateView(generic.CreateView):
    model = inv_models.Order
    fields = ["source", "order_number", "delivered_date", "po_text", "notes"]
    def get_success_url(self):
        return urls.reverse("inventory:order_detail", args=(self.object.id,))


class OrderDeleteView(generic.DeleteView):
    model = inv_models.Order

    def get_success_url(self):
        return urls.reverse("inventory:order_list")

class OrderDetailView(generic.DetailView):
    queryset = inv_models.Order.objects.prefetch_related('line_items').all()


class OrderListView(generic.ListView):
    model = inv_models.Order
    ordering = ["-delivered_date", "source__name"]


class OrderSearchView(generic.TemplateView):
    template_name = "inventory/order_search.html"


class OrderUpdateView(generic.UpdateView):
    model = inv_models.Order
    fields = ["source", "order_number", "delivered_date", "po_text", "notes"]

    def get_success_url(self):
        return urls.reverse("inventory:order_detail", args=(self.object.id,))


class APIOrderView(inv_utils.APISearchView):
    model = inv_models.Order
    serializer = inv_serializers.APIOrderSerializer
    order_fields = ["-delivered_date", "source__name"]
    select_related_fields = ["source"]
    # prefetch_fields = ['line_items', 'line_items__source_item', 'line_items__source_item__item']

    search_terms = {
        'name': [
            "line_items__source_item__item__name", "line_items__source_item__cryptic_name",
            "line_items__source_item__expanded_name", "line_items__source_item__common_name"],
        'code': ["line_items__source_item__item_number", "line_items__source_item__extra_number"],
        'unit': [
            "line_items__source_item__unit_amount", "line_items__source_item__unit_amount_text",
            "line_items__source_item__unit_size__unit",
            "line_items__source_item__subunit_amount", "line_items__source_item__subunit_amount_text",
            "line_items__source_item__subunit_size__unit"],
        'source': ["line_items__source_item__source__name", "line_items__source_item__source__id"],
        'category': ["line_items__source_item__source_category", "line_items__source_item__item__category__name"],
        'order_number': ["order_number"],
    }
