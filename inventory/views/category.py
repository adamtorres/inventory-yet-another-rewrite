from django.views import generic

from inventory import models as inv_models


class CategoryListView(generic.ListView):
    model = inv_models.Category
