from django import urls

from . import views as i_views


app_name = "market"


urlpatterns = [
    urls.path("", i_views.MarketHomepageView.as_view(), name="homepage"),
]
