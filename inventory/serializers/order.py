from rest_framework import serializers

from .. import models as inv_models


class OrderLineItemSerializer(serializers.ModelSerializer):
    item_category = serializers.SerializerMethodField()
    source_item_extra_number = serializers.SerializerMethodField()
    source_item_item_number = serializers.SerializerMethodField()
    source_item_name = serializers.SerializerMethodField()

    class Meta:
        model = inv_models.OrderLineItem
        fields = [
            "id", "line_item_number", "quantity_ordered", "quantity_delivered", "per_pack_price", "extended_price",
            "per_weight_price", "per_pack_weights", "total_weight", "notes",
            "source_item_extra_number", "source_item_item_number", "source_item_name",
            "item_category",
        ]

    @staticmethod
    def get_item_category(obj):
        return obj.source_item.item.category.name

    @staticmethod
    def get_source_item_extra_number(obj):
        return obj.source_item.extra_number

    @staticmethod
    def get_source_item_item_number(obj):
        return obj.source_item.item_number

    @staticmethod
    def get_source_item_name(obj):
        return obj.source_item.expanded_name or obj.source_item.cryptic_name


class OrderSerializer(serializers.ModelSerializer):
    line_items = OrderLineItemSerializer(many=True, read_only=True)

    class Meta:
        model = inv_models.Order
        fields = ["id", "source", "delivered_date", "order_number", "po_text", "notes", "line_items"]
    # TODO: OrderLineItem, OrderLineItem->SourceItem, OrderLineItem->SourceItem->Item?
