from django import urls
from django.views import generic
from rest_framework import response, views

from .. import mixins as inv_mixins, models as inv_models, serializers as inv_serializers


class SourceCreateView(inv_mixins.UserAccessMixin, inv_mixins.PopupCreateMixin, generic.CreateView):
    model = inv_models.Source
    fields = ["name", "customer_number"]

    def get_success_url(self):
        return urls.reverse("inventory:source_detail", args=(self.object.id,))


class SourceDeleteView(inv_mixins.UserAccessMixin, generic.DeleteView):
    model = inv_models.Source

    def get_success_url(self):
        return urls.reverse("inventory:source_list")

class SourceDetailView(inv_mixins.UserAccessMixin, generic.DetailView):
    queryset = inv_models.Source.objects.all()


class SourceListView(inv_mixins.UserAccessMixin, generic.ListView):
    model = inv_models.Source
    ordering = ["name", "customer_number"]


class SourceUpdateView(inv_mixins.UserAccessMixin, generic.UpdateView):
    model = inv_models.Source
    fields = ["name", "active", "customer_number"]

    def get_success_url(self):
        return urls.reverse("inventory:source_detail", args=(self.object.id,))


class APISourceView(views.APIView):
    model = inv_models.Source
    serializer = inv_serializers.SourceSerializer

    def get(self, request, format=None):
        include_inactive = True if request.GET.get("include_inactive", "no") == "yes" else False
        qs = self.get_queryset()
        if not include_inactive:
            qs = qs.filter(active=True)
        return response.Response(self.serializer(qs, many=True).data)

    def get_queryset(self):
        return self.model.objects.all().order_by("name")
