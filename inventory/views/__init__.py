from django.views import generic

from .category import (
    CategoryUpdateView, CategoryListView, CategoryDetailView, CategoryDeleteView, CategoryCreateView, APICategoryView,
    APICategoryReportView, ReportCategoryView)
from .conversion import (
    ConversionCreateView, ConversionDeleteView, ConversionDetailView, ConversionDuplicateView, ConversionListView,
    ConversionUpdateView)
from .item import (
    ItemUpdateView, ItemListCurrentView, ItemListView, ItemDetailView, ItemDeleteView, ItemCreateView, ItemSearchView,
    APIItemView, APISelectedItemDetailView)
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
from .stats import StatsView
from .unit_size import (
    UnitSizeUpdateView, UnitSizeListView, UnitSizeDetailView, UnitSizeDeleteView, UnitSizeCreateView, APIUnitSizeView)

from user import mixins as u_mixins


class InventoryHomepageView(u_mixins.UserAccessMixin, generic.TemplateView):
    template_name = "inventory/homepage.html"
