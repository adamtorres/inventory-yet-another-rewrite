import logging

from django import http, urls
from django.views import generic
from rest_framework import response, views

from .. import models as mkt_models, serializers as mkt_serializers
from user import mixins as u_mixins


logger = logging.getLogger(__name__)


class TagCreateView(u_mixins.UserAccessMixin, generic.CreateView):
    model = mkt_models.Tag
    fields = ["value"]

    def get_success_url(self):
        return urls.reverse("market:tag_detail", args=(self.object.id,))


class TagDeleteView(u_mixins.UserAccessMixin, generic.DeleteView):
    model = mkt_models.Tag

    def get_success_url(self):
        return urls.reverse("market:tag_list")


class TagDetailView(u_mixins.UserAccessMixin, generic.DetailView):
    queryset = mkt_models.Tag.objects.all()


class TagListView(u_mixins.UserAccessMixin, generic.ListView):
    model = mkt_models.Tag
    ordering = ["value"]


class TagUpdateView(u_mixins.UserAccessMixin, generic.UpdateView):
    model = mkt_models.Tag
    fields = ["value"]

    def get_success_url(self):
        return urls.reverse("market:tag_detail", args=(self.object.id,))


class APITagView(views.APIView):
    model = mkt_models.Tag
    serializer = mkt_serializers.TagSerializer

    def get(self, request, format=None):
        return response.Response(self.serializer(self.get_queryset(), many=True).data)

    def get_queryset(self):
        return self.model.objects.all().order_by("value")
