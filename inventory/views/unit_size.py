from django import http, urls
from django.views import generic

from inventory import mixins as inv_mixins, models as inv_models


class UnitSizeCreateView(inv_mixins.PopupCreateMixin, generic.CreateView):
    model = inv_models.UnitSize
    fields = ["unit", "amount"]

    def get_success_url(self):
        return urls.reverse("inventory:unitsize_detail", args=(self.object.id,))


class UnitSizeDeleteView(generic.DeleteView):
    model = inv_models.UnitSize

    def get_success_url(self):
        return urls.reverse("inventory:unitsize_list")

class UnitSizeDetailView(generic.DetailView):
    queryset = inv_models.UnitSize.objects.all()


class UnitSizeListView(generic.ListView):
    model = inv_models.UnitSize
    ordering = ["unit", "amount"]


class UnitSizeUpdateView(generic.UpdateView):
    model = inv_models.UnitSize
    fields = ["unit", "amount"]

    def get_success_url(self):
        return urls.reverse("inventory:unitsize_detail", args=(self.object.id,))
