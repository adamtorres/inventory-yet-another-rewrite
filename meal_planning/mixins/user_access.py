from inventory import mixins as inv_mixins


class UserAccessMixin(inv_mixins.UserAccessMixin):
    """
    subclassing just in case there is anything that needs changed.  Might move UserAccessMixin to user app.
    """
    missing_permission_redirect_url_name = "user:login"
