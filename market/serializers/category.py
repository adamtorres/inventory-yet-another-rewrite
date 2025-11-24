from rest_framework import serializers

from .. import models as mkt_models


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = mkt_models.Category
        fields = ["id", "name"]
