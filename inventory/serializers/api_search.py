from rest_framework import serializers

from .. import models as inv_models


class APIItemSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = inv_models.Item
        fields = ["id", "name", "description", "category"]

    def get_category(self, obj):
        return obj.category.name


class APIOrderSerializer(serializers.ModelSerializer):
    source = serializers.SerializerMethodField()

    class Meta:
        model = inv_models.Order
        fields = ["id", "source", "delivered_date", "order_number", "po_text", "notes"]

    @staticmethod
    def get_source(obj):
        return obj.source.name


class APIOrderLineItemSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    delivered_date = serializers.SerializerMethodField()
    extra_number = serializers.SerializerMethodField()
    item_number = serializers.SerializerMethodField()
    order_id = serializers.SerializerMethodField()
    order_number = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()
    source_item_name = serializers.SerializerMethodField()
    subunit_amount = serializers.SerializerMethodField()
    subunit_amount_text = serializers.SerializerMethodField()
    subunit_size = serializers.SerializerMethodField()
    unit_amount = serializers.SerializerMethodField()
    unit_amount_text = serializers.SerializerMethodField()
    unit_size = serializers.SerializerMethodField()

    class Meta:
        model = inv_models.OrderLineItem
        fields = [
            "id", "order_id",
            "line_item_number", "quantity_ordered", "quantity_delivered",
            "per_pack_price", "extended_price", "tax", "per_weight_price",
            "per_pack_weights", "total_weight", "notes",
            "source", "delivered_date", "order_number", "category",
            "quantity", "unit_amount", "unit_amount_text", "unit_size",
            "subunit_amount", "subunit_amount_text", "subunit_size",
            "source_item_name", "item_number", "extra_number",
        ]

    @staticmethod
    def get_category(obj):
        return obj.source_item.item.category.name

    @staticmethod
    def get_delivered_date(obj):
        return obj.order.delivered_date

    @staticmethod
    def get_extra_number(obj):
        return obj.source_item.extra_number
    
    @staticmethod
    def get_item_number(obj):
        return obj.source_item.item_number

    @staticmethod
    def get_order_id(obj):
        return obj.order.id

    @staticmethod
    def get_order_number(obj):
        return obj.order.order_number

    @staticmethod
    def get_quantity(obj):
        return obj.source_item.quantity
    
    @staticmethod
    def get_source(obj):
        return obj.order.source.name

    @staticmethod
    def get_source_item_name(obj):
        return obj.source_item.expanded_name or obj.source_item.cryptic_name
    
    @staticmethod
    def get_subunit_amount(obj):
        return obj.source_item.subunit_amount
    
    @staticmethod
    def get_subunit_amount_text(obj):
        return obj.source_item.subunit_amount_text
    
    @staticmethod
    def get_subunit_size(obj):
        return obj.source_item.subunit_size.unit if obj.source_item.subunit_size else None
    
    @staticmethod
    def get_unit_amount(obj):
        return obj.source_item.unit_amount
    
    @staticmethod
    def get_unit_amount_text(obj):
        return obj.source_item.unit_amount_text
    
    @staticmethod
    def get_unit_size(obj):
        return obj.source_item.unit_size.unit if obj.source_item.unit_size else None
    

class APISourceItemSerializer(serializers.ModelSerializer):
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
