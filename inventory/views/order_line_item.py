from django import http, urls
from django.views import generic

from inventory import forms as inv_forms, models as inv_models


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
