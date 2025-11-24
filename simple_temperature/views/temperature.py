import datetime
import logging

from django.utils import timezone
from django.views import generic
from rest_framework import generics, parsers, response, status, views

from .. import models as t_models, serializers as t_serializers


logger = logging.getLogger(__name__)


class LeftOffAtView(views.APIView):
    model = t_models.Temperature

    def get(self, request, format=None):
        return response.Response(self.model.objects.get_last_event_datetime())


class NewTemperaturesView(views.APIView):
    def post(self, request, format=None):
        serializer = t_serializers.TemperatureSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TemperatureListView(generics.ListAPIView):
    queryset = t_models.Temperature.objects.all()
    serializer_class = t_serializers.TemperatureSerializer


class TemperatureGraphView(generic.TemplateView):
    template_name = "simple_temperature/temperature_graph.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_dt = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        base_dt = base_dt.replace(day=18)
        start_dt = base_dt
        end_dt = base_dt + datetime.timedelta(days=1)
        temperature_qs = t_models.Temperature.objects.filter(
            event_datetime__range=[start_dt, end_dt],
            location_readings__has_any_keys=t_models.Temperature.get_all_locations()
        )
        context["graph_data"] = t_models.Temperature.objects.flatten_qs(temperature_qs)
        return context
