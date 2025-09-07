from django.contrib.auth import views


class LoginView(views.LoginView):
    template_name = "user/login_form.html"
    redirect_authenticated_user = True


class LogoutView(views.LogoutView):
    template_name = "user/logged_out.html"
