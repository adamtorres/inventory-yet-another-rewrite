from django import urls

from . import views as u_views


app_name = "user"


urlpatterns = [
    urls.path("login/", u_views.LoginView.as_view(), name="login"),
    urls.path("logout/", u_views.LogoutView.as_view(), name="logout"),
]