import logging

from django import urls
from django.contrib.auth import mixins, views
from django import shortcuts


logger = logging.getLogger(__name__)


class UserAccessMixin(mixins.PermissionRequiredMixin):
    missing_permission_redirect_url = ""
    missing_permission_redirect_url_name = "user:login"

    def dispatch(self, request, *args, **kwargs):
        if (not self.request.user.is_authenticated):
            # logger.critical(f"UserAccessMixin:{self.request.get_full_path()}, failed is_authenticated")
            return views.redirect_to_login(
                self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())
        if not self.has_permission():
            # logger.critical(f"UserAccessMixin:{self.request.get_full_path()}, failed has_permission")
            return shortcuts.redirect(self.get_missing_permission_redirect_url())
        # logger.critical(f"UserAccessMixin:{self.request.get_full_path()}, dispatching")
        return super().dispatch(request, *args, **kwargs)

    def get_missing_permission_redirect_url(self):
        """
        The urls seem to not be generated in time for urls.reverse() to be used outside a function.  This allows using
        a url name via missing_permission_redirect_url_name.  Will first use missing_permission_redirect_url if set.
        :return: url string
        """
        if self.missing_permission_redirect_url:
            return self.missing_permission_redirect_url
        return urls.reverse(self.missing_permission_redirect_url_name)

    def get_app_label(self):
        """
        We need the lowercase app_label for generating the default permissions.
        :return: lowercase app_label as used in permission.content_type.app_label
        """
        if hasattr(self, "get_queryset"):
            return self.get_queryset().model._meta.app_label
        if hasattr(self, "model"):
            return self.model._meta.app_label
        return None

    def get_model_name(self):
        """
        We need the lowercase model name for generating the default permissions.
        :return: lowercase model name as used in permission.codename
        """
        if hasattr(self, "get_queryset"):
            return self.get_queryset().model._meta.model_name
        if hasattr(self, "model"):
            return self.model._meta.model_name
        return None

    def get_permission_required(self):
        """
        Defaults the permission_required using the model name and a default list of permissions based on the generic
        class used.
        :return: list of permissions, either ones specified by the class or generated from defaults.
        """
        if self.permission_required is None:
            model_name = self.get_model_name()
            app_label = self.get_app_label()
            if model_name is None:
                return []
            default_permission_list = [
                f"{app_label}.{perm}_{model_name}" for perm in self.get_permission_required_list()]
            # logger.critical(f"default_permission_list = {default_permission_list!r}")
            return default_permission_list
        return super().get_permission_required()

    def get_permission_required_list(self):
        """
        Based on the assumption that generic classes ListView and DetailView only needing view permission, if this CBV
        inherits from one of those, return only "view".  If the CBV does not inherit from one of those, assume all
        permissions are needed.
        :return: list of ["view"] or ["add", "change", "delete", "view"].
        """
        is_view_class = False
        for base_class in self.__class__.__bases__:
            if "ListView" in base_class.__name__ or "DetailView" in base_class.__name__:
                is_view_class = True
        if is_view_class:
            return ["view"]
        return ["add", "change", "delete", "view"]
