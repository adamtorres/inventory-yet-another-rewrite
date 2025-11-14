from django import urls

from . import views as i_views


app_name = "simple_temperature"


urlpatterns = [
    urls.path("", i_views.SimpleTemperatureHomepageView.as_view(), name="homepage"),
    urls.path("left_off_at", i_views.LeftOffAtView.as_view(), name="left_off_at"),
    urls.path("new_temperatures", i_views.NewTemperaturesView.as_view(), name="new_temperature"),
]
