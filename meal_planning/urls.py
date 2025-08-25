from django import urls

from . import views as mp_views


app_name = "meal_planning"


urlpatterns = [
    # urls.path("api/category", i_views.APICategoryView.as_view(), name="api_category"),
    urls.path("ingredients/", mp_views.IngredientListView.as_view(), name="ingredient_list"),

    urls.path("recipes/", mp_views.RecipeListView.as_view(), name="recipe_list"),
    urls.path("recipe/<int:pk>", mp_views.RecipeDetailView.as_view(), name="recipe_detail"),
    urls.path("recipe/<int:pk>/delete", mp_views.RecipeDeleteView.as_view(), name="recipe_delete"),
    urls.path("recipe/<int:pk>/edit", mp_views.RecipeUpdateView.as_view(), name="recipe_update"),
    urls.path("recipe/new", mp_views.RecipeCreateView.as_view(), name="recipe_create"),

    urls.path(
        "recipe/<int:recipe_pk>/ingredient/<int:pk>", mp_views.IngredientDetailView.as_view(),
        name="recipe_ingredient_detail"),
    urls.path(
        "recipe/<int:recipe_pk>/ingredient/<int:pk>/delete", mp_views.IngredientDeleteView.as_view(),
        name="recipe_ingredient_delete"),
    urls.path(
        "recipe/<int:recipe_pk>/ingredient/<int:pk>/edit", mp_views.IngredientUpdateView.as_view(),
        name="recipe_ingredient_update"),
    urls.path(
        "recipe/<int:recipe_pk>/ingredient/new", mp_views.IngredientCreateView.as_view(),
        name="recipe_ingredient_create"),

    urls.path(
        "recipe/<int:recipe_pk>/ingredient_group/<int:pk>", mp_views.IngredientGroupDetailView.as_view(),
        name="recipe_ingredient_group_detail"),
    urls.path(
        "recipe/<int:recipe_pk>/ingredient_group/new", mp_views.IngredientGroupCreateView.as_view(),
        name="recipe_ingredient_group_create"),

    urls.path("", mp_views.IngredientHomepageView.as_view(), name="homepage"),
]
