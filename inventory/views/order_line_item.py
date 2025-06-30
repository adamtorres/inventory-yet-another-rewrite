from django import urls
from django.views import generic

from inventory import models as inv_models


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
        return context

    def get_success_url(self):
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
        return context


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
        return urls.reverse("inventory:orderlineitem_detail", args=(self.object.id,))
