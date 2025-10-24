from django import urls

from . import views as mkt_views


app_name = "market"


urlpatterns = [
    urls.path("", mkt_views.MarketHomepageView.as_view(), name="homepage"),
    urls.path("categories/", mkt_views.CategoryListView.as_view(), name="category_list"),
    urls.path("category/<int:pk>", mkt_views.CategoryDetailView.as_view(), name="category_detail"),
    urls.path("category/<int:pk>/delete", mkt_views.CategoryDeleteView.as_view(), name="category_delete"),
    urls.path("category/<int:pk>/edit", mkt_views.CategoryUpdateView.as_view(), name="category_update"),
    urls.path("category/new", mkt_views.CategoryCreateView.as_view(), name="category_create"),

    urls.path("items/", mkt_views.ItemListView.as_view(), name="item_list"),
    urls.path("item/<int:pk>", mkt_views.ItemDetailView.as_view(), name="item_detail"),
    urls.path("item/<int:pk>/delete", mkt_views.ItemDeleteView.as_view(), name="item_delete"),
    urls.path("item/<int:pk>/edit", mkt_views.ItemUpdateView.as_view(), name="item_update"),
    urls.path("item/new", mkt_views.ItemCreateView.as_view(), name="item_create"),

    urls.path("tags/", mkt_views.TagListView.as_view(), name="tag_list"),
    urls.path("tag/<int:pk>", mkt_views.TagDetailView.as_view(), name="tag_detail"),
    urls.path("tag/<int:pk>/delete", mkt_views.TagDeleteView.as_view(), name="tag_delete"),
    urls.path("tag/<int:pk>/edit", mkt_views.TagUpdateView.as_view(), name="tag_update"),
    urls.path("tag/new", mkt_views.TagCreateView.as_view(), name="tag_create"),
]
