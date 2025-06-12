from django import urls
from django.views import generic

from inventory import models as inv_models


class ItemCreateView(generic.CreateView):
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
