from django import urls

from . import views as i_views


app_name = "inventory"


urlpatterns = [
    urls.path("api/category", i_views.APICategoryView.as_view(), name="api_category"),
    urls.path("api/item", i_views.APIItemView.as_view(), name="api_item"),
    urls.path("api/source", i_views.APISourceView.as_view(), name="api_source"),
    urls.path("api/source_item", i_views.APISourceItemView.as_view(), name="api_sourceitem"),
    urls.path("api/unit_size", i_views.APIUnitSizeView.as_view(), name="api_unitsize"),

    urls.path("categories/", i_views.CategoryListView.as_view(), name="category_list"),
    urls.path("category/<int:pk>", i_views.CategoryDetailView.as_view(), name="category_detail"),
    urls.path("category/<int:pk>/delete", i_views.CategoryDeleteView.as_view(), name="category_delete"),
    urls.path("category/<int:pk>/edit", i_views.CategoryUpdateView.as_view(), name="category_update"),
    urls.path("category/new", i_views.CategoryCreateView.as_view(), name="category_create"),

    urls.path("items/", i_views.ItemListView.as_view(), name="item_list"),
    urls.path("item/<int:pk>", i_views.ItemDetailView.as_view(), name="item_detail"),
    urls.path("item/<int:pk>/delete", i_views.ItemDeleteView.as_view(), name="item_delete"),
    urls.path("item/<int:pk>/edit", i_views.ItemUpdateView.as_view(), name="item_update"),
    urls.path("item/new", i_views.ItemCreateView.as_view(), name="item_create"),
    urls.path("item/search", i_views.ItemSearchView.as_view(), name="item_search"),

    urls.path("orders/", i_views.OrderListView.as_view(), name="order_list"),
    urls.path("order/<int:pk>", i_views.OrderDetailView.as_view(), name="order_detail"),
    urls.path("order/<int:pk>/delete", i_views.OrderDeleteView.as_view(), name="order_delete"),
    urls.path("order/<int:pk>/edit", i_views.OrderUpdateView.as_view(), name="order_update"),
    urls.path("order/new", i_views.OrderCreateView.as_view(), name="order_create"),

    urls.path(
        "order/<int:order_pk>/lineitem/<int:pk>", i_views.OrderLineItemDetailView.as_view(),
        name="orderlineitem_detail"),
    urls.path(
        "order/<int:order_pk>/lineitem/<int:pk>/delete", i_views.OrderLineItemDeleteView.as_view(),
        name="orderlineitem_delete"),
    urls.path(
        "order/<int:order_pk>/lineitem/<int:pk>/edit", i_views.OrderLineItemUpdateView.as_view(),
        name="orderlineitem_update"),
    urls.path(
        "order/<int:order_pk>/lineitem/new", i_views.OrderLineItemCreateView.as_view(),
        name="orderlineitem_create"),
    urls.path(
        "order/<int:order_pk>/lineitems", i_views.OrderLineItemFormsetView.as_view(),
        name="orderlineitem_formset"),

    urls.path("sources/", i_views.SourceListView.as_view(), name="source_list"),
    urls.path("source/<int:pk>", i_views.SourceDetailView.as_view(), name="source_detail"),
    urls.path("source/<int:pk>/delete", i_views.SourceDeleteView.as_view(), name="source_delete"),
    urls.path("source/<int:pk>/edit", i_views.SourceUpdateView.as_view(), name="source_update"),
    urls.path("source/new", i_views.SourceCreateView.as_view(), name="source_create"),

    urls.path("source_items/", i_views.SourceItemListView.as_view(), name="sourceitem_list"),
    urls.path("source_item/<int:pk>", i_views.SourceItemDetailView.as_view(), name="sourceitem_detail"),
    urls.path("source_item/<int:pk>/delete", i_views.SourceItemDeleteView.as_view(), name="sourceitem_delete"),
    urls.path("source_item/<int:pk>/edit", i_views.SourceItemUpdateView.as_view(), name="sourceitem_update"),
    urls.path("source_item/new", i_views.SourceItemCreateView.as_view(), name="sourceitem_create"),
    urls.path("source_item/search", i_views.SourceItemSearchView.as_view(), name="sourceitem_search"),

    urls.path("unit_sizes/", i_views.UnitSizeListView.as_view(), name="unitsize_list"),
    urls.path("unit_size/<int:pk>", i_views.UnitSizeDetailView.as_view(), name="unitsize_detail"),
    urls.path("unit_size/<int:pk>/delete", i_views.UnitSizeDeleteView.as_view(), name="unitsize_delete"),
    urls.path("unit_size/<int:pk>/edit", i_views.UnitSizeUpdateView.as_view(), name="unitsize_update"),
    urls.path("unit_size/new", i_views.UnitSizeCreateView.as_view(), name="unitsize_create"),

    urls.path("", i_views.InventoryHomepageView.as_view(), name="homepage"),
]
