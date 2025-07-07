from rest_framework import response, views

from .. import models as inv_models, serializers as inv_serializers


class APIUnitSizeView(views.APIView):
    model = inv_models.UnitSize
    serializer = inv_serializers.UnitSizeSerializer

    def get(self, request, format=None):
        return response.Response(self.serializer(self.get_queryset(), many=True).data)

    def get_queryset(self):
        return self.model.objects.all().order_by("unit")
