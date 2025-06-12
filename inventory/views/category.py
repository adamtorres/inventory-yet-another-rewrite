from django import urls
from django.views import generic

from inventory import models as inv_models


class CategoryCreateView(generic.CreateView):
    model = inv_models.Category
    fields = ["name"]

    def get_success_url(self):
        return urls.reverse("inventory:category_detail", args=(self.object.id,))


class CategoryDeleteView(generic.DeleteView):
    model = inv_models.Category

    def get_success_url(self):
        return urls.reverse("inventory:category_list")

class CategoryDetailView(generic.DetailView):
    queryset = inv_models.Category.objects.all()


class CategoryListView(generic.ListView):
    model = inv_models.Category


class CategoryUpdateView(generic.UpdateView):
    model = inv_models.Category
    fields = ["name"]

    def get_success_url(self):
        return urls.reverse("inventory:category_detail", args=(self.object.id,))
