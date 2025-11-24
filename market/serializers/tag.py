from rest_framework import serializers

from .. import models as mkt_models


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = mkt_models.Tag
        fields = ["id", "value"]
