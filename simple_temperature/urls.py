from django import urls

from . import views as i_views


app_name = "simple_temperature"


urlpatterns = [
    urls.path("", i_views.SimpleTemperatureHomepageView.as_view(), name="homepage"),
]
