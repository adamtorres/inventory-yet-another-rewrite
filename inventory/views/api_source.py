from rest_framework import response, views

from .. import models as inv_models, serializers as inv_serializers


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
