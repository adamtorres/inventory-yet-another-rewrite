import logging

from rest_framework import parsers, response, status, views

from .. import models as t_models, serializers as t_serializers


logger = logging.getLogger(__name__)


class LeftOffAtView(views.APIView):
    model = t_models.Temperature

    def get(self, request, format=None):
        return response.Response(self.model.objects.get_last_event_datetime())


class NewTemperaturesView(views.APIView):
    def get_parser_context(self, http_request):
        logger.debug(f"NewTemperaturesView.get_parser_context: {http_request}")
        return super().get_parser_context(http_request)

    def post(self, request, format=None):
        serializer = t_serializers.TemperatureSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
