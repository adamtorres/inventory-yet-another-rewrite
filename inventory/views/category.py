import logging

from django import http, urls
from django.views import generic
from rest_framework import response, views

from .. import mixins as inv_mixins, models as inv_models, serializers as inv_serializers


logger = logging.getLogger(__name__)


class CategoryCreateView(inv_mixins.PopupCreateMixin, generic.CreateView):
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
    ordering = ["name"]


class CategoryUpdateView(generic.UpdateView):
    model = inv_models.Category
    fields = ["name"]

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


class ReportCategoryView(generic.TemplateView):
    template_name = "inventory/category_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = inv_models.Category.objects.total_ordered()
        context["start_date"] = data["start_date"]
        context["end_date"] = data["end_date"]
        context["total_ordered"] = data["data"]
        return context
