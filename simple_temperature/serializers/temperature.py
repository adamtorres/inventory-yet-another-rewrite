from rest_framework import serializers

from .. import models as t_models


class TemperatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = t_models.Temperature
        fields = [
            "event_datetime",
            "fahrenheit",
            "celsius",
            "location",
            "raw_data",
            "key_slug",
        ]
