from django import urls

from . import views as i_views


app_name = "inventory"


urlpatterns = [
    urls.path("categories/", i_views.CategoryListView.as_view(), name="category_list"),
    urls.path("category/<int:pk>", i_views.CategoryDetailView.as_view(), name="category_detail"),
    urls.path("category/<int:pk>/delete", i_views.CategoryDeleteView.as_view(), name="category_delete"),
    urls.path("category/<int:pk>/edit", i_views.CategoryUpdateView.as_view(), name="category_update"),
    urls.path("category/new", i_views.CategoryCreateView.as_view(), name="category_create"),
]
