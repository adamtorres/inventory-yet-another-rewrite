from django import urls
from django.views import generic

from inventory import models as inv_models


class SourceCreateView(generic.CreateView):
    model = inv_models.Source
    fields = ["name"]

    def get_success_url(self):
        return urls.reverse("inventory:source_detail", args=(self.object.id,))


class SourceDeleteView(generic.DeleteView):
    model = inv_models.Source

    def get_success_url(self):
        return urls.reverse("inventory:source_list")

class SourceDetailView(generic.DetailView):
    queryset = inv_models.Source.objects.all()


class SourceListView(generic.ListView):
    model = inv_models.Source


class SourceUpdateView(generic.UpdateView):
    model = inv_models.Source
    fields = ["name", "active"]

    def get_success_url(self):
        return urls.reverse("inventory:source_detail", args=(self.object.id,))
