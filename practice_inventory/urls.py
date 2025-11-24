from django.conf import urls
from django.contrib import admin
from django.urls import path
from django.views import generic

from . import views


urlpatterns = [
    path('certainly/not/admin/', admin.site.urls),
    path('inventory/', urls.include('inventory.urls', namespace="inventory")),
    path('market/', urls.include('market.urls', namespace="market")),
    path('meal_planning/', urls.include('meal_planning.urls', namespace="meal_planning")),
    path('usage/', urls.include('usage.urls', namespace="usage")),
    path('user/', urls.include('user.urls', namespace="user")),

    path('htmlcss/flexbox', views.FlexboxView.as_view(), name="flexbox"),
    path('htmlcss/flexbox-examples', views.FlexboxExamplesView.as_view(), name="flexbox_examples"),
    path('htmlcss/responsive_css', views.ResponsiveCSSView.as_view(), name="responsive_css"),
    path('htmlcss/semantic', views.SemanticHTMLView.as_view(), name="semantic_html"),

    path('simple_temperature/', urls.include('simple_temperature.urls', namespace="simple_temperature")),

    path('', generic.RedirectView.as_view(
        pattern_name="inventory:homepage", permanent=False), name="homepage"),
    # Redirect a path-less url to a specific page without it being permanent.
    # path('', generic.RedirectView.as_view(pattern_name="app:urlname", permanent=False), name="homepage"),
]
