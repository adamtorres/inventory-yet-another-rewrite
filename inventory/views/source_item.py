from django import urls
from django.views import generic

from .. import forms as inv_forms, mixins as inv_mixins, models as inv_models, serializers as inv_serializers
from ..models import utils as model_utils
from . import utils as inv_utils
from user import mixins as u_mixins


class SourceItemCreateView(u_mixins.UserAccessMixin, inv_mixins.PopupCreateMixin, generic.CreateView):
    model = inv_models.SourceItem
    fields = [
        "source", "item_number", "extra_number", "cryptic_name", "expanded_name", "common_name",
        "item", "brand", "source_category", "unit_size", "unit_amount", "unit_amount_text", "subunit_size",
        "subunit_amount", "subunit_amount_text", "active", "quantity", "allow_split_pack"]

    def get_success_url(self):
        return urls.reverse("inventory:sourceitem_detail", args=(self.object.id,))


class SourceItemDeleteView(u_mixins.UserAccessMixin, generic.DeleteView):
    model = inv_models.SourceItem

    def get_success_url(self):
        return urls.reverse("inventory:sourceitem_list")


class SourceItemDetailView(u_mixins.UserAccessMixin, generic.DetailView):
    queryset = inv_models.SourceItem.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["totals"] = self.object.total_ordered()
        start_date, end_date = model_utils.calculate_start_and_end_dates()
        context["line_items"] = self.object.line_items.filter(order__delivered_date__range=[start_date, end_date])
        return context


class SourceItemListView(u_mixins.UserAccessMixin, generic.ListView):
    model = inv_models.SourceItem

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by().order_by(
            "source__name", "item__category__name", "common_name", "expanded_name", "cryptic_name")

class SourceItemUpdateView(u_mixins.UserAccessMixin, generic.UpdateView):
    model = inv_models.SourceItem
    fields = [
        "source", "item_number", "extra_number", "cryptic_name", "expanded_name", "common_name",
        "item", "brand", "source_category", "unit_size", "unit_amount", "unit_amount_text", "subunit_size",
        "subunit_amount", "subunit_amount_text", "active", "quantity", "allow_split_pack"]

    def get_success_url(self):
        return urls.reverse("inventory:sourceitem_detail", args=(self.object.id,))


class SourceItemSearchView(u_mixins.UserAccessMixin, generic.TemplateView):
    template_name = "inventory/sourceitem_search.html"
    model = inv_models.SourceItem


class SourceItemTestDropDownView(u_mixins.UserAccessMixin, generic.FormView):
    template_name = "inventory/sourceitem_test_dropdown.html"
    model = inv_models.SourceItem
    form_class = inv_forms.SourceItemTestDropDownForm


class APISourceItemView(inv_utils.APISearchView):
    model = inv_models.SourceItem
    serializer = inv_serializers.APISourceItemSerializer
    order_fields = ["item__name", "expanded_name", "cryptic_name"]
    prefetch_fields = ['source', 'item', 'item__category']
    # select_related_fields = ['source', 'item', 'item__category']

    search_terms = {
        'name': ["item__name", "cryptic_name", "expanded_name", "common_name"],
        'code': ["item_number", "extra_number"],
        'unit': [
            "unit_amount", "unit_amount_text", "unit_size__unit",
            "subunit_amount", "subunit_amount_text", "subunit_size__unit"],
        'source': ["source__name", "source__id"],
        'category': ["source_category", "item__category__name"],
        'wider_search': ["item__name", "cryptic_name", "expanded_name", "common_name", "item_number", "extra_number"]
    }
