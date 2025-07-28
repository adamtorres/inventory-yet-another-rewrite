import json

from django import http, urls
from django.views import generic

from .. import forms as inv_forms, models as inv_models, serializers as inv_serializers
from . import utils as inv_utils


class OrderLineItemCreateView(generic.CreateView):
    model = inv_models.OrderLineItem
    fields = [
        "order", "source_item", "line_item_number", "quantity_ordered", "quantity_delivered", "remote_stock",
        "expect_backorder_delivery", "per_pack_price", "extended_price", "tax", "per_weight_price", "per_pack_weights",
        "total_weight", "notes", "damaged", "rejected", "rejected_reason",]

    def get_initial(self):
        initial = super().get_initial()
        initial['order'] = self.kwargs['order_pk']
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order_pk"] = self.kwargs['order_pk']
        context["source_pk"] = inv_models.Order.objects.get(id=self.kwargs['order_pk']).source.id
        return context

    def get_success_url(self):
        if "save_and_add_another" in self.request.POST:
            return urls.reverse("inventory:orderlineitem_create", args=(self.object.order.pk,))
        return urls.reverse("inventory:orderlineitem_detail", args=(self.object.order.pk, self.object.id,))


class OrderLineItemDeleteView(generic.DeleteView):
    model = inv_models.OrderLineItem

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order_pk"] = self.object.order.pk
        return context

    def get_success_url(self):
        return urls.reverse("inventory:order_detail", args=(self.object.order.pk,))

class OrderLineItemDetailView(generic.DetailView):
    queryset = inv_models.OrderLineItem.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order"] = self.object.order
        context["import_id"] = json.loads(self.object.raw_import_data)["id"]
        return context


class OrderLineItemSearchView(generic.TemplateView):
    template_name = "inventory/orderlineitem_search.html"


class OrderLineItemUpdateView(generic.UpdateView):
    model = inv_models.OrderLineItem
    fields = [
        "order", "source_item", "line_item_number", "quantity_ordered", "quantity_delivered", "remote_stock",
        "expect_backorder_delivery", "per_pack_price", "extended_price", "tax", "per_weight_price", "per_pack_weights",
        "total_weight", "notes", "damaged", "rejected", "rejected_reason",]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order_pk"] = self.kwargs['order_pk']
        return context

    def get_success_url(self):
        return urls.reverse("inventory:orderlineitem_detail", args=(self.object.order.pk, self.object.id,))


class OrderLineItemFormsetView(generic.detail.SingleObjectMixin, generic.FormView):
    # TODO: https://django-autocomplete-light.readthedocs.io/en/master/tutorial.html
    # Or, scrap.forms.widgets.autocomplete to avoid a dependency and possibly allow more customization.
    model = inv_models.Order
    template_name = "inventory/order_line_item_formset_div.html"
    object = None
    pk_url_kwarg = "order_pk"

    def form_valid(self, form):
        form.save()
        # TODO: messages.add_message(blah)
        # self.object.calculate_totals()
        return http.HttpResponseRedirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_form(self, form_class=None):
        # The base get_form does not pass the instance kwarg.
        return inv_forms.OrderLineItemFormset(**self.get_form_kwargs(), instance=self.object)

    def get_success_url(self):
        return urls.reverse("inventory:order_detail", args=(self.object.id,))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class APIOrderLineItemView(inv_utils.APISearchView):
    model = inv_models.OrderLineItem
    serializer = inv_serializers.APIOrderLineItemSerializer
    order_fields = ["-order__delivered_date", "order__source__name", "source_item__cryptic_name"]
    select_related_fields = [
        "source_item", "source_item__item__category", "source_item__unit_size", "source_item__subunit_size", "order"
    ]
    # prefetch_fields = ['line_items', 'line_items__source_item', 'line_items__source_item__item']

    search_terms = {
        'name': [
            "source_item__item__name", "source_item__cryptic_name",
            "source_item__expanded_name", "source_item__common_name"],
        'code': ["source_item__item_number", "source_item__extra_number"],
        'unit': [
            "source_item__unit_amount", "source_item__unit_amount_text",
            "source_item__unit_size__unit",
            "source_item__subunit_amount", "source_item__subunit_amount_text",
            "source_item__subunit_size__unit"],
        'source': ["order__source__name", "order__source__id"],
        'category': ["source_item__source_category", "source_item__item__category__name"],
        'order_number': ["order__order_number"],
    }
