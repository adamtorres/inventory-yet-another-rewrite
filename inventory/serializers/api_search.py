from rest_framework import serializers

from .. import models as inv_models


class ItemSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = inv_models.Item
        fields = ["id", "name", "description", "category"]

    def get_category(self, obj):
        return obj.category.name


class SourceItemSerializer(serializers.ModelSerializer):
    source = serializers.SerializerMethodField()
    item_name = serializers.SerializerMethodField()
    item_category = serializers.SerializerMethodField()
    item_description = serializers.SerializerMethodField()
    unit_size_unit = serializers.SerializerMethodField()
    subunit_size_unit = serializers.SerializerMethodField()

    class Meta:
        model = inv_models.SourceItem
        fields = [
            "id", "source", "item_category", "item_description", "item_name", "brand", "source_category",
            "unit_size_unit", "unit_amount", "unit_amount_text",
            "subunit_size_unit", "subunit_amount", "subunit_amount_text",
            "active", "quantity", "allow_split_pack", "cryptic_name", "expanded_name", "common_name", "item_number",
            "extra_number"]

    def get_item_category(self, obj):
        return obj.item.category.name

    def get_item_description(self, obj):
        return obj.item.description

    def get_item_name(self, obj):
        return obj.item.name

    def get_source(self, obj):
        return obj.source.name

    def get_subunit_size_unit(self, obj):
        return obj.subunit_size.unit if obj.subunit_size else None

    def get_unit_size_unit(self, obj):
        return obj.unit_size.unit if obj.unit_size else None
