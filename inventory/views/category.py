import logging

from django import http, urls
from django.views import generic

from inventory import models as inv_models


logger = logging.getLogger(__name__)


class CategoryCreateView(generic.CreateView):
    model = inv_models.Category
    fields = ["name"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["popup"] = self.request.GET.get("_popup", "0") == "1"
        return context

    def get_success_url(self):
        return urls.reverse("inventory:category_detail", args=(self.object.id,))

    def post(self, request, *args, **kwargs):
        original_return = super().post(request, *args, **kwargs)
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


class CategoryDeleteView(generic.DeleteView):
    model = inv_models.Category

    def get_success_url(self):
        return urls.reverse("inventory:category_list")

class CategoryDetailView(generic.DetailView):
    queryset = inv_models.Category.objects.all()


class CategoryListView(generic.ListView):
    model = inv_models.Category
    ordering = ["name"]


class CategoryUpdateView(generic.UpdateView):
    model = inv_models.Category
    fields = ["name"]

    def get_success_url(self):
        return urls.reverse("inventory:category_detail", args=(self.object.id,))
