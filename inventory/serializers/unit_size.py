from rest_framework import serializers

from .. import models as inv_models


class UnitSizeSerializer(serializers.ModelSerializer):

    class Meta:
        model = inv_models.UnitSize
        fields = ["id", "amount", "unit"]
