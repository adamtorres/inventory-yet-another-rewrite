from django import http


class PopupCreateMixin:
    """
    Used with popup_create.js, this makes the needed adjustments to allow the form to work as a popup.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["popup"] = self.request.GET.get("_popup", "0") == "1"
        return context

    def post(self, request, *args, **kwargs):
        original_return = super().post(request, *args, **kwargs)
        if not (request.GET.get("_popup", "0") == "1"):
            return original_return
        form = self.get_form()
        if not form.is_valid():
            # Don't want to close the popup if there's a problem.
            return original_return
        closing_javascipt = f"""
<script type="text/javascript">
window.opener.postMessage(`{{"id": {self.object.id}}}`, "{request.scheme}://{request.get_host()}");
window.close();
</script>
"""
        return http.HttpResponse(closing_javascipt)
