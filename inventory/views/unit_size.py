from django import http, urls
from django.views import generic
from rest_framework import response, views

from .. import mixins as inv_mixins, models as inv_models, serializers as inv_serializers


class UnitSizeCreateView(inv_mixins.PopupCreateMixin, generic.CreateView):
    model = inv_models.UnitSize
    fields = ["unit"]

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
    ordering = ["unit"]


class UnitSizeUpdateView(generic.UpdateView):
    model = inv_models.UnitSize
    fields = ["unit", "amount"]

    def get_success_url(self):
        return urls.reverse("inventory:unitsize_detail", args=(self.object.id,))


class APIUnitSizeView(views.APIView):
    model = inv_models.UnitSize
    serializer = inv_serializers.UnitSizeSerializer

    def get(self, request, format=None):
        return response.Response(self.serializer(self.get_queryset(), many=True).data)

    def get_queryset(self):
        return self.model.objects.all().order_by("unit")
