from django import urls
from django.views import generic

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
        duration_andor_end_date = inv_models.Setting.objects.get_value("report", "date_range")
        context["totals"] = self.object.total_ordered(**duration_andor_end_date)
        start_date, end_date = model_utils.calculate_start_and_end_dates(**duration_andor_end_date)
        context["source_items"] = self.object.source_items.filter(
            line_items__order__delivered_date__range=[start_date, end_date])
        return context


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
    serializer = inv_serializers.ItemSerializer
    order_fields = ["category__name", "name"]
    prefetch_fields = ['category']
    # select_related_fields = ['category']

    search_terms = {
        'name': [
            "name", "source_items__cryptic_name", "source_items__expanded_name", "source_items__common_name"],
        'category': ["category__name"],
    }

