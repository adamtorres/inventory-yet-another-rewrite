from django.views import generic

from .category import (
    CategoryUpdateView, CategoryListView, CategoryDetailView, CategoryDeleteView, CategoryCreateView, APICategoryView,
    APICategoryReportView, ReportCategoryView)
from .item import (
    ItemUpdateView, ItemListView, ItemDetailView, ItemDeleteView, ItemCreateView, ItemSearchView, APIItemView)
from .order import (
    OrderUpdateView, OrderListView, OrderDetailView, OrderDeleteView, OrderCreateView, OrderSearchView, APIOrderView)
from .order_line_item import (
    OrderLineItemUpdateView, OrderLineItemDetailView, OrderLineItemDeleteView, OrderLineItemCreateView,
    OrderLineItemFormsetView, OrderLineItemSearchView, APIOrderLineItemView)
from .source import (
    SourceUpdateView, SourceListView, SourceDetailView, SourceDeleteView, SourceCreateView, APISourceView)
from .source_item import (
    SourceItemUpdateView, SourceItemListView, SourceItemDetailView, SourceItemDeleteView, SourceItemCreateView,
    SourceItemSearchView, APISourceItemView)
from .unit_size import (
    UnitSizeUpdateView, UnitSizeListView, UnitSizeDetailView, UnitSizeDeleteView, UnitSizeCreateView, APIUnitSizeView)

class InventoryHomepageView(generic.TemplateView):
    template_name = "inventory/homepage.html"
