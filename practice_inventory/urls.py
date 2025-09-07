from django.conf import urls
from django.contrib import admin
from django.urls import path
from django.views import generic


urlpatterns = [
    path('admin/', admin.site.urls),
    path('inventory/', urls.include('inventory.urls', namespace="inventory")),
    path('meal_planning/', urls.include('meal_planning.urls', namespace="meal_planning")),
    path('user/', urls.include('user.urls', namespace="user")),

    path('', generic.RedirectView.as_view(
        pattern_name="inventory:homepage", permanent=False), name="homepage"),
    # Redirect a path-less url to a specific page without it being permanent.
    # path('', generic.RedirectView.as_view(pattern_name="app:urlname", permanent=False), name="homepage"),
]
