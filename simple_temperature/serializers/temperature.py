import logging

from django.utils import timezone
from rest_framework import serializers

from .. import models as t_models


logger = logging.getLogger(__name__)


class TemperatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = t_models.Temperature
        fields = ["event_datetime", "location_readings"]

"""
[
  {
    "event_datetime": "2025-11-14 21:17",
    "location_readings": {
      "Chest Freezer(Bakery)": "-1.4800",
      "Chest Freezer(Congregate)": "-1.6600",
      "Cold Table": "36.5000",
      "Walkin Freezer": "5.1800",
      "Walkin Fridge": "36.1400"
    }
  },
  {
    "event_datetime": "2025-11-14 21:18"
    "location_readings": {
      "Cold Table": "36.5000",
      "Walkin Freezer": "5.3600",
      "Walkin Fridge": "36.3200"
    }
  },
  {
    "event_datetime": "2025-11-14 21:19"
    "location_readings": {
      "Chest Freezer(Bakery)": "-1.1200",
      "Chest Freezer(Congregate)": "-1.8400",
      "Cold Table": "36.8600",
      "Walkin Freezer": "5.1800",
      "Walkin Fridge": "36.3200"
    }
  }
]
"""