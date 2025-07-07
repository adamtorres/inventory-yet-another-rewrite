from django import urls
from django.views import generic

from .. import mixins as inv_mixins, models as inv_models, serializers as inv_serializers
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
        context["source_items"] = self.object.sourceitem_set.all()
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
            "name", "sourceitem__cryptic_name", "sourceitem__expanded_name", "sourceitem__common_name"],
        'category': ["category__name"],
    }

