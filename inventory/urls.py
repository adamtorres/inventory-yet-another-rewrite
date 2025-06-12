from django import urls

from . import views as i_views


app_name = "inventory"


urlpatterns = [
    urls.path("categories/", i_views.CategoryListView.as_view(), name="category_list"),
]
