from rest_framework import serializers

from .. import models as inv_models


class SourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = inv_models.Source
        fields = ["id", "name", "active", "customer_number"]
