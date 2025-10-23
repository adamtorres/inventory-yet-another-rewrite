import logging

from django import http, urls
from django.views import generic
from rest_framework import response, views

from .. import models as mkt_models, serializers as mkt_serializers
from user import mixins as u_mixins


logger = logging.getLogger(__name__)


class CategoryCreateView(u_mixins.UserAccessMixin, generic.CreateView):
    model = mkt_models.Category
    fields = ["name"]

    def get_success_url(self):
        return urls.reverse("market:category_detail", args=(self.object.id,))


class CategoryDeleteView(u_mixins.UserAccessMixin, generic.DeleteView):
    model = mkt_models.Category

    def get_success_url(self):
        return urls.reverse("market:category_list")


class CategoryDetailView(u_mixins.UserAccessMixin, generic.DetailView):
    queryset = mkt_models.Category.objects.all()


class CategoryListView(u_mixins.UserAccessMixin, generic.ListView):
    model = mkt_models.Category
    ordering = ["name"]


class CategoryUpdateView(u_mixins.UserAccessMixin, generic.UpdateView):
    model = mkt_models.Category
    fields = ["name"]

    def get_success_url(self):
        return urls.reverse("market:category_detail", args=(self.object.id,))


class APICategoryView(views.APIView):
    model = mkt_models.Category
    serializer = mkt_serializers.CategorySerializer

    def get(self, request, format=None):
        return response.Response(self.serializer(self.get_queryset(), many=True).data)

    def get_queryset(self):
        return self.model.objects.all().order_by("name")
