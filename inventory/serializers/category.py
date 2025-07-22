from rest_framework import serializers

from .. import models as inv_models


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = inv_models.Category
        fields = ["id", "name"]


class CategoryReportSerializer(serializers.ModelSerializer):
    extended_price = serializers.SerializerMethodField()
    orders = serializers.SerializerMethodField()

    class Meta:
        model = inv_models.Category
        fields = ["id", "name", "extended_price", "orders"]

    def get_extended_price(self, obj):
        return obj["extended_price"]

    def get_orders(self, obj):
        return obj["orders"]
