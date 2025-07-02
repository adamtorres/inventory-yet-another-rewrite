from django.views import generic


from .category import CategoryUpdateView, CategoryListView, CategoryDetailView, CategoryDeleteView, CategoryCreateView
from .item import ItemUpdateView, ItemListView, ItemDetailView, ItemDeleteView, ItemCreateView
from .order import OrderUpdateView, OrderListView, OrderDetailView, OrderDeleteView, OrderCreateView
from .order_line_item import (
    OrderLineItemUpdateView, OrderLineItemDetailView, OrderLineItemDeleteView, OrderLineItemCreateView,
    OrderLineItemFormsetView)
from .source import SourceUpdateView, SourceListView, SourceDetailView, SourceDeleteView, SourceCreateView
from .source_item import (
    SourceItemUpdateView, SourceItemListView, SourceItemDetailView, SourceItemDeleteView, SourceItemCreateView)
from .unit_size import UnitSizeUpdateView, UnitSizeListView, UnitSizeDetailView, UnitSizeDeleteView, UnitSizeCreateView

class InventoryHomepageView(generic.TemplateView):
    template_name = "inventory/homepage.html"
