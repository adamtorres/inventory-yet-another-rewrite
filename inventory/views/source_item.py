from django import urls
from django.views import generic

from inventory import models as inv_models


class SourceItemCreateView(generic.CreateView):
    model = inv_models.SourceItem
    fields = [
        "source", "item_number", "extra_number", "cryptic_name", "expanded_name", "common_name",
        "item", "brand", "source_category", "unit_size", "subunit_size", "active", "quantity", "allow_split_pack"]

    def get_success_url(self):
        return urls.reverse("inventory:sourceitem_detail", args=(self.object.id,))


class SourceItemDeleteView(generic.DeleteView):
    model = inv_models.SourceItem

    def get_success_url(self):
        return urls.reverse("inventory:sourceitem_list")


class SourceItemDetailView(generic.DetailView):
    queryset = inv_models.SourceItem.objects.all()


class SourceItemListView(generic.ListView):
    model = inv_models.SourceItem

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by().order_by(
            "source__name", "item__category__name", "common_name", "expanded_name", "cryptic_name")

class SourceItemUpdateView(generic.UpdateView):
    model = inv_models.SourceItem
    fields = [
        "source", "item_number", "extra_number", "cryptic_name", "expanded_name", "common_name",
        "item", "brand", "source_category", "unit_size", "subunit_size", "active", "quantity", "allow_split_pack"]

    def get_success_url(self):
        return urls.reverse("inventory:sourceitem_detail", args=(self.object.id,))
