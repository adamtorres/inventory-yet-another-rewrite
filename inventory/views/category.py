import logging

from django import http, urls
from django.views import generic
from rest_framework import response, views

from .. import mixins as inv_mixins, models as inv_models, serializers as inv_serializers


logger = logging.getLogger(__name__)


class CategoryCreateView(inv_mixins.UserAccessMixin, inv_mixins.PopupCreateMixin, generic.CreateView):
    model = inv_models.Category
    fields = ["name", "ingredient"]

    def get_success_url(self):
        return urls.reverse("inventory:category_detail", args=(self.object.id,))


class CategoryDeleteView(inv_mixins.UserAccessMixin, generic.DeleteView):
    model = inv_models.Category

    def get_success_url(self):
        return urls.reverse("inventory:category_list")

class CategoryDetailView(inv_mixins.UserAccessMixin, generic.DetailView):
    queryset = inv_models.Category.objects.all()


class CategoryListView(inv_mixins.UserAccessMixin, generic.ListView):
    model = inv_models.Category
    ordering = ["name"]


class CategoryUpdateView(inv_mixins.UserAccessMixin, generic.UpdateView):
    model = inv_models.Category
    fields = ["name", "ingredient"]

    def get_success_url(self):
        return urls.reverse("inventory:category_detail", args=(self.object.id,))


class APICategoryView(views.APIView):
    model = inv_models.Category
    serializer = inv_serializers.CategorySerializer

    def get(self, request, format=None):
        return response.Response(self.serializer(self.get_queryset(), many=True).data)

    def get_queryset(self):
        return self.model.objects.all().order_by("name")


class APICategoryReportView(views.APIView):
    model = inv_models.Category
    serializer = inv_serializers.CategoryReportSerializer

    def get(self, request, format=None):
        return response.Response(self.serializer(self.get_queryset(), many=True).data)

    def get_queryset(self):
        return self.model.objects.total_ordered().order_by("name")


class ReportCategoryView(inv_mixins.UserAccessMixin,    generic.TemplateView):
    template_name = "inventory/category_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = inv_models.Category.objects.total_ordered()
        context["start_date"] = data["start_date"]
        context["end_date"] = data["end_date"]
        context["total_ordered"] = data["data"]
        return context
