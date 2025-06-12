from django import urls
from django.views import generic

from inventory import models as inv_models


class SourceItemCreateView(generic.CreateView):
    model = inv_models.SourceItem
    fields = [
        "source", "discontinued", "item_number", "extra_number", "cryptic_name", "expanded_name", "common_name",
        "item", "brand", "source_category"]

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


class SourceItemUpdateView(generic.UpdateView):
    model = inv_models.SourceItem
    fields = [
        "source", "discontinued", "item_number", "extra_number", "cryptic_name", "expanded_name", "common_name",
        "item", "brand", "source_category"]

    def get_success_url(self):
        return urls.reverse("inventory:sourceitem_detail", args=(self.object.id,))
