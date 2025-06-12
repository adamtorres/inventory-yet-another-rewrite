from django import urls

from . import views as i_views


app_name = "inventory"


urlpatterns = [
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

    urls.path("", i_views.InventoryHomepageView.as_view(), name="homepage"),
]
