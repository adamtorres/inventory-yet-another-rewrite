import logging

from rest_framework import serializers


logger = logging.getLogger(__name__)


class APISelectedItemSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    per_unit_price = serializers.SerializerMethodField()
    unit_size = serializers.SerializerMethodField()
    subunit_size = serializers.SerializerMethodField()
    per_other_unit_price = serializers.SerializerMethodField()
    other_unit = serializers.SerializerMethodField()
    order_date = serializers.SerializerMethodField()

    temp_latest_order = None

    class Meta:
        fields = [
            "id", "name", "category", "per_unit_price", "unit_size", "subunit_size", "per_other_unit_price",
            "other_unit", "order_date"]

    def get_id(self, obj):
        return obj.id

    def get_name(self, obj):
        return obj.name

    def get_category(self, obj):
        return obj.category.name

    def get_order_date(self, obj):
        return obj.order_date

    def get_other_unit(self, obj):
        return obj.to_unit

    def get_per_unit_price(self, obj):
        return obj.per_unit_price

    def get_per_other_unit_price(self, obj):
        return obj.price_in_unit_value

    def get_subunit_size(self, obj):
        return obj.subunit_size

    def get_unit_size(self, obj):
        return obj.unit_size
