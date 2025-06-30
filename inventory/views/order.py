from django import urls
from django.views import generic

from inventory import models as inv_models


class OrderCreateView(generic.CreateView):
    model = inv_models.Order
    fields = ["source", "order_number", "delivered_date", "po_text", "notes"]
    def get_success_url(self):
        return urls.reverse("inventory:order_detail", args=(self.object.id,))


class OrderDeleteView(generic.DeleteView):
    model = inv_models.Order

    def get_success_url(self):
        return urls.reverse("inventory:order_list")

class OrderDetailView(generic.DetailView):
    queryset = inv_models.Order.objects.all()


class OrderListView(generic.ListView):
    model = inv_models.Order
    ordering = ["-delivered_date", "source__name"]


class OrderUpdateView(generic.UpdateView):
    model = inv_models.Order
    fields = ["source", "order_number", "delivered_date", "po_text", "notes"]

    def get_success_url(self):
        return urls.reverse("inventory:order_detail", args=(self.object.id,))
